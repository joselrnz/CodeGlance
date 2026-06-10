"""CLI process entrypoint."""

from __future__ import annotations

import sys

from .parser import SUBCOMMANDS, build_parser


def main(argv: list[str] | None = None) -> int:
    """Parse args, default to `analyze`, and dispatch to a command handler."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in SUBCOMMANDS and argv[0] not in ("-h", "--help", "--version"):
        argv = ["analyze", *argv]

    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
