#!/usr/bin/env python3
"""Validate that the library Pages site is not a duplicate CAD model gallery."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
from build import EXAMPLES, QUALIFICATION_CASES, QUALIFICATION_GROUPS
from api_coverage import EXPORT_COVERAGE, CAPABILITY_COVERAGE
from capability_map import CAPABILITY_GROUPS, SOLIDCRAFT_CAPABILITIES
import scpf


def check(site: Path, sha: str, require_native: bool = False):
    template_dir = ROOT / "qualification" / "templates"
    for template_name in (
        "case.html",
        "index.html",
        "results.html",
        "coverage.html",
        "joint-anatomy.html",
        "report.md",
    ):
        template = template_dir / template_name
        assert template.is_file() and template.stat().st_size > 0, template_name

    home = (site / "index.html").read_text(encoding="utf-8")
    cheatsheet = (site / "cheatsheet" / "index.html").read_text(encoding="utf-8")
    from build import GUIDES
    guide_index = (site / "guide" / "index.html").read_text(encoding="utf-8")
    assert "API Guide" in home and "API Guide" in guide_index
    assert 'class="development-banner"' in home
    assert "Development version." in home
    assert "not a support guarantee" in home
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
    results_page = (
        site / "qualification" / "results" / "index.html"
    ).read_text(encoding="utf-8")
    assert "Qualification results" in results_page
    for page_text in (qualification_index, coverage_page, results_page):
        assert 'class="development-banner"' in page_text
        assert "Development version." in page_text
        assert "not a support guarantee" in page_text
    assert set(scpf.__all__) == set(EXPORT_COVERAGE), (
        "Every public scpf.__all__ symbol must have a declared qualification row"
    )
    assert "SolidCraft functionality coverage" in coverage_page
    for api_name in scpf.__all__:
        assert f"<code>{api_name}</code>" in coverage_page, api_name
    for _, capability, *_ in SOLIDCRAFT_CAPABILITIES:
        assert capability in coverage_page, capability
    statuses = {
        status
        for _, _, _, status, *_ in SOLIDCRAFT_CAPABILITIES
    }
    assert statuses <= {"Supported", "Partial", "Missing"}
    assert "Basic primitives:</strong> 3/5 supported" in coverage_page
    assert "Coverage by area" in coverage_page
    for _, title in CAPABILITY_GROUPS:
        assert title in coverage_page, title
    for group, capability, target, current, cases, note in CAPABILITY_COVERAGE:
        assert capability in coverage_page, capability
        assert target.startswith("Q")
        assert current == "GAP" or current.startswith("Q")

    assert "Qualification" in home and "Qualification" in qualification_index
    assert 'href="joint-anatomy/"' in qualification_index
    joint_anatomy_page = (
        site / "qualification" / "joint-anatomy" / "index.html"
    ).read_text(encoding="utf-8")
    for term in (
        "Placing a corner bracket with Forge",
        "Nederlands — eenvoudige uitleg",
        "English — simple explanation",
        "The real SolidCraft relationship remains explicit",
        "AnchorFrame(",
        "<code>Anchor.RIGHT</code>",
        "child joint origin",
        "4 brackets",
        "8 brackets",
        "No second orientation solver",
        "Anchor.FRONT_TOP_LEFT",
        "z=+Y, x=-Z",
        "Anchor.BACK_TOP_RIGHT",
    ):
        assert term in joint_anatomy_page, term
    for diagram in (
        "solidcraft-joint-anatomy",
        "solidcraft-joint-references",
        "corner-bracket-goal",
        "corner-bracket-depth",
        "corner-bracket-local-axes",
        "corner-bracket-front-corners",
    ):
        for suffix in (".svg", ".dxf", ".cadcraft.json"):
            artifact = site / "qualification" / "joint-anatomy" / f"{diagram}{suffix}"
            assert artifact.is_file() and artifact.stat().st_size > 0, artifact
        assert f'src="{diagram}.svg"' in joint_anatomy_page
        assert f'href="{diagram}.cadcraft.json"' in joint_anatomy_page
    assert "Q1" in qualification_index and "Q6" in qualification_index
    assert 'class="reference-grid qualification-grid"' in qualification_index
    assert qualification_manifest["library_commit"] == sha
    assert qualification_manifest["solidcraft_version"] == "0.30.1"
    assert set(qualification_manifest["cases"]) == {
        case["slug"] for case in QUALIFICATION_CASES
    }
    group_keys = {key for key, _, _ in QUALIFICATION_GROUPS}
    assert all(case["group"] in group_keys for case in QUALIFICATION_CASES)
    for _, title, _ in QUALIFICATION_GROUPS:
        assert title in qualification_index
    assert not (site / "qualification" / "capabilities").exists()
    for case in QUALIFICATION_CASES:
        slug = case["slug"]
        page_text = (
            site / "qualification" / slug / "index.html"
        ).read_text(encoding="utf-8")
        for heading in (
            "1. Test setup",
            "Test goal",
            "Pass criteria",
            "2. Implementation under test",
            "Public Forge API used",
            "Forge model represented by this fixture",
            "3. Generated SolidCraft relationship",
            "6. Evidence and references",
            "Reference models",
        ):
            assert heading in page_text, (slug, heading)
        assert case["title"] in page_text
        setup_name = case.get("diagram", "setup.svg")
        setup_image = site / "qualification" / slug / setup_name
        assert setup_image.is_file() and setup_image.stat().st_size > 0, slug
        assert 'class="qualification-setup-diagram"' in page_text, slug
        assert f'href="{setup_name}"' in page_text, slug
        assert 'target="_blank"' in page_text, slug

        setup_pos = page_text.index("<h2>1. Test setup</h2>")
        implementation_pos = page_text.index("<h2>2. Implementation under test</h2>")
        command_pos = page_text.index("<h2>3. Generated SolidCraft relationship</h2>")
        assert setup_pos < implementation_pos < command_pos, slug

        for placeholder in (
            "$title",
            "$status",
            "$gallery",
            "$results",
            "$source",
        ):
            assert placeholder not in page_text, (slug, placeholder)
        assert (site / "qualification" / slug / "model.py").is_file()
        assert (site / "qualification" / slug / "commands.json").is_file()
        if require_native:
            manifest_case = qualification_manifest["cases"][slug]
            result_path = site / "qualification" / slug / "qualification-result.json"
            assert result_path.is_file(), slug
            structured_result = json.loads(result_path.read_text(encoding="utf-8"))
            assert structured_result["status"] in {
                "pass", "fail", "review", "incomplete"
            }, slug
            assert manifest_case["qualification_status"] == structured_result["status"], slug

            badge = {
                "pass": "PASS",
                "fail": "FAIL",
                "review": "REVIEW",
                "incomplete": "INCOMPLETE",
            }[structured_result["status"]]
            assert f">{badge}</span>" in page_text, slug

            assert structured_result["source_commit"] == sha, slug
            assert structured_result["solidcraft_version"] == "0.30.1", slug
            assert manifest_case["levels"] == structured_result["levels"], slug
            assert "Native runtime:" in page_text, slug
            assert "SolidCraft 0.30.1" in page_text, slug

            image = site / "qualification" / slug / "model.png"
            assert image.is_file() and image.stat().st_size > 0, slug
            assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            native_images = qualification_manifest["cases"][slug]["native_images"]
            for required_image in (
                "model.png",
                "model-front.png",
                "model-right.png",
                "model-iso.png",
            ):
                assert required_image in native_images, (slug, required_image)

            assert "<h2>1. Test setup</h2>" in page_text, slug
            assert "<h3>Test goal</h3>" in page_text, slug
            assert "<h3>Pass criteria</h3>" in page_text, slug
            assert "<h2>2. Implementation under test</h2>" in page_text, slug
            assert "<h2>4. Machine verification</h2>" in page_text, slug
            assert "<h2>5. Visual verification</h2>" in page_text, slug
            machine_pos = page_text.index("<h2>4. Machine verification</h2>")
            visual_pos = page_text.index("<h2>5. Visual verification</h2>")
            evidence_pos = page_text.index("<h2>6. Evidence and references</h2>")
            assert command_pos < machine_pos < visual_pos < evidence_pos, slug
            assert 'class="panel qualification-visual-check"' in page_text, slug
            assert 'class="qualification-image-link"' in page_text, slug
            assert 'href="model-iso.png"' in page_text, slug
            assert 'href="goal-iso.png"' in page_text, slug
            assert 'href="overlay-iso.png"' in page_text, slug
            assert f'src="{slug}/model-iso.png"' in qualification_index, slug
            assert 'class="qualification-case-preview"' in page_text, slug
            assert 'href="model-iso.png"' in page_text, slug
            assert 'src="model-iso.png"' in page_text, slug
            preview_pos = page_text.index('class="qualification-case-preview"')
            setup_pos = page_text.index("<h2>1. Test setup</h2>")
            assert preview_pos < setup_pos, slug
            native_evidence = qualification_manifest["cases"][slug]["native_evidence"]
            assert "measurements.json" in native_evidence, slug
            assert "results.json" in native_evidence, slug
            assert "validation.json" in native_evidence, slug
            assert "visual-validation.json" in native_evidence, slug

            # Qualification status is data, not a hard-coded historical
            # expectation.  The site must render whatever status the current
            # structured result reports (PASS/FAIL/REVIEW/INCOMPLETE).
            status = structured_result["status"]
            assert status in {"pass", "fail", "review", "incomplete"}, slug
            status_class = f'qualification-status {status}'
            assert status_class in page_text, (slug, status)

            if slug == "four-corner-l":
                cadcraft_source = (
                    site / "qualification" / slug / "four-corner-l.cadcraft.json"
                )
                assert cadcraft_source.is_file()
                plan = json.loads(cadcraft_source.read_text(encoding="utf-8"))
                plan_text = json.dumps(plan)
                assert "BOTTOM offset" in plan_text
                assert "CornerFoot contains geometry only" in plan_text
                assert (site / "qualification" / slug / "four-corner-l.dxf").is_file()
                assert "CadCraft source" in page_text
                assert ">DXF</a>" in page_text
                mutation_image = site / "qualification" / slug / "model-size-160x120.png"
                assert mutation_image.is_file() and mutation_image.stat().st_size > 0
                assert "model-size-160x120.png" in native_images
                assert mutation_image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

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
