#!/usr/bin/env python3
"""Build a read-only GitHub Pages gallery from native SolidCraft CI evidence.

All files are copied from a verified workflow run; never upload source models
or preview images to the git source branch. The gallery is a generated output.
"""
import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "output" / "site"
NATIVE = ROOT / "output" / "native"

CASES = (
    ("plate", "Plate", NATIVE / "plate.png", NATIVE / "plate-measurements.json",
     ROOT / "examples/plate/solidcraftforge/model.rs",
     ROOT / "examples/plate/solidcraftforge/solidcraft.json"),
    ("csg-cube", "CSG Cube", NATIVE / "csg-cube/model.png",
     NATIVE / "csg-cube/measurements.json",
     ROOT / "examples/csg-cube/solidcraftforge/model.rs",
     ROOT / "examples/csg-cube/solidcraftforge/solidcraft.json"),
)

def copy_as(source: Path, target: Path) -> bool:
    if not source.is_file():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return True

def esc(value) -> str:
    return html.escape(str(value), quote=True)

def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    cards = []
    for slug, title, image, measurements, model, commands in CASES:
        base = SITE / slug
        base.mkdir(parents=True, exist_ok=True)
        has_preview = copy_as(image, base / "preview.png")
        has_metrics = copy_as(measurements, base / "measurements.json")
        copy_as(model, base / "model.rs")
        copy_as(commands, base / "solidcraft.json")
        if has_metrics:
            data = json.loads(measurements.read_text(encoding="utf-8"))
            total = data.get("total", {})
            volume = total.get("volume_mm3")
            bodies = data.get("bodies", [])
            bbox = bodies[0].get("bbox", {}) if bodies else {}
            detail = (
                f"<p>Volume: <strong>{esc(round(volume, 2))} mm³</strong></p>"
                if isinstance(volume, (int, float)) else ""
            )
            detail += f"<pre>{esc(json.dumps(bbox, indent=2))}</pre>" if bbox else ""
        else:
            detail = "<p>Native measurements unavailable.</p>"
        preview = (
            f'<img src="{slug}/preview.png" alt="{esc(title)} preview" loading="lazy">'
            if has_preview else '<div class="placeholder">Snapshot unavailable</div>'
        )
        cards.append(
            f'<article><h2>{esc(title)}</h2>{preview}{detail}'
            f'<nav><a href="{slug}/model.rs">Rust model</a>'
            f'<a href="{slug}/solidcraft.json">SolidCraft commands</a>'
            + (f'<a href="{slug}/measurements.json">Measurements</a>' if has_metrics else "")
            + '</nav></article>'
        )

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SolidCraftForge — CI model previews</title>
<style>
:root{color-scheme:dark}body{font:16px system-ui,sans-serif;margin:0;background:#101720;color:#e9eef4}
header,main,footer{max-width:1080px;margin:auto;padding:24px}
header{border-bottom:1px solid #354454}h1{margin-bottom:4px}
p{line-height:1.5;color:#b9c7d4}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
article{background:#1b2633;border:1px solid #354454;border-radius:12px;padding:18px;min-width:0}
img{width:100%;aspect-ratio:4/3;object-fit:contain;background:#0c121a;border-radius:6px}
.placeholder{height:220px;display:grid;place-items:center;background:#0c121a;color:#b9c7d4}
nav{display:flex;flex-wrap:wrap;gap:12px}a{color:#9bd5ff}pre{overflow:auto;font-size:12px}
footer{font-size:13px;color:#b9c7d4}
</style></head><body>
<header><h1>SolidCraftForge</h1>
<p>Generated from native SolidCraft CI runs · read-only model comparison</p></header>
<main>__CARDS__</main>
<footer>Preview images are optional. For full STEP / native .sc files, download the
GitHub Actions runtime evidence artifact. This page is overwritten by each successful publish.</footer>
</body></html>"""
    (SITE / "index.html").write_text(page.replace("__CARDS__", "\n".join(cards)), encoding="utf-8")
    (SITE / ".nojekyll").touch()
    print(f"Built {SITE}")

if __name__ == "__main__":
    main()
