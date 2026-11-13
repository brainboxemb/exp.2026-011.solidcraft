"""Eight proportional three-face flightcase corner protectors."""


class CaseBlock:
    _width = 320.0
    _depth = 120.0
    _height = 320.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class FlightcaseCorner:
    x_arm = 80.0
    y_arm = 30.0
    z_arm = 80.0
    THICKNESS = 6.0
    OVERLAP = 0.5

    def build(self):
        x_arm = self.x_arm
        y_arm = self.y_arm
        z_arm = self.z_arm
        t = self.THICKNESS
        overlap = self.OVERLAP

        # Canonical FRONT_TOP_LEFT protector: the case extends inward along
        # +X, +Y and -Z. Three plates genuinely wrap the corner.
        top = Box(x_arm, y_arm, t).move(
            x=x_arm / 2,
            y=y_arm / 2,
            z=t / 2,
        )
        front = Box(
            x_arm,
            t + overlap,
            z_arm + overlap,
        ).move(
            x=x_arm / 2,
            y=(overlap - t) / 2,
            z=(overlap - z_arm) / 2,
        )
        side = Box(
            t + overlap,
            y_arm,
            z_arm + overlap,
        ).move(
            x=(overlap - t) / 2,
            y=y_arm / 2,
            z=(overlap - z_arm) / 2,
        )
        return top + front + side


class EightFlightcaseCorners:
    case_width = 320.0
    case_depth = 120.0
    case_height = 320.0

    def build(self):
        case = CaseBlock(
            _width=self.case_width,
            _depth=self.case_depth,
            _height=self.case_height,
        )
        protector = FlightcaseCorner(
            x_arm=self.case_width / 4,
            y_arm=self.case_depth / 4,
            z_arm=self.case_height / 4,
        )

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
