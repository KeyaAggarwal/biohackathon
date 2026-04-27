# SynthShield L2 Integration - Quick Reference

## Installation

```bash
# Install dependencies (including web3)
pip install -r requirements.txt
```

## Three Ways to Use L2 Integration

### 1️⃣  Mock Mode (No Network Required)

**Best for**: Testing, demos, development

```python
from synthshield.core.forensic_orchestrator import ForensicOrchestrator

orchestrator = ForensicOrchestrator(
    hardware_id="TEST-SYNTH-001",
    tpm_secret=b"test_secret",
    use_mock_l2=True,  # ← Mock mode
    screening_threshold=0.5
)

# Log events, verify, generate proofs, submit
orchestrator.log_synthesis_event(...)
orchestrator.submit_daily_anchor_to_l2()
orchestrator.print_audit_summary()
```

### 2️⃣  Live L2 Mode (With Ethereum)

**Best for**: Production deployment

```python
import os
from synthshield.core.forensic_orchestrator import ForensicOrchestrator

l2_config = {
    "contract_address": os.getenv("L2_CONTRACT_ADDRESS"),
    "rpc_url": os.getenv("L2_RPC_URL"),
    "private_key": os.getenv("L2_PRIVATE_KEY"),
    "network": "optimism"  # or arbitrum, base
}

orchestrator = ForensicOrchestrator(
    hardware_id=os.getenv("L2_HARDWARE_ID"),
    tpm_secret=b"root_of_trust_bytes",
    use_mock_l2=False,  # ← Live mode
    l2_config=l2_config
)

# Same interface as mock mode
orchestrator.log_synthesis_event(...)
orchestrator.submit_daily_anchor_to_l2()
```

### 3️⃣  Direct L2 Submission

**Best for**: Custom workflows

```python
from synthshield.web.ethereum_anchor import EthereumAnchor

anchor = EthereumAnchor(
    contract_address="0x...",
    rpc_url="https://mainnet.optimism.io",
    private_key="0x...",
    hardware_id="SYNTH-001",
    network="optimism"
)

# Submit a merkle root directly
result = anchor.submit_merkle_root(
    merkle_root_hex="0xabcd1234...",
    data_url="ipfs://bafkyabc123"
)
```

## Configuration Files

| File | Purpose |
|------|---------|
| [L2_CONFIG.md](L2_CONFIG.md) | Environment variables & configuration |
| [L2_DEPLOYMENT.md](L2_DEPLOYMENT.md) | Setting up L2 networks & contracts |
| [L2_IMPLEMENTATION_SUMMARY.md](L2_IMPLEMENTATION_SUMMARY.md) | Complete technical overview |

## Getting Started: 5 Steps

### Step 1: Test Locally (Mock Mode)

```bash
cd synthshield/core
python demo_l2_integration.py
# Select: 1. Mock L2 Submission
```

### Step 2: Deploy Smart Contract

Copy [L2_DEPLOYMENT.md](L2_DEPLOYMENT.md), follow the Foundry deployment guide.

### Step 3: Configure Environment

Edit `.env` with your L2 details:
```bash
L2_CONTRACT_ADDRESS=0x...
L2_RPC_URL=https://mainnet.optimism.io
L2_PRIVATE_KEY=0x...
L2_HARDWARE_ID=SYNTH-001
L2_NETWORK=optimism
```

### Step 4: Test on Live L2

```python
from synthshield.core.forensic_orchestrator import ForensicOrchestrator
import os
from dotenv import load_dotenv

load_dotenv()

orchestrator = ForensicOrchestrator(
    hardware_id=os.getenv("L2_HARDWARE_ID"),
    tpm_secret=b"root_secret",
    use_mock_l2=False,
    l2_config={
        "contract_address": os.getenv("L2_CONTRACT_ADDRESS"),
        "rpc_url": os.getenv("L2_RPC_URL"),
        "private_key": os.getenv("L2_PRIVATE_KEY"),
        "network": os.getenv("L2_NETWORK", "optimism")
    }
)

# Test submission
orchestrator.log_synthesis_event("TEST-001", "ATCG", status="success")
orchestrator.submit_daily_anchor_to_l2()
```

### Step 5: Production Deployment

Integrate into your synthesis pipeline and run daily.

## Key Classes

### ForensicOrchestrator
```python
orchestrator.log_synthesis_event(synthesis_id, sequence, embeddings, status)
orchestrator.verify_chain_integrity() → bool
orchestrator.generate_daily_merkle_root() → str
orchestrator.submit_daily_anchor_to_l2(data_url, simulate) → dict
orchestrator.export_audit_log_json(filepath)
orchestrator.print_audit_summary()
orchestrator.get_audit_summary() → dict
```

