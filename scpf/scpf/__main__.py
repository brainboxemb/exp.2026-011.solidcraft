"""CLI: python -m scpf <script.py> --out <commands.json>."""
import argparse
import json
from pathlib import Path

from .runner import run_script


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    document = run_script(args.script)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"{args.out}: {len(document['commands'])} SolidCraft commands")


if __name__ == "__main__":
    main()
