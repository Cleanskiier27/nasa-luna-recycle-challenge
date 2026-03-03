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


def run(cmd, check=True, cwd=None):
    """Run a command as a list or string. Optionally set working directory."""
    if isinstance(cmd, (list, tuple)):
        printable = " ".join(cmd)
    else:
        printable = cmd
        cmd = cmd if isinstance(cmd, (list, tuple)) else cmd.split()

    print(">>> Running:", printable)
    try:
        subprocess.run(cmd, check=check, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command failed (exit {e.returncode}): {printable}")
        sys.exit(e.returncode)


def pip_install(req_file: Path):
    pip_cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", str(req_file)]
    run(pip_cmd)


def npm_install_and_build(build=False, cwd: Path | None = None):
    if not shutil.which("npm"):
        print("npm not found in PATH; skipping npm steps.")
        return
    run(["npm", "install"], cwd=str(cwd) if cwd else None)
    if build:
        run(["npm", "run", "build"], cwd=str(cwd) if cwd else None)


def docker_available() -> bool:
    return shutil.which("docker") is not None


def docker_build(context_path: Path, image_name: str) -> None:
    if not docker_available():
        print("Docker not found in PATH; skipping docker build.")
        return
    print(f"Building Docker image '{image_name}' from {context_path}")
    # Use context '.' and run from the package directory
    run(["docker", "build", "-t", image_name, "."], cwd=str(context_path))


def docker_run(image_name: str, host_port: int = 5174, container_port: int = 80) -> None:
    if not docker_available():
        print("Docker not found in PATH; skipping docker run.")
        return
    print(f"Running Docker image '{image_name}' mapping host:{host_port} -> container:{container_port}")
    run(["docker", "run", "--rm", "-d", "-p", f"{host_port}:{container_port}", image_name])


DEFAULT_PACKAGES = ["dashboard", "challengerepo/real-time-overlay"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-deps", action="store_true", help="Skip installing Python requirements")
    p.add_argument("--build", action="store_true", help="Run build step (npm build if --npm set)")
    p.add_argument("--npm", action="store_true", help="Run npm install/build where appropriate")
    p.add_argument("--migrate", action="store_true", help="Run Django/Flask migration step (customize as needed)")

    p.add_argument("--docker", action="store_true", help="Build Docker images for Vite packages")
    p.add_argument("--packages", nargs="+", default=DEFAULT_PACKAGES, help="List of package paths to dockerize")
    p.add_argument("--image", help="Image name to use for built images (if omitted, uses <pkgname>:latest)")
    p.add_argument("--docker-run", action="store_true", help="Run built Docker images after building")
    p.add_argument("--docker-host-port", type=int, default=None, help="Host port to map to container (if omitted, uses defaults per package)")

    args = p.parse_args()

    req = Path("requirements.txt")
    if not args.no_deps and req.exists():
        pip_install(req)
    else:
        print("Skipping Python deps (no requirements.txt or --no-deps).")

    if args.npm:
        # Run npm install/build at repo root; package-specific builds are handled during docker steps
        npm_install_and_build(build=args.build, cwd=None)

    if args.migrate:
        # Customize this command to your framework:
        # run([sys.executable, "manage.py", "migrate"])  # Django
        print("Migration requested but no default command defined. Customize `--migrate` behavior in the script.")

    if args.docker:
        for pkg in args.packages:
            pkg_path = Path(pkg)
            if not pkg_path.exists():
                print(f"Package path not found: {pkg_path} — skipping")
                continue

            # Default image name
            image_name = args.image if args.image else f"{pkg_path.name}:latest"

            # Build with docker
            docker_build(pkg_path, image_name)

            # Optionally run it locally
            if args.docker_run:
                # sensible defaults per package if host port not provided
                if args.docker_host_port:
                    host_port = args.docker_host_port
                elif pkg_path.name == "dashboard":
                    host_port = 5174
                elif "overlay" in pkg_path.name or "real-time-overlay" in pkg_path.as_posix():
                    host_port = 5175
                else:
                    host_port = 8000

                # container ports: the Dockerfiles expose 80 (dashboard) and 3000 (overlay serve), so attempt common mapping
                container_port = 80 if pkg_path.name == "dashboard" else 3000 if "overlay" in pkg_path.name or "real-time-overlay" in pkg_path.as_posix() else 80
                docker_run(image_name, host_port=host_port, container_port=container_port)

    print("Install script completed successfully.")


if __name__ == "__main__":
    main()
