# SynthShield Unified Pipeline: Usage Guide & Examples

**Date:** April 26, 2026  
**Version:** 2.0 - Unified Pipeline  
**Status:** Complete & Ready for Production

---

## Quick Start

### Installation & Import

```python
from synthshield.pipeline import SynthShieldPipeline, create_pipeline, SynthesisDecision

# Create pipeline (simple)
pipeline = create_pipeline(
    hardware_id="SYNTH-LAB-001",
    config={
        'toxin_references': ["ATCG...", "GCTA..."],
        'use_blockchain': True,
        'enable_edison_guard': True
    }
)

# Or create with full control
from synthshield.pipeline import SynthShieldPipeline

pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-FACTORY-001",
    toxin_references=[...],
    use_blockchain=True,
    use_trained_classifier=True,
    enable_edison_guard=True,
    enable_logging=True
)
```

### Basic Usage (Single DNA Sequence)

```python
# Process one DNA synthesis order
dna = "ATCGATCGATCGATCGATCG"

result = pipeline.process_synthesis_order(
    dna_sequence=dna,
    metadata={
        'customer': 'AcmeBio Inc.',
        'lab': 'Lab-A',
        'timestamp': time.time()
    }
)

# Access results
print(f"Decision: {result.decision}")                    # APPROVED, BLOCKED, or REVIEW
print(f"Risk Score: {result.risk_scores.combined:.1%}")
print(f"Hardware Auth: {result.hardware_authorized}")
print(f"L2 Record: {result.blockchain_record}")

# Full JSON report
print(result.to_json())
```

### Output Structure

```python
result = pipeline.process_synthesis_order(dna)

# Decision information
result.decision                  # SynthesisDecision enum: APPROVED|BLOCKED|REVIEW
result.decision_reasoning        # Human-readable explanation
result.recommendations           # List of actionable recommendations

# Risk scores
result.risk_scores.combined      # 0.0-1.0 (combined evasion + neural)
result.risk_scores.evasion       # 0.0-1.0 (semantic attack risk)
result.risk_scores.neural        # 0.0-1.0 (neural screening risk)
result.risk_level                # RiskLevel enum: LOW|MEDIUM|HIGH|CRITICAL

# Evasion detection details
result.evasion_details.detected                      # bool: was evasion detected?
result.evasion_details.attacks_found                 # List[str]: types of attacks
result.evasion_details.reverse_complement_risk       # 0.0-1.0
result.evasion_details.frame_shift_risk              # 0.0-1.0
result.evasion_details.junk_interleaving_risk        # 0.0-1.0
result.evasion_details.codon_optimization_risk       # 0.0-1.0
result.evasion_details.synthetic_pattern_risk        # 0.0-1.0

# Hardware & blockchain
result.hardware_authorized       # bool: did hardware accept token?
result.valve_state              # 'OPEN'|'CLOSED'|'ERROR'
result.blockchain_record        # dict: L2 submission details
result.block_hash               # str: black box chain hash

# Metadata
result.sequence_hash            # str: SHA-256 of input DNA
result.processing_time_ms       # float: total processing time
result.metadata                 # dict: echoed back input metadata
result.audit_trail              # list: all 8 stages with timestamps
```

---

## Complete Examples

### Example 1: Single Sequence Screening

```python
from synthshield.pipeline import SynthShieldPipeline, SynthesisDecision

# Initialize
pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-001",
    toxin_references=["ATCGATCGATCG"],
    use_blockchain=False,
    mock_blockchain=True
)

# Screen a sequence
dna = "ATCGATCGATCGATCGATCG"
result = pipeline.process_synthesis_order(
    dna_sequence=dna,
    metadata={'customer': 'Test Customer'}
)

# Handle decision
if result.decision == SynthesisDecision.APPROVED:
    print("✓ DNA approved for synthesis")
    if result.hardware_authorized:
        print("✓ Hardware valve opened automatically")
    else:
        print("! Hardware authorization failed")

elif result.decision == SynthesisDecision.BLOCKED:
    print(f"✗ DNA blocked: {result.decision_reasoning}")
    print("Recommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")

else:  # REVIEW
    print("? Manual review needed")
    print(f"Risk: {result.risk_scores.combined:.1%}")
    if result.evasion_details.detected:
        print(f"Attacks detected: {', '.join(result.evasion_details.attacks_found)}")
```

### Example 2: Fragment-Based Assembly (Split-Order Detection)

