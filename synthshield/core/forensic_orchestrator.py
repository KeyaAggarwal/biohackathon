"""
Forensic Orchestrator: Ties BlackBoxChain to L2 Ethereum anchoring.
Provides a unified interface for logging synthesis events and submitting daily proofs.
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from .screening import FunctionalManifoldScreener
from .embeddings import EmbeddingWrapper
from ..hardware.blackbox import BlackBoxChain
from ..hardware.edison_window import EdisonAssemblyGuard
from ..blockchain.ethereum_anchor import EthereumAnchor, MockEthereumAnchor


class ForensicOrchestrator:
    """
    Unified forensic system combining:
    1. Real-time AI screening (Sentinel Head)
    2. Cryptographic event logging (Black Box)
    3. Daily L2 anchoring (Ethereum)
    """
    
    def __init__(
        self,
        hardware_id: str,
        tpm_secret: bytes,
        use_mock_l2: bool = False,
        l2_config: Optional[Dict] = None,
        sentinel_head=None,
        screening_threshold: float = 0.5,
        embedding_wrapper=None,
        enable_edison_rescreen: bool = False,
        embedding_model_name: str = "facebook/esm2_t33_650M_UR50D",
        trained_classifier=None,
    ):
        """
        Initialize the forensic orchestrator.
        
        Args:
            hardware_id: Unique TPM/hardware identifier
            tpm_secret: Root-of-trust secret key (from secure enclave)
            use_mock_l2: If True, use MockEthereumAnchor (no network required)
            l2_config: Dict with keys: contract_address, rpc_url, private_key, network
            sentinel_head: Optional SentinelFunctionalHead for screening
            screening_threshold: Risk score threshold (0.0 - 1.0)
            embedding_wrapper: Optional initialized embedding wrapper
            enable_edison_rescreen: Enable pLM-based Edison virtual contig screening
            embedding_model_name: HF model name used when auto-initializing wrapper
            trained_classifier: Optional TrainedESMClassifier from notebook research
        """
        self.hardware_id = hardware_id
        self.tpm_secret = tpm_secret
        self.use_mock_l2 = use_mock_l2
        
        # Initialize black box chain
        self.black_box = BlackBoxChain(secret_key=tpm_secret)
        
        # Initialize screening with trained classifier if provided
        self.screener = FunctionalManifoldScreener(
            risk_threshold=screening_threshold,
            trained_classifier=trained_classifier
        )
        self.sentinel_head = sentinel_head
        self.embedding_wrapper = embedding_wrapper
        self.enable_edison_rescreen = enable_edison_rescreen
        self.trained_classifier = trained_classifier

        if self.enable_edison_rescreen and self.sentinel_head is not None and self.embedding_wrapper is None:
            try:
                self.embedding_wrapper = EmbeddingWrapper(model_name=embedding_model_name)
            except Exception as exc:
                print(f"[EDISON] Embedding init failed, continuing without re-screening: {exc}")
                self.embedding_wrapper = None
        
        # Initialize Edison Assembly Guard (split-order attack detection)
        self.edison_guard = EdisonAssemblyGuard(
            max_bp=50000,
            window_size=100,
            trigger_threshold_bp=10000,
            risk_threshold=screening_threshold,
            sentinel_head=sentinel_head,
            embedding_wrapper=self.embedding_wrapper
        )
        
        # Initialize L2 anchor
        if use_mock_l2:
            self.l2_anchor = MockEthereumAnchor(hardware_id=hardware_id)
        else:
            if not l2_config:
                raise ValueError("L2 config required when use_mock_l2=False")
            self.l2_anchor = EthereumAnchor(
                contract_address=l2_config['contract_address'],
                rpc_url=l2_config['rpc_url'],
                private_key=l2_config['private_key'],
                hardware_id=hardware_id,
                network=l2_config.get('network', 'optimism')
            )
        
        # Tracking
        self.synthesis_events = []
        self.last_merkle_root = None
        self.last_anchor_time = None
        
        self._log_init()
    
    def _log_init(self):
        """Log initialization."""
        l2_mode = "Mock L2" if self.use_mock_l2 else "Live L2"
        print(f"\n[FORENSIC ORCHESTRATOR] Initialized")
        print(f"  Hardware ID: {self.hardware_id}")
        print(f"  L2 Mode:     {l2_mode}")
        print(f"  Black Box:   Ready")
    
    def log_synthesis_event(
        self,
        synthesis_id: str,
        sequence: str,
        embeddings=None,
        status: str = "pending",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Log a synthesis event with optional screening.
        
        Args:
            synthesis_id: Unique synthesis request ID
            sequence: DNA/protein sequence
            embeddings: Optional ESM-2 embeddings for screening
            status: Event status ('pending', 'success', 'blocked')
            metadata: Additional event metadata
        
        Returns:
            Event result dict with risk_score, decision, and block_hash
        """
        event_data = {
            "type": "synthesis_event",
            "synthesis_id": synthesis_id,
            "sequence_hash": hashlib.sha256(sequence.encode()).hexdigest()[:16],
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Screen if embeddings provided
        screening_result = None
        if embeddings is not None and self.sentinel_head is not None:
            screening_result = self.screener.screen_sequence(
                embeddings,
                self.sentinel_head,
                sequence=sequence
            )
            event_data['risk_score'] = screening_result['risk_score']
            event_data['decision'] = screening_result['decision']
            event_data['release_token'] = screening_result['release_token']
            
            # Update status based on screening
            if screening_result['decision'] == 'BLOCKED':
                event_data['status'] = 'blocked'
        
        # Add to Edison Assembly Guard for split-order attack detection
        edison_result = self.edison_guard.add_fragment(
            fragment=sequence,
            synthesis_id=synthesis_id,
            timestamp=datetime.now()
        )
        
        # Log to black box
        block_hash = self.black_box.log_event(event_data)
        
        result = {
            "synthesis_id": synthesis_id,
            "block_hash": block_hash,
            "event_data": event_data,
            "screening_result": screening_result,
            "edison_result": edison_result
        }
        
        self.synthesis_events.append(result)
        
        print(f"[EVENT] {synthesis_id}")
        print(f"  Block Hash: {block_hash[:16]}...")
        if screening_result:
            print(f"  Risk Score: {screening_result['risk_score']:.3f}")
            print(f"  Decision: {screening_result['decision']}")
        
        # Alert if split-order attack detected
        if edison_result and edison_result.get('is_split_order_attack'):
            print(f"  ⚠️ SPLIT-ORDER ATTACK DETECTED")
            print(f"     Indicators: {edison_result['attack_indicators']}")
        
        return result
    
    def verify_chain_integrity(self) -> bool:
        """
        Verify the entire black box chain is intact (no tampering).
        
        Returns:
            True if chain is valid, False if tampering detected
        """
        is_valid = self.black_box.verify_chain()
        
        status = "✓ VALID" if is_valid else "✗ COMPROMISED"
        print(f"\n[CHAIN VERIFICATION] {status}")
        print(f"  Total Events: {len(self.black_box.chain)}")
        print(f"  Chain Length: {len(self.black_box.chain)} blocks")
        
        if not is_valid:
            print("  WARNING: Chain integrity violation detected!")
        
        return is_valid
    
    def generate_daily_merkle_root(self) -> str:
        """
        Generate Merkle root for daily log aggregation.
        
        Returns:
            Merkle root hash (hex string)
        """
        merkle_root = self.black_box.get_merkle_root()
        self.last_merkle_root = merkle_root
        
        print(f"\n[MERKLE ROOT] Generated for daily aggregation")
        print(f"  Root: {merkle_root[:32]}...")
        print(f"  Events Aggregated: {len(self.black_box.chain)}")
        
        return merkle_root
    
    def submit_daily_anchor_to_l2(
        self,
        data_url: str = "ipfs://bafkyabc123",
        simulate: bool = False
    ) -> Optional[Dict]:
        """
        Submit daily Merkle root to L2 for immutable anchoring.
        
        Args:
            data_url: IPFS hash or URL for full log retrieval
            simulate: If True, estimate gas without submitting
        
        Returns:
            Submission result dict or None on failure
        """
        # Generate fresh Merkle root
        merkle_root = self.generate_daily_merkle_root()
        
        if not merkle_root:
            print("[L2 ANCHOR] No events to anchor")
            return None
        
        # Submit to L2
        print(f"\n[L2 ANCHOR] Submitting daily proof...")
        result = self.l2_anchor.submit_merkle_root(
            merkle_root_hex=merkle_root,
            data_url=data_url,
            simulate=simulate,
            wait_for_receipt=not simulate
        )
        
        if result:
            self.last_anchor_time = datetime.now()
            print(f"[L2 ANCHOR] Daily anchor submitted successfully")
        
        return result
    
    def get_audit_summary(self) -> Dict:
        """
        Generate a comprehensive audit summary for regulatory compliance.
        
        Returns:
            Dict with audit metrics, chain status, L2 submissions, and Edison results
        """
        chain_is_valid = self.black_box.verify_chain()
        merkle_root = self.black_box.get_merkle_root()
        
        # Count synthesis events by status
        status_counts = {}
        for event in self.synthesis_events:
            event_status = event['event_data'].get('status', 'unknown')
            status_counts[event_status] = status_counts.get(event_status, 0) + 1
        
        # Get Edison results
        edison_status = self.edison_guard.get_buffer_status()
        edison_report = self.edison_guard.get_attack_report()
        
        summary = {
            "hardware_id": self.hardware_id,
            "timestamp": datetime.now().isoformat(),
            "chain_valid": chain_is_valid,
            "total_events": len(self.black_box.chain),
            "total_synthesis_requests": len(self.synthesis_events),
            "status_distribution": status_counts,
            "current_merkle_root": merkle_root,
            "last_anchor_time": self.last_anchor_time.isoformat() if self.last_anchor_time else None,
            "l2_submissions": len(self.l2_anchor.get_submission_history()),
            "l2_mode": "Mock" if self.use_mock_l2 else "Live",
            "edison_assembly_guard": {
                "buffer_status": edison_status,
                "split_order_attacks_detected": edison_report['total_attacks_flagged'],
                "reassemblies_triggered": len(edison_report['reassemblies_history'])
            }
        }
        
        return summary
    
    def export_audit_log_json(self, filepath: str = "audit_log.json"):
        """
        Export audit log as JSON for external verification.
        
        Args:
            filepath: Output file path
        """
        edison_report = self.edison_guard.get_attack_report()
        
        audit_data = {
            "metadata": {
                "hardware_id": self.hardware_id,
                "exported_at": datetime.now().isoformat(),
                "l2_mode": "mock" if self.use_mock_l2 else "live"
            },
            "chain_summary": {
                "total_blocks": len(self.black_box.chain),
                "chain_valid": self.black_box.verify_chain(),
                "merkle_root": self.black_box.get_merkle_root()
            },
            "events": [
                event['event_data'] for event in self.synthesis_events
            ],
            "l2_submissions": self.l2_anchor.get_submission_history(),
            "edison_assembly_guard": {
                "total_split_order_attacks": edison_report['total_attacks_flagged'],
                "flagged_attacks": edison_report['attacks'],
                "reassembly_history": edison_report['reassemblies_history']
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        print(f"\n[AUDIT LOG] Exported to {filepath}")
    
    def print_audit_summary(self):
        """Print formatted audit summary."""
        summary = self.get_audit_summary()
        
        print("\n" + "="*70)
        print("FORENSIC AUDIT SUMMARY")
        print("="*70)
        print(f"Hardware ID:        {summary['hardware_id']}")
        print(f"Timestamp:          {summary['timestamp']}")
        print(f"Chain Valid:        {'✓' if summary['chain_valid'] else '✗'}")
        print(f"Total Events:       {summary['total_events']}")
        print(f"Synthesis Requests: {summary['total_synthesis_requests']}")
        print(f"Status Distribution: {summary['status_distribution']}")
        print(f"Current Merkle Root: {summary['current_merkle_root'][:32]}..." if summary['current_merkle_root'] else "None")
        print(f"L2 Submissions:     {summary['l2_submissions']}")
        print(f"L2 Mode:            {summary['l2_mode']}")
        
        # Edison Assembly Guard results
        edison = summary['edison_assembly_guard']
        print(f"\nEdison Assembly Guard:")
        print(f"  Split-Order Attacks:  {edison['split_order_attacks_detected']}")
        print(f"  Reassemblies:         {edison['reassemblies_triggered']}")
        print(f"  Buffer Status:        {edison['buffer_status']['buffer_bp']:.0f} / {edison['buffer_status']['max_bp']} bp ({edison['buffer_status']['utilization_percent']:.1f}%)")
        print("="*70)
