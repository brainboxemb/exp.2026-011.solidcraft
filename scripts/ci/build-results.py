#!/usr/bin/env python3
"""Build a self-contained static CAD-results website (no third-party deps).

Content is generated from the current SCPF source and command JSON.
A rendered CAD screenshot is published only if native verification metadata
proves it belongs to exactly this source commit.
"""
import argparse
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODELS = {
    "plate": {
        "title": "Plate", "tagline": "A rounded plate with four holes",
        "description": "A feature-based plate: sketch, extrusion, four vertical fillets and a through-hole sketch.",
        "parameters": "100 × 60 × 10 mm; four Ø8 mm holes",
        "diagram": "plate",
        "stages": ["Sketch the rectangle", "Extrude the base", "Fillet vertical corners",
                   "Sketch four hole centres", "Cut the holes"],
    },
    "csg-cube": {
        "title": "CsgCube", "tagline": "A cube, sphere and three crossing bores",
        "description": "A constructive solid geometry demonstration: intersect a cube with a sphere, then subtract cylinders along three axes.",
        "parameters": "50 mm cube; three crossing cylindrical cuts",
        "diagram": "csg",
        "stages": ["Create the sphere", "Intersect with a cube",
                   "Cut along X, Y and Z"],
    },
    "sample-plate": {
        "title": "SamplePlate",
        "tagline": "Rounded plate with two holes, boss and through-bore",
        "description": "Reverse engineered from a saved SolidCraft design: rectangle, positive extrusion, four R6 vertical fillets, two Ø8 mounting holes, an offset Ø24 boss and a central Ø12 bore.",
        "parameters": "80 × 50 × 8 mm; R6; Ø24 × 14 boss",
        "diagram": "sample",
        "stages": ["Sketch XY rectangle (80 × 50)", "Extrude base by 8 mm",
                   "Fillet four vertical corners, R6",
                   "Cut two mounting holes Ø8",
                   "Join Ø24 boss above plate, height 14",
                   "Cut central Ø12 bore through full 22 mm"],
    },
    "bracket": {
        "title": "Bracket", "tagline": "An L-shaped extrusion with two mounting holes",
        "description": "An XZ polygon extruded along Y, with an edge fillet and an XY sketch for the two mounting holes.",
        "parameters": "60 mm wide; 6 mm wall; two Ø8 mm holes",
        "diagram": "bracket",
        "stages": ["Draw the L profile", "Extrude its width",
                   "Round an exposed edge", "Sketch mounting holes", "Cut through the flange"],
    },
}