```python
from synthshield.pipeline import SynthShieldPipeline
import time

pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-002",
    toxin_references=["DANGEROUS_TOXIN_ATCG"],
    enable_edison_guard=True
)

# Customer orders DNA in 3 fragments (split-order attack pattern)
fragments = [
    ("frag_1", "ATCG..."),  # Fragment 1: benign on its own
    ("frag_2", "GCTA..."),  # Fragment 2: benign on its own
    ("frag_3", "TTAA...")   # Fragment 3: benign on its own
]

# Process each fragment
for frag_id, frag_dna in fragments:
    result = pipeline.process_synthesis_order(
        dna_sequence=frag_dna,
        metadata={'customer': 'BadActor Inc.'},
        is_fragment=True,
        fragment_id=frag_id
    )
    
    if result.is_split_order_attack:
        print(f"✗ SPLIT-ORDER ATTACK DETECTED on {frag_id}")
        print(f"  Full assembly would create: DANGEROUS_TOXIN")
        print(f"  Blocked: {result.decision_reasoning}")
        break
    else:
        print(f"✓ {frag_id}: OK (buffer_size={result.edison_status.get('buffer_size')})")
```

### Example 3: Batch Processing with L2 Anchoring

```python
from synthshield.pipeline import create_pipeline, SynthesisDecision
import json

pipeline = create_pipeline(
    hardware_id="SYNTH-FACILITY-001",
    config={
        'toxin_references': ["TOXIN1", "TOXIN2", "TOXIN3"],
        'use_blockchain': True,
        'enable_edison_guard': True,
        'mock_blockchain': False  # Real L2 submission
    }
)

# Batch of orders to process
orders = [
    {
        'dna': 'ATCGATCGATCGATCGATCG',
        'customer': 'CustA',
        'order_id': 'ORD-001'
    },
    {
        'dna': 'GCTAGCTAGCTAGCTAGCTA',
        'customer': 'CustB',
        'order_id': 'ORD-002'
    },
    {
        'dna': 'TTAATTAATTAATTAATTAA',
        'customer': 'CustC',
        'order_id': 'ORD-003'
    }
]

# Process all
results = []
for order in orders:
    result = pipeline.process_synthesis_order(
        dna_sequence=order['dna'],
        metadata={
            'customer': order['customer'],
            'order_id': order['order_id'],
            'timestamp': time.time()
        }
    )
    results.append(result)
    
    # Report status
    status = "✓" if result.decision == SynthesisDecision.APPROVED else "✗"
    print(f"{status} {order['order_id']}: {result.decision.value} "
          f"(risk={result.risk_scores.combined:.1%}, time={result.processing_time_ms:.0f}ms)")

# Generate batch report
print("\n=== BATCH SUMMARY ===")
approved = sum(1 for r in results if r.decision == SynthesisDecision.APPROVED)
blocked = sum(1 for r in results if r.decision == SynthesisDecision.BLOCKED)
review = sum(1 for r in results if r.decision == SynthesisDecision.REVIEW)
total_time = sum(r.processing_time_ms for r in results)

print(f"Approved: {approved}/{len(results)}")
print(f"Blocked: {blocked}/{len(results)}")
print(f"Review: {review}/{len(results)}")
print(f"Total time: {total_time:.0f}ms")

# L2 blockchain anchoring (if using blockchain)
print(f"\nBlockchain Records:")
for i, result in enumerate(results):
    if result.blockchain_record:
        print(f"  Order {i+1}: {result.blockchain_record}")
```

### Example 4: Handling Evasion Attacks

```python
from synthshield.pipeline import SynthShieldPipeline

pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-003",
    toxin_references=["ATCGATCGATCG"],  # Real toxin
    enable_logging=True
)

# Test different evasion techniques
test_cases = {
    "reverse_complement": "CGAT",  # Reverse complement of toxic region
    "frame_shift": "ATCGATCGATCGATCGATCG",  # With frame shift
    "junk_inserted": "NNNATCGATCGATCGATCGATCGNN",  # With junk sequences
    "codon_optimized": "ATTCGTTCTGATCGATCGATCG",  # Optimized codons
    "normal_sequence": "GATTACA",  # Control: should be safe
}

for attack_name, dna in test_cases.items():
    result = pipeline.process_synthesis_order(
        dna_sequence=dna,
        metadata={'attack_type': attack_name}
    )
    
    print(f"\n{attack_name.upper()}")
    print(f"  Decision: {result.decision.value}")
    if result.evasion_details.detected:
        print(f"  Evasion Risk: {result.evasion_details.detected}")
        print(f"  Attacks: {result.evasion_details.attacks_found}")
        print(f"  Individual scores:")
        for score_name, score_val in result.risk_scores.individual_evasion_scores.items():
            if score_val > 0:
                print(f"    - {score_name}: {score_val:.3f}")
    else:
        print(f"  Risk: {result.risk_scores.combined:.1%}")
```

### Example 5: Audit Trail Inspection

