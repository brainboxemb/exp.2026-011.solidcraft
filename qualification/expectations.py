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
        {"label": "FrameBlock", "min": [-160, -60, 0], "max": [160, 60, 160]},
        {"label": "middle top-left", "min": [-168, -4, 124], "max": [-124, 4, 168]},
        {"label": "middle top-right", "min": [124, -4, 124], "max": [168, 4, 168]},
        {"label": "middle bottom-right", "min": [124, -4, -8], "max": [168, 4, 36]},
        {"label": "middle bottom-left", "min": [-168, -4, -8], "max": [-124, 4, 36]},
    ],
    "eight-corner-brackets": [
        {"label": "FrameBlock", "min": [-160, -60, 0], "max": [160, 60, 160]},
        {"label": "front top-left", "min": [-168, -68, 124], "max": [-124, -60, 168]},
        {"label": "front top-right", "min": [124, -68, 124], "max": [168, -60, 168]},
        {"label": "front bottom-right", "min": [124, -68, -8], "max": [168, -60, 36]},
        {"label": "front bottom-left", "min": [-168, -68, -8], "max": [-124, -60, 36]},
        {"label": "rear top-left", "min": [-168, 60, 124], "max": [-124, 68, 168]},
        {"label": "rear top-right", "min": [124, 60, 124], "max": [168, 68, 168]},
        {"label": "rear bottom-right", "min": [124, 60, -8], "max": [168, 68, 36]},
        {"label": "rear bottom-left", "min": [-168, 60, -8], "max": [-124, 68, 36]},
    ],
    "eight-flightcase-corners": [
        {"label": "CaseBlock", "min": [-160, -60, 0], "max": [160, 60, 320]},
        {"label": "front top-left", "min": [-166, -66, 240], "max": [-80, -30, 326]},
        {"label": "front top-right", "min": [80, -66, 240], "max": [166, -30, 326]},
        {"label": "front bottom-right", "min": [80, -66, -6], "max": [166, -30, 80]},
        {"label": "front bottom-left", "min": [-166, -66, -6], "max": [-80, -30, 80]},
        {"label": "rear top-left", "min": [-166, 30, 240], "max": [-80, 66, 326]},
        {"label": "rear top-right", "min": [80, 30, 240], "max": [166, 66, 326]},
        {"label": "rear bottom-right", "min": [80, 30, -6], "max": [166, 66, 80]},
        {"label": "rear bottom-left", "min": [-166, 30, -6], "max": [-80, 66, 80]},
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
        {"label": "FrameBlock", "min": [-200, -80, 0], "max": [200, 80, 200]},
        {"label": "middle top-left", "min": [-208, -4, 164], "max": [-164, 4, 208]},
        {"label": "middle top-right", "min": [164, -4, 164], "max": [208, 4, 208]},
        {"label": "middle bottom-right", "min": [164, -4, -8], "max": [208, 4, 36]},
        {"label": "middle bottom-left", "min": [-208, -4, -8], "max": [-164, 4, 36]},
    ],
    "eight-corner-brackets": [
        {"label": "FrameBlock", "min": [-200, -80, 0], "max": [200, 80, 200]},
        {"label": "front top-left", "min": [-208, -88, 164], "max": [-164, -80, 208]},
        {"label": "front top-right", "min": [164, -88, 164], "max": [208, -80, 208]},
        {"label": "front bottom-right", "min": [164, -88, -8], "max": [208, -80, 36]},
        {"label": "front bottom-left", "min": [-208, -88, -8], "max": [-164, -80, 36]},
        {"label": "rear top-left", "min": [-208, 80, 164], "max": [-164, 88, 208]},
        {"label": "rear top-right", "min": [164, 80, 164], "max": [208, 88, 208]},
        {"label": "rear bottom-right", "min": [164, 80, -8], "max": [208, 88, 36]},
        {"label": "rear bottom-left", "min": [-208, 80, -8], "max": [-164, 88, 36]},
    ],
    "eight-flightcase-corners": [
        {"label": "CaseBlock", "min": [-200, -80, 0], "max": [200, 80, 400]},
        {"label": "front top-left", "min": [-206, -86, 300], "max": [-100, -40, 406]},
        {"label": "front top-right", "min": [100, -86, 300], "max": [206, -40, 406]},
        {"label": "front bottom-right", "min": [100, -86, -6], "max": [206, -40, 100]},
        {"label": "front bottom-left", "min": [-206, -86, -6], "max": [-100, -40, 100]},
        {"label": "rear top-left", "min": [-206, 40, 300], "max": [-100, 86, 406]},
        {"label": "rear top-right", "min": [100, 40, 300], "max": [206, 86, 406]},
        {"label": "rear bottom-right", "min": [100, 40, -6], "max": [206, 86, 100]},
        {"label": "rear bottom-left", "min": [-206, 40, -6], "max": [-100, 86, 100]},
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
    {"label": "FrameBlock", "min": [-160, -60, 0], "max": [160, 60, 160]},
    {"label": "MTL top arm", "min": [-168, -4, 160], "max": [-124, 4, 168]},
    {"label": "MTL side arm", "min": [-168, -4, 124], "max": [-160, 4, 168]},
    {"label": "MTR top arm", "min": [124, -4, 160], "max": [168, 4, 168]},
    {"label": "MTR side arm", "min": [160, -4, 124], "max": [168, 4, 168]},
    {"label": "MBR bottom arm", "min": [124, -4, -8], "max": [168, 4, 0]},
    {"label": "MBR side arm", "min": [160, -4, -8], "max": [168, 4, 36]},
    {"label": "MBL bottom arm", "min": [-168, -4, -8], "max": [-124, 4, 0]},
    {"label": "MBL side arm", "min": [-168, -4, -8], "max": [-160, 4, 36]},
]