# Purely schematic line art; never mistaken for a native SolidCraft render.
DIAGRAMS = {
    "sample": """<path d="M65 115 300 50 425 100 185 175Z" fill="#bcd4ee" stroke="#285785" stroke-width="5"/><path d="M65 115 V160 L185 222 V175 M185 222 425 150 V100" fill="#8eb5db" stroke="#285785" stroke-width="4"/><ellipse cx="293" cy="100" rx="62" ry="39" fill="#5f92c6" stroke="#285785" stroke-width="4"/><path d="M231 100 V60 A62 39 0 0 1 355 60 V100" fill="#b4d0e9" stroke="#285785" stroke-width="4"/><ellipse cx="293" cy="60" rx="62" ry="39" fill="#d1e4f4" stroke="#285785" stroke-width="4"/><ellipse cx="293" cy="60" rx="29" ry="18" fill="#edf4fb" stroke="#285785" stroke-width="4"/><ellipse cx="130" cy="116" rx="15" ry="10" fill="#edf4fb" stroke="#285785" stroke-width="4"/><ellipse cx="385" cy="129" rx="15" ry="10" fill="#edf4fb" stroke="#285785" stroke-width="4"/>""",
    "plate": """<rect x="95" y="25" width="310" height="165" rx="16" fill="#d6e4f5" stroke="#285785" stroke-width="5"/><path d="M95 175 145 218 H420 V65 L405 25" fill="#99bad9" stroke="#285785" stroke-width="4"/><ellipse cx="155" cy="78" rx="12" ry="10" fill="#fff" stroke="#285785" stroke-width="4"/><ellipse cx="345" cy="78" rx="12" ry="10" fill="#fff" stroke="#285785" stroke-width="4"/><ellipse cx="155" cy="151" rx="12" ry="10" fill="#fff" stroke="#285785" stroke-width="4"/><ellipse cx="345" cy="151" rx="12" ry="10" fill="#fff" stroke="#285785" stroke-width="4"/>""",
    "csg": """<path d="M130 68 250 15 376 68 376 188 250 241 130 188Z" fill="#d6e4f5" stroke="#285785" stroke-width="5"/><path d="M130 68 250 125 376 68 M250 125 V241" fill="none" stroke="#285785" stroke-width="4"/><ellipse cx="250" cy="129" rx="39" ry="37" fill="#f1f6fc" stroke="#285785" stroke-width="5"/><ellipse cx="250" cy="130" rx="14" ry="34" fill="#acc6e3" stroke="#285785" stroke-width="3"/><path d="M196 90 307 162 M185 155 310 100" stroke="#285785" stroke-width="4" stroke-dasharray="8 8"/>""",
    "bracket": """<path d="M104 195 104 34 145 34 145 163 388 163 388 207 104 207Z" fill="#b4cde9" stroke="#285785" stroke-width="5"/><path d="M145 163 174 188 407 188 388 163 M388 207 407 188" fill="none" stroke="#285785" stroke-width="4"/><ellipse cx="230" cy="187" rx="14" ry="8" fill="#f4f7fc" stroke="#285785" stroke-width="4"/><ellipse cx="330" cy="187" rx="14" ry="8" fill="#f4f7fc" stroke="#285785" stroke-width="4"/>""",
}


def esc(value):
    return html.escape(str(value), quote=True)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def screenshot_info(native_root, commit, model):
    if native_root is None:
        return None
    manifest = native_root / "verification.json"
    if not manifest.is_file():
        return None
    metadata = read_json(manifest)
    if metadata.get("source_commit") != commit or metadata.get("verified") is not True:
        return None
    rel = {"plate": "plate.png", "csg-cube": "csg-cube/model.png", "bracket": "bracket/model.png", "sample-plate": "sample-plate/model.png"}.get(model)
    if not rel:
        return None
    candidate = native_root / rel
    return candidate if candidate.is_file() and candidate.stat().st_size else None


def diagram(model):
    return f'<svg role="img" aria-label="Schematic illustration; not a native CAD render" viewBox="0 0 500 260" xmlns="http://www.w3.org/2000/svg">{DIAGRAMS[MODELS[model]["diagram"]]}</svg>'


