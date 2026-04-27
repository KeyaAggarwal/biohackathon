# Edison Assembly Guard: Sliding Window Assembly Detection
# Detects split-order attacks by tracking and re-screening reassembled fragments over time.
# Per S.3741 requirements: "The system continuously reassembles fragments in the buffer 
# and re-screens the virtual contig using pLMs."

import hashlib
import torch
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class EdisonAssemblyGuard:
    """
    Full Edison Assembly Guard implementation for detecting split-order attacks.
    
    Architecture:
    - Rolling buffer: Tracks last 50,000 bp across synthesis events
    - Temporal tracking: Records timestamp for each fragment
    - Virtual assembly: Reassembles fragments and checks for hidden toxins
    - Re-screening: Runs Sentinel Head on virtual contigs to detect evasion
    - Cross-day analysis: Detects slow assembly of pathogenic sequences
    """
    
    def __init__(
        self,
        max_bp: int = 50000,
        window_size: int = 100,
        trigger_threshold_bp: int = 10000,
        risk_threshold: float = 0.5,
        sentinel_head=None,
        embedding_wrapper=None
    ):
        """
        Initialize Edison Assembly Guard.
        
        Args:
            max_bp: Maximum buffer size in base pairs (~50,000)
            window_size: Sliding window size for fragment detection
            trigger_threshold_bp: Re-screen buffer when this size exceeded
            risk_threshold: Risk score threshold for flagging sequences
            sentinel_head: SentinelFunctionalHead model for screening
            embedding_wrapper: ESM-2 embedding wrapper for generating embeddings
        """
        self.max_bp = max_bp
        self.window_size = window_size
        self.trigger_threshold_bp = trigger_threshold_bp
        self.risk_threshold = risk_threshold
        self.sentinel_head = sentinel_head
        self.embedding_wrapper = embedding_wrapper
        
        # Rolling buffer with temporal metadata
        self.buffer = []  # List of {'fragment': str, 'timestamp': datetime, 'synthesis_id': str}
        self.buffer_bp = 0  # Current buffer size in bp
        
        # Attack detection log
        self.attacks_flagged = []
        self.reassembly_history = []
    
    def add_fragment(
        self,
        fragment: str,
        synthesis_id: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Add a fragment to the rolling buffer and trigger re-screening if threshold exceeded.
        
        Args:
            fragment: DNA/protein sequence
            synthesis_id: Unique synthesis request ID
            timestamp: When fragment was synthesized (default: now)
        
        Returns:
            Screening result if triggered, None otherwise
        """
        if not timestamp:
            timestamp = datetime.now()
        
        # Add to buffer
        self.buffer.append({
            'fragment': fragment,
            'synthesis_id': synthesis_id,
            'timestamp': timestamp,
            'length': len(fragment)
        })
        self.buffer_bp += len(fragment)
        
        # Trim buffer if exceeded max size (FIFO)
        while self.buffer_bp > self.max_bp and self.buffer:
            removed = self.buffer.pop(0)
            self.buffer_bp -= removed['length']
        
        # Trigger re-screening at threshold
        screening_result = None
        if self.buffer_bp >= self.trigger_threshold_bp:
            screening_result = self._reassemble_and_screen()
        
        return screening_result
    
    def _reassemble_and_screen(self) -> Dict:
        """
        Reassemble all buffered fragments and re-screen the virtual contig.
        
        Returns:
            Dict with virtual sequence, risk score, and attack detection flag
        """
        if not self.buffer:
            return None
        
        # Reassemble virtual contig (all fragments concatenated)
        virtual_sequence = ''.join([item['fragment'] for item in self.buffer])
        virtual_hash = hashlib.sha256(virtual_sequence.encode()).hexdigest()
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'virtual_sequence': virtual_sequence,
            'virtual_hash': virtual_hash,
            'buffer_bp': self.buffer_bp,
            'fragment_count': len(self.buffer),
            'risk_score': None,
            'decision': 'UNKNOWN',
            'is_split_order_attack': False,
            'attack_indicators': []
        }
        
        # Re-screen virtual contig if sentinel head is available
        if self.sentinel_head and self.embedding_wrapper:
            try:
                # Get embeddings for virtual sequence
                embeddings = self.embedding_wrapper.get_embeddings(virtual_sequence)
                
                # Run through sentinel head
                if not isinstance(embeddings, torch.Tensor):
                    embeddings = torch.tensor(embeddings, dtype=torch.float32)
                
                if embeddings.dim() == 1:
                    embeddings = embeddings.unsqueeze(0)
                
                risk_scores, release_tokens = self.sentinel_head(embeddings, sequence_hash=virtual_hash)
                risk_value = risk_scores.item()
                
                result['risk_score'] = risk_value
                result['decision'] = 'BLOCKED' if risk_value >= self.risk_threshold else 'APPROVED'
                
                # Detect split-order attack: individual fragments were safe, but assembly is dangerous
                individual_risks = self._check_individual_fragment_risks()
                if individual_risks['all_safe'] and risk_value >= self.risk_threshold:
                    result['is_split_order_attack'] = True
                    result['attack_indicators'].append("Individual fragments safe, assembly dangerous")
                
            except Exception as e:
                result['error'] = str(e)
        
        # Temporal analysis: detect slow assembly patterns
        temporal_flags = self._analyze_temporal_patterns()
        if temporal_flags:
            result['is_split_order_attack'] = True
            result['attack_indicators'].extend(temporal_flags)
        
        # Record in history
        self.reassembly_history.append(result)
        
        # Flag if attack detected
        if result['is_split_order_attack']:
            self.attacks_flagged.append(result)
            print(f"\n⚠️  SPLIT-ORDER ATTACK DETECTED")
            print(f"  Virtual Hash: {virtual_hash[:16]}...")
            print(f"  Risk Score: {result['risk_score']}")
            print(f"  Indicators: {result['attack_indicators']}")
        
        return result
    
    def _check_individual_fragment_risks(self) -> Dict:
        """
        Check if individual fragments all pass screening but assembly fails.
        This indicates a split-order attack where fragments are innocuous but dangerous when combined.
        
        Returns:
            Dict with individual risk assessments
        """
        if not self.sentinel_head or not self.embedding_wrapper:
            return {'all_safe': True, 'fragments_checked': 0}
        
        all_safe = True
        risky_count = 0
        
        try:
            for item in self.buffer:
                fragment = item['fragment']
                embeddings = self.embedding_wrapper.get_embeddings(fragment)
                
                if not isinstance(embeddings, torch.Tensor):
                    embeddings = torch.tensor(embeddings, dtype=torch.float32)
                
                if embeddings.dim() == 1:
                    embeddings = embeddings.unsqueeze(0)
                
                risk_scores, _ = self.sentinel_head(embeddings)
                risk_value = risk_scores.item()
                
                if risk_value >= self.risk_threshold:
                    all_safe = False
                    risky_count += 1
        
        except Exception as e:
            return {'error': str(e), 'all_safe': True}
        
        return {
            'all_safe': all_safe,
            'fragments_checked': len(self.buffer),
            'risky_fragments': risky_count
        }
    
    def _analyze_temporal_patterns(self) -> List[str]:
        """
        Analyze temporal patterns to detect slow assembly attacks.
        Looks for:
        - Same attacker ordering fragments from different sequences over multiple days
        - Fragments ordered with significant time delays
        
        Returns:
            List of temporal attack indicators
        """
        indicators = []
        
        if len(self.buffer) < 2:
            return indicators
        
        # Check time distribution
        timestamps = [item['timestamp'] for item in self.buffer]
        time_span = max(timestamps) - min(timestamps)
        
        # If fragments span multiple days, could be slow assembly
        if time_span > timedelta(days=1):
            indicators.append(f"Fragments ordered over {time_span.days} days (slow assembly pattern)")
        
        # Check for large time gaps between ordered fragments
        for i in range(len(timestamps) - 1):
            gap = timestamps[i + 1] - timestamps[i]
            if gap > timedelta(hours=24):
                indicators.append(f"Large time gap ({gap.days}d) between fragments {i} and {i+1}")
        
        return indicators
    
    def detect_fragments(self, sequence: str) -> List[str]:
        """
        Create sliding window fragments from a sequence.
        Useful for analyzing incoming sequences for fragment patterns.
        
        Args:
            sequence: DNA/protein sequence
        
        Returns:
            List of overlapping window fragments
        """
        if len(sequence) < self.window_size:
            return [sequence]
        
        fragments = []
        for i in range(len(sequence) - self.window_size + 1):
            fragments.append(sequence[i:i+self.window_size])
        
        return fragments
    
    def get_buffer_status(self) -> Dict:
        """Get current buffer status and statistics."""
        return {
            'buffer_bp': self.buffer_bp,
            'max_bp': self.max_bp,
            'utilization_percent': (self.buffer_bp / self.max_bp) * 100,
            'fragment_count': len(self.buffer),
            'attacks_flagged': len(self.attacks_flagged),
            'reassemblies_triggered': len(self.reassembly_history),
            'oldest_fragment': self.buffer[0]['timestamp'].isoformat() if self.buffer else None,
            'newest_fragment': self.buffer[-1]['timestamp'].isoformat() if self.buffer else None
        }
    
    def clear_buffer(self):
        """Clear the rolling buffer (e.g., at end of day for next day analysis)."""
        self.buffer = []
        self.buffer_bp = 0
    
    def get_attack_report(self) -> Dict:
        """Generate attack detection report."""
        return {
            'total_attacks_flagged': len(self.attacks_flagged),
            'attacks': self.attacks_flagged,
            'reassemblies_history': self.reassembly_history
        }


# Legacy compatibility class
class SlidingWindowDetector(EdisonAssemblyGuard):
    """
    Backward compatibility wrapper for legacy code.
    Use EdisonAssemblyGuard directly for new code.
    """
    def __init__(self, window_size=100, reassembly_threshold=0.8):
        super().__init__(
            window_size=window_size,
            risk_threshold=reassembly_threshold
        )


# Example usage
if __name__ == "__main__":
    guard = EdisonAssemblyGuard(window_size=5)
    
    # Simulate adding fragments over time
    fragment_1 = "ATCGTAGCTAGCTA"
    fragment_2 = "TAGCATGCATGCAT"
    
    guard.add_fragment(fragment_1, "SYN-001")
    guard.add_fragment(fragment_2, "SYN-002")
    
    print("Buffer Status:", guard.get_buffer_status())
    print("Detected fragments:", guard.detect_fragments(fragment_1))
