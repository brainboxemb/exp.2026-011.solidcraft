"""Eight reusable L-brackets mounted outside a rectangular frame."""


class FrameBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(self._width, self._depth, self._height).fillet(8, edges=Edges.VERTICAL)


class LBracket:
    ARM_LENGTH = 28.0
    WALL = 8.0
    THICKNESS = 4.0

    def build(self):
        # Neutral reusable component in its own local XZ plane.
        # The profile starts at its local corner and the material is extruded
        # in local +Y. It has no front/rear/top/bottom frame knowledge.
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


class EightCornerBrackets:
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

        # Placement belongs to this assembly. Think in four XZ corner lines:
        # each line receives two occurrences, one near each end of the depth.
        # The FRONT/BACK topology identifies those ends, while a negative gap
        # moves the 4 mm profile inward so it sits on the side/corner line
        # rather than outside the front or rear face.
        bracket_corner = AnchorFrame(
            origin=(0, 0, 0),
            z=Anchor.FRONT,
            x=Anchor.RIGHT,
        )

        front_top_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )
        front_top_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )
        front_bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )
        front_bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )

        rear_top_left = bracket.copy().attach(
            frame,
            parent=Anchor.BACK_TOP_LEFT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )
        rear_top_right = bracket.copy().attach(
            frame,
            parent=Anchor.BACK_TOP_RIGHT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )
        rear_bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.BACK_BOTTOM_RIGHT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )
        rear_bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.BACK_BOTTOM_LEFT,
            child=bracket_corner,
            gap=-LBracket.THICKNESS,
        )

        return (
            frame
            + front_top_left
            + front_top_right
            + front_bottom_right
            + front_bottom_left
            + rear_top_left
            + rear_top_right
            + rear_bottom_right
            + rear_bottom_left
        )


EightCornerBrackets()
