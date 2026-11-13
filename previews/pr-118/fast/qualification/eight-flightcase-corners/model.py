"""Eight trihedral flightcase corner protectors around one case."""


class CaseBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class FlightcaseCorner:
    ARM = 30.0
    THICKNESS = 4.0
    OVERLAP = 0.5

    def build(self):
        arm = self.ARM
        t = self.THICKNESS
        overlap = self.OVERLAP

        # Neutral outside corner cap for FRONT_TOP_LEFT.
        # The case extends inward along +X, +Y and -Z.
        #
        # Three square plates meet at the same corner:
        #   top plate   : +X / +Y, thickness outward in +Z
        #   front plate : +X / -Z, thickness outward in -Y
        #   side plate  : +Y / -Z, thickness outward in -X
        top = Box(arm, arm, t).move(
            x=arm / 2,
            y=arm / 2,
            z=t / 2,
        )
        # A tiny internal overlap keeps the three native box joins robust.
        # It is entirely inside the cap and does not change the outer bounds.
        front = Box(arm, t + overlap, arm + overlap).move(
            x=arm / 2,
            y=(overlap - t) / 2,
            z=(overlap - arm) / 2,
        )
        side = Box(t + overlap, arm, arm + overlap).move(
            x=(overlap - t) / 2,
            y=arm / 2,
            z=(overlap - arm) / 2,
        )
        return top + front + side


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

        # One neutral trihedral protector is reused at all eight topology
        # corners. Its three plates must always wrap the outside corner and
        # extend inward over the three adjacent case faces.
        corner_frame = AnchorFrame(
            origin=(0, 0, 0),
            z=BACK,
            x=DOWN,
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
