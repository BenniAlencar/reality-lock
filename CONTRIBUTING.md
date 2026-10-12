# Contributing to Reality Lock

Thank you for your interest in contributing to **Reality Lock**, the Zero-Trust & Verifiable Evidence Framework for AI Agents & MCP.

## Reality Lock Engineering Standards

We adhere to the **Benni Master OS Engineering Doctrine**:
1. **Evidence-First Development**: Never submit a PR without tests proving observed execution (`pytest tests`).
2. **Type Safety**: Strictly typed Python (`mypy` / PEP 561 compliant).
3. **Deterministic Receipts**: No random execution digests without cryptographically verifiable components.
4. **Zero-Trust**: Do not relax Default-Deny boundaries without explicit architectural discussion.

## Local Development Setup

```bash
# Clone the repository
git clone https://github.com/benni-os/reality-lock.git
cd reality-lock

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests -v
```

## Pull Request Checklist

- [ ] All tests pass cleanly (`pytest tests`).
- [ ] New verifiers or adapters include dedicated test cases in `tests/`.
- [ ] Code is formatted and typed.
- [ ] Updates to public APIs are documented in `README.md` and `CHANGELOG.md`.