```python
from synthshield.pipeline import SynthShieldPipeline
import json

pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-004",
    toxin_references=["ATCGATCGATCG"],
    enable_logging=True
)

result = pipeline.process_synthesis_order(
    dna_sequence="ATCGATCGATCG",
    metadata={'customer': 'Audit Customer'}
)

# Inspect audit trail
print("=== AUDIT TRAIL ===")
print(f"Total stages: {len(result.audit_trail)}")
print(f"Processing time: {result.processing_time_ms:.1f}ms")
print(f"Chain valid: {result.chain_valid}")
print(f"Block hash: {result.block_hash}")

print("\nStage-by-stage breakdown:")
for stage in result.audit_trail:
    stage_num = stage.get('stage', '?')
    stage_name = stage.get('name', 'Unknown')
    status = stage.get('status', 'unknown')
    timestamp = stage.get('timestamp', 0)
    
    print(f"  Stage {stage_num}: {stage_name} [{status}]")
    
    # Show stage-specific details
    for key, val in stage.items():
        if key not in ['stage', 'name', 'status', 'timestamp']:
            print(f"    - {key}: {val}")

# Export full audit log
audit_json = json.dumps(result.audit_trail, indent=2)
with open(f"audit_{result.sequence_hash}.json", "w") as f:
    f.write(audit_json)
```

### Example 6: Integration with External Systems

```python
from synthshield.pipeline import create_pipeline, SynthesisDecision
import requests
from datetime import datetime

# Pipeline for production facility
pipeline = create_pipeline(
    hardware_id="SYNTH-PRODUCTION-01",
    config={
        'toxin_references': ["TOXIN_A", "TOXIN_B", "TOXIN_C"],
        'use_blockchain': True,
        'enable_edison_guard': True
    }
)

def process_and_report_to_lims(dna: str, order_id: str, customer_email: str):
    """
    Process DNA and report results to LIMS (Laboratory Information Management System)
    """
    
    # Process through pipeline
    result = pipeline.process_synthesis_order(
        dna_sequence=dna,
        metadata={
            'order_id': order_id,
            'customer_email': customer_email,
            'timestamp': datetime.now().isoformat()
        }
    )
    
    # Prepare LIMS report
    lims_report = {
        'order_id': order_id,
        'decision': result.decision.value,
        'risk_level': result.risk_level.value,
        'risk_score': result.risk_scores.combined,
        'approved': result.decision == SynthesisDecision.APPROVED,
        'hardware_ready': result.hardware_authorized,
        'blockchain_record': result.blockchain_record.get('tx_hash', 'pending'),
        'processing_time_ms': result.processing_time_ms,
        'audit_trail_hash': result.block_hash,
        'timestamp': datetime.now().isoformat()
    }
    
    # Send to LIMS
    try:
        response = requests.post(
            'https://lims.company.com/api/synthesis-results',
            json=lims_report,
            headers={'Authorization': f'Bearer {LIMS_API_TOKEN}'}
        )
        if response.status_code == 200:
            print(f"✓ LIMS report submitted for {order_id}")
        else:
            print(f"✗ LIMS submission failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error reporting to LIMS: {e}")
    
    # Send email notification
    if result.decision == SynthesisDecision.BLOCKED:
        send_email(
            to=customer_email,
            subject=f"DNA Order {order_id} - Cannot Process",
            body=f"Your DNA sequence was blocked due to: {result.decision_reasoning}\n\n"
                 f"Recommendations:\n" + "\n".join(f"- {r}" for r in result.recommendations)
        )
    elif result.decision == SynthesisDecision.APPROVED:
        send_email(
            to=customer_email,
            subject=f"DNA Order {order_id} - Approved for Synthesis",
            body=f"Your DNA sequence has been approved and synthesis is proceeding.\n"
                 f"Risk assessment: {result.risk_scores.combined:.1%}\n"
                 f"Blockchain record: {result.blockchain_record.get('tx_hash', 'N/A')}"
        )
    
    return result, lims_report
```

---

## Configuration Options

### Basic Configuration

```python
# Minimal config (safe defaults)
pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-001"
)

# Medium config (recommended)
pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-LAB-001",
    toxin_references=["ATCG...", "GCTA..."],
    use_blockchain=False,  # Enable for production
    use_trained_classifier=True,
    enable_edison_guard=True,
    enable_logging=True
)

# Full production config
pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-PROD-001",
    toxin_references=[...],  # Load from database
    use_blockchain=True,      # Real L2 anchoring
    use_trained_classifier=True,
    trained_classifier_path="/path/to/model.pkl",
    enable_edison_guard=True,
    enable_logging=True,
    mock_blockchain=False,
    tpm_secret=os.environ['TPM_SECRET']
)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hardware_id` | str | Required | Hardware identifier |
| `toxin_references` | List[str] | [] | Known dangerous sequences |
| `use_blockchain` | bool | False | Enable L2 anchoring |
| `use_trained_classifier` | bool | True | Use ML classifier ensemble |
| `trained_classifier_path` | Optional[str] | None | Path to trained model |
| `enable_edison_guard` | bool | True | Enable split-order detection |
| `enable_logging` | bool | True | Enable cryptographic logging |
| `mock_blockchain` | bool | False | Use mock instead of real L2 |
| `tpm_secret` | bytes | default | TPM secret key |

