"""Package entry point so `python -m scopinglang` runs the CLI."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
