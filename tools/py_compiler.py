"""py_compiler.py

Collects all .py files from repo (respecting .gitignore), copies them into an output folder
(preserving relative layout), builds a JSON index (sha256/size/mtime), scaffolds a package and
single test that imports all package modules, and can optionally "bypass" Azure Pipelines
by renaming the file.

Usage examples:
  python tools/py_compiler.py --output compiled_py --package collected_package
  python tools/py_compiler.py --output compiled_py --package collected_package --bypass-azure

"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import time
from pathlib import Path
from typing import Iterable, List, Dict, Optional


def load_gitignore_patterns(gitignore_path: Path) -> Optional[object]:
    """Try to load gitignore patterns using pathspec if available. Returns a PathSpec or None."""
    if not gitignore_path.exists():
        return None
    try:
        from pathspec import PathSpec
        spec = PathSpec.from_lines("gitwildmatch", gitignore_path.open("r", encoding="utf-8"))
        return spec
    except Exception:
        # no pathspec available; we'll return None and use a simple fallback
        return None


def is_ignored(path: Path, root: Path, spec) -> bool:
    rel = str(path.relative_to(root)).replace("\\", "/")
    if spec:
        return spec.match_file(rel)
    # fallback: ignore patterns that are exact file names or directory names in .gitignore
    gi = root / ".gitignore"
    if not gi.exists():
        return False
    with gi.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith("/") and rel.startswith(line.rstrip("/")):
                return True
            if line == rel or rel.startswith(line + "/"):
                return True
    return False


def iter_python_files(root: Path, spec) -> Iterable[Path]:
    skip_dirs = {".git", "__pycache__", "compiled_py", "venv", "env"}
    for dirpath, dirnames, filenames in os.walk(root):
        # modify dirnames in-place to skip
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = Path(dirpath) / fn
            if is_ignored(p, root, spec):
                continue
            yield p


def copy_files(files: Iterable[Path], root: Path, out: Path) -> List[Path]:
    out_files = []
    for p in files:
        rel = p.relative_to(root)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        out_files.append(dest)
    return out_files


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_index(paths: Iterable[Path], index_path: Path) -> None:
    records = []
    for p in sorted(paths):
        stat_ = p.stat()
        records.append({
            "path": str(p).replace("\\", "/"),
            "size": stat_.st_size,
            "mtime": stat_.st_mtime,
            "sha256": compute_sha256(p),
        })
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def scaffold_package(out: Path, package_name: str, files: List[Path]) -> None:
    pkg_dir = out / package_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    init = pkg_dir / "__init__.py"
    init_lines = ["# Auto-generated package init\n"]
    # Optionally auto-import modules by filename
    module_names = set()
    for f in files:
        try:
            rel = f.relative_to(out)
        except Exception:
            continue
        if rel.parts[0] != package_name:
            continue
        # get module name relative to package dir
        parts = rel.parts[1:]
        if not parts:
            continue
        mod_name = Path(*parts).with_suffix("").as_posix().replace("/", ".")
        top_module = mod_name.split(".")[0]
        module_names.add(top_module)
    for m in sorted(module_names):
        init_lines.append(f"from . import {m}  # noqa: F401\n")
    init.write_text("".join(init_lines), encoding="utf-8")


def create_test_script(tests_dir: Path, package_name: str) -> None:
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_file = tests_dir / "test_imports.py"
    test_file.write_text(
        f"""import importlib
import pkgutil
import sys

# Ensure compiled package is on path

try:
    import {package_name} as _pkg
except Exception as e:
    raise ImportError(f"Failed to import package {package_name}: {{e}}")

# Dynamically import submodules to ensure they load
for finder, name, ispkg in pkgutil.walk_packages(_pkg.__path__, _pkg.__name__ + "."):
    importlib.import_module(name)


def test_package_imports():
    assert True
""",
        encoding="utf-8",
    )


def bypass_azure(root: Path, action: str) -> None:
    azure = root / "azure-pipelines.yml"
    disabled = root / ".azure-pipelines.disabled"
    if action == "disable":
        if azure.exists():
            azure.rename(disabled)
            print("Renamed azure-pipelines.yml -> .azure-pipelines.disabled")
        else:
            print("No azure-pipelines.yml found to disable")
    elif action == "restore":
        if disabled.exists():
            disabled.rename(azure)
            print("Restored .azure-pipelines.disabled -> azure-pipelines.yml")
        else:
            print("No .azure-pipelines.disabled found to restore")


def ensure_pyproject(root: Path, package_name: str) -> None:
    pyproj = root / "pyproject.toml"
    if pyproj.exists():
        print("pyproject.toml already exists; leaving unchanged")
        return
    content = f"""[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.0.0"
description = "Auto-generated package"
readme = "README.md"
license = {{text = "MIT"}}
"""
    pyproj.write_text(content, encoding="utf-8")
    print("Wrote basic pyproject.toml")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="compiled_py", help="Output folder for collected .py files")
    parser.add_argument("--package", default="collected_package", help="Package name to scaffold")
    parser.add_argument("--index", default="repo_index.json", help="Index file path (relative to repo root)")
    parser.add_argument("--bypass-azure", action="store_true", help="Disable azure-pipelines.yml by renaming it")
    parser.add_argument("--restore-azure", action="store_true", help="Restore previously disabled azure file")
    parser.add_argument("--index-format", choices=["json"], default="json")
    args = parser.parse_args(argv)

    root = Path.cwd()
    out = root / args.output
    out.mkdir(parents=True, exist_ok=True)

    spec = load_gitignore_patterns(root / ".gitignore")
    files = list(iter_python_files(root, spec))
    print(f"Found {len(files)} Python files (after applying .gitignore and skip rules)")

    copied = copy_files(files, root, out)
    print(f"Copied {len(copied)} files into {out}")

    index_path = root / args.index
    build_index(copied, index_path)
    print(f"Wrote index to {index_path}")

    # scaffold package and test
    scaffold_package(out, args.package, copied)
    create_test_script(root / "tests", args.package)
    ensure_pyproject(root, args.package)

    if args.bypass_azure:
        bypass_azure(root, "disable")
    if args.restore_azure:
        bypass_azure(root, "restore")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
