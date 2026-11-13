"""Eight asymmetric 3D flightcase corner protectors around one case."""


class CaseBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class FlightcaseCorner:
    # Deliberately unequal arms make every 3D orientation observable.
    X_ARM = 36.0
    Y_ARM = 28.0
    Z_ARM = 24.0
    THICKNESS = 8.0

    def build(self):
        t = self.THICKNESS
        x_arm = Box(self.X_ARM, t, t).move(
            x=self.X_ARM / 2,
            z=-(t / 2),
        )
        y_arm = Box(t, self.Y_ARM, t).move(
            y=self.Y_ARM / 2,
            z=-(t / 2),
        )
        z_arm = Box(t, t, self.Z_ARM)
        return x_arm + y_arm + z_arm


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

        # One neutral 3D protector is reused at all eight topology corners.
        # The unequal arms make accidental mirroring or clocking visible.
        corner_frame = AnchorFrame(
            origin=(0, 0, 0),
            z=FRONT,
            x=RIGHT,
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
