# Repo Compiler Tooling

This workspace includes `tools/py_compiler.py` which:

- Collects all `.py` files from the repository (respects `.gitignore` when `pathspec` is available)
- Copies them into an output folder (`compiled_py` by default)
- Generates `repo_index.json` with file metadata (size, mtime, sha256)
- Scaffolds a package (default name: `collected_package`) and a single test that imports submodules
- Optionally disables Azure Pipelines by renaming `azure-pipelines.yml` to `.azure-pipelines.disabled`

Quick start

1. Install tools locally:
   python -m pip install -r requirements.txt

2. Run the compiler (defaults):
   python tools/py_compiler.py

3. Build and run tests in Docker:
   docker build -t repo-tools .
   docker run --rm repo-tools

CI / Main build

This repo includes a GitHub Actions workflow at `.github/workflows/build-and-test.yml` that runs on pushes to `main` and on pull requests. The workflow will:

- Install dependencies
- Run `tools/py_compiler.py` to collect Python files
- Run test suite (`pytest`)
- Build distribution artifacts (`python -m build`)
- Upload `dist/` as workflow artifacts

You can reproduce the main build locally with:

    python -m pip install -r requirements.txt
    python tools/build_release.py


Flags

- `--output` output folder (default: `compiled_py`)
- `--package` package name (default: `collected_package`)
- `--bypass-azure` rename `azure-pipelines.yml` to `.azure-pipelines.disabled`
- `--restore-azure` restore it back

Notes

- If `pathspec` is not installed, the script uses a simple fallback for some `.gitignore` rules.
- The script preserves relative layout of collected files under the output folder.
