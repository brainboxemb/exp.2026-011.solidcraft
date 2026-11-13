#!/usr/bin/env python3
"""Build a *library* API site from self-contained, regression-tested SCPF samples.

The complete mechanical CAD catalog belongs to 2026-011-02.cad.solidcraft.
This site deliberately contains only tiny fixtures and the SCPF cheatsheet.
"""
import argparse
import html
import json
from pathlib import Path
import shutil
from string import Template
import sys

ROOT = Path(__file__).resolve().parents[1]

from scpf.runner import run_script
from scpf.version import TESTED_SOLIDCRAFT_VERSION
from guides import GUIDES
from api_coverage import EXPORT_COVERAGE, CAPABILITY_COVERAGE
from capability_map import CAPABILITY_GROUPS, SOLIDCRAFT_CAPABILITIES, REFERENCE_MODELS

sys.path.insert(0, str(ROOT))
try:
    from qualification.cases import (
        QUALIFICATION_CASES,
        QUALIFICATION_LEVELS,
        QUALIFICATION_GROUPS,
        REFERENCE_URLS,
    )
finally:
    sys.path.pop(0)

LIBRARY_URL = "https://github.com/brainboxemb/lib.py.solidcraft.forge"
CAD_SITE = "https://brainboxemb.github.io/2026-011-02.cad.solidcraft/"

# Keep the public catalog deliberately small; advanced tests remain in the repo.
EXAMPLES = {
    "simple-box": {
        "title": "1 · Simple box",
        "description": "A plain Python class with three dimensions and one Box.",
        "concepts": ["Box", "build()", "parameters"],
    },
    "anchored-holes": {
        "title": "2 · Two holes",
        "description": "An extruded rectangle and two patterned through-holes.",
        "concepts": ["Rectangle2D", "extrude", "Hole", "pattern", "attach"],
    },
    "components": {
        "title": "3 · Reuse a component",
        "description": "Two instances of one Block definition, placed relative to meaningful component references.",
        "concepts": ["component", "occurrence", "Anchor", "attach"],
    },
    "corner-anchor": {
        "title": "4 · Associative corner anchor",
        "description": "Attach one reusable component to a named corner that follows parent size changes.",
        "concepts": ["Anchor", "attach", "corner", "associative placement"],
    },
    "custom-anchor": {
        "title": "5 · Named attachment frame",
        "description": "Expose a named local AnchorFrame from a component when the datum belongs to that reusable part.",
        "concepts": ["AnchorFrame", "anchors()", "attach", "named datum"],
    },
}

CHEATSHEET = [
    ("Model classes", [
        ("class Example: ... build(self)", "Write a Python model. No main() or show() is required.",
         "class SimpleBox:\n    def build(self):\n        return Box(40, 30, 10)", "simple-box"),
        ("Model parameters", "Numeric model fields become named SolidCraft parameters.",
         "length = 40.0\nBox(self.length, 30, 10)", "simple-box"),
    ]),
    ("Shapes and sketches", [
        ("Box(length, width, height)", "Solid, centered in XY; its bottom is at Z=0.",
         "Box(40, 30, 10)", "simple-box"),
        ("Rectangle2D(width, depth)", "Planar XY profile. Extrude it to create a solid.",
         "Rectangle2D(100, 60).extrude(10)", "anchored-holes"),
        ("Circle2D(d=...)", "A round 2D sketch. Use .at() or sketch operations to position it.",
         "Circle2D(d=8).at(12, 25)", None),
        ("Polygon2D(points, plane=...)", "A closed profile on XY, XZ or YZ.",
         "Polygon2D([(0,0), (40,0), (0,30)], plane='XZ')", None),
        ("Cylinder(d=..., h=...)", "Direct 3D cylinder, with its base at the placement point.",
         "Cylinder(d=24, h=14).at(0, 0, 8)", None),
    ]),
    ("Features and placement", [
        ("profile.extrude(distance)", "Convert a supported 2D profile into an editable native extrude.",
         "Rectangle2D(80, 50).extrude(8)", "anchored-holes"),
        ("Hole(d=..., depth=...)", "A native hole. THROUGH_ALL follows the target body.",
         "Hole(d=8, depth=Depth.THROUGH_ALL)", "anchored-holes"),
        ("shape.on(target, face=...)", "Place a feature on a selected face of another shape.",
         "Hole(d=8, depth=Depth.THROUGH_ALL).on(plate, face=Faces.TOP)", "anchored-holes"),
        ("shape.pattern(...)", "Repeat a supported feature before placing it on its parent shape.",
         "Hole(d=8, depth=Depth.THROUGH_ALL).pattern(count=2, spacing=40, axis=Axis.Y)", "anchored-holes"),
        ("shape.fillet(...)", "Round selected edges of a feature-based body.",
         "body.fillet(2, edges=Edges.VERTICAL)", None),
        ("shape.shell(...)", "Create an open-sided shell (supported feature trees only).",
         "Box(80, 50, 30).shell(2, open=Faces.TOP)", None),
        ("a + b / a - b / a & b", "Join, cut or intersect supported shapes; operation support depends on the shape types.",
         "body + Hole(d=8).at(0, 0, 10)", None),
    ]),
    ("Reusable components", [
        ("model.copy().move(x=...)", "Copy an occurrence of one definition; preserve editable feature history.",
         "second = first.copy().move(x=40)", "components"),
        ("model.attach(...)", "Fix one reusable component to another through explicit attachment references.",
         "right = Block().attach(left, parent=Anchor.RIGHT, child=Anchor.LEFT)", "components"),
        ("attach(offset=(u, v))", "Keep an in-plane attachment offset associative; parameter expressions become native planar-joint values.",
         "part.attach(base, parent=Anchor.FRONT_TOP_LEFT, child=mount, offset=(0, -wall + 12))", "components"),
        ("assembly.with_anchor(...) / anchor(...)", "Expose a semantic attachment datum owned by an assembly without adding application-specific anchors to a generic component.",
         "frame = (left + right).with_anchor(\"front_top_left\", left, ref)\nparent = frame.anchor(\"front_top_left\")", "components"),
        ("corner anchors", "Use one of the eight rectangular corner references when attaching components.",
         "marker = Marker().attach(base, parent=Anchor.FRONT_TOP_RIGHT, child=Anchor.BACK_TOP_RIGHT)", "corner-anchor"),
        ("AnchorFrame", "Define an oriented local attachment frame. Return it from anchors() when the datum belongs to the reusable component, or pass it directly to attach() when it belongs only to the assembly.",
         "mount = AnchorFrame(origin=(0,0,-12), z=(0,1,0), x=(0,0,-1))\npart.attach(base, parent=Anchor.FRONT_TOP_LEFT, child=mount)", "custom-anchor"),
        ("AnchorTopology", "Keep a named or assembly-local attachment reference on a planar-face edge or one of its endpoints so SolidCraft can follow changing geometry.",
         "def anchors(self):\n    return {\"mount\": AnchorTopology(edge=(0,10,5), on=(0,10,10), corner=(0,0,5))}", "custom-anchor"),
        ("model.rotate(axis=..., degrees=...)", "Orient a native occurrence; rotation does not alter the shared component.",
         "second = first.copy().move(x=40).rotate(axis=(0,0,1), degrees=180)", None),
    ]),
    ("Compile and inspect", [
        ("python -m scpf ... --out", "Compile a model to SolidCraft command JSON; no SolidCraft app needed.",
         "python -m scpf examples/simple-box/scpf/model.py --out output/box.json", "simple-box"),
        ("python -m scpf replay ...", "Send existing command JSON to an open SolidCraft session; does not recompile.",
         "python -m scpf replay output/box.json", None),
        ("python -m scpf ... --connect", "Execute a model in an open SolidCraft GUI document.",
         "python -m scpf examples/simple-box/scpf/model.py --connect", None),
    ]),
]


