#!/usr/bin/env python3
"""Visual regression checks for fixed-camera native qualification renders."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
BASELINES = ROOT / "qualification" / "visual_baselines.json"
VIEWS = ("front", "right", "iso")
REFERENCE_SIZE = (96, 72)
DEFAULT_MEAN_ABS_THRESHOLD = 6.0
DEFAULT_CHANGED_PIXEL_FRACTION = 0.08


def normalized_gray(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image = image.resize(REFERENCE_SIZE, Image.Resampling.LANCZOS)
    return image.convert("L")


def encode_reference(image: Image.Image) -> str:
    return base64.b64encode(image.tobytes()).decode("ascii")


def decode_reference(text: str) -> Image.Image:
    raw = base64.b64decode(text)
    expected = REFERENCE_SIZE[0] * REFERENCE_SIZE[1]
    if len(raw) != expected:
        raise ValueError(f"invalid visual baseline byte count: {len(raw)} != {expected}")
    return Image.frombytes("L", REFERENCE_SIZE, raw)


def metrics(current: Image.Image, reference: Image.Image) -> dict:
    diff = ImageChops.difference(current, reference)
    pixels = list(diff.getdata())
    mean_abs = sum(pixels) / len(pixels)
    changed = sum(1 for value in pixels if value >= 12) / len(pixels)
    return {
        "mean_abs": round(mean_abs, 4),
        "changed_pixel_fraction": round(changed, 6),
    }


def overlay(current: Image.Image, reference: Image.Image, out: Path) -> None:
    # Green = current luminance, magenta = reference luminance.
    zero = Image.new("L", REFERENCE_SIZE, 0)
    rgb = Image.merge("RGB", (reference, current, reference))
    rgb = rgb.resize((REFERENCE_SIZE[0] * 6, REFERENCE_SIZE[1] * 6), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(rgb)
    draw.rectangle((0, 0, rgb.width - 1, rgb.height - 1), outline=(255, 255, 255), width=2)
    rgb.save(out)


def load_baselines() -> dict:
    if not BASELINES.is_file():
        return {"schema_version": 1, "cases": {}}
    return json.loads(BASELINES.read_text(encoding="utf-8"))


def validate_case(case_dir: Path, slug: str, baseline: dict | None) -> dict:
    views = {}
    missing = []
    review = False
    failed = False

    for view in VIEWS:
        path = case_dir / f"model-{view}.png"
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(path.name)
            continue

        current = normalized_gray(path)
        reference_data = (baseline or {}).get("views", {}).get(view)
        if not reference_data:
            views[view] = {
                "status": "review",
                "image": path.name,
                "reason": "no approved visual baseline",
            }
            review = True
            continue

        reference = decode_reference(reference_data["pixels"])
        result = metrics(current, reference)
        mean_limit = float(reference_data.get("mean_abs_threshold", DEFAULT_MEAN_ABS_THRESHOLD))
        changed_limit = float(reference_data.get(
            "changed_pixel_fraction_threshold",
            DEFAULT_CHANGED_PIXEL_FRACTION,
        ))
        passed = (
            result["mean_abs"] <= mean_limit
            and result["changed_pixel_fraction"] <= changed_limit
        )
        diff_name = f"visual-diff-{view}.png"
        overlay(current, reference, case_dir / diff_name)
        views[view] = {
            "status": "pass" if passed else "fail",
            "image": path.name,
            "diff": diff_name,
            "metrics": result,
            "limits": {
                "mean_abs": mean_limit,
                "changed_pixel_fraction": changed_limit,
            },
        }
        failed = failed or not passed

    if missing:
        status = "missing"
    elif failed:
        status = "fail"
    elif review:
        status = "review"
    else:
        status = "pass"

    return {
        "case": slug,
        "status": status,
        "views": views,
        "missing": missing,
    }


def baseline_entry(case_dir: Path, slug: str) -> dict:
    views = {}
    for view in VIEWS:
        path = case_dir / f"model-{view}.png"
        image = normalized_gray(path)
        views[view] = {
            "pixels": encode_reference(image),
            "mean_abs_threshold": DEFAULT_MEAN_ABS_THRESHOLD,
            "changed_pixel_fraction_threshold": DEFAULT_CHANGED_PIXEL_FRACTION,
        }
    return {"case": slug, "views": views}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--qualification-dir", type=Path, required=True)
    parser.add_argument("--baseline-case", help="print a baseline JSON entry for one approved case")
    args = parser.parse_args()

    if args.baseline_case:
        print(json.dumps(
            baseline_entry(args.native_root / args.baseline_case, args.baseline_case),
            indent=2,
        ))
        return 0

    baselines = load_baselines().get("cases", {})
    rows = ["case\tstatus\n"]
    summary = {}

    for case_dir in sorted(path for path in args.native_root.iterdir() if path.is_dir()):
        slug = case_dir.name
        result = validate_case(case_dir, slug, baselines.get(slug))
        summary[slug] = result
        (case_dir / "visual-validation.json").write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )
        rows.append(f"{slug}\t{result['status'].upper()}\n")

    args.qualification_dir.mkdir(parents=True, exist_ok=True)
    (args.qualification_dir / "visual-validation.tsv").write_text(
        "".join(rows), encoding="utf-8"
    )
    (args.qualification_dir / "visual-validation.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    counts = {}
    for result in summary.values():
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    print("Visual qualification: " + ", ".join(
        f"{key}={value}" for key, value in sorted(counts.items())
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
