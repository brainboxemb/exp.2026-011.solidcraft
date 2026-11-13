"""Independent expected geometry for native qualification cases.

These values describe the intended Forge contract, not the current SolidCraft
output. Native validators and visual goal overlays consume the same data so a
wrong implementation cannot become its own reference.
"""

EXPECTED_BOUNDS = {
    "simple-box": [
        {"label": "SimpleBox", "min": [-20, -15, 0], "max": [20, 15, 10]},
    ],
    "anchored-holes": [
        {"label": "AnchoredHoles", "min": [0, 0, 0], "max": [100, 60, 10]},
    ],
    "parameter-scope": [
        {"label": "local", "min": [-20, -10, 0], "max": [20, 10, 10]},
        {"label": "override", "min": [70, -10, 0], "max": [130, 10, 10]},
        {"label": "shared_a", "min": [180, -10, 0], "max": [260, 10, 10]},
        {"label": "shared_b", "min": [300, -10, 0], "max": [380, 10, 10]},
        {"label": "derived", "min": [440, -10, 0], "max": [480, 10, 10]},
    ],
    "components": [
        {"label": "left", "min": [-20, -15, 0], "max": [20, 15, 10]},
        {"label": "right", "min": [20, -15, 0], "max": [60, 15, 10]},
    ],
    "parametric-attach": [
        {"label": "Base", "min": [-20, -15, 0], "max": [20, 15, 10]},
        {"label": "Block", "min": [30, -10, 0], "max": [50, 10, 10]},
    ],
    "parametric-offset": [
        {"label": "Base", "min": [-20, -15, 0], "max": [20, 15, 20]},
        {"label": "Marker", "min": [10, -25, 15], "max": [20, -15, 25]},
    ],
    "parametric-anchor": [
        {"label": "Base", "min": [-20, -15, 0], "max": [20, 15, 10]},
        {"label": "Block", "min": [20, -10, 0], "max": [40, 10, 10]},
    ],
    "corner-anchor": [
        {"label": "Base", "min": [-20, -15, 0], "max": [20, 15, 20]},
        {"label": "Marker", "min": [10, -25, 10], "max": [20, -15, 20]},
    ],
    "four-corner-l": [
        {"label": "FrameBlock", "min": [-60, -15, 0], "max": [60, 15, 80]},
        {"label": "top-left", "min": [-60, -27, 40], "max": [-20, -3, 80]},
        {"label": "top-right", "min": [20, -27, 40], "max": [60, -3, 80]},
        {"label": "bottom-right", "min": [20, -27, 0], "max": [60, -3, 40]},
        {"label": "bottom-left", "min": [-60, -27, 0], "max": [-20, -3, 40]},
    ],
    "custom-anchor": [
        {"label": "Arm", "min": [-5, -20, 0], "max": [5, 20, 10]},
        {"label": "Marker", "min": [-5, 15, 0], "max": [5, 25, 10]},
    ],
    "xz-anchor": [
        {"label": "Board", "min": [-20, 0, 0], "max": [20, 12, 20]},
        {"label": "right Marker", "min": [10, -10, 10], "max": [20, 0, 20]},
        {"label": "left Marker", "min": [-20, -10, 10], "max": [-10, 0, 20]},
    ],
    "primitive-csg": [
        {"label": "PrimitiveCsg", "min": [-20, -20, 0], "max": [25, 20, 20]},
    ],
    "bracket": [
        {"label": "Bracket", "min": [0, -12, -40], "max": [40, 12, 0]},
    ],
}


EXPECTED_MUTATION_BOUNDS = {
    "parameter-scope": [
        {"label": "local", "min": [-20, -10, 0], "max": [20, 10, 10]},
        {"label": "override", "min": [70, -10, 0], "max": [130, 10, 10]},
        {"label": "shared_a", "min": [170, -10, 0], "max": [270, 10, 10]},
        {"label": "shared_b", "min": [290, -10, 0], "max": [390, 10, 10]},
        {"label": "derived", "min": [435, -10, 0], "max": [485, 10, 10]},
    ],
    "parametric-attach": [
        {"label": "Base", "min": [-20, -15, 0], "max": [20, 15, 10]},
        {"label": "Block", "min": [50, -10, 0], "max": [70, 10, 10]},
    ],
    "parametric-offset": [
        {"label": "Base", "min": [-20, -15, 0], "max": [20, 15, 20]},
        {"label": "Marker", "min": [10, -25, 20], "max": [20, -15, 30]},
    ],
    "parametric-anchor": [
        {"label": "Base", "min": [-40, -15, 0], "max": [40, 15, 10]},
        {"label": "Block", "min": [40, -10, 0], "max": [60, 10, 10]},
    ],
    "corner-anchor": [
        {"label": "Base", "min": [-40, -15, 0], "max": [40, 15, 40]},
        {"label": "Marker", "min": [30, -25, 30], "max": [40, -15, 40]},
    ],
    "four-corner-l": [
        {"label": "FrameBlock", "min": [-80, -15, 0], "max": [80, 15, 120]},
        {"label": "top-left", "min": [-80, -27, 80], "max": [-40, -3, 120]},
        {"label": "top-right", "min": [40, -27, 80], "max": [80, -3, 120]},
        {"label": "bottom-right", "min": [40, -27, 0], "max": [80, -3, 40]},
        {"label": "bottom-left", "min": [-80, -27, 0], "max": [-40, -3, 40]},
    ],
    "xz-anchor": [
        {"label": "Board", "min": [-40, 0, 0], "max": [40, 12, 40]},
        {"label": "right Marker", "min": [30, -10, 30], "max": [40, 0, 40]},
        {"label": "left Marker", "min": [-40, -10, 30], "max": [-30, 0, 40]},
    ],
}


# Visual overlays may use a more detailed decomposition than the Q4 outer
# bounds. In particular an L-profile can be mirrored/rotated incorrectly while
# retaining the same overall bounding box, so draw its two arms separately.
EXPECTED_VISUAL_BOXES = dict(EXPECTED_BOUNDS)

EXPECTED_VISUAL_BOXES["bracket"] = [
    {"label": "arm X", "min": [0, -12, -12], "max": [40, 12, 0]},
    {"label": "arm Z", "min": [0, -12, -40], "max": [12, 12, 0]},
]

EXPECTED_VISUAL_BOXES["four-corner-l"] = [
    {"label": "FrameBlock", "min": [-60, -15, 0], "max": [60, 15, 80]},

    # top-left: inward +X, downward -Z
    {"label": "TL arm X", "min": [-60, -27, 68], "max": [-20, -3, 80]},
    {"label": "TL arm Z", "min": [-60, -27, 40], "max": [-48, -3, 80]},

    # top-right: inward -X, downward -Z
    {"label": "TR arm X", "min": [20, -27, 68], "max": [60, -3, 80]},
    {"label": "TR arm Z", "min": [48, -27, 40], "max": [60, -3, 80]},

    # bottom-right: inward -X, upward +Z
    {"label": "BR arm X", "min": [20, -27, 0], "max": [60, -3, 12]},
    {"label": "BR arm Z", "min": [48, -27, 0], "max": [60, -3, 40]},

    # bottom-left: inward +X, upward +Z
    {"label": "BL arm X", "min": [-60, -27, 0], "max": [-20, -3, 12]},
    {"label": "BL arm Z", "min": [-60, -27, 0], "max": [-48, -3, 40]},
]