# A deliberately simple, labelled fallback for local/offline site builds.
# Production GitHub Pages uses real native SolidCraft snapshots from CI.
SCHEMATICS = {
  "simple-box": "<path d=\"M95 76 231 30 368 81 232 129Z\" fill=\"#bad8f2\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M95 76 232 129 V222 L95 168Z\" fill=\"#729eca\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M232 129 368 81 V169 L232 222Z\" fill=\"#91badf\" stroke=\"#31577c\" stroke-width=\"4\"/>",
  "anchored-holes": "<path d=\"M68 116 286 42 430 104 207 189Z\" fill=\"#bbd9f1\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M68 116 V143 L207 216 V189Z\" fill=\"#6f9fc9\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M207 189 430 104 V131 L207 216Z\" fill=\"#8bb8dc\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<ellipse cx=\"175\" cy=\"111\" rx=\"18\" ry=\"10\" fill=\"#f6faff\" stroke=\"#31577c\" stroke-width=\"3\"/>\n<ellipse cx=\"321\" cy=\"117\" rx=\"18\" ry=\"10\" fill=\"#f6faff\" stroke=\"#31577c\" stroke-width=\"3\"/>",
  "components": "<path d=\"M50 113 137 83 223 113 136 143Z\" fill=\"#bad8f2\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M50 113 V183 L136 212 V143Z\" fill=\"#729eca\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M136 143 223 113 V183 L136 212Z\" fill=\"#91badf\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M238 113 325 83 412 113 325 143Z\" fill=\"#b9d6f2\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M238 113 V183 L325 212 V143Z\" fill=\"#729eca\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M325 143 412 113 V183 L325 212Z\" fill=\"#91badf\" stroke=\"#31577c\" stroke-width=\"4\"/>",
  "corner-anchor": "<path d=\"M78 142 250 84 410 142 238 204Z\" fill=\"#bad8f2\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M78 142 V190 L238 246 V204Z\" fill=\"#729eca\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M238 204 410 142 V190 L238 246Z\" fill=\"#91badf\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M380 90 425 75 462 88 417 104Z\" fill=\"#d9e7f5\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<circle cx=\"410\" cy=\"142\" r=\"8\" fill=\"#ffffff\" stroke=\"#31577c\" stroke-width=\"3\"/>",
  "custom-anchor": "<path d=\"M210 35 245 47 245 215 210 203Z\" fill=\"#91badf\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M210 35 280 12 315 24 245 47Z\" fill=\"#bad8f2\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M245 47 315 24 315 192 245 215Z\" fill=\"#729eca\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<path d=\"M196 210 225 200 254 210 225 220Z\" fill=\"#d9e7f5\" stroke=\"#31577c\" stroke-width=\"4\"/>\n<circle cx=\"225\" cy=\"200\" r=\"7\" fill=\"#fff\" stroke=\"#31577c\" stroke-width=\"3\"/>"
}


