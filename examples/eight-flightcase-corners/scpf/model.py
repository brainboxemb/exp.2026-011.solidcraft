"""Eight reusable 3D flightcase corner protectors around one case."""


class CaseBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class FlightcaseCorner:
    ARM = 30.0
    THICKNESS = 4.0

    def build(self):
        arm = self.ARM
        t = self.THICKNESS

        # Neutral trihedral outside corner. In its canonical orientation the
        # case extends inward along +X, +Y and -Z. The three plates therefore
        # wrap the top, front/back and side faces instead of merely hovering
        # near the corner point.
        top = Box(arm, arm, t).move(
            x=arm / 2,
            y=arm / 2,
        )
        face = Box(arm, t, arm).move(
            x=arm / 2,
            y=-(t / 2),
            z=-arm,
        )
        side = Box(t, arm, arm).move(
            x=-(t / 2),
            y=arm / 2,
            z=-arm,
        )
        return top + face + side


class EightFlightcaseCorners:
    case_width = 120.0
    case_depth = 80.0
    case_height = 60.0

    def build(self):
        case = CaseBlock(
            _width=self.case_width,
            _depth=self.case_depth,
            _height=self.case_height,
        )
        protector = FlightcaseCorner()

        # The reusable protector publishes one canonical local frame. The
        # topology-backed parent corner supplies the occurrence-specific
        # position and orientation for all eight corners.
        corner_frame = AnchorFrame(
            origin=(0, 0, 0),
            z=Anchor.FRONT,
            x=Anchor.RIGHT,
        )

        front_top_left = protector.copy().attach(
            case, parent=Anchor.FRONT_TOP_LEFT, child=corner_frame,
        )
        front_top_right = protector.copy().attach(
            case, parent=Anchor.FRONT_TOP_RIGHT, child=corner_frame,
        )
        front_bottom_right = protector.copy().attach(
            case, parent=Anchor.FRONT_BOTTOM_RIGHT, child=corner_frame,
        )
        front_bottom_left = protector.copy().attach(
            case, parent=Anchor.FRONT_BOTTOM_LEFT, child=corner_frame,
        )
        rear_top_left = protector.copy().attach(
            case, parent=Anchor.BACK_TOP_LEFT, child=corner_frame,
        )
        rear_top_right = protector.copy().attach(
            case, parent=Anchor.BACK_TOP_RIGHT, child=corner_frame,
        )
        rear_bottom_right = protector.copy().attach(
            case, parent=Anchor.BACK_BOTTOM_RIGHT, child=corner_frame,
        )
        rear_bottom_left = protector.copy().attach(
            case, parent=Anchor.BACK_BOTTOM_LEFT, child=corner_frame,
        )

        return (
            case
            + front_top_left + front_top_right
            + front_bottom_right + front_bottom_left
            + rear_top_left + rear_top_right
            + rear_bottom_right + rear_bottom_left
        )


EightFlightcaseCorners()
