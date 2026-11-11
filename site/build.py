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

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_URL = "https://github.com/brainboxemb/lib.py.solidcraft"
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
        ("pattern(...).attach(...)", "Pattern holes relative to the parent; no manual world-space coordinate table.",
         "Hole(d=8, depth=Depth.THROUGH_ALL).pattern(count=2, spacing=40, axis=Axis.Y).attach(plate, parent=Anchor.TOP)", "anchored-holes"),
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
        ("model.attach(...)", "Create a rigid native attachment between component occurrences.",
         "right = Block().attach(left, parent=Anchor.RIGHT, child=Anchor.LEFT)", "components"),
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
<nav aria-label="Main"><a href="{escape(home)}">Examples</a><a href="{escape(cheatsheet)}">Cheatsheet</a>
<a href="{LIBRARY_URL}">Source</a></nav></div></header>
{body}
<footer><div class="wrap"><strong>SCPF</strong> generates commands; native SolidCraft creates the geometry.
<a href="{CAD_SITE}">Full SolidCraft CAD projects →</a></div></footer>
</body></html>"""


def text(path):
    return path.read_text(encoding="utf-8")


def build(out, sha):
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
        manifest["examples"][slug] = {"source": f"examples/{slug}/model.py",
                                      "commands": f"examples/{slug}/commands.json",
                                      "command_count": count}
        kinds = [row["command"] for row in commands["commands"]]
        timeline = "".join(f"<li><code>{escape(kind)}</code></li>" for kind in kinds)
        source_url = f"{LIBRARY_URL}/blob/main/examples/{slug}/scpf/model.py"
        body = f"""<main class="wrap"><div class="crumb"><a href="../../">← Examples</a> / {escape(info['title'])}</div>
<section class="hero small"><p class="eyebrow">Small API regression fixture</p>
<h1>{escape(info['title'])}</h1><p>{escape(info['description'])}</p>
<p class="meta"><span>Compiled: {count} native commands</span><span>Not a native BRep render</span></p></section>
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
        cards.append(f"""<article class="card"><p class="eyebrow">Regression example</p>
<h2><a href="examples/{slug}/">{escape(info['title'])}</a></h2>
<p>{escape(info['description'])}</p><div class="tags">{tags}</div>
<p class="meta">{count} generated SolidCraft commands</p>
<a class="button" href="examples/{slug}/">View source and command steps →</a></article>""")

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
<section class="hero small"><p class="eyebrow">SCPF reference</p><h1>Cheatsheet</h1>
<p>Common SCPF syntax alongside tiny examples that CI compiles. Advanced features belong in
<a href="{LIBRARY_URL}/blob/main/scpf/README.md">the API guide</a>.</p></section>
<div class="notice"><strong>What is verified?</strong> The linked examples and API unit tests run in GitHub Actions.
Cheatsheet fragments describe API calls; a fragment alone is not a complete runnable model.</div>
{"".join(sections)}</main>"""
    (out / "cheatsheet").mkdir(exist_ok=True)
    (out / "cheatsheet" / "index.html").write_text(
        page("Cheatsheet", cheat, stylesheet="../style.css", home="../", cheatsheet="./"),
        encoding="utf-8")

    home = f"""<main class="wrap"><section class="hero"><p class="eyebrow">lib.py.solidcraft / reusable Python interface</p>
<h1>SCPF examples & API cheatsheet</h1><p>Small, readable Python examples to verify the SCPF command compiler.
This is <strong>not</strong> the SolidCraft CAD model gallery.</p>
<div class="actions"><a class="button primary" href="cheatsheet/">Open cheatsheet →</a>
<a class="button" href="{CAD_SITE}">See real CAD models →</a></div></section>
<section class="section-heading"><h2>Three small examples</h2><p>Each source produces its own native-command JSON.
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
    options = parser.parse_args()
    build(options.out, options.source_sha)
    print(f"Built independent SCPF library site: {options.out}")
