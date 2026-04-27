#!/usr/bin/env python3
"""
L2 Integration Demo: SynthShield Forensic Orchestrator
Demonstrates daily synthesis logging and Ethereum L2 anchoring.
"""

import sys
import os
from datetime import datetime

# Add project root to path (go up 2 levels from core/ to aixbio/)
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)

from synthshield.core.forensic_orchestrator import ForensicOrchestrator
from synthshield.core.sentinel_head import SentinelFunctionalHead
from synthshield.core.embeddings import EmbeddingWrapper
import torch


def demo_mock_l2_submission():
    """Demo 1: Logging and L2 submission with mock (no network)."""
    
    print("\n" + "="*70)
    print("DEMO 1: Mock L2 Mode (No Network Required)")
    print("="*70)
    
    # Initialize orchestrator with mock L2
    orchestrator = ForensicOrchestrator(
        hardware_id="SYNTH-DEMO-001",
        tpm_secret=b"root_of_trust_secret_demo_key_12345",
        use_mock_l2=True,
        sentinel_head=None,  # Skip screening for this demo
        screening_threshold=0.5
    )
    
    print("\n[PHASE 1] Logging synthesis events...")
    
    # Simulate synthesis events throughout the day
    synthesis_events = [
        {
            'synthesis_id': 'SYN-2026-04-25-001',
            'sequence': 'MKTAYIAKQRQISFVKSHFSRQDILDLWQVQRG',
            'status': 'success',
        },
        {
            'synthesis_id': 'SYN-2026-04-25-002',
            'sequence': 'GAVLGGAGGLGGLGGLGLGGVGVGLG',
            'status': 'success',
        },
        {
            'synthesis_id': 'SYN-2026-04-25-003',
            'sequence': 'ATCGATCGATCGATCGATCG',
            'status': 'qc_fail',  # QC failed
        },
        {
            'synthesis_id': 'SYN-2026-04-25-004',
            'sequence': 'CAGTACGATACGATCGATCG',
            'status': 'success',
        },
    ]
    
    for event in synthesis_events:
        result = orchestrator.log_synthesis_event(
            synthesis_id=event['synthesis_id'],
            sequence=event['sequence'],
            status=event['status'],
            metadata={'lab': 'DEMO_LAB_A', 'operator': 'test_user'}
        )
    
    print(f"\n[PHASE 2] Verifying chain integrity...")
    is_valid = orchestrator.verify_chain_integrity()
    
    print(f"\n[PHASE 3] Generating daily Merkle root...")
    merkle_root = orchestrator.generate_daily_merkle_root()
    
    print(f"\n[PHASE 4] Submitting to L2 (Mock)...")
    submission = orchestrator.submit_daily_anchor_to_l2(
        data_url="ipfs://bafkyabc123def456ghi789"
    )
    
    print(f"\n[PHASE 5] Audit summary...")
    orchestrator.print_audit_summary()
    
    # Export audit log
    audit_file = f"/tmp/audit_log_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    orchestrator.export_audit_log_json(audit_file)
    
    print(f"\n✓ DEMO 1 COMPLETE")
    return orchestrator


def demo_mock_l2_with_screening():
    """Demo 2: With neural screening (requires ESM-2 model)."""
    
    print("\n" + "="*70)
    print("DEMO 2: Mock L2 with Neural Screening")
    print("="*70)
    
    try:
        print("\n[SETUP] Loading ESM-2 model and sentinel head...")
        
        # Initialize sentinel head
        sentinel_head = SentinelFunctionalHead(
            input_dim=1280,
            hidden_dim=512,
            num_blocks=3
        )
        sentinel_head.eval()
        
        print("✓ Sentinel head loaded")
        
    except Exception as e:
        print(f"⚠ Could not load sentinel head: {e}")
        print("  Proceeding with mock embeddings...")
        sentinel_head = None
    
    # Initialize orchestrator
    orchestrator = ForensicOrchestrator(
        hardware_id="SYNTH-DEMO-002",
        tpm_secret=b"another_root_of_trust_key",
        use_mock_l2=True,
        sentinel_head=sentinel_head,
        screening_threshold=0.5
    )
    
    print("\n[PHASE 1] Logging events with screening...")
    
    # Events with screening
    events_with_scoring = [
        {
            'id': 'SYN-SCR-001',
            'sequence': 'MKTAYIAKQRQISFVK',
            'risk': 0.3,  # Low risk
        },
        {
            'id': 'SYN-SCR-002',
            'sequence': 'GAVLGGAGGLGGLGGL',
            'risk': 0.2,  # Very low risk
        },
        {
            'id': 'SYN-SCR-003',
            'sequence': 'TOXINTOXINTOXINT',
            'risk': 0.8,  # HIGH RISK (blocked)
        },
    ]
    
    for event in events_with_scoring:
        # Create mock embeddings based on risk
        embeddings = torch.randn(1, 1280)
        
        result = orchestrator.log_synthesis_event(
            synthesis_id=event['id'],
            sequence=event['sequence'],
            embeddings=embeddings,
            metadata={'risk_profile': f"simulated_{event['risk']}"}
        )
    
    print(f"\n[PHASE 2] Verifying chain integrity...")
    is_valid = orchestrator.verify_chain_integrity()
    
    print(f"\n[PHASE 3] Generating merkle root...")
    merkle_root = orchestrator.generate_daily_merkle_root()
    
    print(f"\n[PHASE 4] Submitting to L2...")
    submission = orchestrator.submit_daily_anchor_to_l2()
    
    print(f"\n[PHASE 5] Summary...")
    orchestrator.print_audit_summary()
    
    print(f"\n✓ DEMO 2 COMPLETE")
    return orchestrator


