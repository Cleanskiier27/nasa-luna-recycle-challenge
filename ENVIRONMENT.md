# Environment Snapshot — NetworkBuster

**Generated:** 2026-01-03

## Summary
- Virtual environment: `.venv` (Python 3.14.2)
- Files created/updated:
  - `requirements.txt` — full venv freeze
  - `requirements-ml.txt` — ML-focused requirements (created)
  - `env-packages-venv.json`, `env-packages-system.json`, `env-packages-global.json` — package exports
  - `env-metadata.json` — metadata about Python/environment

## Notes
- TensorFlow: not installed because no official wheel is available for Python 3.14 in this environment; PyTorch (`torch==2.9.1`) was installed as an alternative. To use TensorFlow, consider creating a venv with Python 3.11/3.12.

## How to reproduce locally
1. Create venv: `python -m venv .venv`
2. Activate: `.\.venv\Scripts\Activate.ps1` (PowerShell)
3. Install full env: `pip install -r requirements.txt`
4. Or install ML-only: `pip install -r requirements-ml.txt`

## Next steps
- If you want TensorFlow specifically, tell me which Python version you prefer and I can prepare a reproducible venv and instructions.
