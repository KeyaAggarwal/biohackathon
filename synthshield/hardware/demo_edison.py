#!/usr/bin/env python3
"""
Edison Assembly Guard Demo: Split-Order Attack Detection
Demonstrates the rolling buffer, fragment reassembly, and virtual screening.
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)

from synthshield.hardware.edison_window import EdisonAssemblyGuard
from synthshield.data.datasets import SPLIT_ORDER_FRAGMENTS


def demo_basic_buffer_management():
    """Demo 1: Basic buffer management and retrieval."""
    
    print("\n" + "="*70)
    print("DEMO 1: Edison Buffer Management")
    print("="*70)
    
    guard = EdisonAssemblyGuard(max_bp=1000, trigger_threshold_bp=500)
    
    print("\n[PHASE 1] Adding fragments to rolling buffer...")
    
    fragments = [
        ("SYN-001", "ATCGATCGATCGATCG" * 10),  # 160 bp
        ("SYN-002", "GCTAGCTAGCTAGCTA" * 10),  # 160 bp
        ("SYN-003", "TTTTAAAAAGGGGCCCC" * 10), # 160 bp
    ]
    
    for syn_id, seq in fragments:
        result = guard.add_fragment(seq, syn_id)
        if result:
            print(f"  ✓ Fragment added, reassembly triggered")
            print(f"    Virtual sequence length: {len(result['virtual_sequence'])} bp")
    
    status = guard.get_buffer_status()
    print(f"\n[BUFFER STATUS]")
    print(f"  Current Size:  {status['buffer_bp']} bp / {status['max_bp']} bp")
    print(f"  Utilization:   {status['utilization_percent']:.1f}%")
    print(f"  Fragments:     {status['fragment_count']}")
    print(f"  Oldest:        {status['oldest_fragment']}")
    print(f"  Newest:        {status['newest_fragment']}")


def demo_split_order_fragments():
    """Demo 2: Simulating split-order attack with real dataset."""
    
    print("\n" + "="*70)
    print("DEMO 2: Split-Order Attack Detection (with Dataset)")
    print("="*70)
    
    print(f"\n[DATASET] Loaded {len(SPLIT_ORDER_FRAGMENTS)} split-order attack fragments")
    for frag in SPLIT_ORDER_FRAGMENTS[:2]:
        print(f"\n  Fragment: {frag['id']}")
        print(f"    Description: {frag['description']}")
        print(f"    Part: {frag['part']}/{frag['total_parts']}")
        print(f"    Sequence: {frag['sequence'][:30]}... (length: {len(frag['sequence'])} bp)")
        if 'time_delay_hours' in frag:
            print(f"    Delay: {frag['time_delay_hours']} hours")
    
    guard = EdisonAssemblyGuard(max_bp=5000, trigger_threshold_bp=1000)
    
    print(f"\n[PHASE 1] Simulating split-order attack...")
    print(f"  Day 1: Order part 1 of pore-former")
    
    # Add part 1
    now = datetime.now()
    result = guard.add_fragment(
        SPLIT_ORDER_FRAGMENTS[0]['sequence'],
        SPLIT_ORDER_FRAGMENTS[0]['id'],
        timestamp=now
    )
    
    print(f"  Day 3: Order part 2 (48 hours later)")
    
    # Add part 2
    result = guard.add_fragment(
        SPLIT_ORDER_FRAGMENTS[1]['sequence'],
        SPLIT_ORDER_FRAGMENTS[1]['id'],
        timestamp=now + timedelta(hours=48)
    )
    
    if result and result.get('is_split_order_attack'):
        print(f"\n  ⚠️  SPLIT-ORDER ATTACK DETECTED!")
        print(f"      Indicators: {result['attack_indicators']}")


def demo_temporal_analysis():
    """Demo 3: Temporal pattern detection."""
    
    print("\n" + "="*70)
    print("DEMO 3: Temporal Pattern Analysis")
    print("="*70)
    
    guard = EdisonAssemblyGuard(max_bp=2000, trigger_threshold_bp=500)
    
    print("\n[SCENARIO] User orders DNA fragments over 3 days")
    print("  Each fragment is individually benign")
    print("  But together they form a dangerous pathogen")
    
    base_time = datetime.now()
    
    sequences = [
        ("FRAG-DAY1-A", "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"),  # Day 1
        ("FRAG-DAY1-B", "GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT"),  # Day 1
        ("FRAG-DAY2-A", "TTTTAAAAAGGGGCCCCTTTTAAAAAGGGGCCCCTTTTAAAAAGGGGCCCC"),  # Day 2
        ("FRAG-DAY3-A", "AAAAAGGGGCCCCTTTTAAAAAGGGGCCCCTTTTAAAAAGGGGCCCCTTTT"),  # Day 3
    ]
    
    for i, (syn_id, seq) in enumerate(sequences):
        day = 1 + (i // 2)
        time_offset = timedelta(days=day, hours=i % 2 * 12)
        timestamp = base_time + time_offset
        
        print(f"\n  [{syn_id}] Day {day}, {timestamp.strftime('%H:%M')}")
        result = guard.add_fragment(seq, syn_id, timestamp=timestamp)
        
        if result:
            print(f"    ✓ Reassembly triggered")
            print(f"    Virtual contig length: {len(result['virtual_sequence'])} bp")
            if result.get('attack_indicators'):
                print(f"    Temporal flags: {result['attack_indicators']}")


def demo_window_fragments():
    """Demo 4: Sliding window fragment detection."""
    
    print("\n" + "="*70)
    print("DEMO 4: Sliding Window Fragment Detection")
    print("="*70)
    
    guard = EdisonAssemblyGuard(window_size=10)
    
    sequence = "ATCGATCGATCGATCGATCGATCG"
    print(f"\nSequence: {sequence}")
    print(f"Length: {len(sequence)} bp")
    print(f"Window size: 10 bp")
    
    fragments = guard.detect_fragments(sequence)
    print(f"\nDetected sliding window fragments:")
    for i, frag in enumerate(fragments):
        print(f"  [{i}] {frag}")


def demo_buffer_overflow():
    """Demo 5: Buffer behavior at max capacity."""
    
    print("\n" + "="*70)
    print("DEMO 5: Buffer Behavior at Max Capacity")
    print("="*70)
    
    guard = EdisonAssemblyGuard(max_bp=500, trigger_threshold_bp=200)
    
    print(f"\nMax buffer: 500 bp")
    print("Adding fragments that exceed capacity...")
    
    for i in range(5):
        seq = "ATCGATCG" * 30  # 240 bp each
        result = guard.add_fragment(f"FRAG-{i:02d}", seq)
        
        status = guard.get_buffer_status()
        print(f"\n[Fragment {i}] Added 240 bp")
        print(f"  Buffer: {status['buffer_bp']} bp / {status['max_bp']} bp")
        print(f"  Fragments in buffer: {status['fragment_count']}")
        
        if status['buffer_bp'] > status['max_bp']:
            print(f"  → Buffer exceeded max, trimming oldest fragments")


def main():
    """Run Edison demos."""
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         Edison Assembly Guard Demo Suite                          ║")
    print("║         Split-Order Attack Detection System                       ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    demos = [
        ("Buffer Management", demo_basic_buffer_management),
        ("Split-Order Fragments", demo_split_order_fragments),
        ("Temporal Pattern Analysis", demo_temporal_analysis),
        ("Sliding Window Detection", demo_window_fragments),
        ("Buffer Overflow", demo_buffer_overflow),
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos)+1}. Run All Demos")
    print(f"  0. Exit")
    
    choice = input("\nSelect demo (0-6): ").strip()
    
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
    
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    main()
