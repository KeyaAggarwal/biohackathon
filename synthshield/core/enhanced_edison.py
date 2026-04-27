"""
Enhanced Edison Guard with Evasion Detection.

Integrates advanced evasion detection into the existing Edison Assembly Guard
to overcome reassembly and semantic evasion attacks.
"""

from synthshield.core.evasion_detection import EvasionEnsembleScreener
from synthshield.hardware.edison_window import EdisonAssemblyGuard
from typing import Dict, List, Optional


class EvasionAwareEdisonGuard(EdisonAssemblyGuard):
    """
    Enhanced Edison Guard that detects evasion techniques.
    
    Extends the base Edison Guard with:
    - Reverse complement detection
    - Frame shift detection
    - Junk interleaving detection
    - Codon optimization detection
    - Synthetic biology pattern detection
    """
    
    def __init__(self, 
                 max_bp: int = 50000,
                 trigger_threshold_bp: int = 10000,
                 toxin_references: List[str] = None):
        """
        Initialize Evasion-Aware Edison Guard.
        
        Args:
            max_bp: Maximum buffer size (bp)
            trigger_threshold_bp: Threshold to trigger reassembly (bp)
            toxin_references: Known toxin sequences for evasion detection
        """
        super().__init__(max_bp=max_bp, trigger_threshold_bp=trigger_threshold_bp)
        
        self.toxin_references = toxin_references or []
        self.evasion_screener = (
            EvasionEnsembleScreener(toxin_references) 
            if toxin_references else None
        )
        
        # Tracking evasion attempts
        self.evasion_attempts = []
        self.evasion_stats = {
            'reverse_complement': 0,
            'frame_shift': 0,
            'junk_interleaving': 0,
            'codon_optimization': 0,
            'synthetic_patterns': 0,
            'total_evasion_attacks': 0
        }
    
    def add_fragment_with_evasion_check(self, 
                                       fragment: str, 
                                       synthesis_id: str, 
                                       timestamp: float) -> Dict:
        """
        Add fragment and check for evasion techniques.
        
        Args:
            fragment: DNA sequence fragment
            synthesis_id: Unique synthesis order ID
            timestamp: Unix timestamp of order
        
        Returns:
            {
                'added': bool,
                'reason': str,
                'evasion_detected': bool,
                'evasion_details': Dict or None,
                'risk_score': float,
                'recommendation': str
            }
        """
        
        # First, check for evasion techniques
        evasion_result = None
        if self.evasion_screener:
            evasion_result = self.evasion_screener.screen_for_evasion(fragment)
            
            # Track evasion attempts
            if evasion_result['evasion_detected']:
                self.evasion_attempts.append({
                    'synthesis_id': synthesis_id,
                    'timestamp': timestamp,
                    'fragment_length': len(fragment),
                    'attacks': evasion_result['attacks'],
                    'risk_score': evasion_result['risk_score']
                })
                
                # Update statistics
                for attack_type, detected in evasion_result['attacks'].items():
                    if detected:
                        self.evasion_stats[attack_type] += 1
                self.evasion_stats['total_evasion_attacks'] += 1
        
        # Block if evasion detected and high confidence
        if evasion_result and evasion_result['risk_score'] >= 0.6:
            return {
                'added': False,
                'reason': f"Evasion attack detected: {evasion_result['recommendation']}",
                'evasion_detected': True,
                'evasion_details': evasion_result,
                'risk_score': evasion_result['risk_score'],
                'recommendation': 'BLOCK'
            }
        
        # Flag for review if medium confidence
        if evasion_result and evasion_result['risk_score'] >= 0.3:
            print(f"⚠️  Suspicious fragment detected (risk={evasion_result['risk_score']:.2f})")
            print(f"   Evasion attacks: {[k for k,v in evasion_result['attacks'].items() if v]}")
        
        # Otherwise, proceed with normal Edison Guard screening
        self.add_fragment(fragment, synthesis_id, timestamp)
        
        return {
            'added': True,
            'reason': 'Fragment added to buffer',
            'evasion_detected': evasion_result is not None and evasion_result['evasion_detected'],
            'evasion_details': evasion_result,
            'risk_score': evasion_result['risk_score'] if evasion_result else 0.0,
            'recommendation': evasion_result['recommendation'] if evasion_result else 'APPROVE'
        }
    
    def get_evasion_report(self) -> Dict:
        """Generate evasion detection report."""
        return {
            'total_evasion_attempts': self.evasion_stats['total_evasion_attacks'],
            'evasion_attempts_by_type': {
                k: v for k, v in self.evasion_stats.items() 
                if k != 'total_evasion_attacks'
            },
            'blocked_fragments': len(self.evasion_attempts),
            'recent_attempts': self.evasion_attempts[-10:] if self.evasion_attempts else []
        }


