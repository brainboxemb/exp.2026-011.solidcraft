#!/usr/bin/env python3
"""Validate that the library Pages site is not a duplicate CAD model gallery."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
from build import EXAMPLES


def check(site: Path, sha: str, require_native: bool = False):
    home = (site / "index.html").read_text(encoding="utf-8")
    cheatsheet = (site / "cheatsheet" / "index.html").read_text(encoding="utf-8")
    from build import GUIDES
    guide_index = (site / "guide" / "index.html").read_text(encoding="utf-8")
    assert "API Guide" in home and "API Guide" in guide_index
    assert "full API Guide" in cheatsheet
    for chapter in GUIDES:
        page = (site / "guide" / chapter["slug"] / "index.html").read_text(encoding="utf-8")
        assert chapter["title"] in page
        assert "guide-sidebar" in page and "guide-article" in page
        assert len(page) > 1400, chapter["slug"]
    transformations = (site / "guide" / "transformations" / "index.html").read_text(encoding="utf-8")
    for term in ("orient(", "rotate(", "occurrence.move", "does not compose", "rotate(Z, 180)"):
        assert term in transformations, term
    components = (site / "guide" / "components" / "index.html").read_text(encoding="utf-8")
    for term in (
        "AnchorFrame",
        "point plus orientation",
        "child=mount",
        "anchors()",
        "joint.create",
        "direct <code>AnchorFrame</code>",
        "AnchorTopology",
        "follow an edge or corner",
    ):
        assert term in components, term
    assert "AnchorFrame" in cheatsheet and "child=mount" in cheatsheet
    assert "AnchorTopology" in cheatsheet
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
        image = site / info["preview"]
        assert image.is_file() and image.stat().st_size > 0
        assert info["preview_kind"] in ("native-snapshot", "schematic")
        assert f'src="{image.name}"' in page
        assert f'examples/{slug}/{image.name}' in home
        if require_native:
            assert info["preview_kind"] == "native-snapshot", slug
        if info["preview_kind"] == "native-snapshot":
            assert image.suffix == ".png"
            assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            assert "Native SolidCraft 0.30.1 render" in page
        else:
            assert image.suffix == ".svg"
            assert "Schematic illustration only" in page
        assert "commands.json" in page and "model.py" in page
    print(f"OK: {len(EXAMPLES)} compiled library examples, cheatsheet, no CAD duplicates")


if __name__ == "__main__":
    check(Path(sys.argv[1]), sys.argv[2], require_native="--require-native" in sys.argv[3:])
