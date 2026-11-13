"""Four associative front-corner placements using the minimal L-profile."""


class FrameBlock:
    width = 120.0
    DEPTH = 30.0
    height = 80.0

    def build(self):
        return Box(self.width, self.DEPTH, self.height)


class LBracket:
    THICKNESS = 4.0
    ARM_LENGTH = 40.0
    ARM_HEIGHT = 12.0

    def build(self):
        profile = Polygon2D(
            [
                (0, 0),
                (self.ARM_LENGTH, 0),
                (self.ARM_LENGTH, self.ARM_HEIGHT),
                (self.ARM_HEIGHT, self.ARM_HEIGHT),
                (self.ARM_HEIGHT, self.ARM_LENGTH),
                (0, self.ARM_LENGTH),
            ],
            plane="XZ",
        )
        # The bracket is a flat plate on the outside of the front face.
        # Its attachment frame points toward -Y, so a negative extrusion keeps
        # the complete 4 mm plate outside the parent instead of straddling it.
        return profile.extrude(
            self.THICKNESS,
            direction=Direction.NEGATIVE,
        )


class FourCornerL:
    def build(self):
        frame = FrameBlock()
        bracket = LBracket()

        # The neutral L occupies +X and -Z from this local corner. Its
        # attachment frame points toward the front (-Y). At every parent
        # corner the complete plate must remain outside the front face while
        # the two L arms run inward along the frame edges.
        mount = AnchorFrame(
            origin=(0, 0, 0),
            z=(0, -1, 0),
            x=(1, 0, 0),
        )

        top_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=mount,
            angle=0,
        )
        top_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=mount,
            angle=0,
        )
        bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=mount,
            angle=0,
        )
        bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=mount,
            angle=0,
        )

        return frame + top_left + top_right + bottom_right + bottom_left


FourCornerL()