def layout(title, body, css_path, home_path):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · SolidCraft CAD experiments</title><link rel="stylesheet" href="{esc(css_path)}"></head>
<body><header class="top"><div class="wrap"><nav><a class="brand" href="{esc(home_path)}">SolidCraft · CAD experiments</a>
<a href="{esc(home_path)}">Models</a><a href="{esc(home_path)}cheatsheet/">SCPF cheatsheet</a><a href="https://github.com/brainboxemb/exp.2026-011.solidcraft">Source on GitHub</a></nav></div></header>
{body}<footer><div class="wrap">SCPF (Python) and SCRF (Rust) produce native SolidCraft command plans. All geometry is built by SolidCraft.</div></footer>
</body></html>"""


def command_stages(commands):
    descriptions = {
        "parameters.add": "Named CAD parameter",
        "sketch.create": "Create sketch",
        "sketch.rectangle.two_point": "Rectangle",
        "sketch.line": "Profile edges",
        "sketch.circle.center": "Circle",
        "sketch.finish": "Finish sketch",
        "solid.extrude": "Extrusion / cut",
        "solid.fillet": "Rounded edge",
        "solid.box": "Box primitive",
        "solid.sphere": "Sphere primitive",
        "solid.cylinder": "Cylinder primitive",
    }
    items = []
    for entry in commands:
        kind = entry["command"]
        description = descriptions.get(kind, kind)
        details = []
        params = entry.get("params", {})
        for key in ("name", "plane", "direction", "operation", "body_name"):
            if key in params:
                details.append(f"{key}: {params[key]}")
        items.append(f'<li><strong>{esc(description)}</strong><small>{esc(kind)}'
                     + (f' · {esc(", ".join(details))}' if details else "")
                     + '</small></li>')
    return "\n".join(items)


def copy_if_exists(source, target):
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def build(out, commit, native_root=None, generated_root=None, previous_site=None):
    out.mkdir(parents=True, exist_ok=True)
    copy_if_exists(ROOT / "site/results.css", out / "results.css")
    cards = []
    verified_count = 0
    for slug, info in MODELS.items():
        work = out / "models" / slug
        work.mkdir(parents=True, exist_ok=True)
        source = ROOT / "examples" / slug / "scpf" / "model.py"
        command_file = ((generated_root / slug / "scpf" / "solidcraft.json")
                        if generated_root is not None else
                        ROOT / "examples" / slug / "scpf" / "solidcraft.json")
        commands = read_json(command_file)["commands"]
        copy_if_exists(source, work / "model.py")
        copy_if_exists(command_file, work / "solidcraft.json")
        if (ROOT / "examples" / slug / "scrf" / "model.rs").exists():
            copy_if_exists(ROOT / "examples" / slug / "scrf" / "model.rs", work / "model.rs")
        screenshot = screenshot_info(native_root, commit, slug)
        has_native = screenshot is not None
        # A lightweight preview may reuse a published render as an illustration,
        # but MUST NOT report that older render as verified for this PR revision.
        previously_verified = None
        if not has_native and previous_site is not None and slug != "sample-plate":
            prior = previous_site / "models" / slug / "native.png"
            if prior.is_file() and prior.stat().st_size:
                previously_verified = prior
        preview_image = screenshot or previously_verified
        if preview_image is not None:
            copy_if_exists(preview_image, work / "native.png")
        if has_native:
            verified_count += 1
        photo = ('<img src="native.png" alt="SolidCraft CAD render">' if preview_image
                 else diagram(slug))
        status = ("Native verified · snapshot from matching run" if has_native
                  else "Previously verified render from main · not verified for this PR"
                  if previously_verified else
                  "Generated command plan · native render not verified for this commit")
        badge = "verified" if has_native else "pending"
        stage_summary = "".join(f"<li>{esc(s)}</li>" for s in info["stages"])
        script = esc(source.read_text(encoding="utf-8"))
        view = f"""<section class="hero"><div class="wrap"><div class="eyebrow">CAD design / {esc(slug)}</div>
<h1>{esc(info["title"])}</h1><p>{esc(info["tagline"])}</p></div></section>
<main class="wrap"><div class="metadata"><span class="badge {badge}">{esc(status)}</span>
<span class="badge">{len(commands)} commands</span><span class="badge">{esc(info["parameters"])}</span></div>
<div class="two"><section class="panel"><h2>Model preview</h2><div class="picture">{photo}</div>
<p class="small muted">{"Native SolidCraft image, matching this source revision." if has_native else "Previously verified SolidCraft render from main; this PR revision is not yet native-verified." if previously_verified else "Schematic drawing only; it is not a SolidCraft geometry render."}</p>
<p>{esc(info["description"])}</p></section>
<section class="panel"><h2>Files</h2><p>Download the source and the generated command plan.</p>
<div class="links"><a class="btn" href="model.py">SCPF source</a><a class="btn secondary" href="solidcraft.json">Command JSON</a>
{'<a class="btn secondary" href="model.rs">SCRF source</a>' if (work / "model.rs").exists() else ''}</div>
<p class="small muted">Command JSON describes CAD actions; it is not an already-saved .sc design.</p>
<h3>Construction stages</h3><ol>{stage_summary}</ol></section></div>
<h2>Python model</h2><pre><code>{script}</code></pre>
<h2>Native SolidCraft command sequence</h2><section class="panel"><ol class="timeline">{command_stages(commands)}</ol></section>
<div class="notice"><strong>Verification:</strong> {esc(status)}.
The source and JSON here are from this checkout. A matching native snapshot appears only after successful SolidCraft verification.
Native qualification is reported only when the matching verified image exists.</div>
<p><a href="../../">← Back to all models</a></p></main>"""
        (work / "index.html").write_text(
            layout(info["title"], view, "../../results.css", "../../"),
            encoding="utf-8",
        )
        cards.append(f"""<article class="card"><div class="picture">{f'<img src="models/{slug}/native.png" alt="SolidCraft model render">' if preview_image else diagram(slug)}</div>
