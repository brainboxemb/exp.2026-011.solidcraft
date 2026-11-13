"""Eight simple L-brackets on the eight outer frame corners."""


class FrameBlock:
    _width = 320.0
    _depth = 120.0
    _height = 160.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class CornerBracket:
    ARM_LENGTH = 36.0
    WALL = 8.0
    THICKNESS = 8.0

    def build(self):
        # Qualification geometry only: one plain L polygon in local XZ.
        # The local inside corner at (0, 0, 0) is the attachment datum.
        # The inside corner is (0, 0). Material sits outside the
        # parent corner: +X runs inward over one face, -Z runs inward over
        # the adjacent face, while -X/+Z are the external wall thickness.
        profile = Polygon2D(
            [
                (0, 0),
                (self.ARM_LENGTH, 0),
                (self.ARM_LENGTH, self.WALL),
                (-self.WALL, self.WALL),
                (-self.WALL, -self.ARM_LENGTH),
                (0, -self.ARM_LENGTH),
            ],
            plane="XZ",
        )
        return profile.extrude(
            self.THICKNESS,
            direction=Direction.SYMMETRIC,
        )


class EightCornerBrackets:
    frame_width = 320.0
    frame_depth = 120.0
    frame_height = 160.0

    def build(self):
        frame = FrameBlock(
            _width=self.frame_width,
            _depth=self.frame_depth,
            _height=self.frame_height,
        )
        bracket = CornerBracket()

        bracket_corner = AnchorFrame(
            origin=(0, 0, 0),
            z=FRONT,
            x=RIGHT,
        )

        # Symmetric extrusion plus half-thickness outward gap makes the
        # bracket touch the selected face without floating or cutting through.
        outside_gap = CornerBracket.THICKNESS / 2

        front_top_left = bracket.copy().attach(
            frame, parent=Anchor.FRONT_TOP_LEFT,
            child=bracket_corner, gap=outside_gap,
        )
        front_top_right = bracket.copy().attach(
            frame, parent=Anchor.FRONT_TOP_RIGHT,
            child=bracket_corner, gap=outside_gap,
        )
        front_bottom_right = bracket.copy().attach(
            frame, parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=bracket_corner, gap=outside_gap,
        )
        front_bottom_left = bracket.copy().attach(
            frame, parent=Anchor.FRONT_BOTTOM_LEFT,
            child=bracket_corner, gap=outside_gap,
        )
        rear_top_left = bracket.copy().attach(
            frame, parent=Anchor.BACK_TOP_LEFT,
            child=bracket_corner, gap=outside_gap,
        )
        rear_top_right = bracket.copy().attach(
            frame, parent=Anchor.BACK_TOP_RIGHT,
            child=bracket_corner, gap=outside_gap,
        )
        rear_bottom_right = bracket.copy().attach(
            frame, parent=Anchor.BACK_BOTTOM_RIGHT,
            child=bracket_corner, gap=outside_gap,
        )
        rear_bottom_left = bracket.copy().attach(
            frame, parent=Anchor.BACK_BOTTOM_LEFT,
            child=bracket_corner, gap=outside_gap,
        )

        return (
            frame
            + front_top_left + front_top_right
            + front_bottom_right + front_bottom_left
            + rear_top_left + rear_top_right
            + rear_bottom_right + rear_bottom_left
        )


EightCornerBrackets()