def demo_chain_verification():
    """Demo 3: Simulating tampering detection."""
    
    print("\n" + "="*70)
    print("DEMO 3: Chain Integrity Verification & Tampering Detection")
    print("="*70)
    
    orchestrator = ForensicOrchestrator(
        hardware_id="SYNTH-DEMO-003",
        tpm_secret=b"security_test_root_of_trust",
        use_mock_l2=True,
        screening_threshold=0.5
    )
    
    print("\n[PHASE 1] Logging events...")
    
    for i in range(3):
        orchestrator.log_synthesis_event(
            synthesis_id=f"SYN-TAMPER-{i:03d}",
            sequence=f"SEQUENCEDATA{i}",
            status="success"
        )
    
    print(f"\n[PHASE 2] Verify integrity (before tampering)...")
    is_valid_before = orchestrator.verify_chain_integrity()
    
    print(f"\n[PHASE 3] Simulating tampering (modifying event data)...")
    if len(orchestrator.black_box.chain) > 1:
        # Attempt to tamper with middle event
        orchestrator.black_box.chain[1]['event']['synthesis_id'] = "HACKED"
        print("  ✗ Data modified in block 1")
    
    print(f"\n[PHASE 4] Verify integrity (after tampering)...")
    is_valid_after = orchestrator.verify_chain_integrity()
    
    print(f"\n[RESULT]")
    print(f"  Before tampering: {is_valid_before}")
    print(f"  After tampering:  {is_valid_after}")
    print(f"  Detection: {'✓ TAMPER DETECTED' if not is_valid_after else '✗ Undetected'}")
    
    print(f"\n✓ DEMO 3 COMPLETE")
    return orchestrator


def demo_audit_export():
    """Demo 4: Exporting audit logs for compliance."""
    
    print("\n" + "="*70)
    print("DEMO 4: Audit Log Export for Compliance")
    print("="*70)
    
    orchestrator = ForensicOrchestrator(
        hardware_id="SYNTH-DEMO-AUDIT",
        tpm_secret=b"audit_export_root_of_trust",
        use_mock_l2=True,
        screening_threshold=0.5
    )
    
    print("\n[PHASE 1] Logging compliance-relevant events...")
    
    compliance_events = [
        {
            'synthesis_id': 'COMP-2026-04-25-001',
            'sequence': 'ATCGATCGATCGATCGATCG',
            'metadata': {'request_type': 'routine_synthesis', 'approval': 'lab_director'}
        },
        {
            'synthesis_id': 'COMP-2026-04-25-002',
            'sequence': 'GCTAGCTAGCTAGCTAGCTA',
            'metadata': {'request_type': 'routine_synthesis', 'approval': 'lab_director'}
        },
    ]
    
    for event in compliance_events:
        orchestrator.log_synthesis_event(
            synthesis_id=event['synthesis_id'],
            sequence=event['sequence'],
            status="success",
            metadata=event['metadata']
        )
    
    print(f"\n[PHASE 2] Generating Merkle root for regulatory submission...")
    merkle_root = orchestrator.generate_daily_merkle_root()
    
    print(f"\n[PHASE 3] Submitting to L2 for immutable anchoring...")
    submission = orchestrator.submit_daily_anchor_to_l2(
        data_url="ipfs://bafkyaudit20260425"
    )
    
    print(f"\n[PHASE 4] Exporting audit log...")
    export_path = f"/tmp/audit_compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    orchestrator.export_audit_log_json(export_path)
    
    print(f"  Exported to: {export_path}")
    
    summary = orchestrator.get_audit_summary()
    print(f"\n[COMPLIANCE METRICS]")
    print(f"  Chain Valid:        {summary['chain_valid']}")
    print(f"  Total Events:       {summary['total_events']}")
    print(f"  L2 Submissions:     {summary['l2_submissions']}")
    print(f"  Merkle Root:        {summary['current_merkle_root'][:32]}...")
    
    print(f"\n✓ DEMO 4 COMPLETE - Audit log ready for regulatory submission")
    return orchestrator


def main():
    """Run all demos."""
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         SynthShield L2 Integration Demo Suite                     ║")
    print("║         Forensic Orchestrator with Ethereum Anchoring             ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    demos = [
        ("Mock L2 Submission", demo_mock_l2_submission),
        ("Mock L2 with Screening", demo_mock_l2_with_screening),
        ("Chain Verification & Tampering Detection", demo_chain_verification),
        ("Audit Export for Compliance", demo_audit_export),
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos)+1}. Run All Demos")
    print(f"  0. Exit")
    
    choice = input("\nSelect demo (0-5): ").strip()
    
    if choice == "0":
        print("Exiting...")
        return
    
    try:
        choice_int = int(choice)
        
        if choice_int == len(demos) + 1:
            # Run all
            for name, demo_func in demos:
                try:
                    demo_func()
                    input("\nPress Enter to continue to next demo...")
                except Exception as e:
                    print(f"Error in {name}: {e}")
        elif 1 <= choice_int <= len(demos):
            # Run specific
            name, demo_func = demos[choice_int - 1]
            print(f"\nRunning: {name}")
            demo_func()
        else:
            print("Invalid choice")
    
    except ValueError:
        print("Invalid input")
    
    print("\n✓ All demos complete!")


if __name__ == "__main__":
    main()