<div class="inside"><span class="badge {badge}">{'Native verified' if has_native else 'Render from main' if previously_verified else 'Command plan available'}</span>
<h3><a href="models/{slug}/">{esc(info["title"])}</a></h3><p>{esc(info["tagline"])}</p>
<p class="small muted">{esc(info["parameters"])}</p>
<a class="btn" href="models/{slug}/">Explore model →</a></div></article>""")
    home = f"""<section class="hero"><div class="wrap"><div class="eyebrow">SCPF · SCRF · SolidCraft</div>
<h1>CAD models, from readable code to native geometry</h1>
<p>Explore four small CAD designs and their construction stages. Python SCPF and Rust SCRF emit native SolidCraft commands; SolidCraft itself creates the final BRep model.</p></div></section>
<main class="wrap"><section class="intro"><h2>Getting started</h2><p>New to SCPF? <a href="cheatsheet/">Open the SCPF cheatsheet</a> for 2D/3D primitives, operations and examples.</p><h2>Model catalog</h2>
<p>Each model has its Python source, generated command JSON and a readable operation timeline. PR previews may show existing main renders for reference, explicitly labelled as not verified for the PR revision.</p>
<p><span class="badge">{len(MODELS)} models</span> <span class="badge verified">{verified_count} matching native screenshots</span></p></section>
<div class="grid">{''.join(cards)}</div><h2>How it works</h2>
<div class="two"><section class="panel"><h3>1 · Write the model</h3><p>Use a Python dataclass and a <code>build()</code> method, without a mandatory <code>show()</code> or explicit <code>return</code>.</p>
<h3>2 · Compile commands</h3><p>SCPF outputs native SolidCraft commands, with named parameters and a sequence of CAD operations.</p></section>
<section class="panel"><h3>3 · Execute in SolidCraft</h3><p>The SolidCraft engine creates editable geometry, and CI validates its results. CAD and verification assets are only published when they match the source revision.</p>
<h3>4 · Inspect the result</h3><p>Review the command timeline, native measurements and optional rendered preview. An unverified model is labelled as such.</p></section></div>
<p class="small muted">Source revision: <code>{esc(commit)}</code></p></main>"""
    (out / "index.html").write_text(
        layout("Models", home, "results.css", "./"), encoding="utf-8"
    )
    make_cheatsheet(out)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(MODELS)} CAD result pages in {out} ({verified_count} native screenshots)")



def make_cheatsheet(out):
    """Quick reference reflects implemented SCPF APIs, not BOSL2's full API."""
    sections = [
        ("2D shapes · sketches", [
            ("Rectangle2D(width, depth)", "XY rectangle whose lower-left corner is at (0, 0).",
             "Rectangle2D(80, 50)"),
            ("Circle2D(d=... or r=...)", "Circle with diameter or radius; use it in a sketch.",
             "Circle2D(d=8).at(12, 25)"),
            ("Polygon2D(points, plane='XY')", "Closed planar polygon; XY, XZ or YZ.",
             "Polygon2D([(0, 0), (40, 0), (0, 30)])"),
        ]),
        ("3D shapes · volumes (no suffix)", [
            ("Box(length, width, height)", "Rectangular 3D box; in SCPF it is centered in X/Y and starts at Z=0.",
             "Box(80, 50, 8)"),
            ("Cylinder(d=..., h=...)", "Direct 3D cylinder, positioned by the center of its bottom face.",
             "Cylinder(d=24, h=14).at(40, 25, 8)"),
            ("Sphere(radius)", "3D sphere centered on the origin.",
             "Sphere(20)"),
            ("Cube(size)", "A special case of Box with three equal sides, centered on the origin. OpenSCAD also uses cube([x, y, z]) for rectangular boxes.",
             "Cube(50)"),
        ]),
        ("Operations", [
            ("shape.at(x, y, z)", "Place a Circle2D, Rectangle2D or Cylinder3D; 2D z offsets the sketch plane.",
             "Circle2D(d=8).at(12, 25)"),
            ("profile.extrude(distance)", "Extrude a planar sketch into a 3D solid.",
             "Rectangle2D(80, 50).extrude(8)"),
            ("profile.extrude(distance, direction='negative')", "Extrude towards negative sketch normal.",
             "Circle2D(d=8).extrude(8, direction='negative')"),
            ("a + b", "Union/join. An extruded circular sketch or direct Cylinder3D can join a rectangular base.",
             "plate + Cylinder(d=24, h=14).at(40, 25, 8)"),
            ("a - b", "Difference/cut. Keep the original left-hand solid.",
             "plate - Cylinder(d=12, h=22).at(40, 25, 0)"),
            ("a & b", "Intersection for supported CSG primitives.",
             "Sphere(30) & Cube(50)"),
            ("solid.fillet(radius, edges='vertical')", "Round four vertical edges of an extruded rectangular base.",
             "plate.fillet(6, edges='vertical')"),
        ]),
        ("Run and inspect", [
            ("python -m scpf model.py --out out.json", "Compile commands without starting SolidCraft.",
             "python -m scpf examples/sample-plate/scpf/model.py --out output/sample.json"),
            ("python -m scpf model.py --connect", "Apply commands to an already open, empty SolidCraft GUI document.",
             "python -m scpf examples/sample-plate/scpf/model.py --connect"),
            ("python -m scpf replay file.json", "Execute an existing command JSON unchanged in SolidCraft.",
             "python -m scpf replay examples/bracket/scpf/solidcraft.json"),
        ]),
    ]
    blocks = []
    for heading, entries in sections:
        cards = "".join(
            '<article class="panel"><h3><code>' + esc(api) + '</code></h3>'
            '<p>' + esc(description) + '</p><pre><code>' + esc(example) +
            '</code></pre></article>'
            for api, description, example in entries
        )
        blocks.append('<section><h2>' + esc(heading) +
                      '</h2><div class="cheatsheet-grid">' + cards +
                      '</div></section>')
    body = (
        '<section class="hero"><div class="wrap"><div class="eyebrow">SCPF / API reference</div>'
        '<h1>SCPF cheatsheet</h1><p>2D sketches, 3D volumes and native SolidCraft operations.</p></div></section>'
        '<main class="wrap"><div class="notice">Only a subset of the generic API is implemented.'
        ' Older names <code>Rectangle</code>, <code>Circle</code>, <code>Polygon</code>,'
        ' <code>Box3D</code>, <code>Cylinder3D</code> and <code>Sphere3D</code> are temporary aliases.'
        ' Legacy <code>Cylinder(height, diameter)</code> is centered vertically;'
        ' new <code>Cylinder(d=..., h=...)</code> starts at its base. Examples describe the API,'
        ' not guarantees that every combination of operations is supported.</div>'
        + "".join(blocks) +
        '<section><h2>Next iteration · not implemented</h2><p>Generic object-relative anchors,'
        ' face/edge references and fully associative SolidCraft constraints are tracked in'
        ' <a href="https://github.com/brainboxemb/exp.2026-011.solidcraft/issues/5">issue #5</a>.'
        ' The current coordinate-based examples are not equivalent to fully constrained features.</p></section>'
        '<p><a href="../">← Back to model catalog</a></p></main>'
    )
    dest = out / "cheatsheet"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(
        layout("SCPF cheatsheet", body, "../results.css", "../"), encoding="utf-8"
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--previous-site", type=Path,
                        help="Published main site renders for non-verified previews")
    parser.add_argument("--generated", type=Path,
                        help="Root of freshly compiled output/examples")
    args = parser.parse_args()
    build(args.out, args.commit, args.native, args.generated, args.previous_site)


if __name__ == "__main__":
    main()
