"""SCPF: compile Python CAD models or replay command JSON in SolidCraft."""
import argparse
import json
from pathlib import Path

from .live import LiveError, send_commands
from .runner import run_script


def read_command_file(path):
    """Load an existing SolidCraft command document without translating it."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read SolidCraft JSON {path}: {exc}") from exc
    if not isinstance(document, dict) or not isinstance(document.get("commands"), list):
        raise ValueError("SolidCraft JSON must contain a 'commands' array")
    if not document["commands"]:
        raise ValueError("SolidCraft JSON has no commands")
    for index, item in enumerate(document["commands"]):
        if (not isinstance(item, dict) or not isinstance(item.get("command"), str)
                or not isinstance(item.get("params", {}), dict)):
            raise ValueError(f"Invalid SolidCraft command at index {index}")
    return document


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "script", type=Path,
        help="SCPF model.py, or 'replay' followed by an existing SolidCraft JSON file",
    )
    parser.add_argument("replay_file", nargs="?", type=Path)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--out", type=Path, help="Write compiled SolidCraft command JSON")
    output.add_argument(
        "--connect", nargs="?", const="auto", metavar="PORT",
        help="Send commands to open SolidCraft; optional 127.0.0.1:PORT",
    )
    args = parser.parse_args(argv)

    replay = str(args.script) == "replay"
    if replay:
        if args.replay_file is None:
            parser.error("replay requires a SolidCraft .json file")
        if args.out is not None:
            parser.error("replay directly executes existing JSON; --out is not applicable")
        try:
            document = read_command_file(args.replay_file)
        except ValueError as exc:
            parser.error(str(exc))
    else:
        if args.replay_file is not None:
            parser.error("unexpected second file; use 'replay <file.json>'")
        if args.out is None and args.connect is None:
            parser.error("model scripts require --out or --connect")
        document = run_script(args.script)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        print(f"{args.out}: {len(document['commands'])} SolidCraft commands")
        return 0

    # Replay defaults to the active GUI; no conversion, no implicit doc.new.
    # If a source uses parameters.change, those params must already exist.
    try:
        result = send_commands(
            document["commands"], connect=args.connect or "auto"
        )
    except LiveError as exc:
        parser.exit(1, f"SCPF live: {exc}\n")
    print(f"Live SolidCraft: {result['completed']} commands applied to the open design")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
