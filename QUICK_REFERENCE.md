# SynthShield: Quick Reference Card

## 🚀 Quick Start (30 seconds)

```bash
# 1. Clone
git clone https://github.com/USERNAME/synthshield.git
cd synthshield

# 2. Install
pip install -e .

# 3. Screen DNA
python
>>> from synthshield.core.screening import FunctionalManifoldScreener
>>> s = FunctionalManifoldScreener()
>>> s.screen("ATCGATCGATCG...")
{'decision': 'BLOCKED', 'risk_score': 0.73, ...}
```

---

## 📚 File Reference Quick Lookup

### "I need to understand..."

| What? | File | What It Does |
|-------|------|------------|
| AI risk scoring | `core/sentinel_head.py` | Neural network analyzes sequences |
| Decision logic | `core/screening.py` | APPROVED/BLOCKED based on score |
| ESM-2 embeddings | `core/embeddings.py` | Converts DNA→protein→1280D vector |
| All 6 stages at once | `core/forensic_orchestrator.py` | Runs complete pipeline |
| Split order attacks | `hardware/edison_window.py` | Detects fragments from multiple orders |
| Event logging | `hardware/blackbox.py` | HMAC-chained audit trail |
| Evasion attacks | `core/evasion_detection.py` | 5 attack vectors (RC, frame shift, etc.) |
| Blockchain submission | `web/ethereum_anchor.py` | L2 anchoring |
| Hardware valve control | `hardware/interlock.py` | Solenoid control |
| Research integration | `core/notebook_integration.py` | Connect Jupyter to production |
| Forensic audit | `audit/verify_chain.py` | Check if logs were tampered |
| Test data | `data/datasets.py` | Toxin/benign sequences |

### "I want to see examples..."

| What? | File | What It Shows |
|-------|------|-------------|
| Edison Guard demo (5 scenarios) | `hardware/demo_edison.py` | Running as script |
| L2 integration example | `core/demo_l2_integration.py` | Blockchain submission |
| ESM-2 research (notebook) | `docs/notebooks/01_esm_biosecurity_screening.ipynb` | 52 cells, 84% catch rate |
| Integration demo | `docs/notebooks/02_notebook_integration_demo.ipynb` | Connecting research to prod |
| Evasion detection (interactive) | `docs/notebooks/04_evasion_detection_demo.ipynb` | 5 attack types explained |
| Edison explained (detailed) | `docs/notebooks/03_edison_explained.ipynb` | Architecture walkthrough |

---

## 🎯 Core Concepts in 30 Seconds

```
Sequence: ATCGATCGATCG... (1000 bp)
    ↓
ESM-2 Model: Converts to 1280D embedding
    ↓
Risk Score: 0.73 (0=safe, 1=dangerous)
    ↓
Decision: BLOCKED (if score ≥ 0.5)
    ↓
Evasion Check: Reverse comp? Frame shift? Junk DNA?
    ↓
Split Order Check: Other customers have complementary fragments?
    ↓
Log Entry: HMAC-chained event added to audit trail
    ↓
Daily Hash: Merkle root of all day's events
    ↓
Blockchain: Submit root to Ethereum L2 (~$0.05)
    ↓
Hardware: Close synthesizer valve (if dangerous)
```

---

## 💾 Essential Commands

### Installation & Setup
```bash
# Install from source
pip install -e .

# Install with dev tools
pip install -e ".[dev,test]"

# Check it works
python -c "import synthshield; print('✅')"
```

### Running Demos
```bash
# Demo 1: Edison (split order detection)
python -m synthshield.hardware.demo_edison

# Demo 2: L2 Integration
python -m synthshield.core.demo_l2_integration

# Demo 3: Evasion detection (Jupyter)
jupyter notebook docs/notebooks/04_evasion_detection_demo.ipynb
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run one test file
pytest tests/test_evasion.py -v

# Run with coverage
pytest tests/ --cov=synthshield --cov-report=html
```

### Code Quality
```bash
# Format code
black synthshield/

# Check style
flake8 synthshield/

# Check imports
isort synthshield/
```

### Git & GitHub
```bash
# Check status
git status

# Add files
git add .

# Commit
git commit -m "feat: add evasion detection"

# Push
git push origin main

# Create branch for feature
git checkout -b feature/new-detection

# Merge when done
git checkout main
git merge feature/new-detection
```

---

## 🔍 File Navigation Map