def schematic(slug):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 260" '
        'role="img" aria-label="Schematic preview; not a SolidCraft render">'
        + SCHEMATICS[slug] + '</svg>'
    )


def escape(value):
    return html.escape(str(value), quote=True)


def _format_vector(values):
    return "[" + ", ".join(f"{float(value):g}" for value in values) + "]"


def _qualification_status(result):
    labels = {
        "pass": "PASS",
        "fail": "FAIL",
        "review": "REVIEW",
        "incomplete": "INCOMPLETE",
        "missing": "MISSING",
        "not-required": "N/R",
    }
    details = []
    for name in ("q1", "q2", "q3", "q4", "q5", "q6"):
        state = result.get("levels", {}).get(name, {}).get("status", "missing")
        q = name.upper()
        if state == "pass":
            details.append(q)
        elif state == "not-required":
            details.append(f"{q} N/R")
        else:
            details.append(f"{q} {labels.get(state, state.upper())}")
    overall_state = result.get("status", "incomplete")
    return labels.get(overall_state, overall_state.upper()), " · ".join(details)


def _qualification_status_html(overall, detail):
    status_class = {
        "PASS": "pass",
        "FAIL": "fail",
        "REVIEW": "review",
        "INCOMPLETE": "incomplete",
        "NOT RUN": "not-run",
    }.get(overall, "incomplete")
    return (
        '<div class="qualification-status-line">'
        f'<span class="qualification-status {status_class}">{escape(overall)}</span>'
        f'<span class="qualification-levels">{escape(detail)}</span>'
        '</div>'
    )


def _image_sort_key(name):
    if name == "model.png":
        return (0, "", 0)
    for view_index, view in enumerate(("front", "right", "iso"), 1):
        order = {
            f"model-{view}.png": 0,
            f"goal-{view}.png": 1,
            f"overlay-{view}.png": 2,
            f"visual-diff-{view}.png": 3,
        }
        if name in order:
            return (view_index, view, order[name])
    return (10, name, 0)


def _image_caption(name):
    if name == "model.png":
        return "Native baseline render."
    for view in ("front", "right", "iso"):
        if name == f"model-{view}.png":
            return f"Actual SolidCraft {view} view."
        if name == f"goal-{view}.png":
            return f"Expected/goal geometry in the same {view} camera."
        if name == f"overlay-{view}.png":
            return f"Actual {view} render with expected geometry overlaid."
        if name == f"visual-diff-{view}.png":
            return f"Visual regression diff for the {view} view."
    return f"Additional native evidence: {name}."


