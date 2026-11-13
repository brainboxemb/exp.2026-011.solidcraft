#!/usr/bin/env python3
"""Validate native SolidCraft qualification evidence against Forge semantics.

The validator intentionally reads only generated native evidence. It does not
reuse Forge's placement implementation to calculate expected positions; doing
so would let the code under test validate itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qualification.expectations import EXPECTED_BOUNDS, EXPECTED_MUTATION_BOUNDS


TOL = 1e-3


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(float(a) - float(b)) <= tol


def vector_close(actual, expected, tol: float = TOL) -> bool:
    return len(actual) == len(expected) and all(close(a, b, tol) for a, b in zip(actual, expected))


def bbox(body: dict) -> tuple[list[float], list[float]]:
    return body["bbox"]["min"], body["bbox"]["max"]


def bbox_close(body: dict, expected_min, expected_max, tol: float = TOL) -> bool:
    actual_min, actual_max = bbox(body)
    return vector_close(actual_min, expected_min, tol) and vector_close(actual_max, expected_max, tol)


def widths(data: dict) -> list[float]:
    return sorted(round(body["bbox"]["max"][0] - body["bbox"]["min"][0], 6) for body in data["bodies"])


def _bounds_match(data: dict, expected: list[dict], tol: float = TOL) -> bool:
    actual = [
        (body["bbox"]["min"], body["bbox"]["max"])
        for body in data.get("bodies", [])
        if body.get("bbox")
    ]
    if len(actual) != len(expected):
        return False

    unmatched = list(actual)
    for target in expected:
        hit = next(
            (
                index for index, (lo, hi) in enumerate(unmatched)
                if vector_close(lo, target["min"], tol)
                and vector_close(hi, target["max"], tol)
            ),
            None,
        )
        if hit is None:
            return False
        unmatched.pop(hit)
    return not unmatched


def _check_declared_bounds(
    validation,
    data: dict,
    case: str,
    *,
    level: str = "q4",
    mutation: bool = False,
    tol: float = TOL,
):
    source = EXPECTED_MUTATION_BOUNDS if mutation else EXPECTED_BOUNDS
    expected = source.get(case)
    if expected is None:
        return
    validation.check(
        "declared target geometry" if not mutation else "declared mutation target geometry",
        _bounds_match(data, expected, tol),
        expected,
        [
            {"min": body["bbox"]["min"], "max": body["bbox"]["max"]}
            for body in data.get("bodies", [])
            if body.get("bbox")
        ],
        level,
    )


def params(data: dict) -> dict[str, float]:
    return {row["name"]: float(row["value"]) for row in data.get("params", [])}


def bodies_named(data: dict, prefix: str) -> list[dict]:
    return [body for body in data["bodies"] if body["name"].startswith(prefix)]


def one_body(data: dict, prefix: str) -> dict:
    rows = bodies_named(data, prefix)
    if len(rows) != 1:
        raise AssertionError(f"expected one body starting with {prefix!r}, found {len(rows)}")
    return rows[0]


class Validation:
    def __init__(self, case: str):
        self.case = case
        self.checks: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, expected=None, actual=None, level: str = "q4"):
        self.checks.append({
            "name": name,
            "level": level,
            "status": "pass" if condition else "fail",
            "expected": expected,
            "actual": actual,
        })

    def status(self, level: str) -> str:
        rows = [row for row in self.checks if row["level"] == level]
        if not rows:
            return "not-required" if level == "q5" else "review"
        return "pass" if all(row["status"] == "pass" for row in rows) else "fail"

    def result(self) -> dict:
        return {
            "case": self.case,
            "q4": self.status("q4"),
            "q5": self.status("q5"),
            "checks": self.checks,
        }


def validate_simple_box(root: Path) -> Validation:
    v = Validation("simple-box")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "simple-box")
    v.check("one body", d["body_count"] == 1, 1, d["body_count"])
    b = d["bodies"][0]
    v.check("40x30x10 bounds", bbox_close(b, [-20, -15, 0], [20, 15, 10]),
            {"min": [-20, -15, 0], "max": [20, 15, 10]}, b["bbox"])
    v.check("parameters", params(d) == {"length": 40.0, "width": 30.0, "height": 10.0},
            {"length": 40.0, "width": 30.0, "height": 10.0}, params(d))
    return v


def validate_anchored_holes(root: Path) -> Validation:
    v = Validation("anchored-holes")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "anchored-holes")
    v.check("one plate body", d["body_count"] == 1, 1, d["body_count"])
    b = d["bodies"][0]
    v.check("plate outer bounds", bbox_close(b, [0, 0, 0], [100, 60, 10]),
            {"min": [0, 0, 0], "max": [100, 60, 10]}, b["bbox"])
    cylinders = b.get("face_types", {}).get("cylinder", 0)
    v.check("two cylindrical hole walls", cylinders == 2, 2, cylinders)
    expected_volume = 100 * 60 * 10 - 2 * 3.141592653589793 * 4 * 4 * 10
    v.check("two through holes remove expected volume", close(b["volume_mm3"], expected_volume, 0.5),
            expected_volume, b["volume_mm3"])
    return v


def validate_parameter_scope(root: Path) -> Validation:
    v = Validation("parameter-scope")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "parameter-scope")
    v.check("baseline widths", widths(d) == [40.0, 40.0, 60.0, 80.0, 80.0],
            [40, 40, 60, 80, 80], widths(d))
    v.check("baseline parameters", params(d) == {
        "Panel_width": 40.0, "Panel_2_width": 60.0, "shared_width": 80.0
    }, {"Panel_width": 40.0, "Panel_2_width": 60.0, "shared_width": 80.0}, params(d))

    m = load(root / "measurements-shared-width-100.json")
    _check_declared_bounds(v, m, "parameter-scope", level="q5", mutation=True)
    v.check("mutated shared width", params(m).get("shared_width") == 100.0, 100.0,
            params(m).get("shared_width"), "q5")
    v.check("dependent widths rebuild", widths(m) == [40.0, 50.0, 60.0, 100.0, 100.0],
            [40, 50, 60, 100, 100], widths(m), "q5")
    return v


def validate_components(root: Path) -> Validation:
    v = Validation("components")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "components")
    rows = bodies_named(d, "Block")
    v.check("two block occurrences", len(rows) == 2, 2, len(rows))
    actual = sorted((body["bbox"]["min"], body["bbox"]["max"]) for body in rows)
    expected = sorted([
        ([-20, -15, 0], [20, 15, 10]),
        ([20, -15, 0], [60, 15, 10]),
    ])
    v.check("RIGHT-to-LEFT faces touch", actual == expected, expected, actual)
    return v


def validate_parametric_attach(root: Path) -> Validation:
    v = Validation("parametric-attach")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "parametric-attach")
    base = one_body(d, "Base")
    block = one_body(d, "Block")
    v.check("base bounds", bbox_close(base, [-20, -15, 0], [20, 15, 10]))
    v.check("10 mm gap", bbox_close(block, [30, -10, 0], [50, 10, 10]),
            {"min": [30, -10, 0], "max": [50, 10, 10]}, block["bbox"])

    m = load(root / "measurements-gap-30.json")
    _check_declared_bounds(v, m, "parametric-attach", level="q5", mutation=True)
    block2 = one_body(m, "Block")
    v.check("30 mm gap mutation", bbox_close(block2, [50, -10, 0], [70, 10, 10]),
            {"min": [50, -10, 0], "max": [70, 10, 10]}, block2["bbox"], "q5")
    return v


def validate_parametric_offset(root: Path) -> Validation:
    v = Validation("parametric-offset")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "parametric-offset")
    marker = one_body(d, "Marker")
    # FRONT_TOP_RIGHT of the parent meets BACK_TOP_RIGHT of the child.
    # The child top therefore ends at parent z=20. The planar v=-5 offset
    # follows +Z in this parent corner frame, moving it upward by 5 mm.
    v.check("top-right anchor + 5 mm local offset",
            bbox_close(marker, [10, -25, 15], [20, -15, 25]),
            {"min": [10, -25, 15], "max": [20, -15, 25]}, marker["bbox"])

    m = load(root / "measurements-shift-10.json")
    _check_declared_bounds(v, m, "parametric-offset", level="q5", mutation=True)
    marker2 = one_body(m, "Marker")
    v.check("10 mm local offset mutation",
            bbox_close(marker2, [10, -25, 20], [20, -15, 30]),
            {"min": [10, -25, 20], "max": [20, -15, 30]}, marker2["bbox"], "q5")
    return v


def validate_parametric_anchor(root: Path) -> Validation:
    v = Validation("parametric-anchor")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "parametric-anchor")
    v.check("RIGHT-to-LEFT baseline",
            bbox_close(one_body(d, "Block"), [20, -10, 0], [40, 10, 10]))
    m = load(root / "measurements-width-80.json")
    _check_declared_bounds(v, m, "parametric-anchor", level="q5", mutation=True)
    v.check("RIGHT anchor follows width mutation",
            bbox_close(one_body(m, "Block"), [40, -10, 0], [60, 10, 10]),
            {"min": [40, -10, 0], "max": [60, 10, 10]},
            one_body(m, "Block")["bbox"], "q5")
    return v


def validate_corner_anchor(root: Path) -> Validation:
    v = Validation("corner-anchor")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "corner-anchor")
    marker = one_body(d, "Marker")
    # BACK_TOP_RIGHT is the child's top/back/right corner. Aligning it with
    # parent FRONT_TOP_RIGHT means the child's top ends at z=20.
    v.check("BACK_TOP_RIGHT meets parent FRONT_TOP_RIGHT",
            bbox_close(marker, [10, -25, 10], [20, -15, 20]),
            {"min": [10, -25, 10], "max": [20, -15, 20]}, marker["bbox"])

    m = load(root / "measurements-size-80x40.json")
    _check_declared_bounds(v, m, "corner-anchor", level="q5", mutation=True)
    marker2 = one_body(m, "Marker")
    v.check("corner follows 80x40 mutation",
            bbox_close(marker2, [30, -25, 30], [40, -15, 40]),
            {"min": [30, -25, 30], "max": [40, -15, 40]}, marker2["bbox"], "q5")
    return v


def validate_four_corner_l(root: Path) -> Validation:
    v = Validation("four-corner-l")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "four-corner-l")
    frame = one_body(d, "FrameBlock")
    v.check("frame bounds", bbox_close(frame, [-60, -40, 0], [60, 40, 60]))

    m = load(root / "measurements-size-160x120.json")
    _check_declared_bounds(v, m, "four-corner-l", level="q5", mutation=True)
    return v


def validate_four_corner_brackets(root: Path) -> Validation:
    v = Validation("four-corner-brackets")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "four-corner-brackets")
    v.check("five bodies: frame plus four middle-plane brackets",
            d["body_count"] == 5, 5, d["body_count"])
    m = load(root / "measurements-size-400x160x200.json")
    _check_declared_bounds(v, m, "four-corner-brackets", level="q5", mutation=True)
    v.check("five bodies after saved-design mutation",
            m["body_count"] == 5, 5, m["body_count"], "q5")
    return v


def validate_eight_corner_brackets(root: Path) -> Validation:
    v = Validation("eight-corner-brackets")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "eight-corner-brackets")
    v.check("nine bodies: frame plus eight outer brackets",
            d["body_count"] == 9, 9, d["body_count"])
    m = load(root / "measurements-size-400x160x200.json")
    _check_declared_bounds(v, m, "eight-corner-brackets", level="q5", mutation=True)
    v.check("nine bodies after saved-design mutation",
            m["body_count"] == 9, 9, m["body_count"], "q5")
    return v


def validate_eight_flightcase_corners(root: Path) -> Validation:
    v = Validation("eight-flightcase-corners")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "eight-flightcase-corners")
    v.check("nine bodies: case plus eight three-face protectors",
            d["body_count"] == 9, 9, d["body_count"])
    m = load(root / "measurements-size-400x160x400.json")
    _check_declared_bounds(v, m, "eight-flightcase-corners", level="q5", mutation=True)
    v.check("nine bodies after saved-design mutation",
            m["body_count"] == 9, 9, m["body_count"], "q5")
    return v


def validate_custom_anchor(root: Path) -> Validation:
    v = Validation("custom-anchor")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "custom-anchor")
    arm = one_body(d, "Arm")
    marker = one_body(d, "Marker")
    v.check("rotated arm bounds", bbox_close(arm, [-5, -20, 0], [5, 20, 10]))
    v.check("marker follows rotated tip", bbox_close(marker, [-5, 15, 0], [5, 25, 10]),
            {"min": [-5, 15, 0], "max": [5, 25, 10]}, marker["bbox"])
    return v


def _xz_expected(width: float, height: float):
    return {
        "right": ([width / 2 - 10, -10, height - 10], [width / 2, 0, height]),
        "left": ([-width / 2, -10, height - 10], [-width / 2 + 10, 0, height]),
    }


def validate_xz_anchor(root: Path) -> Validation:
    v = Validation("xz-anchor")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "xz-anchor")
    markers = bodies_named(d, "Marker")
    expected = _xz_expected(40, 20)
    actual_boxes = [(b["bbox"]["min"], b["bbox"]["max"]) for b in markers]
    v.check("two markers", len(markers) == 2, 2, len(markers))
    for side, (emin, emax) in expected.items():
        hit = any(bbox_close(b, emin, emax) for b in markers)
        v.check(f"{side} BACK_TOP corner alignment", hit,
                {"min": emin, "max": emax}, actual_boxes)

    m = load(root / "measurements-size-80x40.json")
    markers2 = bodies_named(m, "Marker")
    expected2 = _xz_expected(80, 40)
    actual2 = [(b["bbox"]["min"], b["bbox"]["max"]) for b in markers2]
    for side, (emin, emax) in expected2.items():
        hit = any(bbox_close(b, emin, emax) for b in markers2)
        v.check(f"{side} corner follows size mutation", hit,
                {"min": emin, "max": emax}, actual2, "q5")
    return v


def validate_primitive_csg(root: Path) -> Validation:
    v = Validation("primitive-csg")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "primitive-csg", tol=0.01)
    v.check("single resulting CSG body", d["body_count"] == 1, 1, d["body_count"])
    b = d["bodies"][0]
    faces = b.get("face_types", {})
    v.check("sphere survives CSG", faces.get("sphere") == 1, 1, faces.get("sphere"))
    v.check("cylindrical bore survives CSG", faces.get("cylinder") == 1, 1, faces.get("cylinder"))
    v.check("clipped bounds", bbox_close(b, [-20, -20, 0], [25, 20, 20], 0.01),
            {"min": [-20, -20, 0], "max": [25, 20, 20]}, b["bbox"])
    return v


def validate_bracket(root: Path) -> Validation:
    v = Validation("bracket")
    d = load(root / "measurements.json")
    _check_declared_bounds(v, d, "bracket")
    b = d["bodies"][0]
    v.check("single L body", d["body_count"] == 1, 1, d["body_count"])
    v.check("L-profile bounds", bbox_close(b, [0, -12, -40], [40, 12, 0]),
            {"min": [0, -12, -40], "max": [40, 12, 0]}, b["bbox"])
    v.check("L-profile volume", close(b["volume_mm3"], 19584.0), 19584.0, b["volume_mm3"])
    return v


VALIDATORS = {
    "simple-box": validate_simple_box,
    "anchored-holes": validate_anchored_holes,
    "parameter-scope": validate_parameter_scope,
    "components": validate_components,
    "parametric-attach": validate_parametric_attach,
    "parametric-offset": validate_parametric_offset,
    "parametric-anchor": validate_parametric_anchor,
    "corner-anchor": validate_corner_anchor,
    "four-corner-l": validate_four_corner_l,
    "four-corner-brackets": validate_four_corner_brackets,
    "eight-corner-brackets": validate_eight_corner_brackets,
    "eight-flightcase-corners": validate_eight_flightcase_corners,
    "custom-anchor": validate_custom_anchor,
    "xz-anchor": validate_xz_anchor,
    "primitive-csg": validate_primitive_csg,
    "bracket": validate_bracket,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--qualification-dir", type=Path, required=True)
    args = parser.parse_args()

    args.qualification_dir.mkdir(parents=True, exist_ok=True)
    rows = ["case\tq4\tq5\n"]
    summary = {}

    for case, validator in VALIDATORS.items():
        result = validator(args.native_root / case).result()
        summary[case] = result
        case_dir = args.native_root / case
        (case_dir / "validation.json").write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )
        rows.append(f"{case}\t{result['q4'].upper()}\t{result['q5'].upper()}\n")

    (args.qualification_dir / "native-validation.tsv").write_text(
        "".join(rows), encoding="utf-8"
    )
    (args.qualification_dir / "native-validation.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    failed = [
        case for case, result in summary.items()
        if "fail" in (result["q4"], result["q5"])
    ]
    print(f"Validated {len(summary)} native cases")
    if failed:
        print("Native semantic failures: " + ", ".join(failed))
    # Validation failures are data for the report. A final workflow gate may
    # fail the PR after artifacts and Pages have been published.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
