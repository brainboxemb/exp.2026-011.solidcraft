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
        {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
        {"label": "front-left foot", "min": [-60, -40, -30], "max": [-32, -12, 0]},
        {"label": "front-right foot", "min": [32, -40, -30], "max": [60, -12, 0]},
        {"label": "back-right foot", "min": [32, 12, -30], "max": [60, 40, 0]},
        {"label": "back-left foot", "min": [-60, 12, -30], "max": [-32, 40, 0]},
    ],
    "four-corner-brackets": [
        {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
        {"label": "front top-left", "min": [-72, -64, 12], "max": [0, -40, 84]},
        {"label": "front top-right", "min": [0, -64, 12], "max": [72, -40, 84]},
        {"label": "front bottom-right", "min": [0, -64, -24], "max": [72, -40, 48]},
        {"label": "front bottom-left", "min": [-72, -64, -24], "max": [0, -40, 48]},
    ],
    "eight-hub75-corner-brackets": [
        {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
        {"label": "front top-left", "min": [-72, -64, 12], "max": [0, -40, 84]},
        {"label": "front top-right", "min": [0, -64, 12], "max": [72, -40, 84]},
        {"label": "front bottom-right", "min": [0, -64, -24], "max": [72, -40, 48]},
        {"label": "front bottom-left", "min": [-72, -64, -24], "max": [0, -40, 48]},
        {"label": "rear top-left", "min": [-72, 40, 12], "max": [0, 64, 84]},
        {"label": "rear top-right", "min": [0, 40, 12], "max": [72, 64, 84]},
        {"label": "rear bottom-right", "min": [0, 40, -24], "max": [72, 64, 48]},
        {"label": "rear bottom-left", "min": [-72, 40, -24], "max": [0, 64, 48]},
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
        {"label": "front top-left", "min": [-60, -44, 32], "max": [-32, -40, 60]},
        {"label": "front top-right", "min": [32, -44, 32], "max": [60, -40, 60]},
        {"label": "front bottom-right", "min": [32, -44, 0], "max": [60, -40, 28]},
        {"label": "front bottom-left", "min": [-60, -44, 0], "max": [-32, -40, 28]},
        {"label": "rear top-left", "min": [-60, 40, 32], "max": [-32, 44, 60]},
        {"label": "rear top-right", "min": [32, 40, 32], "max": [60, 44, 60]},
        {"label": "rear bottom-right", "min": [32, 40, 0], "max": [60, 44, 28]},
        {"label": "rear bottom-left", "min": [-60, 40, 0], "max": [-32, 44, 28]},
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
        {"label": "FrameBlock", "min": [-80, -60, 0], "max": [80, 60, 60]},
        {"label": "front-left foot", "min": [-80, -60, -30], "max": [-52, -32, 0]},
        {"label": "front-right foot", "min": [52, -60, -30], "max": [80, -32, 0]},
        {"label": "back-right foot", "min": [52, 32, -30], "max": [80, 60, 0]},
        {"label": "back-left foot", "min": [-80, 32, -30], "max": [-52, 60, 0]},
    ],
    "four-corner-brackets": [
        {"label": "FrameBlock", "min": [-80, -60, 0], "max": [80, 60, 90]},
        {"label": "front top-left", "min": [-92, -84, 42], "max": [-20, -60, 114]},
        {"label": "front top-right", "min": [20, -84, 42], "max": [92, -60, 114]},
        {"label": "front bottom-right", "min": [20, -84, -24], "max": [92, -60, 48]},
        {"label": "front bottom-left", "min": [-92, -84, -24], "max": [-20, -60, 48]},
    ],
    "eight-hub75-corner-brackets": [
        {"label": "FrameBlock", "min": [-80, -60, 0], "max": [80, 60, 90]},
        {"label": "front top-left", "min": [-92, -84, 42], "max": [-20, -60, 114]},
        {"label": "front top-right", "min": [20, -84, 42], "max": [92, -60, 114]},
        {"label": "front bottom-right", "min": [20, -84, -24], "max": [92, -60, 48]},
        {"label": "front bottom-left", "min": [-92, -84, -24], "max": [-20, -60, 48]},
        {"label": "rear top-left", "min": [-92, 60, 42], "max": [-20, 84, 114]},
        {"label": "rear top-right", "min": [20, 60, 42], "max": [92, 84, 114]},
        {"label": "rear bottom-right", "min": [20, 60, -24], "max": [92, 84, 48]},
        {"label": "rear bottom-left", "min": [-92, 60, -24], "max": [-20, 84, 48]},
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
        {"label": "front top-left", "min": [-80, -64, 62], "max": [-52, -60, 90]},
        {"label": "front top-right", "min": [52, -64, 62], "max": [80, -60, 90]},
        {"label": "front bottom-right", "min": [52, -64, 0], "max": [80, -60, 28]},
        {"label": "front bottom-left", "min": [-80, -64, 0], "max": [-52, -60, 28]},
        {"label": "rear top-left", "min": [-80, 60, 62], "max": [-52, 64, 90]},
        {"label": "rear top-right", "min": [52, 60, 62], "max": [80, 64, 90]},
        {"label": "rear bottom-right", "min": [52, 60, 0], "max": [80, 64, 28]},
        {"label": "rear bottom-left", "min": [-80, 60, 0], "max": [-52, 64, 28]},
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

    # front-left: local +X/+Y both point inward
    {"label": "FL arm X", "min": [-60, -40, -30], "max": [-32, -32, 0]},
    {"label": "FL arm Y", "min": [-60, -40, -30], "max": [-52, -12, 0]},

    # front-right: same foot rotated 90 degrees
    {"label": "FR arm X", "min": [52, -40, -30], "max": [60, -12, 0]},
    {"label": "FR arm Y", "min": [32, -40, -30], "max": [60, -32, 0]},

    # back-right: same foot rotated 180 degrees
    {"label": "BR arm X", "min": [32, 32, -30], "max": [60, 40, 0]},
    {"label": "BR arm Y", "min": [52, 12, -30], "max": [60, 40, 0]},

    # back-left: same foot rotated 270 degrees
    {"label": "BL arm X", "min": [-60, 12, -30], "max": [-52, 40, 0]},
    {"label": "BL arm Y", "min": [-60, 32, -30], "max": [-32, 40, 0]},
]

EXPECTED_VISUAL_BOXES["four-corner-brackets"] = [
    {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},
    {"label": "FTL top arm", "min": [-60, -44, 52], "max": [-32, -40, 60]},
    {"label": "FTL side arm", "min": [-60, -44, 32], "max": [-52, -40, 60]},
    {"label": "FTR top arm", "min": [32, -44, 52], "max": [60, -40, 60]},
    {"label": "FTR side arm", "min": [52, -44, 32], "max": [60, -40, 60]},
    {"label": "FBR bottom arm", "min": [32, -44, 0], "max": [60, -40, 8]},
    {"label": "FBR side arm", "min": [52, -44, 0], "max": [60, -40, 28]},
    {"label": "FBL bottom arm", "min": [-60, -44, 0], "max": [-32, -40, 8]},
    {"label": "FBL side arm", "min": [-60, -44, 0], "max": [-52, -40, 28]},
]

EXPECTED_VISUAL_BOXES["eight-corner-brackets"] = [
    {"label": "FrameBlock", "min": [-60, -40, 0], "max": [60, 40, 60]},

    {"label": "FTL top arm", "min": [-60, -44, 52], "max": [-32, -40, 60]},
    {"label": "FTL side arm", "min": [-60, -44, 32], "max": [-52, -40, 60]},
    {"label": "FTR top arm", "min": [32, -44, 52], "max": [60, -40, 60]},
    {"label": "FTR side arm", "min": [52, -44, 32], "max": [60, -40, 60]},
    {"label": "FBR bottom arm", "min": [32, -44, 0], "max": [60, -40, 8]},
    {"label": "FBR side arm", "min": [52, -44, 0], "max": [60, -40, 28]},
    {"label": "FBL bottom arm", "min": [-60, -44, 0], "max": [-32, -40, 8]},
    {"label": "FBL side arm", "min": [-60, -44, 0], "max": [-52, -40, 28]},

    {"label": "RTL top arm", "min": [-60, 40, 52], "max": [-32, 44, 60]},
    {"label": "RTL side arm", "min": [-60, 40, 32], "max": [-52, 44, 60]},
    {"label": "RTR top arm", "min": [32, 40, 52], "max": [60, 44, 60]},
    {"label": "RTR side arm", "min": [52, 40, 32], "max": [60, 44, 60]},
    {"label": "RBR bottom arm", "min": [32, 40, 0], "max": [60, 44, 8]},
    {"label": "RBR side arm", "min": [52, 40, 0], "max": [60, 44, 28]},
    {"label": "RBL bottom arm", "min": [-60, 40, 0], "max": [-32, 44, 8]},
    {"label": "RBL side arm", "min": [-60, 40, 0], "max": [-52, 44, 28]},
]