def _render_validation_checks(native_case):
    path = native_case / "validation.json"
    if not path.is_file():
        return ""
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for check in data.get("checks", []):
        status = check.get("status", "missing").upper()
        cls = "pass" if status == "PASS" else "fail"
        expected = json.dumps(check.get("expected"), ensure_ascii=False)
        actual = json.dumps(check.get("actual"), ensure_ascii=False)
        rows.append(
            "<tr>"
            f"<td><span class=\"qualification-status {cls}\">{escape(status)}</span></td>"
            f"<td>{escape(check.get('level', '').upper())}</td>"
            f"<td>{escape(check.get('name'))}</td>"
            f"<td><code>{escape(expected)}</code></td>"
            f"<td><code>{escape(actual)}</code></td>"
            "</tr>"
        )
    if not rows:
        return ""
    return (
        '<h3>Semantic validation</h3>'
        '<table class="qualification-checks"><thead><tr>'
        '<th>Status</th><th>Level</th><th>Check</th><th>Expected</th><th>Actual</th>'
        '</tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    )


def _render_native_results(native_case, solidcraft_version):
    measurement_files = sorted(native_case.glob("measurements*.json"))
    if not measurement_files:
        return (
            '<section class="panel"><h2>3. Results</h2>'
            '<p>No measurement JSON was produced.</p></section>',
            None,
            None,
        )

    sections = []
    baseline_body_count = None
    baseline_parameter_count = None

    for measurement in measurement_files:
        data = json.loads(measurement.read_text(encoding="utf-8"))
        label = (
            "Baseline"
            if measurement.name == "measurements.json"
            else measurement.stem.replace("measurements-", "").replace("-", " ")
        )

        bodies = data.get("bodies", [])
        params = data.get("params", [])
        if measurement.name == "measurements.json":
            baseline_body_count = data.get("body_count", len(bodies))
            baseline_parameter_count = len(params)

        parameter_rows = "".join(
            f"<tr><td><code>{escape(row.get('name'))}</code></td>"
            f"<td>{escape(row.get('value'))}</td></tr>"
            for row in params
        )
        parameter_table = (
            '<h4>Parameters</h4><table><thead><tr><th>Name</th><th>Value</th>'
            f'</tr></thead><tbody>{parameter_rows}</tbody></table>'
            if parameter_rows else "<p>No editable parameters in this result.</p>"
        )

        body_rows = "".join(
            f"<tr><td>{escape(body.get('name'))}</td>"
            f"<td><code>{escape(_format_vector(body['bbox']['min']))}</code></td>"
            f"<td><code>{escape(_format_vector(body['bbox']['max']))}</code></td></tr>"
            for body in bodies
            if body.get("bbox")
        )
        body_table = (
            '<h4>Bodies</h4><table><thead><tr><th>Body</th><th>BBox min</th>'
            f'<th>BBox max</th></tr></thead><tbody>{body_rows}</tbody></table>'
            if body_rows else "<p>No body measurements in this result.</p>"
        )

        sections.append(
            f'<details{" open" if measurement.name == "measurements.json" else ""}>'
            f'<summary><strong>{escape(label)}</strong> · '
            f'{escape(data.get("body_count", len(bodies)))} bodies · '
            f'<a href="{escape(measurement.name)}">{escape(measurement.name)}</a>'
            f'</summary>{parameter_table}{body_table}</details>'
        )

    return (
        '<section class="panel"><h2>3. Results</h2>'
        f'<p class="meta">Native runtime: <strong>SolidCraft '
        f'{escape(solidcraft_version)}</strong>. These values come from the '
        'saved native design, not from Python-side estimates.</p>'
        + "".join(sections)
        + _render_validation_checks(native_case)
        + "</section>",
        baseline_body_count,
        baseline_parameter_count,
    )


def page(title, body, *, stylesheet, home, cheatsheet):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{escape(title)} · SCPF Python library</title>
<link rel="stylesheet" href="{escape(stylesheet)}"></head>
<body><header class="top"><div class="wrap nav">
<a class="brand" href="{escape(home)}">SCPF <span>Python library</span></a>
<nav aria-label="Main"><a href="{escape(home)}">Examples</a><a href="{escape(home)}guide/">API Guide</a><a href="{escape(home)}qualification/">Qualification</a><a href="{escape(cheatsheet)}">Cheatsheet</a>\n<a href="{LIBRARY_URL}">Source</a></nav></div></header>
{body}
<footer><div class="wrap"><strong>SCPF</strong> generates commands; native SolidCraft creates the geometry.
<a href="{CAD_SITE}">Full SolidCraft CAD projects →</a></div></footer>
</body></html>"""


def text(path):
    return path.read_text(encoding="utf-8")


def render_template(name, **values):
    template_path = ROOT / "qualification" / "templates" / name
    return Template(text(template_path)).substitute(values)


def build(out, sha, native_root=None):
    """Compile the public examples and attach verified native screenshots if available.

    A .png is accepted only when the native verification file identifies the
    exact source SHA and the expected SolidCraft runtime. Outside native CI,
    emit plainly labelled SVG schematics rather than pretending a render.
    """
    verified = False
    metadata = {}
    if native_root is not None:
        meta_file = native_root / "verification.json"
        if not meta_file.is_file():
            raise ValueError("Native directory is missing verification.json")
        metadata = json.loads(meta_file.read_text(encoding="utf-8"))
        verified = (metadata.get("source_commit") == sha
                    and metadata.get("verified") is True
                    and metadata.get("solidcraft_version") == "0.30.1")
        if not verified:
            raise ValueError("Native screenshots do not match this source commit")

    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "site" / "style.css", out / "style.css")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    cards = []
    manifest = {"library_commit": sha, "qualifier": "command-generation", "examples": {}}
    for slug, info in EXAMPLES.items():
        source_path = ROOT / "examples" / slug / "scpf" / "model.py"
        commands = run_script(source_path)
        assert commands.get("commands"), f"{slug}: empty command list"
        dest = out / "examples" / slug
        dest.mkdir(parents=True, exist_ok=True)
        source = text(source_path)
        (dest / "model.py").write_text(source, encoding="utf-8")
        (dest / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
        count = len(commands["commands"])
        screenshot = native_root / slug / "model.png" if verified else None
        if screenshot is not None:
            if not screenshot.is_file() or screenshot.stat().st_size == 0:
                raise ValueError(f"Native screenshot missing or empty: {screenshot}")
            shutil.copyfile(screenshot, dest / "preview.png")
            preview_path = "preview.png"
            preview_kind = "native-snapshot"
            preview_caption = "Native SolidCraft 0.30.1 render, verified against this source commit."
        else:
            (dest / "preview.svg").write_text(schematic(slug), encoding="utf-8")
            preview_path = "preview.svg"
            preview_kind = "schematic"
            preview_caption = "Schematic illustration only; run the native CI job for a SolidCraft render."
        manifest["examples"][slug] = {"source": f"examples/{slug}/model.py",
                                      "commands": f"examples/{slug}/commands.json",
                                      "command_count": count,
                                      "preview": f"examples/{slug}/{preview_path}",
                                      "preview_kind": preview_kind}
        kinds = [row["command"] for row in commands["commands"]]
        timeline = "".join(f"<li><code>{escape(kind)}</code></li>" for kind in kinds)
        source_url = f"{LIBRARY_URL}/blob/main/examples/{slug}/scpf/model.py"
        body = f"""<main class="wrap"><div class="crumb"><a href="../../">← Examples</a> / {escape(info['title'])}</div>
<section class="hero small"><p class="eyebrow">Small API regression fixture</p>
<h1>{escape(info['title'])}</h1><p>{escape(info['description'])}</p>
<p class="meta"><span>Compiled: {count} native commands</span><span>{escape(preview_caption)}</span></p></section>
<figure class="example-image"><img src="{preview_path}" alt="{escape(info['title'])}: {escape(preview_caption)}" loading="lazy">
<figcaption>{escape(preview_caption)}</figcaption></figure>
<div class="twocol"><section class="panel"><h2>Python source</h2><pre><code>{escape(source)}</code></pre>
<a href="{escape(source_url)}">Open the editable source in GitHub →</a></section>
<section class="panel"><h2>Generated command sequence</h2><ol class="commands">{timeline}</ol>
<p><a class="button" href="commands.json">View command JSON →</a></p></section></div>
<section class="notice">The generated JSON is automatically rebuilt and checked by CI for every relevant change.
These examples are API smoke tests, not substitutes for a full mechanical CAD project or a native geometry certification.</section>
<p><a href="../../cheatsheet/">Related SCPF syntax in the cheatsheet →</a></p></main>"""
        (dest / "index.html").write_text(
            page(info["title"], body, stylesheet="../../style.css", home="../../", cheatsheet="../../cheatsheet/"),
            encoding="utf-8")
        tags = "".join(f'<span class="tag">{escape(x)}</span>' for x in info["concepts"])
        cards.append(f"""<article class="card"><a href="examples/{slug}/" class="card-image" aria-label="View {escape(info['title'])}"><img src="examples/{slug}/{preview_path}" alt="{escape(info['title'])} preview" loading="lazy"></a><div class="card-content"><p class="eyebrow">Regression example</p>
<h2><a href="examples/{slug}/">{escape(info['title'])}</a></h2>
<p>{escape(info['description'])}</p><div class="tags">{tags}</div>
<p class="meta">{count} generated SolidCraft commands</p>
<a class="button" href="examples/{slug}/">View source and command steps →</a></div></article>""")

    # Expanded, navigable documentation remains separate from tiny smoke-test
    # examples and from the quick cheatsheet.
    guide_root = out / "guide"
    guide_root.mkdir(exist_ok=True)
    guide_cards = []
    for chapter in GUIDES:
        slug = chapter["slug"]
        dest = guide_root / slug
        dest.mkdir(exist_ok=True)
        aside = "".join(
            f'<a href="../{escape(item["slug"])}/">{escape(item["title"])}</a>'
            for item in GUIDES
        )
        body = (
            '<main class="wrap guide-layout"><aside class="guide-sidebar">'
            '<h2>API Guide</h2><a href="../">All chapters</a>'
            + aside + '</aside><article class="guide-article">'
            + f'<p class="crumb"><a href="../">← API Guide</a> / {escape(chapter["title"])}</p>'
            + f'<h1>{escape(chapter["title"])}</h1>'
            + f'<p class="guide-lead">{escape(chapter["summary"])}</p>'
            + chapter["body"] + '</article></main>'
        )
        (dest / "index.html").write_text(
            page(chapter["title"], body, stylesheet="../../style.css",
                 home="../../", cheatsheet="../../cheatsheet/"),
            encoding="utf-8",
        )
        guide_cards.append(
            f'<article class="reference"><h2><a href="{escape(slug)}/">'
            f'{escape(chapter["title"])}</a></h2>'
            f'<p>{escape(chapter["summary"])}</p></article>'
        )
    guide_index = (
        '<main class="wrap"><section class="hero small">'
        '<p class="eyebrow">Detailed SCPF documentation</p>'
        '<h1>API Guide</h1>'
        '<p>Learn the concepts, understand the generated native commands, '
        'and check current support and limitations. '
        'The cheatsheet is a quick lookup, not a substitute for this guide.</p>'
        '</section><div class="reference-grid">'
        + "".join(guide_cards) + '</div></main>'
    )
    (guide_root / "index.html").write_text(
        page("API Guide", guide_index, stylesheet="../style.css",
             home="../", cheatsheet="../cheatsheet/"), encoding="utf-8"
    )

    # Qualification pages explain the full contract for each native fixture:
    # public API -> Forge model -> SolidCraft commands -> native evidence.
    qualification_root = out / "qualification"
    qualification_root.mkdir(exist_ok=True)
    qualification_cards = {key: [] for key, _, _ in QUALIFICATION_GROUPS}
    qualification_manifest = {}

    for case in QUALIFICATION_CASES:
        slug = case["slug"]
        source_path = ROOT / "examples" / slug / "scpf" / "model.py"
        commands = run_script(source_path)
        case_dir = qualification_root / slug
        case_dir.mkdir(exist_ok=True)
        source = text(source_path)
        (case_dir / "model.py").write_text(source, encoding="utf-8")
        (case_dir / "commands.json").write_text(
            json.dumps(commands, indent=2) + "\n",
            encoding="utf-8",
        )

        joint_commands = [
            command for command in commands["commands"]
            if command["command"].startswith("joint.")
        ]
        lowering_detail = (
            json.dumps(joint_commands, indent=2)
            if joint_commands
            else "\n".join(command["command"] for command in commands["commands"])
        )

        native_case = native_root / slug if verified else None
        native_files = []
        native_images = []
        qualification_result = None
        body_count = None
        parameter_count = None
        results_html = (
            '<section class="panel"><h2>3. Results</h2>'
            '<div class="notice">Native result data was not supplied to this '
            'site build. Run the native qualification for measured results.</div>'
            '</section>'
        )
        preview_html = (
            '<div class="notice">No source-matched native verification was supplied '
            'to this site build. The case sheet and command contract are still shown.</div>'
        )
        status = "NOT RUN"
        status_detail = "Q1 Q2 documented"
        if native_case is not None and native_case.is_dir():
            result_file = native_case / "qualification-result.json"
            if not result_file.is_file():
                raise ValueError(f"Structured qualification result missing: {result_file}")
            qualification_result = json.loads(result_file.read_text(encoding="utf-8"))
            if (
                qualification_result.get("source_commit") != sha
                or qualification_result.get("solidcraft_version") != metadata.get("solidcraft_version")
            ):
                raise ValueError(f"Qualification result does not match this build: {result_file}")
            snapshot = native_case / "model.png"
            if not snapshot.is_file() or snapshot.stat().st_size == 0:
                raise ValueError(f"Qualification snapshot missing or empty: {snapshot}")

            image_paths = sorted(
                native_case.glob("*.png"),
                key=lambda path: _image_sort_key(path.name),
            )
            for image in image_paths:
                if image.stat().st_size == 0:
                    raise ValueError(f"Qualification snapshot empty: {image}")
                shutil.copyfile(image, case_dir / image.name)
                native_images.append(image.name)

            for pattern in (
                "results*.json",
                "measurements*.json",
                "change-*.json",
                "parameters*.json",
                "joint-*.json",
                "model.json",
                "model*.sc",
                "model*.step",
                "export-*.json",
                "qualification-result.json",
                "validation.json",
                "visual-validation.json",
                "camera-*.json",
            ):
                for evidence in sorted(native_case.glob(pattern)):
                    shutil.copyfile(evidence, case_dir / evidence.name)
                    native_files.append(evidence.name)
            figures = []
            for index, image_name in enumerate(native_images):
                caption = _image_caption(image_name)
                figures.append(
                    '<figure class="qualification-image">'
                    f'<img src="{escape(image_name)}" '
                    f'alt="{escape(case["title"])} native SolidCraft evidence {index + 1}" loading="lazy">'
                    f'<figcaption>{escape(caption)}</figcaption></figure>'
                )
            preview_html = (
                '<div class="qualification-gallery">'
                + "".join(figures)
                + "</div>"
            )
            status, status_detail = _qualification_status(qualification_result)
            results_html, body_count, parameter_count = _render_native_results(
                native_case,
                metadata["solidcraft_version"],
            )

        reference_items = []
        for label, description in case["references"]:
            url = REFERENCE_URLS.get(label)
            label_html = (
                f'<a href="{escape(url)}">{escape(label)}</a>'
                if url else escape(label)
            )
            reference_items.append(
                f"<li><strong>{label_html}:</strong> {escape(description)}</li>"
            )

        evidence_items = [
            '<li><a href="model.py">Fixture source</a></li>',
            '<li><a href="commands.json">Generated command JSON</a></li>',
        ]
        evidence_items.extend(
            f'<li><a href="{escape(name)}">{escape(name)}</a></li>'
            for name in native_files
        )
        if native_images:
            evidence_items.extend(
                f'<li><a href="{escape(name)}">Native snapshot: {escape(name)}</a></li>'
                for name in native_images
            )

        case_body = render_template(
            "case.html",
            title=escape(case["title"]),
            status_badge=_qualification_status_html(status, status_detail),
            intent=escape(case["intent"]),
            gallery=preview_html,
            forge_api=escape(case["forge_api"]),
            forge_model=escape(case["forge_model"]),
            lowering=escape(case["lowering"]),
            native_expectation=escape(case["native_expectation"]),
            mutation=escape(case["mutation"]),
            evidence_items="".join(evidence_items),
            results=results_html,
            lowering_detail=escape(lowering_detail),
            reference_items="".join(reference_items),
            source=escape(source),
        )
        (case_dir / "index.html").write_text(
            page(
                f"Qualification · {case['title']}",
                case_body,
                stylesheet="../../style.css",
                home="../../",
                cheatsheet="../../cheatsheet/",
            ),
            encoding="utf-8",
        )

        qualification_manifest[slug] = {
            "title": case["title"],
            "status": status,
            "status_detail": status_detail,
            "command_count": len(commands["commands"]),
            "native_evidence": native_files,
            "native_images": native_images,
            "qualification_status": (
                qualification_result.get("status") if qualification_result else None
            ),
            "levels": (
                qualification_result.get("levels") if qualification_result else {}
            ),
            "solidcraft_version": (
                metadata.get("solidcraft_version") if verified else None
            ),
            "body_count": body_count,
            "parameter_count": parameter_count,
        }
        card_preview = (
            "model-iso.png" if "model-iso.png" in native_images
            else "model.png" if "model.png" in native_images
            else None
        )
        card_image = (
            f'<a href="{escape(slug)}/" class="qualification-card-image">'
            f'<img src="{escape(slug)}/{escape(card_preview)}" '
            f'alt="{escape(case["title"])} native isometric preview" loading="lazy"></a>'
            if card_preview else ""
        )
        qualification_cards[case["group"]].append(
            f'<article class="reference qualification-card">{card_image}'
            f'<div class="qualification-card-content">'
            + _qualification_status_html(status, status_detail)
            + f'<h2><a href="{escape(slug)}/">{escape(case["title"])}</a></h2>'
            f'<p>{escape(case["intent"])}</p>'
            f'<p><code>{escape(case["forge_api"])}</code></p>'
            + (
                f'<p class="meta">SolidCraft {escape(metadata.get("solidcraft_version"))}'
                f' · {escape(body_count)} bodies · {escape(parameter_count)} parameters</p>'
                if verified and body_count is not None else ""
            )
            + f'<a class="button" href="{escape(slug)}/">Open case sheet →</a></div></article>'
        )

    results_root = qualification_root / "results"
    results_root.mkdir(exist_ok=True)
    result_rows = []
    for case in QUALIFICATION_CASES:
        row = qualification_manifest[case["slug"]]
        result_rows.append(
            f"<tr><td><a href=\"../{escape(case['slug'])}/\">"
            f"{escape(case['title'])}</a></td>"
            f"<td>{_qualification_status_html(row['status'], row.get('status_detail', ''))}</td>"
            f"<td>{escape(row.get('solidcraft_version') or '—')}</td>"
            f"<td>{escape(row.get('body_count') if row.get('body_count') is not None else '—')}</td>"
            f"<td>{escape(row.get('parameter_count') if row.get('parameter_count') is not None else '—')}</td>"
            f"<td>{escape(len(row.get('native_evidence', [])))}</td></tr>"
        )
    results_body = render_template(
        "results.html",
        source_sha=escape(sha),
        solidcraft_version=escape(
            metadata.get("solidcraft_version") if verified else TESTED_SOLIDCRAFT_VERSION
        ),
        result_rows="".join(result_rows),
    )
    (results_root / "index.html").write_text(
        page(
            "Qualification results",
            results_body,
            stylesheet="../../style.css",
            home="../../",
            cheatsheet="../../cheatsheet/",
        ),
        encoding="utf-8",
    )

    level_rows = "".join(
        f"<tr><td><strong>{escape(level)}</strong></td><td>{escape(title)}</td>"
        f"<td>{escape(description)}</td></tr>"
        for level, title, description in QUALIFICATION_LEVELS
    )
    group_sections = "".join(
        f'<section class="section-heading"><h2>{escape(title)}</h2><p>{escape(description)}</p></section>'
        f'<div class="reference-grid qualification-grid">{"".join(qualification_cards[key])}</div>'
        for key, title, description in QUALIFICATION_GROUPS
        if qualification_cards[key]
    )
    qualification_index = render_template(
        "index.html",
        source_sha=escape(sha),
        solidcraft_version=escape(TESTED_SOLIDCRAFT_VERSION),
        level_rows=level_rows,
        group_sections=group_sections,
    )
    capability_root = qualification_root / "capabilities"
    capability_root.mkdir(exist_ok=True)
    capability_sections = []
    for group_key, group_title in CAPABILITY_GROUPS:
        rows = []
        for group, capability, solidcraft, forge, need, references, note in SOLIDCRAFT_CAPABILITIES:
            if group != group_key:
                continue
            rows.append(
                f"<tr><td><strong>{escape(capability)}</strong></td>"
                f"<td>{escape(solidcraft)}</td><td>{escape(forge)}</td>"
                f"<td>{escape(need)}</td><td>{escape(references)}</td>"
                f"<td>{escape(note)}</td></tr>"
            )
        if rows:
            capability_sections.append(
                f'<section class="panel"><h2>{escape(group_title)}</h2>'
                '<table><thead><tr><th>Capability</th><th>SolidCraft</th>'
                '<th>Forge today</th><th>Need</th><th>API reference</th>'
                '<th>Design note</th></tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table></section>'
            )

    reference_cards = "".join(
        f'<article class="reference"><h2><a href="{escape(item["url"])}">'
        f'{escape(item["name"])}</a></h2><p><strong>{escape(item["role"])}</strong></p>'
        f'<p>{escape(item["use"])}</p><p>{escape(item["strength"])}</p></article>'
        for item in REFERENCE_MODELS
    )
    capability_body = render_template(
        "capabilities.html",
        reference_cards=reference_cards,
        capability_sections="".join(capability_sections),
    )
    (capability_root / "index.html").write_text(
        page(
            "CAD capability map",
            capability_body,
            stylesheet="../../style.css",
            home="../../",
            cheatsheet="../../cheatsheet/",
        ),
        encoding="utf-8",
    )

    coverage_root = qualification_root / "coverage"
    coverage_root.mkdir(exist_ok=True)
    case_slugs = {case["slug"] for case in QUALIFICATION_CASES}

    def coverage_case_links(cases):
        links = []
        for name in cases:
            if name in case_slugs:
                links.append(f'<a href="../{escape(name)}/">{escape(name)}</a>')
            else:
                links.append(escape(name))
        return ", ".join(links) if links else "—"

    export_rows = []
    for api_name, (target, current, cases, note) in EXPORT_COVERAGE.items():
        export_rows.append(
            f"<tr><td><code>{escape(api_name)}</code></td>"
            f"<td>{escape(target)}</td><td><strong>{escape(current)}</strong></td>"
            f"<td>{coverage_case_links(cases)}</td><td>{escape(note)}</td></tr>"
        )

    capability_rows = []
    for group, capability, target, current, cases, note in CAPABILITY_COVERAGE:
        capability_rows.append(
            f"<tr><td>{escape(group)}</td><td><code>{escape(capability)}</code></td>"
            f"<td>{escape(target)}</td><td><strong>{escape(current)}</strong></td>"
            f"<td>{coverage_case_links(cases)}</td><td>{escape(note)}</td></tr>"
        )

    gap_exports = sum(1 for row in EXPORT_COVERAGE.values() if row[1] == "GAP")
    gap_capabilities = sum(1 for row in CAPABILITY_COVERAGE if row[3] == "GAP")
    coverage_body = render_template(
        "coverage.html",
        gap_exports=escape(gap_exports),
        gap_capabilities=escape(gap_capabilities),
        export_rows="".join(export_rows),
        capability_rows="".join(capability_rows),
    )
    (coverage_root / "index.html").write_text(
        page(
            "Qualification coverage",
            coverage_body,
            stylesheet="../../style.css",
            home="../../",
            cheatsheet="../../cheatsheet/",
        ),
        encoding="utf-8",
    )

    (qualification_root / "index.html").write_text(
        page(
            "Qualification",
            qualification_index,
            stylesheet="../style.css",
            home="../",
            cheatsheet="../cheatsheet/",
        ),
        encoding="utf-8",
    )
    (qualification_root / "manifest.json").write_text(
        json.dumps(
            {
                "library_commit": sha,
                "solidcraft_version": TESTED_SOLIDCRAFT_VERSION,
                "native_verified": verified,
                "cases": qualification_manifest,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    sections = []
    for heading, items in CHEATSHEET:
        boxes = []
        for title, description, snippet, linked in items:
            ref = (f'<p class="tip"><a href="../examples/{linked}/">View working example →</a></p>'
                   if linked in EXAMPLES else "")
            boxes.append(f"""<article class="reference"><h3><code>{escape(title)}</code></h3>
<p>{escape(description)}</p><pre><code>{escape(snippet)}</code></pre>{ref}</article>""")
        sections.append(f'<section><h2>{escape(heading)}</h2><div class="reference-grid">{"".join(boxes)}</div></section>')
    cheat = f"""<main class="wrap"><div class="crumb"><a href="../">← Library</a> / Cheatsheet</div>
<section class="hero small"><p class="eyebrow">SCPF reference</p><h1>Cheatsheet</h1><p>SolidCraft version: <strong>{TESTED_SOLIDCRAFT_VERSION} tested</strong>; older versions are refused and newer versions trigger a compatibility warning.</p>
<p>Common SCPF syntax alongside tiny examples that CI compiles. For explanations, examples and limitations, read the
<a href="../guide/">full API Guide</a>.</p></section>
<div class="notice"><strong>What is verified?</strong> The linked examples and API unit tests run in GitHub Actions.
Cheatsheet fragments describe API calls; a fragment alone is not a complete runnable model.</div>
{"".join(sections)}</main>"""
    (out / "cheatsheet").mkdir(exist_ok=True)
    (out / "cheatsheet" / "index.html").write_text(
        page("Cheatsheet", cheat, stylesheet="../style.css", home="../", cheatsheet="./"),
        encoding="utf-8")

    home = f"""<main class="wrap"><section class="hero"><p class="eyebrow">lib.py.solidcraft.forge / Python Forge</p>
<h1>SCPF examples & API cheatsheet</h1><p class="meta">Tested SolidCraft version: {TESTED_SOLIDCRAFT_VERSION} · older releases rejected, newer releases warned</p><p>Small, readable Python examples to verify the SCPF command compiler.
This is <strong>not</strong> the SolidCraft CAD model gallery.</p>
<div class="actions"><a class="button primary" href="guide/">Read the API Guide →</a>\n<a class="button" href="qualification/">Qualification →</a>\n<a class="button" href="cheatsheet/">Quick cheatsheet →</a>\n<a class="button" href="{CAD_SITE}">See real CAD models →</a></div></section>
<section class="section-heading"><h2>Small public examples</h2><p>Each source produces its own native-command JSON.
Source and commands are regenerated together by CI.</p></section>
<div class="cards">{"".join(cards)}</div>
<div class="twocol"><section class="panel"><h2>Developing the library</h2>
<pre><code>python -m pip install -e ./scpf
python -m unittest discover -s scpf/tests -v
python -m scpf examples/simple-box/scpf/model.py --out output/box.json</code></pre>
<p>API and command tests stay here; mechanical assembly and render qualification live in the CAD project.</p></section>
<section class="panel"><h2>Continue with the real CAD project</h2><p>Corner Bracket, HUB75, enclosures and native
STEP/SC/PNG renders are maintained independently in <strong>2026-011-02.cad.solidcraft</strong>,
using the library as a pinned external dependency.</p><p><a href="{CAD_SITE}">Open the CAD project website →</a></p></section></div>
<p class="source-stamp">Library source commit: <code>{escape(sha)}</code></p></main>"""
    (out / "index.html").write_text(
        page("Examples & cheatsheet", home, stylesheet="style.css", home="./", cheatsheet="cheatsheet/"),
        encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "site")
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--native", type=Path, help="Source-matched native screenshot directory")
    options = parser.parse_args()
    build(options.out, options.source_sha, native_root=options.native)
    print(f"Built independent SCPF library site: {options.out}")