### EthereumAnchor
```python
anchor.submit_merkle_root(merkle_root_hex, data_url, simulate) → dict
anchor.verify_anchor_on_chain(synthesizer_address, merkle_root_hex) → bool
anchor.get_submission_history() → list
anchor.from_env() → EthereumAnchor  # Static method
```

### BlackBoxChain
```python
black_box.log_event(event) → str
black_box.verify_chain() → bool
black_box.get_merkle_root() → str
```

## Supported L2 Networks

| Network | RPC URL | Chain ID | Testnet |
|---------|---------|----------|---------|
| **Optimism** | https://mainnet.optimism.io | 10 | Sepolia |
| **Arbitrum** | https://arb1.arbitrum.io/rpc | 42161 | Sepolia |
| **Base** | https://mainnet.base.org | 8453 | Sepolia |

## File Structure

```
aixbio/
├── synthshield/
│   ├── web/
│   │   └── ethereum_anchor.py ← L2 submission client
│   ├── core/
│   │   ├── forensic_orchestrator.py ← Main orchestrator
│   │   └── demo_l2_integration.py ← Interactive demos
│   ├── contracts/
│   │   └── ForensicAnchor.sol ← Smart contract
│   ├── hardware/
│   │   └── blackbox.py ← Encryption chain
│   └── ...
├── L2_DEPLOYMENT.md ← Deployment guide
├── L2_CONFIG.md ← Configuration reference
├── L2_IMPLEMENTATION_SUMMARY.md ← Full technical docs
└── requirements.txt ← Python dependencies
```

## Data Flow Summary

```
Synthesis Events 
    ↓
Real-time Neural Screening (ESM-2 + Sentinel Head)
    ↓
Decisions (APPROVED/BLOCKED)
    ↓
LogEvent (Black Box Chain)
    ↓
HMAC-SHA256 Chaining with RoT Secret
    ↓
Daily: Generate Merkle Root
    ↓
Daily: Submit to L2 Smart Contract
    ↓
✓ Immutably Anchored on Ethereum
    ↓
Export Audit Log (JSON + IPFS)
    ↓
Compliance Report Ready
```

## Common Tasks

### Log a synthesis event
```python
orchestrator.log_synthesis_event(
    synthesis_id="SYN-2026-04-25-001",
    sequence="ATCGATCG...",
    embeddings=torch.randn(1, 1280),  # ESM-2 embeddings
    status="success",
    metadata={"operator": "lab_tech_A", "lab": "LAB-1"}
)
```

### Verify chain integrity (detect tampering)
```python
is_valid = orchestrator.verify_chain_integrity()
# ✓ VALID    - No tampering detected
# ✗ COMPROMISED  - Tampering detected!
```

### Generate daily proof
```python
merkle_root = orchestrator.generate_daily_merkle_root()
# Returns: 0xabc123def456...
```

### Submit to L2
```python
submission = orchestrator.submit_daily_anchor_to_l2(
    data_url="ipfs://bafkyabc123"
)
print(submission['tx_hash'])  # 0x...
print(submission['status'])   # 'confirmed'
```

### Export audit trail
```python
orchestrator.export_audit_log_json("audit_20260425.json")
# Exports JSON with all events, chain status, L2 submissions
```

## Troubleshooting

### Error: "web3 library required"
```bash
pip install web3 eth-account
```

### Error: "Failed to connect to optimism"
- Check RPC URL is correct
- Verify internet connectivity
- Try alternative RPC (Alchemy, Infura, Ankr)

### Error: "Synthesizer not authorized"
- Call `authorizeSynthesizer(wallet_address)` in smart contract
- Ensure wallet is on correct L2 network

### Error: "Insufficient funds"
- Fund wallet with ETH on L2
- ~$0.01-0.05 per daily submission

## Performance

| Operation | Time |
|-----------|------|
| Log event | <1ms |
| Verify chain | O(n) in events |
| Generate Merkle root | <100ms |
| Submit to L2 | 1-2 minutes |
| On-chain verification | <1s |

## Security Checklist

- [ ] Private key in `.env` (not hardcoded)
- [ ] `.env` added to `.gitignore`
- [ ] Different wallets for testnet/mainnet
- [ ] Wallet authorized in smart contract
- [ ] Tested with mock mode first
- [ ] Contract address verified
- [ ] RPC endpoint from trusted provider
- [ ] Keys rotated periodically

## S.3741 Compliance

✅ Real-time synthesis logging  
✅ Cryptographic binding (HMAC-SHA256)  
✅ Hardware root-of-trust integration  
✅ Daily Merkle root anchoring  
✅ Immutable on-chain storage  
✅ Third-party auditability (IPFS)  

---

**Quick Help**
- Docs: See `L2_*.md` files
- Demo: Run `python demo_l2_integration.py`
- Code: Check `synthshield/core/forensic_orchestrator.py`