```
Looking for: "How do sequences get scored?"
Path: core/sentinel_head.py
  ├─ Class: SentinelFunctionalHead
  ├─ Method: forward() - returns risk_score
  └─ Uses: ESM-2 embeddings from core/embeddings.py

Looking for: "What happens after scoring?"
Path: core/screening.py
  ├─ Class: FunctionalManifoldScreener
  ├─ Method: screen() - APPROVED/BLOCKED
  └─ Uses: sentinel_head.py results

Looking for: "How do we detect split orders?"
Path: hardware/edison_window.py
  ├─ Class: EdisonAssemblyGuard
  ├─ Method: add_fragment() - buffer fragments
  ├─ Method: analyze() - check reassembly
  └─ Uses: Sliding window buffer

Looking for: "How is everything logged?"
Path: hardware/blackbox.py
  ├─ Class: BlackBoxChain
  ├─ Method: add_event() - HMAC chain
  └─ Method: daily_merkle() - aggregate

Looking for: "How do we detect evasion?"
Path: core/evasion_detection.py
  ├─ Class: DNATransformationDetector - RC/frame/junk
  ├─ Class: CodonOptimizationDetector - codon/synthetic
  └─ Class: EvasionEnsembleScreener - combined check

Looking for: "How do all 6 stages work together?"
Path: core/forensic_orchestrator.py
  ├─ Class: FunctionalManifoldOrchestrator
  ├─ Method: process_order() - full pipeline
  └─ Uses: All 6 stages in sequence
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Create .env file
cat > .env << EOF
# Ethereum
ETHEREUM_PRIVATE_KEY=0x...
ETHEREUM_RPC_URL=https://arbitrum-goerli.infura.io
CONTRACT_ADDRESS=0x...

# Security
HMAC_SECRET_KEY=your-secret-key-here
HARDWARE_PORT=/dev/ttyUSB0

# ML Model
ESM_MODEL_PATH=facebook/esm2_t33_650M_UR50D
DEVICE=cpu  # or cuda
EOF
```

### Settings

```python
# synthshield/config.py (or create it)
RISK_THRESHOLD = 0.5          # BLOCKED if ≥ 0.5
BUFFER_SIZE = 50000           # Edison window: bp
TRIGGER_SIZE = 10000          # Edison: when to check
DAILY_ANCHOR_HOUR = 23        # When to submit to L2
EVASION_CONFIDENCE = 0.75     # Confidence threshold
```

---

## 🐛 Troubleshooting

### "ImportError: No module named synthshield"
```bash
# Make sure you installed it
pip install -e .

# Or run from repo root
cd /path/to/synthshield
python -m synthshield.core.demo_l2_integration
```

### "CUDA out of memory"
```bash
# Use CPU instead
export DEVICE=cpu

# Or specify in code
from synthshield.core.embeddings import ProteinEmbedder
embedder = ProteinEmbedder(device="cpu")
```

### "Ethereum connection failed"
```bash
# Check RPC URL
python -c "from web3 import Web3; print(Web3().is_connected())"

# Use fallback RPC
export ETHEREUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### "ESM-2 model not found"
```bash
# Download model
python -c "from transformers import AutoModel; \
  AutoModel.from_pretrained('facebook/esm2_t33_650M_UR50D')"
```

---

## 📊 API Cheat Sheet

### Simple API (Most Common)

```python
from synthshield.core.screening import FunctionalManifoldScreener

screener = FunctionalManifoldScreener()

result = screener.screen("ATCGATCG...")

# Result keys:
# - decision: "APPROVED" or "BLOCKED"
# - risk_score: 0.0-1.0
# - token: HMAC token for hardware
# - audit_hash: For forensic verification
```

### Full Pipeline API

```python
from synthshield.core.forensic_orchestrator import FunctionalManifoldOrchestrator

orchestrator = FunctionalManifoldOrchestrator()

result = orchestrator.process_order({
    "order_id": "ORD-12345",
    "sequence": "ATCGATCG...",
    "customer_id": "CUST-789",
    "timestamp": "2024-11-20T10:00:00Z"
})

# Result keys:
# - order_id, sequence, customer_id, timestamp
# - ai_screening: {decision, risk_score, token}
# - evasion_detection: {evasion_detected, attacks, risk}
# - split_order: {detected, fragments, recommendations}
# - event_hash: Logged to audit trail
# - blockchain_tx: Submitted to L2 (if daily)
# - hardware_status: Valve control status
```

### Evasion Detection API

```python
from synthshield.core.evasion_detection import EvasionEnsembleScreener

screener = EvasionEnsembleScreener()

