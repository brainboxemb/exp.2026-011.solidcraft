"""Four reusable outside L-brackets on the front corners of a frame."""


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
        # Neutral reusable component in its own local XZ plane.
        # Placement/orientation belongs entirely to the assembly.
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


class FourCornerBrackets:
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

        bracket_corner = AnchorFrame(
            origin=(0, 0, 0),
            z=FRONT,
            x=RIGHT,
        )

        top_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=bracket_corner,
        )
        top_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=bracket_corner,
        )
        bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=bracket_corner,
        )
        bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=bracket_corner,
        )

        return frame + top_left + top_right + bottom_right + bottom_left


FourCornerBrackets()
