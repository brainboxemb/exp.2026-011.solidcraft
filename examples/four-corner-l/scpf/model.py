"""Four reusable L-profiles centred on the four XZ corner lines."""


class FrameBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class LBracket:
    ARM_LENGTH = 28.0
    WALL = 8.0
    THICKNESS = 4.0

    def build(self):
        # Neutral reusable L-profile in its local XZ plane.
        profile = Polygon2D(
            [
                (0, 0),
                (self.ARM_LENGTH, 0),
                (self.ARM_LENGTH, self.WALL),
                (self.WALL, self.WALL),
                (self.WALL, self.ARM_LENGTH),
                (0, self.ARM_LENGTH),
            ],
            plane="XZ",
        )
        return profile.extrude(
            self.THICKNESS,
            direction=Direction.POSITIVE,
        )


class FourCornerL:
    frame_width = 120.0
    frame_depth = 80.0
    frame_height = 60.0

    def build(self):
        frame = FrameBlock(
            _width=self.frame_width,
            _depth=self.frame_depth,
            _height=self.frame_height,
        )
        bracket = LBracket()

        # Use the same neutral child frame as the eight-profile case.
        bracket_corner = AnchorFrame(
            origin=(0, 0, 0),
            z=Anchor.FRONT,
            x=Anchor.RIGHT,
        )

        # The FRONT topology gives us the four XZ corner identities. A
        # parametric negative gap then moves each profile along that corner
        # line to the middle of the frame depth. The profile's 4 mm extrusion
        # is centred around Y=0.
        centre_gap = -(self.frame_depth / 2 + LBracket.THICKNESS / 2)

        top_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=bracket_corner,
            gap=centre_gap,
        )
        top_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=bracket_corner,
            gap=centre_gap,
        )
        bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=bracket_corner,
            gap=centre_gap,
        )
        bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=bracket_corner,
            gap=centre_gap,
        )

        return frame + top_left + top_right + bottom_right + bottom_left


FourCornerL()
