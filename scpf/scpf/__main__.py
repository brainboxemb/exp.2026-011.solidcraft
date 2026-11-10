"""SCPF compiler: generate SolidCraft command JSON or send to a running GUI."""
import argparse
import json
from pathlib import Path

from .live import LiveError, send_commands
from .runner import run_script


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="Trusted SCPF Python model script")
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--out", type=Path, help="Write generated native SolidCraft command JSON")
    output.add_argument(
        "--connect", nargs="?", const="auto", metavar="PORT",
        help="Send commands to the open SolidCraft GUI; optional 127.0.0.1:PORT",
    )
    args = parser.parse_args(argv)
    document = run_script(args.script)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        print(f"{args.out}: {len(document['commands'])} SolidCraft commands")
        return 0

    # Intentionally no implicit GUI launch, file open, or destructive doc.new.
    # The user should have an empty GUI document before the first demo.
    try:
        result = send_commands(document["commands"], connect=args.connect)
    except LiveError as exc:
        parser.exit(1, f"SCPF live: {exc}\n")
    print(f"Live SolidCraft: {result['completed']} commands applied to the open design")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