---

## Error Handling

```python
from synthshield.pipeline import SynthShieldPipeline, SynthesisDecision

pipeline = SynthShieldPipeline(hardware_id="SYNTH-001", toxin_references=["ATCG"])

try:
    # Invalid DNA sequence (too short)
    result = pipeline.process_synthesis_order("ATCG")  # Will still work
    
    # Invalid DNA sequence (non-ATCG characters)
    try:
        result = pipeline.process_synthesis_order("ATCG XYZ ATCG")
    except ValueError as e:
        print(f"Invalid sequence: {e}")
    
    # Network errors (L2 blockchain)
    try:
        result = pipeline.process_synthesis_order("ATCGATCG")
    except Exception as e:
        print(f"Processing failed: {e}")
        # The pipeline logs what it can and marks L2 as failed
        # But returns result with decision still available

except Exception as e:
    print(f"Pipeline error: {e}")
```

---

## Decision Thresholds

The pipeline uses these thresholds for decisions:

| Score Range | Decision | Action |
|-------------|----------|--------|
| < 0.3 | APPROVED | Synthesize, open valve |
| 0.3 - 0.5 | REVIEW | Hold, manual review required |
| 0.5 - 0.7 | BLOCKED | Reject, notify customer |
| ≥ 0.7 | BLOCKED | Critical block, security alert |

---

## Performance Characteristics

Typical processing times per stage:

| Stage | Time (ms) | Notes |
|-------|-----------|-------|
| Embedding Generation | 50-150 | GPU accelerated |
| Evasion Detection | 20-50 | 5 parallel checks |
| Neural Screening | 10-30 | Fast inference |
| Ensemble Decision | <1 | Threshold comparison |
| Edison Guard | 5-20 | If fragments enabled |
| Black Box Logging | 2-5 | Cryptographic hashing |
| L2 Anchoring | 50-500 | Network dependent |
| Hardware Interlock | 100-500 | Hardware dependent |
| **TOTAL** | **150-1500** | Typical: 300-400ms |

---

## Troubleshooting

### Pipeline Won't Initialize

```python
# Check torch/GPU
import torch
print(f"CUDA available: {torch.cuda.is_available()}")

# Check imports
from synthshield.core.embeddings import EmbeddingWrapper
from synthshield.core.sentinel_head import SentinelFunctionalHead
```

### Slow Processing

```python
# Check GPU usage
import torch
torch.cuda.synchronize()  # Wait for GPU
# If slow, running on CPU - check CUDA setup

# Batch processing is faster than individual
results = []
for dna in dna_list:
    result = pipeline.process_synthesis_order(dna)
    results.append(result)
```

### Hardware Authorization Fails

```python
# Check token generation
result = pipeline.process_synthesis_order("ATCG")
if not result.neural_screening_result.get('release_token'):
    print("No token generated - decision must be APPROVED for token")

# Check interlock connection
from synthshield.hardware.interlock import SolenoidValveController
controller = SolenoidValveController()
print(f"Controller ready: {controller is not None}")
```

### L2 Blockchain Submission Fails

```python
# Check network
import requests
try:
    response = requests.get('https://mainnet.optimism.io', timeout=5)
    print(f"Network reachable: {response.status_code}")
except:
    print("Network error - L2 submission will fail")

# Use mock for testing
pipeline = SynthShieldPipeline(
    hardware_id="SYNTH-TEST",
    use_blockchain=True,
    mock_blockchain=True  # Don't use real network
)
```

---

## Next Steps

1. **Deploy in lab:** Replace manual screening with pipeline.process_synthesis_order()
2. **Load real toxin references:** Update toxin_references with real dangerous sequences
3. **Enable blockchain:** Set use_blockchain=True for production
4. **Monitor audit trails:** Review audit_trail in results for compliance
5. **Train classifier:** Use notebook_integration to train on your lab's data
6. **Connect hardware:** Ensure SolenoidValveController can reach your synthesis hardware

---

## API Reference

See `synthshield/pipeline.py` for complete API documentation:

- `SynthShieldPipeline.__init__()` - Initialize pipeline
- `SynthShieldPipeline.process_synthesis_order()` - Main processing function
- `SynthesisResult` - Output dataclass with all results
- `SynthesisDecision` - Enum: APPROVED, BLOCKED, REVIEW
- `RiskScores` - Container for all risk scores
- `EvasionDetails` - Evasion detection results

---

**Questions or Issues?** Contact the SynthShield development team.
