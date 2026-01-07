from __future__ import annotations
import sys


def compile_main(argv=None):
    # Delegate to tools.py_compiler
    try:
        from tools.py_compiler import main as _main
    except Exception:
        # Fallback to compiled location
        from compiled_py.tools.py_compiler import main as _main
    return _main(argv)


def build_main(argv=None):
    try:
        from tools.build_release import main as _main
    except Exception:
        from compiled_py.tools.build_release import main as _main
    return _main(argv)


def main():
    # Simple CLI entry that defaults to compile
    return compile_main()


if __name__ == "__main__":
    raise SystemExit(main())