class EnhancedScreeningPipeline:
    """
    Multi-layer screening combining traditional and evasion detection.
    """
    
    def __init__(self, 
                 toxin_references: List[str],
                 use_evasion_detection: bool = True):
        """
        Initialize enhanced screening pipeline.
        
        Args:
            toxin_references: Known toxin sequences
            use_evasion_detection: Enable advanced evasion detection
        """
        self.toxin_references = toxin_references
        self.use_evasion_detection = use_evasion_detection
        self.evasion_screener = (
            EvasionEnsembleScreener(toxin_references) 
            if use_evasion_detection else None
        )
        
        # Metrics
        self.screening_log = []
    
    def screen_sequence(self, 
                       sequence: str, 
                       order_metadata: Dict = None) -> Dict:
        """
        Comprehensive screening with multiple layers.
        
        Layer 1: Check sequence against known toxins (traditional)
        Layer 2: Check for evasion techniques (advanced)
        Layer 3: Check for synthetic/unnatural patterns (deep)
        
        Args:
            sequence: DNA sequence to screen
            order_metadata: Additional order information (customer, email, etc.)
        
        Returns:
            {
                'decision': 'APPROVE'|'REVIEW'|'BLOCK',
                'risk_score': float,
                'layer_1_result': {...},
                'layer_2_result': {...},
                'layer_3_result': {...},
                'reasoning': str,
                'recommended_action': str
            }
        """
        
        results = {
            'sequence_length': len(sequence),
            'layers': {}
        }
        
        # Layer 1: Traditional toxin screening
        layer1_risk = self._screen_against_toxins(sequence)
        results['layers']['toxin_match'] = layer1_risk
        
        # Layer 2: Evasion technique detection
        layer2_risk = 0.0
        layer2_details = None
        if self.evasion_screener:
            evasion_result = self.evasion_screener.screen_for_evasion(sequence)
            layer2_risk = evasion_result['risk_score']
            layer2_details = evasion_result
            results['layers']['evasion_detection'] = evasion_result
        
        # Combine risk scores
        # Strategy: Take max (conservative: if ANY layer flags, escalate)
        combined_risk = max(layer1_risk, layer2_risk)
        
        # Make decision
        if combined_risk >= 0.7:
            decision = 'BLOCK'
            reasoning = 'High-risk sequence detected'
        elif combined_risk >= 0.4:
            decision = 'REVIEW'
            reasoning = 'Moderate-risk sequence requires human review'
        else:
            decision = 'APPROVE'
            reasoning = 'Sequence passed all screening layers'
        
        log_entry = {
            'decision': decision,
            'risk_score': combined_risk,
            'layer1_risk': layer1_risk,
            'layer2_risk': layer2_risk,
            'reasoning': reasoning
        }
        self.screening_log.append(log_entry)
        
        return {
            'decision': decision,
            'risk_score': combined_risk,
            'layer_1_risk': layer1_risk,
            'layer_2_risk': layer2_risk,
            'layer_1_details': results['layers']['toxin_match'],
            'layer_2_details': layer2_details,
            'reasoning': reasoning,
            'recommended_action': 'Block and report' if decision == 'BLOCK' else 'Review manually' if decision == 'REVIEW' else 'Approve'
        }
    
    def _screen_against_toxins(self, sequence: str) -> float:
        """
        Traditional toxin screening: check if sequence matches known toxins.
        
        Returns risk score 0-1.
        """
        if not self.toxin_references:
            return 0.0
        
        # Calculate similarity to each reference
        max_similarity = 0.0
        for toxin_ref in self.toxin_references:
            similarity = self._calculate_similarity(sequence, toxin_ref)
            max_similarity = max(max_similarity, similarity)
        
        # Convert similarity to risk score
        return min(max_similarity, 1.0)
    
    @staticmethod
    def _calculate_similarity(seq1: str, seq2: str) -> float:
        """Calculate sequence similarity."""
        if len(seq1) == 0 or len(seq2) == 0:
            return 0.0
        min_len = min(len(seq1), len(seq2))
        matches = sum(1 for i in range(min_len) if seq1[i] == seq2[i])
        return matches / max(len(seq1), len(seq2))
    
    def get_screening_statistics(self) -> Dict:
        """Get screening statistics."""
        if not self.screening_log:
            return {'no_screening_conducted': True}
        
        total_screens = len(self.screening_log)
        approved = sum(1 for log in self.screening_log if log['decision'] == 'APPROVE')
        review = sum(1 for log in self.screening_log if log['decision'] == 'REVIEW')
        blocked = sum(1 for log in self.screening_log if log['decision'] == 'BLOCK')
        
        return {
            'total_screens': total_screens,
            'approved': approved,
            'review': review,
            'blocked': blocked,
            'approval_rate': approved / total_screens if total_screens > 0 else 0,
            'block_rate': blocked / total_screens if total_screens > 0 else 0,
            'avg_risk_score': sum(log['risk_score'] for log in self.screening_log) / total_screens if total_screens > 0 else 0
        }
