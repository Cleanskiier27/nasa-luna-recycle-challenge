#!/usr/bin/env python3
"""
Install helper: installs Python deps and optionally runs migrations / builds.
Usage:
  python ./scripts/install.py          # default: install requirements if present
  python ./scripts/install.py --no-deps
  python ./scripts/install.py --build --npm
  python ./scripts/install.py --migrate

This script uses the current Python interpreter for pip installs and avoids shell=True calls.
"""
import argparse
import subprocess
import sys
from pathlib import Path
import shutil


def run(cmd, check=True):
    if isinstance(cmd, (list, tuple)):
        print(">>> Running:", " ".join(cmd))
    else:
        print(">>> Running:", cmd)
        cmd = cmd if isinstance(cmd, (list, tuple)) else cmd.split()
    try:
        subprocess.run(cmd, check=check)
    except subprocess.CalledProcessError as e:
        print(f"Command failed (exit {e.returncode}): {' '.join(cmd)}")
        sys.exit(e.returncode)


def pip_install(req_file: Path):
    pip_cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", str(req_file)]
    run(pip_cmd)


def npm_install_and_build(build=False):
    if not shutil.which("npm"):
        print("npm not found in PATH; skipping npm steps.")
        return
    run(["npm", "install"])
    if build:
        run(["npm", "run", "build"]) 


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-deps", action="store_true", help="Skip installing Python requirements")
    p.add_argument("--build", action="store_true", help="Run build step (npm build if --npm set)")
    p.add_argument("--npm", action="store_true", help="Run npm install/build where appropriate")
    p.add_argument("--migrate", action="store_true", help="Run Django/Flask migration step (customize as needed)")
    args = p.parse_args()

    req = Path("requirements.txt")
    if not args.no_deps and req.exists():
        pip_install(req)
    else:
        print("Skipping Python deps (no requirements.txt or --no-deps).")

    if args.npm:
        npm_install_and_build(build=args.build)

    if args.migrate:
        # Customize this command to your framework:
        # run([sys.executable, "manage.py", "migrate"])  # Django
        print("Migration requested but no default command defined. Customize `--migrate` behavior in the script.")

    print("Install script completed successfully.")


if __name__ == "__main__":
    main()