result = screener.detect_evasion("ATCGATCG...")

# Result keys:
# - evasion_detected: True/False
# - risk_score: 0.0-1.0
# - attacks: {
#     "reverse_complement": {...},
#     "frame_shifts": {...},
#     "junk_interleaving": {...},
#     "codon_optimization": {...},
#     "synthetic_patterns": {...}
#   }
# - recommendation: "APPROVE", "BLOCK", or "REVIEW"
```

### Split Order Detection API

```python
from synthshield.hardware.edison_window import EdisonAssemblyGuard

edison = EdisonAssemblyGuard()

# Add fragments
edison.add_fragment("ATCGAT...", customer_id="A")
edison.add_fragment("GATCGA...", customer_id="B")

# Analyze
result = edison.analyze()

# Result keys:
# - dangerous_fragments: List of (customer_A, customer_B) pairs
# - reassembly_matches: Dangerous sequences found
# - temporal_analysis: Timing of orders
# - recommendations: ["BLOCK fragments A and B", ...]
```

---

## 📈 Performance Benchmarks

| Operation | Time | Throughput |
|-----------|------|-----------|
| ESM-2 embedding | 10ms | 100 seq/sec |
| Risk scoring | 1ms | 1000 seq/sec |
| Evasion detection | 100ms | 10 seq/sec |
| HMAC logging | 1ms | 10,000 events/sec |
| Merkle aggregation | 5s | 1M events → 1 hash |
| L2 submission | 1 min | 1 per day |

---

## 🔐 Security Checklist

Before deploying:

- [ ] Secret key rotated (yearly)
- [ ] Ethereum private key stored in .env (never committed)
- [ ] Hardware port restricted (only one process can access)
- [ ] Logs encrypted at rest
- [ ] Backups made daily
- [ ] L2 Merkle roots verified on blockchain
- [ ] HMAC chain integrity checked weekly

---

## 📖 Documentation Roadmap

```
START HERE ↓

README.md (2 min) ← Overview
     ↓
COMPLETE_REPOSITORY_GUIDE.md (15 min) ← Deep dive
     ↓
docs/ARCHITECTURE.md (10 min) ← System design
     ↓
docs/GETTING_STARTED.md (10 min) ← Installation
     ↓
docs/API.md (5 min) ← API reference
     ↓
Jupyter notebooks (30 min) ← Interactive examples
     ↓
Source code (2 hours) ← Full implementation
```

---

## 🎯 Decision Tree: "Which file should I look at?"

```
Do I want to...

├─ Understand what this does?
│  └─ Read: README.md + COMPLETE_REPOSITORY_GUIDE.md
│
├─ Use it for screening?
│  └─ Use: FunctionalManifoldScreener from core/screening.py
│
├─ Detect split orders?
│  └─ Use: EdisonAssemblyGuard from hardware/edison_window.py
│
├─ Detect evasion attacks?
│  └─ Use: EvasionEnsembleScreener from core/evasion_detection.py
│
├─ Run everything (6 stages)?
│  └─ Use: FunctionalManifoldOrchestrator from core/forensic_orchestrator.py
│
├─ Add a new attack detector?
│  └─ Modify: core/evasion_detection.py
│
├─ Improve the AI model?
│  └─ Start: docs/notebooks/01_esm_biosecurity_screening.ipynb
│
├─ Deploy to production?
│  └─ Read: docs/DEPLOYMENT.md
│
├─ Check if logs were tampered?
│  └─ Run: audit/verify_chain.py
│
└─ Contribute back?
   └─ Follow: CONTRIBUTING.md
```

---

## 🚀 GitHub Push Checklist

```bash
# 1. Make sure repo is clean
git status  # Should show: "nothing to commit, working tree clean"

# 2. Verify imports work
python -c "import synthshield; print('✅')"

# 3. Run tests (if any)
pytest tests/ -v

# 4. Add remote
git remote add origin https://github.com/USERNAME/synthshield.git

# 5. Push
git push -u origin main

# 6. Verify on GitHub
# Go to: https://github.com/USERNAME/synthshield
# Check files are there and README renders
```

---

## ✨ You're Ready!

Next steps:
1. Read: `COMPLETE_REPOSITORY_GUIDE.md` (full understanding)
2. Run: `python -m synthshield.hardware.demo_edison` (see it work)
3. Push: `git push origin main` (deploy to GitHub)
4. Share: Send GitHub link to collaborators
5. Contribute: Help others contribute back

**Questions?** Check `/docs` folder or open GitHub Issue.

