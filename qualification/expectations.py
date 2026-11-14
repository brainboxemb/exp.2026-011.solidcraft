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
    "parent-derived-child-size": [
        {"label": "ParentBlock", "min": [-60, -40, 0], "max": [60, 40, 10]},
        {"label": "DerivedChild", "min": [-30, -20, 20], "max": [30, 20, 26]},
    ],
    "components": [
        {"label": "left", "min": [-20, -15, 0], "max": [20, 15, 10]},
        {"label": "right", "min": [20, -15, 0], "max": [60, 15, 10]},
    ],
    "attach-angle": [
        {"label": "Base", "min": [-30, -30, 0], "max": [30, 30, 10]},
        {"label": "Arm", "min": [-5, -15, 10], "max": [5, 15, 16]},
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
    "anchor-topology-mutation": [
        {"label": "Board", "min": [-20, -10, 0], "max": [20, 10, 20]},
        {"label": "Marker", "min": [-25, -20, 15], "max": [-15, -10, 25]},
    ],
    "assembly-owned-anchor": [
        {"label": "Base", "min": [-20, -15, 0], "max": [20, 15, 20]},
        {"label": "Companion", "min": [65, -5, 0], "max": [75, 5, 10]},
        {"label": "Marker", "min": [10, -25, 10], "max": [20, -15, 20]},
    ],
    "four-corner-l": [
        {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
        {"label": "top-left", "min": [-60, -2, 32], "max": [-32, 2, 60]},
        {"label": "top-right", "min": [32, -2, 32], "max": [60, 2, 60]},
        {"label": "bottom-right", "min": [32, -2, 0], "max": [60, 2, 28]},
        {"label": "bottom-left", "min": [-60, -2, 0], "max": [-32, 2, 28]},
    ],
    "eight-flightcase-corners": [
        {"label": "CaseBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
        {"label": "front top-left", "min": [-64, -44, 30], "max": [-30, -10, 64]},
        {"label": "front top-right", "min": [30, -44, 30], "max": [64, -10, 64]},
        {"label": "front bottom-right", "min": [30, -44, -4], "max": [64, -10, 30]},
        {"label": "front bottom-left", "min": [-64, -44, -4], "max": [-30, -10, 30]},
        {"label": "rear top-left", "min": [-64, 10, 30], "max": [-30, 44, 64]},
        {"label": "rear top-right", "min": [30, 10, 30], "max": [64, 44, 64]},
        {"label": "rear bottom-right", "min": [30, 10, -4], "max": [64, 44, 30]},
        {"label": "rear bottom-left", "min": [-64, 10, -4], "max": [-30, 44, 30]},
    ],
    "eight-corner-brackets": [
        {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
        {"label": "top-left front", "min": [-60, -40, 32], "max": [-32, -36, 60]},
        {"label": "top-right front", "min": [32, -40, 32], "max": [60, -36, 60]},
        {"label": "bottom-right front", "min": [32, -40, 0], "max": [60, -36, 28]},
        {"label": "bottom-left front", "min": [-60, -40, 0], "max": [-32, -36, 28]},
        {"label": "top-left rear", "min": [-60, 36, 32], "max": [-32, 40, 60]},
        {"label": "top-right rear", "min": [32, 36, 32], "max": [60, 40, 60]},
        {"label": "bottom-right rear", "min": [32, 36, 0], "max": [60, 40, 28]},
        {"label": "bottom-left rear", "min": [-60, 36, 0], "max": [-32, 40, 28]},
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
    "assembly-owned-anchor": [
        {"label": "Base", "min": [-40, -15, 0], "max": [40, 15, 40]},
        {"label": "Companion", "min": [65, -5, 0], "max": [75, 5, 10]},
        {"label": "Marker", "min": [30, -25, 30], "max": [40, -15, 40]},
    ],
    "anchor-topology-mutation": [
        {"label": "Board", "min": [-40, -10, 0], "max": [40, 10, 40]},
        {"label": "Marker", "min": [-45, -20, 35], "max": [-35, -10, 45]},
    ],
    "parent-derived-child-size": [
        {"label": "ParentBlock", "min": [-80, -60, 0], "max": [80, 60, 10]},
        {"label": "DerivedChild", "min": [-40, -30, 20], "max": [40, 30, 26]},
    ],
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
        {"label": "FrameBlock", "min": [-80, -60, 0], "max": [80, 60, 60]},
        {"label": "top-left", "min": [-80, -2, 32], "max": [-52, 2, 60]},
        {"label": "top-right", "min": [52, -2, 32], "max": [80, 2, 60]},
        {"label": "bottom-right", "min": [52, -2, 0], "max": [80, 2, 28]},
        {"label": "bottom-left", "min": [-80, -2, 0], "max": [-52, 2, 28]},
    ],
    "eight-flightcase-corners": [
        {"label": "CaseBlock", "min": [-80, -60, 0], "max": [80, 60, 90]},
        {"label": "front top-left", "min": [-84, -64, 60], "max": [-50, -30, 94]},
        {"label": "front top-right", "min": [50, -64, 60], "max": [84, -30, 94]},
        {"label": "front bottom-right", "min": [50, -64, -4], "max": [84, -30, 30]},
        {"label": "front bottom-left", "min": [-84, -64, -4], "max": [-50, -30, 30]},
        {"label": "rear top-left", "min": [-84, 30, 60], "max": [-50, 64, 94]},
        {"label": "rear top-right", "min": [50, 30, 60], "max": [84, 64, 94]},
        {"label": "rear bottom-right", "min": [50, 30, -4], "max": [84, 64, 30]},
        {"label": "rear bottom-left", "min": [-84, 30, -4], "max": [-50, 64, 30]},
    ],
    "eight-corner-brackets": [
        {"label": "FrameBlock", "min": [-80, -60, 0], "max": [80, 60, 90]},
        {"label": "top-left front", "min": [-80, -60, 62], "max": [-52, -56, 90]},
        {"label": "top-right front", "min": [52, -60, 62], "max": [80, -56, 90]},
        {"label": "bottom-right front", "min": [52, -60, 0], "max": [80, -56, 28]},
        {"label": "bottom-left front", "min": [-80, -60, 0], "max": [-52, -56, 28]},
        {"label": "top-left rear", "min": [-80, 56, 62], "max": [-52, 60, 90]},
        {"label": "top-right rear", "min": [52, 56, 62], "max": [80, 60, 90]},
        {"label": "bottom-right rear", "min": [52, 56, 0], "max": [80, 60, 28]},
        {"label": "bottom-left rear", "min": [-80, 56, 0], "max": [-52, 60, 28]},
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
    {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
    {"label": "TL top arm", "min": [-60, -2, 52], "max": [-32, 2, 60]},
    {"label": "TL side arm", "min": [-60, -2, 32], "max": [-52, 2, 60]},
    {"label": "TR top arm", "min": [32, -2, 52], "max": [60, 2, 60]},
    {"label": "TR side arm", "min": [52, -2, 32], "max": [60, 2, 60]},
    {"label": "BR bottom arm", "min": [32, -2, 0], "max": [60, 2, 8]},
    {"label": "BR side arm", "min": [52, -2, 0], "max": [60, 2, 28]},
    {"label": "BL bottom arm", "min": [-60, -2, 0], "max": [-32, 2, 8]},
    {"label": "BL side arm", "min": [-60, -2, 0], "max": [-52, 2, 28]},
]

EXPECTED_VISUAL_BOXES["eight-flightcase-corners"] = [
    {"label": "CaseBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},

    # Front top left: three thin plates wrap the X-, Y- and Z-facing sides.
    {"label": "FTL top", "min": [-60, -40, 60], "max": [-30, -10, 64]},
    {"label": "FTL front", "min": [-60, -44, 30], "max": [-30, -40, 60]},
    {"label": "FTL side", "min": [-64, -40, 30], "max": [-60, -10, 60]},

    {"label": "FTR top", "min": [30, -40, 60], "max": [60, -10, 64]},
    {"label": "FTR front", "min": [30, -44, 30], "max": [60, -40, 60]},
    {"label": "FTR side", "min": [60, -40, 30], "max": [64, -10, 60]},

    {"label": "FBR bottom", "min": [30, -40, -4], "max": [60, -10, 0]},
    {"label": "FBR front", "min": [30, -44, 0], "max": [60, -40, 30]},
    {"label": "FBR side", "min": [60, -40, 0], "max": [64, -10, 30]},

    {"label": "FBL bottom", "min": [-60, -40, -4], "max": [-30, -10, 0]},
    {"label": "FBL front", "min": [-60, -44, 0], "max": [-30, -40, 30]},
    {"label": "FBL side", "min": [-64, -40, 0], "max": [-60, -10, 30]},

    {"label": "RTL top", "min": [-60, 10, 60], "max": [-30, 40, 64]},
    {"label": "RTL rear", "min": [-60, 40, 30], "max": [-30, 44, 60]},
    {"label": "RTL side", "min": [-64, 10, 30], "max": [-60, 40, 60]},

    {"label": "RTR top", "min": [30, 10, 60], "max": [60, 40, 64]},
    {"label": "RTR rear", "min": [30, 40, 30], "max": [60, 44, 60]},
    {"label": "RTR side", "min": [60, 10, 30], "max": [64, 40, 60]},

    {"label": "RBR bottom", "min": [30, 10, -4], "max": [60, 40, 0]},
    {"label": "RBR rear", "min": [30, 40, 0], "max": [60, 44, 30]},
    {"label": "RBR side", "min": [60, 10, 0], "max": [64, 40, 30]},

    {"label": "RBL bottom", "min": [-60, 10, -4], "max": [-30, 40, 0]},
    {"label": "RBL rear", "min": [-60, 40, 0], "max": [-30, 44, 30]},
    {"label": "RBL side", "min": [-64, 10, 0], "max": [-60, 40, 30]},
]

EXPECTED_VISUAL_BOXES["eight-corner-brackets"] = [
    {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},

    {"label": "TL front top arm", "min": [-60, -40, 52], "max": [-32, -36, 60]},
    {"label": "TL front side arm", "min": [-60, -40, 32], "max": [-52, -36, 60]},
    {"label": "TR front top arm", "min": [32, -40, 52], "max": [60, -36, 60]},
    {"label": "TR front side arm", "min": [52, -40, 32], "max": [60, -36, 60]},
    {"label": "BR front bottom arm", "min": [32, -40, 0], "max": [60, -36, 8]},
    {"label": "BR front side arm", "min": [52, -40, 0], "max": [60, -36, 28]},
    {"label": "BL front bottom arm", "min": [-60, -40, 0], "max": [-32, -36, 8]},
    {"label": "BL front side arm", "min": [-60, -40, 0], "max": [-52, -36, 28]},

    {"label": "TL rear top arm", "min": [-60, 36, 52], "max": [-32, 40, 60]},
    {"label": "TL rear side arm", "min": [-60, 36, 32], "max": [-52, 40, 60]},
    {"label": "TR rear top arm", "min": [32, 36, 52], "max": [60, 40, 60]},
    {"label": "TR rear side arm", "min": [52, 36, 32], "max": [60, 40, 60]},
    {"label": "BR rear bottom arm", "min": [32, 36, 0], "max": [60, 40, 8]},
    {"label": "BR rear side arm", "min": [52, 36, 0], "max": [60, 40, 28]},
    {"label": "BL rear bottom arm", "min": [-60, 36, 0], "max": [-32, 40, 8]},
    {"label": "BL rear side arm", "min": [-60, 36, 0], "max": [-52, 40, 28]},
]