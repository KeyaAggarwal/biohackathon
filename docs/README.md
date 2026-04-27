# SynthShield Documentation

Welcome to the SynthShield documentation! Choose your path based on what you want to do:

## 🚀 Getting Started (NEW USER)

→ **[Getting Started Guide](GETTING_STARTED.md)**
- Installation steps
- Quick start examples
- Running tests
- Running Jupyter notebooks

## 🏗️ Understanding the System

→ **[Architecture Documentation](ARCHITECTURE.md)**
- System overview (6-layer defense)
- Component descriptions
- Data flow diagrams
- Integration points

## 💻 Using the Code

→ **[API Reference](API.md)**
- Complete module documentation
- All classes and functions
- Usage examples
- Parameters and return types

## 🛡️ Evasion Detection

→ **[Evasion Detection Guide](EVASION_DETECTION.md)**
- Attack types (5 techniques)
- How detection works
- Success rates
- Integration guide

## 🚢 Deployment & Operations

→ **[Deployment Guide](DEPLOYMENT.md)**
- Production setup
- L2 Ethereum configuration
- Hardware integration
- Monitoring and logging
- Performance tuning

## 📓 Interactive Notebooks

→ **[Jupyter Notebooks](notebooks/)**

0. **Start here:** `01_esm_biosecurity_screening.ipynb`
   - Research foundation
   - ESM-2 embeddings explained
   - Classifier training

1. **Integration demo:** `02_notebook_integration_demo.ipynb`
   - How research connects to production
   - End-to-end pipeline

2. **Attack demonstrations:** `03_evasion_detection_demo.ipynb`
   - Live examples of all 5 evasion attacks
   - How each detector works
   - Performance metrics

3. **Deep dive:** `04_edison_explained.ipynb`
   - Edison Assembly Guard architecture
   - Buffer management
   - Temporal analysis

4. **Full system:** `05_complete_system_demo.ipynb`
   - All 6 layers working together
   - Real synthesis scenario
   - Compliance audit

## 🔍 Quick Reference

### Installation

```bash
pip install -e .
```

### Basic Screening

```python
from synthshield.core.evasion_detection import EvasionEnsembleScreener

screener = EvasionEnsembleScreener(['ATCG...'])
result = screener.screen_for_evasion('ATCG...')
print(result['recommendation'])  # BLOCK, REVIEW, or APPROVE
```

### Run Tests

```bash
pytest tests/ -v
```

### Run Notebooks

```bash
jupyter notebook notebooks/
```

## 📊 System Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **AI Screening** | ESM-2 embeddings + risk scoring | `synthshield/core/` |
| **Evasion Detection** | 5 attack type detection | `synthshield/core/` |
| **Edison Guard** | Split-order attack detection | `synthshield/hardware/` |
| **Cryptography** | HMAC-SHA256 event chaining | `synthshield/hardware/` |
| **Blockchain** | L2 Ethereum anchoring | `synthshield/web/` |
| **Orchestration** | 6-layer coordination | `synthshield/core/` |

## ❓ FAQ

**Q: How accurate is detection?**  
A: 83% for known attacks, varies by attack type. See [EVASION_DETECTION.md](EVASION_DETECTION.md).

**Q: Can I use this in production?**  
A: Partially. Needs provider coordination for multi-provider defense. See [DEPLOYMENT.md](DEPLOYMENT.md).

**Q: How do I integrate with my synthesizer?**  
A: See hardware integration section in [DEPLOYMENT.md](DEPLOYMENT.md).

**Q: What about false positives?**  
A: <2% false positive rate. Can tune thresholds in `screening.py`.

**Q: How long does screening take?**  
A: ~50-100ms per sequence (CPU), faster on GPU.

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Development setup
- Running tests
- Code style
- Pull request process

## 📧 Support

- Questions? Open an issue or discussion on GitHub
- Security concerns? Email security@synthshield.io
- Found a bug? Open an issue with reproduction steps

## 📚 Additional Resources

- [Project README](../README.md) - Project overview
- [License](../LICENSE) - Apache 2.0
- [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute
- [GitHub Repository](https://github.com/yourusername/aixbio)

---

**Start with [Getting Started](GETTING_STARTED.md) if you're new!**
