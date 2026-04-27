# Contributing to SynthShield

Thank you for your interest in contributing! We welcome contributions from everyone.

## Code of Conduct

Be respectful, inclusive, and professional. Biosecurity is important.

## Development Setup

### Prerequisites
- Python 3.10+
- Git
- pip or conda

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/aixbio.git
cd aixbio

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=synthshield --cov-report=html

# Run specific test file
pytest tests/test_evasion_detection.py

# Run specific test function
pytest tests/test_evasion_detection.py::test_reverse_complement
```

## Code Style

We use `black`, `flake8`, and `isort` for code formatting and linting.

```bash
# Format code with black
black synthshield/

# Check with flake8
flake8 synthshield/ --max-line-length=100

# Sort imports
isort synthshield/

# Type checking with mypy
mypy synthshield/

# Or run all at once (if you set up pre-commit)
pre-commit run --all-files
```

## Git Workflow

### Creating a Feature Branch

```bash
# Create and checkout new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description

# Or for documentation
git checkout -b docs/documentation-update
```

### Committing Changes

```bash
# Stage changes
git add synthshield/

# Commit with meaningful message
git commit -m "Add reverse complement evasion detection"

# Follow conventional commits when possible:
# feat: new feature
# fix: bug fix
# docs: documentation
# test: tests
# refactor: code restructuring
# perf: performance improvement
```

### Pushing and Creating PR

```bash
# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub with:
# - Clear title
# - Description of changes
# - Reference to related issues (#123)
# - Checklist of testing done
```

## Pull Request Guidelines

Before submitting a PR:

- [ ] Tests pass: `pytest tests/`
- [ ] Code style passes: `black`, `flake8`, `isort`
- [ ] All new functions have docstrings
- [ ] Changes documented in commit messages
- [ ] No large files committed (data files go to `.gitignore`)
- [ ] PR description explains why this change is needed

## Adding Features

### New Module Example

If adding a new module to `synthshield/core/`:

1. Create file: `synthshield/core/my_module.py`
2. Add to `synthshield/core/__init__.py`
3. Add tests: `tests/test_my_module.py`
4. Add to documentation: `docs/API.md`
5. Add example: `examples/XX_my_module_example.py`

### New Test

```python
# tests/test_my_module.py
import pytest
from synthshield.core.my_module import MyClass

def test_basic_functionality():
    """Test that MyClass does X."""
    obj = MyClass()
    result = obj.method()
    assert result == expected_value

def test_edge_case():
    """Test edge case handling."""
    with pytest.raises(ValueError):
        MyClass().bad_input()
```

## Documentation

### Docstring Style

We use Google-style docstrings:

```python
def screen_sequence(sequence: str, threshold: float = 0.5) -> Dict[str, Any]:
    """Screen DNA sequence for biosecurity threats.
    
    Args:
        sequence: DNA sequence as string of ATGC
        threshold: Risk score threshold (0-1)
    
    Returns:
        Dictionary with keys:
            - decision: str, 'APPROVE', 'REVIEW', or 'BLOCK'
            - risk_score: float, 0-1
            - reasoning: str, explanation
    
    Raises:
        ValueError: If sequence contains invalid characters
        
    Examples:
        >>> result = screen_sequence("ATCGATCG")
        >>> result['decision']
        'APPROVE'
    """
```

### Documentation Files

- `docs/ARCHITECTURE.md` - System design and components
- `docs/GETTING_STARTED.md` - Installation and quick start
- `docs/API.md` - Module and function reference
- `docs/EVASION_DETECTION.md` - Evasion technique documentation
- `docs/DEPLOYMENT.md` - Production deployment guide

## Reporting Issues

When reporting a bug:

1. **Check existing issues** - Don't duplicate
2. **Provide minimal reproduction** - Exact steps to reproduce
3. **Include environment info** - Python version, OS, dependencies
4. **Add expected vs actual behavior** - What should happen vs what did

Example:

```markdown
## Bug Report: Reverse Complement Detection False Negative

### Reproduction Steps
1. Load toxin reference "ATCGTAGC..."
2. Create reverse complement
3. Call check_reverse_complement()

### Expected
Should detect as reverse complement (risk_score > 0.8)

### Actual
Returns risk_score = 0.1, is_rc_attack = False

### Environment
- Python 3.10
- synthshield 1.0.0
- torch 2.4.1
```

## Release Process

(For maintainers)

```bash
# Update version in pyproject.toml
# Update CHANGELOG
# Create release branch
git checkout -b release/v1.1.0

# Tag release
git tag -a v1.1.0 -m "Version 1.1.0"
git push origin release/v1.1.0 --tags

# Build distributions
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Getting Help

- **Questions:** Open a discussion on GitHub
- **Bugs:** Open an issue with reproduction steps
- **Security:** Email security@synthshield.io (do not use public issues)

## License

By contributing, you agree that your contributions will be licensed under the same Apache 2.0 license as the project.

Thank you for contributing to SynthShield! 🛡️
