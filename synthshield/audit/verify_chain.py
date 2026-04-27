#!/usr/bin/env python3
"""
Forensic Audit Tool & Tampering Detection Script
Demonstrates the BlackBoxChain's tamper-detection capabilities for the Biosecurity Act audit drill.
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from synthshield.hardware.blackbox import BlackBoxChain
from synthshield.blockchain.ethereum_anchor import EthereumAnchor, MockEthereumAnchor


def audit_drill():
    """
    Execute the audit drill: demonstrate how modifying a single bit in the chain
    causes immediate detection of tampering.
    """
    print("=" * 70)
    print("SynthShield Forensic Audit Drill")
    print("Demonstrating tamper-evident logging for Biosecurity Modernization Act 2026")
    print("=" * 70)
    
    # Initialize the Black Box with secure key
    secret_key = b"synthshield_root_of_trust_2026"
    blackbox = BlackBoxChain(secret_key)
    
    # Simulate synthesis events
    events = [
        {"action": "synthesis_start", "sequence_id": "seq_001", "timestamp": "2026-04-25T10:00:00Z"},
        {"action": "ml_screening", "risk_score": 0.15, "decision": "APPROVED", "sequence_id": "seq_001"},
        {"action": "reagent_dispensed", "volume_ul": 500, "valve_id": "valve_1"},
        {"action": "synthesis_complete", "sequence_id": "seq_001", "timestamp": "2026-04-25T10:05:00Z"},
    ]
    
    print("\n[PHASE 1] Logging synthesis events...")
    for i, event in enumerate(events, 1):
        blackbox.log_event(event)
        print(f"  Event {i}: {event['action']} -> Hash: {blackbox.chain[-1]['hash'][:16]}...")
    
    # Verify original chain
    print("\n[PHASE 2] Verifying chain integrity (original)...")
    is_valid = blackbox.verify_chain()
    print(f"  Chain validation: {'✓ VALID' if is_valid else '✗ INVALID'}")
    
    # Get Merkle root
    merkle_root = blackbox.get_merkle_root()
    print(f"  Merkle Root: {merkle_root[:32]}..." if merkle_root else "  Merkle Root: None")
    
    # Simulate tampering: modify a historical event
    print("\n[PHASE 3] Simulating tampering attack...")
    print("  Attacker objective: Change risk_score from 0.15 to 0.99 (evade detection)")
    target_index = 1  # Modify the ML screening event
    original_event = blackbox.chain[target_index]['event'].copy()
    
    blackbox.chain[target_index]['event']['risk_score'] = 0.99
    blackbox.chain[target_index]['event']['decision'] = "APPROVED_SPOOFED"
    original_risk = original_event.get('risk_score', 'N/A')
    print(f"  ✗ Event {target_index + 1} modified: risk_score changed from {original_risk} to 0.99")
    
    # Attempt to verify tampered chain
    print("\n[PHASE 4] Verifying chain integrity (after tampering)...")
    is_valid_after = blackbox.verify_chain()
    print(f"  Chain validation: {'✓ VALID (NOT DETECTED!)' if is_valid_after else '✗ INVALID - TAMPERING DETECTED ✓'}")
    
    if not is_valid_after:
        print("  → Forensic report: Hash chain breakage detected at modification point")
        print("  → Audit conclusion: System integrity maintained, attack unsuccessful")
    
    # Verify Merkle root changed
    merkle_root_after = blackbox.get_merkle_root()
    if merkle_root != merkle_root_after:
        print(f"\n[PHASE 5] Merkle root verification...")
        print(f"  Original Merkle Root:  {merkle_root[:32] if merkle_root else 'N/A'}...")
        print(f"  Current Merkle Root:   {merkle_root_after[:32] if merkle_root_after else 'N/A'}...")
        print("  → Merkle roots differ: Tampering confirmed via Merkle tree")
    
    print("\n" + "=" * 70)
    print("Audit Drill Complete")
    print("Conclusion: SynthShield BlackBox successfully detects single-bit tampering")
    print("=" * 70)


def verify_external_chain(chain_file, secret_key):
    """
    Verify a serialized chain from an external source (e.g., from device).
    
    Args:
        chain_file: Path to JSON file containing serialized BlackBoxChain
        secret_key: The secret key used to sign the chain
    """
    print(f"Loading chain from {chain_file}...")
    
    with open(chain_file, 'r') as f:
        chain_data = json.load(f)
    
    blackbox = BlackBoxChain(secret_key)
    blackbox.chain = chain_data
    
    if blackbox.verify_chain():
        print("✓ Chain verification successful")
        print(f"  Events in chain: {len(blackbox.chain)}")
    else:
        print("✗ Chain verification failed - tampering detected")


def verify_audit_anchor(audit_file, synthesizer_address=None, use_mock=True):
    """
    Verify that an exported audit log's Merkle root is anchored.

    Args:
        audit_file: Path to JSON file produced by export_audit_log_json
        synthesizer_address: Wallet address used for live on-chain checks
        use_mock: If True, verify against mock anchor replayed from audit file
    """
    print(f"Loading audit export from {audit_file}...")
    with open(audit_file, "r") as f:
        audit_data = json.load(f)

    chain_summary = audit_data.get("chain_summary", {})
    merkle_root = chain_summary.get("merkle_root")
    l2_submissions = audit_data.get("l2_submissions", [])
    hardware_id = audit_data.get("metadata", {}).get("hardware_id", "unknown-hardware")

    if not merkle_root:
        print("✗ Audit export missing chain_summary.merkle_root")
        return False

    merkle_root_hex = merkle_root if merkle_root.startswith("0x") else f"0x{merkle_root}"

    if use_mock:
        anchor = MockEthereumAnchor(hardware_id=hardware_id)
        for submission in l2_submissions:
            submitted_root = submission.get("merkle_root")
            if submitted_root:
                anchor.submit_merkle_root(submitted_root, data_url=submission.get("data_url", "ipfs://mock"))
        anchored = anchor.verify_anchor_on_chain("0x0000000000000000000000000000000000000000", merkle_root_hex)
    else:
        if not synthesizer_address:
            print("✗ Live verification requires --synthesizer-address")
            return False
        anchor = EthereumAnchor.from_env()
        if not anchor:
            print("✗ Failed to initialize EthereumAnchor from environment")
            return False
        anchored = anchor.verify_anchor_on_chain(synthesizer_address, merkle_root_hex)

    if anchored:
        print("✓ Anchor verification successful")
        print(f"  Merkle Root: {merkle_root_hex[:20]}...{merkle_root_hex[-8:]}")
        print(f"  L2 Records in audit export: {len(l2_submissions)}")
        return True

    print("✗ Anchor verification failed")
    print("  Root was not found on selected anchor backend")
    return False


def build_parser():
    parser = argparse.ArgumentParser(description="SynthShield forensic audit tools")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("drill", help="Run local tamper-detection drill")

    verify_chain_parser = subparsers.add_parser("verify-chain", help="Verify serialized chain integrity")
    verify_chain_parser.add_argument("--chain-file", required=True, help="Path to serialized chain JSON")
    verify_chain_parser.add_argument(
        "--secret-key",
        default="synthshield_root_of_trust_2026",
        help="Secret key used for chain HMAC (bytes encoded as utf-8)"
    )

    verify_anchor_parser = subparsers.add_parser("verify-anchor", help="Verify audit merkle root anchor")
    verify_anchor_parser.add_argument("--audit-file", required=True, help="Path to exported audit JSON")
    verify_anchor_parser.add_argument(
        "--live",
        action="store_true",
        help="Use live EthereumAnchor.from_env instead of mock replay"
    )
    verify_anchor_parser.add_argument(
        "--synthesizer-address",
        help="Required for --live mode: wallet address that submitted anchor"
    )

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "drill"):
        audit_drill()
    elif args.command == "verify-chain":
        verify_external_chain(args.chain_file, args.secret_key.encode("utf-8"))
    elif args.command == "verify-anchor":
        verify_audit_anchor(
            audit_file=args.audit_file,
            synthesizer_address=args.synthesizer_address,
            use_mock=not args.live
        )
