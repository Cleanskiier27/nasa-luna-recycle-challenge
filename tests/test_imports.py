import importlib
import pkgutil
import sys
from pathlib import Path

# Ensure compiled package is on path (add `compiled_py` output folder if present)
repo_root = Path(__file__).resolve().parents[1]
compiled = repo_root / "compiled_py"
if compiled.exists() and str(compiled) not in sys.path:
    sys.path.insert(0, str(compiled))

try:
    import collected_package as _pkg
except Exception as e:
    raise ImportError(f"Failed to import package collected_package: {e}")

# Dynamically import submodules to ensure they load
for finder, name, ispkg in pkgutil.walk_packages(_pkg.__path__, _pkg.__name__ + "."):
    importlib.import_module(name)


def test_package_imports():
    assert True
