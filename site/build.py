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

from scpf.runner import run_script
from scpf.version import TESTED_SOLIDCRAFT_VERSION
from guides import GUIDES

ROOT = Path(__file__).resolve().parents[1]
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
        "description": "Two instances of one Block definition, joined by a rigid attachment.",
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


def page(title, body, *, stylesheet, home, cheatsheet):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{escape(title)} · SCPF Python library</title>
<link rel="stylesheet" href="{escape(stylesheet)}"></head>
<body><header class="top"><div class="wrap nav">
<a class="brand" href="{escape(home)}">SCPF <span>Python library</span></a>
<nav aria-label="Main"><a href="{escape(home)}">Examples</a><a href="{escape(home)}guide/">API Guide</a><a href="{escape(cheatsheet)}">Cheatsheet</a>
<a href="{LIBRARY_URL}">Source</a></nav></div></header>
{body}
<footer><div class="wrap"><strong>SCPF</strong> generates commands; native SolidCraft creates the geometry.
<a href="{CAD_SITE}">Full SolidCraft CAD projects →</a></div></footer>
</body></html>"""


def text(path):
    return path.read_text(encoding="utf-8")


def build(out, sha, native_root=None):
    """Compile the public examples and attach verified native screenshots if available.

    A .png is accepted only when the native verification file identifies the
    exact source SHA and the expected SolidCraft runtime. Outside native CI,
    emit plainly labelled SVG schematics rather than pretending a render.
    """
    verified = False
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
<div class="actions"><a class="button primary" href="guide/">Read the API Guide →</a>\n<a class="button" href="cheatsheet/">Quick cheatsheet →</a>
<a class="button" href="{CAD_SITE}">See real CAD models →</a></div></section>
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