EXPECTED_VISUAL_BOXES["eight-corner-brackets"] = [
    {"label": "FrameBlock", "min": [-160, -60, 0], "max": [160, 60, 160]},
    {"label": "FTL top arm", "min": [-168, -68, 160], "max": [-124, -60, 168]},
    {"label": "FTL side arm", "min": [-168, -68, 124], "max": [-160, -60, 168]},
    {"label": "FTR top arm", "min": [124, -68, 160], "max": [168, -60, 168]},
    {"label": "FTR side arm", "min": [160, -68, 124], "max": [168, -60, 168]},
    {"label": "FBR bottom arm", "min": [124, -68, -8], "max": [168, -60, 0]},
    {"label": "FBR side arm", "min": [160, -68, -8], "max": [168, -60, 36]},
    {"label": "FBL bottom arm", "min": [-168, -68, -8], "max": [-124, -60, 0]},
    {"label": "FBL side arm", "min": [-168, -68, -8], "max": [-160, -60, 36]},
    {"label": "RTL top arm", "min": [-168, 60, 160], "max": [-124, 68, 168]},
    {"label": "RTL side arm", "min": [-168, 60, 124], "max": [-160, 68, 168]},
    {"label": "RTR top arm", "min": [124, 60, 160], "max": [168, 68, 168]},
    {"label": "RTR side arm", "min": [160, 60, 124], "max": [168, 68, 168]},
    {"label": "RBR bottom arm", "min": [124, 60, -8], "max": [168, 68, 0]},
    {"label": "RBR side arm", "min": [160, 60, -8], "max": [168, 68, 36]},
    {"label": "RBL bottom arm", "min": [-168, 60, -8], "max": [-124, 68, 0]},
    {"label": "RBL side arm", "min": [-168, 60, -8], "max": [-160, 68, 36]},
]

EXPECTED_VISUAL_BOXES["eight-flightcase-corners"] = [
    {"label": "CaseBlock", "min": [-160, -60, 0], "max": [160, 60, 320]},
    {"label": "FTL top", "min": [-160, -60, 320], "max": [-80, -30, 326]},
    {"label": "FTL front", "min": [-160, -66, 240], "max": [-80, -60, 320]},
    {"label": "FTL side", "min": [-166, -60, 240], "max": [-160, -30, 320]},
    {"label": "FTR top", "min": [80, -60, 320], "max": [160, -30, 326]},
    {"label": "FTR front", "min": [80, -66, 240], "max": [160, -60, 320]},
    {"label": "FTR side", "min": [160, -60, 240], "max": [166, -30, 320]},
    {"label": "FBR bottom", "min": [80, -60, -6], "max": [160, -30, 0]},
    {"label": "FBR front", "min": [80, -66, 0], "max": [160, -60, 80]},
    {"label": "FBR side", "min": [160, -60, 0], "max": [166, -30, 80]},
    {"label": "FBL bottom", "min": [-160, -60, -6], "max": [-80, -30, 0]},
    {"label": "FBL front", "min": [-160, -66, 0], "max": [-80, -60, 80]},
    {"label": "FBL side", "min": [-166, -60, 0], "max": [-160, -30, 80]},
    {"label": "RTL top", "min": [-160, 30, 320], "max": [-80, 60, 326]},
    {"label": "RTL rear", "min": [-160, 60, 240], "max": [-80, 66, 320]},
    {"label": "RTL side", "min": [-166, 30, 240], "max": [-160, 60, 320]},
    {"label": "RTR top", "min": [80, 30, 320], "max": [160, 60, 326]},
    {"label": "RTR rear", "min": [80, 60, 240], "max": [160, 66, 320]},
    {"label": "RTR side", "min": [160, 30, 240], "max": [166, 60, 320]},
    {"label": "RBR bottom", "min": [80, 30, -6], "max": [160, 60, 0]},
    {"label": "RBR rear", "min": [80, 60, 0], "max": [160, 66, 80]},
    {"label": "RBR side", "min": [160, 30, 0], "max": [166, 60, 80]},
    {"label": "RBL bottom", "min": [-160, 30, -6], "max": [-80, 60, 0]},
    {"label": "RBL rear", "min": [-160, 60, 0], "max": [-80, 66, 80]},
    {"label": "RBL side", "min": [-166, 30, 0], "max": [-160, 60, 80]},
]

