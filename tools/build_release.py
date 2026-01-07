"""Simple build script to run compiler, tests, and build distribution artifacts.

Usage:
  python tools/build_release.py --version 0.1.0
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd, check=True):
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, check=check)
    return res.returncode


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="Optional version to set in pyproject.toml")
    args = parser.parse_args(argv)

    root = Path.cwd()

    # Step 1: run compiler to collect files
    run([sys.executable, "tools/py_compiler.py", "--output", "compiled_py", "--package", "collected_package"]) 

    # Step 2: run tests
    run([sys.executable, "-m", "pytest", "-q"]) 

    # Step 3: build artifacts
    run([sys.executable, "-m", "pip", "install", "--upgrade", "build"]) 
    run([sys.executable, "-m", "build", "--sdist", "--wheel"]) 

    print("Build finished. Artifacts available in ./dist/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
