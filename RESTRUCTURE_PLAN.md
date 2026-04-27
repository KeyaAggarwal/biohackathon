# SynthShield Repository Restructure Guide

## Executive Summary

Your repository has:
- **11 Python modules** (synthshield/)
- **5 Jupyter notebooks** (research + demos)
- **7 documentation files** (scattered, disorganized)
- **Data folders** (toxins, embeddings, results)

**Problem:** Documentation is scattered. Hard to understand what each component does.

**Solution:** Clear hierarchy with organized README files at each level.

---

## Current State Analysis

### ✅ What's Working Well

1. **Modular design** - Code is already well-organized in `synthshield/`
2. **Functional separation** - Clear layers (core, hardware, web, audit, data)
3. **Test coverage** - Demo files show everything works
4. **Documentation** - Exists, but scattered

### ❌ What Needs Fixing

1. **Documentation chaos**
   - 7 markdown files in root directory
   - No clear entry point for GitHub visitors
   - Hard to understand project purpose

2. **Notebooks scattered**
   - 5 notebooks in root (should be in `/docs` or `/notebooks`)
   - No clear purpose/ordering

3. **No clear project structure**
   - Visitors don't know where to start
   - No "Quick Start" guide
   - No architecture diagram

4. **Missing files**
   - No `.gitignore` (may be committing venv, pycache, etc.)
   - No `setup.py` or `pyproject.toml` (can't pip install)
   - No `LICENSE`
   - No `CONTRIBUTING.md`
   - No GitHub workflows

---

## Proposed Structure

```
aixbio/
│
├── 📄 README.md                          [Main entry point - START HERE]
├── 📄 LICENSE                             [Apache 2.0 or MIT]
├── 📄 .gitignore                          [What not to commit]
├── 📄 pyproject.toml                      [Project metadata + dependencies]
├── 📄 CONTRIBUTING.md                     [How to contribute]
│
├── 📁 synthshield/                        [Main package]
│   ├── __init__.py
│   ├── __version__.py                     [Version string]
│   │
│   ├── 📁 core/                           [AI Screening + Orchestration]
│   │   ├── __init__.py
│   │   ├── embeddings.py                  [ESM-2 wrapper]
│   │   ├── sentinel_head.py               [ResNet MLP risk scorer]
│   │   ├── screening.py                   [Threshold-based decisions]
│   │   ├── forensic_orchestrator.py       [6-stage orchestration]
│   │   ├── trained_classifier.py          [Research classifier]
│   │   ├── notebook_integration.py        [Research→production]
│   │   ├── evasion_detection.py           [NEW: Evasion detection]
│   │   ├── enhanced_edison.py             [NEW: Enhanced Edison]
│   │   └── demo_l2_integration.py         [Demo]
│   │
│   ├── 📁 hardware/                       [Hardware + Cryptography]
│   │   ├── __init__.py
│   │   ├── blackbox.py                    [Cryptographic logging]
│   │   ├── edison_window.py               [Split-order detection]
│   │   ├── interlock.py                   [Solenoid valve control]
│   │   └── demo_edison.py                 [Edison demos]
│   │
│   ├── 📁 web/                            [Blockchain Layer]
│   │   ├── __init__.py
│   │   └── ethereum_anchor.py             [L2 Ethereum]
│   │
│   ├── 📁 audit/                          [Forensic Tools]
│   │   ├── __init__.py
│   │   └── verify_chain.py                [Chain verification]
│   │
│   └── 📁 data/                           [Datasets]
│       ├── __init__.py
│       └── datasets.py                    [Dataset utilities]
│
├── 📁 docs/                               [ALL DOCUMENTATION]
│   ├── 📄 README.md                       [Docs home page]
│   ├── 📄 ARCHITECTURE.md                 [System architecture]
│   ├── 📄 GETTING_STARTED.md              [Installation + quick start]
│   ├── 📄 API.md                          [API reference]
│   ├── 📄 EVASION_DETECTION.md            [Evasion detection guide]
│   ├── 📄 DEPLOYMENT.md                   [Deployment guide]
│   │
│   └── 📁 notebooks/                      [Jupyter notebooks]
│       ├── 01_esm_biosecurity_screening.ipynb          [Research baseline]
│       ├── 02_notebook_integration_demo.ipynb          [Integration]
│       ├── 03_evasion_detection_demo.ipynb             [Evasion demo]
│       ├── 04_edison_explained.ipynb                   [Edison deep dive]
│       └── 05_complete_system_demo.ipynb               [Full integration]
│
├── 📁 data/                               [DATA & RESOURCES]
│   ├── benign/                            [Benign sequences]
│   ├── dangerous/
│   │   └── canonical.json                 [Known toxins]
│   ├── embeddings/                        [Precomputed ESM-2]
│   ├── families/                          [Toxin families]
│   └── results/                           [Analysis results]
│
├── 📁 tests/                              [TESTS (currently missing)]
│   ├── __init__.py
│   ├── test_evasion_detection.py
│   ├── test_screening.py
│   ├── test_edison_guard.py
│   ├── test_forensic_orchestrator.py
│   └── conftest.py                        [Pytest fixtures]
│
├── 📁 examples/                           [USAGE EXAMPLES]
│   ├── 01_basic_screening.py
│   ├── 02_evasion_detection.py
│   ├── 03_full_orchestration.py
│   └── 04_live_l2_deployment.py
│
└── 📁 .github/                            [GITHUB SPECIFIC]
    └── workflows/                         [CI/CD pipelines]
        ├── tests.yml                      [Run tests on push]
        ├── docs.yml                       [Build docs on release]
        └── security.yml                   [Security checks]
```

---

## What Goes Where: Decision Tree

### Root Files (/)
- Keep: `README.md`, `LICENSE`, `pyproject.toml`, `.gitignore`, `CONTRIBUTING.md`
- Move: Everything else to `/docs`

### /synthshield/ (Package Code)
- **core/** - AI & orchestration (embeddings, screening, orchestrator)
- **hardware/** - Physical security (cryptography, buffer, valve control)
- **web/** - Blockchain integration (L2 Ethereum)
- **audit/** - Forensic tools (chain verification)
- **data/** - Dataset utilities

### /docs/ (Documentation + Notebooks)
- `README.md` - Docs homepage
- `ARCHITECTURE.md` - System design
- `GETTING_STARTED.md` - Install & run
- `API.md` - Reference
- `EVASION_DETECTION.md` - Technical guide
- `DEPLOYMENT.md` - Production setup
- `/notebooks/` - All 5 Jupyter notebooks

### /tests/ (NEW - Testing)
- Unit tests for each module
- Integration tests
- Pytest configuration

### /examples/ (NEW - Usage Examples)
- Copy-paste ready code snippets
- Shows how to use each component

### /data/ (Research Data)
- Toxin sequences (dangerous/)
- Benign sequences (benign/)
- Precomputed embeddings (embeddings/)
- Toxin families (families/)

---

## Reorganization Checklist

### Phase 1: Create Directory Structure

```bash
# Create new directories
mkdir -p docs/notebooks
mkdir -p tests
mkdir -p examples
mkdir -p .github/workflows

# Verify
ls -la docs/ tests/ examples/ .github/
```

### Phase 2: Consolidate Documentation

**Consolidate to 6 core docs:**

1. **docs/README.md**
   - Documentation homepage
   - Links to all other docs
   - Quick reference

2. **docs/ARCHITECTURE.md**
   - System design (6 layers)
   - Component descriptions
   - Data flow diagrams
   - Integration points

3. **docs/GETTING_STARTED.md**
   - Installation steps
   - Quick start example
   - Running tests
   - Running notebooks

4. **docs/API.md**
   - Module reference
   - Class/function documentation
   - Usage examples for each

5. **docs/EVASION_DETECTION.md**
   - Evasion attack types
   - Detection methods
   - Integration guide

6. **docs/DEPLOYMENT.md**
   - Production setup
   - L2 configuration
   - Hardware integration
   - Monitoring

### Phase 3: Move Notebooks

```bash
# Move notebooks to docs/notebooks with numbers
mv esm_biosecurity_screening.ipynb docs/notebooks/01_esm_biosecurity_screening.ipynb
mv notebook_integration_demo.ipynb docs/notebooks/02_notebook_integration_demo.ipynb
mv EVASION_DETECTION_DEMO.ipynb docs/notebooks/03_evasion_detection_demo.ipynb
mv EDISON_EXPLAINED.ipynb docs/notebooks/04_edison_explained.ipynb
# Create new: 05_complete_system_demo.ipynb
```

### Phase 4: Create Root-Level Entry Points

1. **Main README.md** (root)
   - What is SynthShield?
   - Why it matters
   - Quick demo
   - Links to docs

2. **pyproject.toml**
   - Project metadata
   - Dependencies
   - Entry points
   - Install instructions

3. **.gitignore**
   - Python caches
   - Virtual environments
   - IDE files
   - Large data files
   - Credentials

4. **LICENSE**
   - Choose: Apache 2.0, MIT, or GPL

5. **CONTRIBUTING.md**
   - How to contribute
   - Development setup
   - Testing requirements
   - PR process

### Phase 5: Create Stub Files (NEW)

Create basic test structure:
- `tests/conftest.py` - Pytest fixtures
- `tests/test_screening.py` - Screening tests
- `tests/test_evasion_detection.py` - Evasion tests
- `tests/test_orchestration.py` - Full pipeline tests

Create example scripts:
- `examples/01_basic_screening.py`
- `examples/02_evasion_detection.py`
- `examples/03_full_orchestration.py`

---

## File-by-File Plan

### What to Create

1. **docs/README.md**
   ```markdown
   # SynthShield Documentation
   
   Welcome! Choose your path:
   - [Getting Started](GETTING_STARTED.md) - Install and run
   - [Architecture](ARCHITECTURE.md) - How it works
   - [API Reference](API.md) - All modules
   - [Evasion Detection](EVASION_DETECTION.md) - Attack resistance
   - [Deployment](DEPLOYMENT.md) - Production setup
   - [Notebooks](notebooks/) - Interactive examples
   ```

2. **docs/GETTING_STARTED.md**
   ```
   ## Installation
   ```
   pip install -e .
   ```
   
   ## Quick Start
   
   ### Run Pre-screening
   ```python
   from synthshield.core.evasion_detection import EvasionEnsembleScreener
   
   screener = EvasionEnsembleScreener(['ATCGTAGC...'])
   result = screener.screen_for_evasion('ATCGATCG...')
   print(result['recommendation'])  # BLOCK, REVIEW, or APPROVE
   ```
   ...more examples
   ```

3. **docs/ARCHITECTURE.md**
   - Move from INTEGRATION_ARCHITECTURE.md
   - Clean up structure
   - Add system diagrams

4. **docs/API.md**
   - Document all public classes/functions
   - Usage examples for each
   - Parameter descriptions

5. **docs/EVASION_DETECTION.md**
   - Move from EVASION_SOLUTIONS_GUIDE.md
   - Expand with technical details
   - Add detection success rates

6. **docs/DEPLOYMENT.md**
   - Move from L2_*.md files
   - Add hardware setup
   - Add monitoring guide

### What to Delete or Move

**Delete (consolidate to docs/):**
- EDISON_COMPLETE.md → docs/ARCHITECTURE.md (merge)
- EDISON_EXPLAINED.ipynb → docs/notebooks/04_
- L2_CONFIG.md → docs/DEPLOYMENT.md (merge)
- L2_DEPLOYMENT.md → docs/DEPLOYMENT.md (merge)
- L2_IMPLEMENTATION_SUMMARY.md → docs/API.md (merge)
- L2_QUICK_REFERENCE.md → delete or merge to API.md
- EVASION_SOLUTIONS_GUIDE.md → docs/EVASION_DETECTION.md
- INTEGRATION_ARCHITECTURE.md → docs/ARCHITECTURE.md
- FILE_STRUCTURE.md → delete (redundant)

**Keep (still needed):**
- README.md (root - update)
- requirements.txt (or move to pyproject.toml)

---

## Step-by-Step Implementation

### Step 1: Create New Directories

```bash
cd /Users/keya/Desktop/hackathon/bio/aixbio

mkdir -p docs/notebooks
mkdir -p tests
mkdir -p examples
mkdir -p .github/workflows
```

### Step 2: Create Root Files

**Create `.gitignore`:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# Environment
.env
.env.local

# Data
data/embeddings/*.npy
data/results/

# OS
.DS_Store
Thumbs.db
```

**Create `pyproject.toml`:**
```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "synthshield"
version = "1.0.0"
description = "AI-powered DNA synthesis security with split-order attack detection"
readme = "README.md"
license = {text = "Apache-2.0"}
authors = [{name = "SynthShield Team"}]
requires-python = ">=3.10"
keywords = ["biosecurity", "DNA", "synthesis", "AI", "security"]

dependencies = [
    "torch>=2.4.1",
    "transformers>=4.41.0",
    "web3>=7.15.0",
    "eth-account>=0.13.7",
    "eth-keys>=0.7.0",
    "eth-typing>=6.0.0",
    "numpy>=2.4.4",
    "scikit-learn>=1.3.0",
    "pydantic>=2.13.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "flake8>=6.0",
    "mypy>=1.0",
]
docs = [
    "jupyter>=1.0",
    "nbconvert>=7.0",
]

[tool.setuptools]
packages = ["synthshield"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

**Create `CONTRIBUTING.md`:**
```markdown
# Contributing to SynthShield

## Development Setup

```bash
git clone https://github.com/yourusername/aixbio.git
cd aixbio
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/
pytest tests/ -v  # Verbose
pytest tests/ --cov=synthshield  # With coverage
```

## Code Style

- Use black: `black synthshield/`
- Use flake8: `flake8 synthshield/`
- Use mypy: `mypy synthshield/`

## Pull Request Process

1. Create branch: `git checkout -b feature/your-feature`
2. Make changes with tests
3. Run tests: `pytest`
4. Commit: `git commit -am "Add feature"`
5. Push: `git push origin feature/your-feature`
6. Create PR on GitHub
```

**Update `README.md` (root):**
```markdown
# SynthShield: AI-Powered DNA Synthesis Security

Detect split-order attacks, evasion techniques, and anomalies in real-time DNA synthesis orders.

## Features

✅ **AI Screening** - ESM-2 embeddings + neural risk scoring  
✅ **Split-Order Detection** - Edison Assembly Guard (buffer + temporal analysis)  
✅ **Evasion Detection** - Reverse complement, frame shift, codon optimization  
✅ **Cryptographic Logging** - HMAC-SHA256 event chaining + Merkle trees  
✅ **Hardware Interlock** - Solenoid valve control with HMAC tokens  
✅ **L2 Anchoring** - Ethereum blockchain records for compliance  

## Quick Start

```bash
# Install
pip install -e .

# Quick example
python examples/01_basic_screening.py

# Run tests
pytest tests/

# Explore notebooks
jupyter notebook docs/notebooks/
```

## Documentation

→ [Full Documentation](docs/)

- [Getting Started](docs/GETTING_STARTED.md)
- [Architecture](docs/ARCHITECTURE.md)  
- [API Reference](docs/API.md)
- [Evasion Detection](docs/EVASION_DETECTION.md)
- [Deployment](docs/DEPLOYMENT.md)

## System Architecture

[6-layer defense system]
1. AI Screening (ESM-2)
2. Cryptographic Logging
3. Split-Order Detection  
4. Daily Aggregation
5. L2 Anchoring
6. Hardware Interlock

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Effectiveness

- Detection rate: 83% (vs industry 85%+)
- Attack types: Reverse complement, frame shift, junk interleaving, codon optimization, synthetic patterns
- Multi-provider gap: Requires external coordination layer

## License

Apache License 2.0

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
```
```

### Step 3: Consolidate Docs

I'll create a master docs file that consolidates everything:

```bash
# Consolidate docs to docs/ folder
mv INTEGRATION_ARCHITECTURE.md docs/ARCHITECTURE.md
mv EVASION_SOLUTIONS_GUIDE.md docs/EVASION_DETECTION.md
# Merge L2_*.md into docs/DEPLOYMENT.md
# etc.
```

### Step 4: Move Notebooks

```bash
# Move and rename notebooks
mv esm_biosecurity_screening.ipynb docs/notebooks/01_esm_biosecurity_screening.ipynb
mv notebook_integration_demo.ipynb docs/notebooks/02_notebook_integration_demo.ipynb
mv EVASION_DETECTION_DEMO.ipynb docs/notebooks/03_evasion_detection_demo.ipynb
mv EDISON_EXPLAINED.ipynb docs/notebooks/04_edison_explained.ipynb
```

### Step 5: Create Example Scripts

Create `examples/01_basic_screening.py`:
```python
"""Basic screening example."""
from synthshield.core.evasion_detection import EvasionEnsembleScreener

TOXIN_REFS = ["ATGGTGTCTACC..."]  # Known toxins

def main():
    screener = EvasionEnsembleScreener(TOXIN_REFS)
    
    # Test sequence
    test_seq = "ATCGATCGATCG..."
    
    result = screener.screen_for_evasion(test_seq)
    print(f"Risk: {result['risk_score']:.2f}")
    print(f"Decision: {result['recommendation']}")

if __name__ == "__main__":
    main()
```

---

## Summary of Changes

| Category | Current | Proposed | Benefit |
|----------|---------|----------|---------|
| Root docs | 7 scattered .md files | 1 root README + /docs | Clear entry point |
| Notebooks | 5 in root | 5 in docs/notebooks/ | Organized |
| Tests | None | tests/ folder + pytest | Maintainability |
| Examples | None | examples/ folder | Onboarding |
| Project metadata | requirements.txt only | pyproject.toml | pip installable |
| Git | No .gitignore | .gitignore | Cleaner repo |
| CI/CD | None | .github/workflows/ | Auto testing |

---

## GitHub Ready Checklist

- [ ] Created .gitignore
- [ ] Created pyproject.toml
- [ ] Consolidated documentation to /docs
- [ ] Moved notebooks to /docs/notebooks
- [ ] Created /tests structure
- [ ] Created /examples scripts
- [ ] Updated root README.md
- [ ] Created CONTRIBUTING.md
- [ ] Created LICENSE
- [ ] Removed duplicate/old doc files
- [ ] Tested `pip install -e .` works
- [ ] Tested `pytest tests/` works
- [ ] Created .github/workflows for CI/CD
- [ ] All files have proper docstrings
- [ ] Added __version__.py to synthshield/

---

## Next Steps

1. Run the reorganization (I'll help)
2. Create stub test files
3. Create example scripts
4. Set up GitHub repo
5. Configure CI/CD workflows
6. Push code!

**Ready to proceed?**
