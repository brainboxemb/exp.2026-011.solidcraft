#!/usr/bin/env python3
"""Validate that the library Pages site is not a duplicate CAD model gallery."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
from build import EXAMPLES


def check(site: Path, sha: str):
    home = (site / "index.html").read_text(encoding="utf-8")
    cheatsheet = (site / "cheatsheet" / "index.html").read_text(encoding="utf-8")
    manifest = json.loads((site / "manifest.json").read_text(encoding="utf-8"))
    assert (site / ".nojekyll").is_file()
    assert (site / "style.css").is_file()
    assert set(manifest["examples"]) == set(EXAMPLES)
    assert manifest["qualifier"] == "command-generation"
    assert manifest["library_commit"] == sha and sha in home
    assert "SolidCraft CAD projects" in home and "SCPF examples" in home
    assert "Full SolidCraft CAD projects" in home
    assert "Cheatsheet" in home and "Cheatsheet" in cheatsheet
    for concept in ("Box(", "Rectangle2D(", "Hole(", "copy()", "rotate(", "python -m scpf"):
        assert concept in cheatsheet, concept
    # The library page has only tiny fixtures. CAD models and native renders
    # MUST NOT be copied into this independent site.
    assert not (site / "models").exists()
    assert not (site / "previews").exists()
    assert not list(site.rglob("native.png"))
    for slug, info in manifest["examples"].items():
        page = (site / "examples" / slug / "index.html").read_text(encoding="utf-8")
        src = (site / info["source"]).read_text(encoding="utf-8")
        commands = json.loads((site / info["commands"]).read_text(encoding="utf-8"))["commands"]
        assert src.strip()
        assert len(commands) == info["command_count"] > 0
        assert "Not a native BRep render" in page
        assert "commands.json" in page and "model.py" in page
    print(f"OK: {len(EXAMPLES)} compiled library examples, cheatsheet, no CAD duplicates")


if __name__ == "__main__":
    check(Path(sys.argv[1]), sys.argv[2])
