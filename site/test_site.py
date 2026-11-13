#!/usr/bin/env python3
"""Validate that the library Pages site is not a duplicate CAD model gallery."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
from build import EXAMPLES
from qualification_cases import QUALIFICATION_CASES, QUALIFICATION_GROUPS
from api_coverage import EXPORT_COVERAGE, CAPABILITY_COVERAGE
from capability_map import SOLIDCRAFT_CAPABILITIES, REFERENCE_MODELS
import scpf


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
    for term in ("rotate(", "occurrence.move", "does not compose", "rotate(Z, 180)"):
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
        "Assembly-owned named anchors",
        "with_anchor()",
        "Associative in-plane attachment offset",
        "attach(offset=(u, v))",
        "front_top_left",
    ):
        assert term in components, term
    assert "AnchorFrame" in cheatsheet and "child=mount" in cheatsheet
    assert "AnchorTopology" in cheatsheet
    assert "assembly.with_anchor" in cheatsheet
    assert "attach(offset=(u, v))" in cheatsheet
    qualification_index = (site / "qualification" / "index.html").read_text(encoding="utf-8")
    qualification_manifest = json.loads(
        (site / "qualification" / "manifest.json").read_text(encoding="utf-8")
    )
    coverage_page = (
        site / "qualification" / "coverage" / "index.html"
    ).read_text(encoding="utf-8")
    assert set(scpf.__all__) == set(EXPORT_COVERAGE), (
        "Every public scpf.__all__ symbol must have a declared qualification row"
    )
    assert "API & SolidCraft coverage matrix" in coverage_page
    for api_name in scpf.__all__:
        assert f"<code>{api_name}</code>" in coverage_page, api_name
    for group, capability, target, current, cases, note in CAPABILITY_COVERAGE:
        assert capability in coverage_page, capability
        assert target.startswith("Q")
        assert current == "GAP" or current.startswith("Q")

    assert "Qualification" in home and "Qualification" in qualification_index
    assert "Q1" in qualification_index and "Q6" in qualification_index
    assert qualification_manifest["library_commit"] == sha
    assert qualification_manifest["solidcraft_version"] == "0.30.1"
    assert set(qualification_manifest["cases"]) == {
        case["slug"] for case in QUALIFICATION_CASES
    }
    group_keys = {key for key, _, _ in QUALIFICATION_GROUPS}
    assert all(case["group"] in group_keys for case in QUALIFICATION_CASES)
    for _, title, _ in QUALIFICATION_GROUPS:
        assert title in qualification_index
    capability_page = (
        site / "qualification" / "capabilities" / "index.html"
    ).read_text(encoding="utf-8")
    assert "SolidCraft capability & Forge API map" in capability_page
    for item in REFERENCE_MODELS:
        assert item["name"] in capability_page
    for _, capability, *_ in SOLIDCRAFT_CAPABILITIES:
        assert capability in capability_page
    for case in QUALIFICATION_CASES:
        slug = case["slug"]
        page_text = (
            site / "qualification" / slug / "index.html"
        ).read_text(encoding="utf-8")
        for heading in (
            "Forge contract",
            "Internal Forge model",
            "SolidCraft lowering",
            "Native verification",
            "Parametric mutation",
            "Reference models",
        ):
            assert heading in page_text, (slug, heading)
        assert case["title"] in page_text
        assert (site / "qualification" / slug / "model.py").is_file()
        assert (site / "qualification" / slug / "commands.json").is_file()
        if require_native:
            assert "Q1–Q6 native verified" in page_text, slug
            image = site / "qualification" / slug / "model.png"
            assert image.is_file() and image.stat().st_size > 0, slug
            assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            native_evidence = qualification_manifest["cases"][slug]["native_evidence"]
            assert "measurements.json" in native_evidence, slug
            assert "results.json" in native_evidence, slug

    manifest = json.loads((site / "manifest.json").read_text(encoding="utf-8"))
    assert (site / ".nojekyll").is_file()
    assert (site / "style.css").is_file()
    assert set(manifest["examples"]) == set(EXAMPLES)
    assert manifest["qualifier"] == "command-generation"
    assert manifest["library_commit"] == sha and sha in home
    assert "SolidCraft CAD projects" in home and "SCPF examples" in home
    assert "Full SolidCraft CAD projects" in home
    assert "Cheatsheet" in home and "Cheatsheet" in cheatsheet
    assert "Qualification" in home
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
