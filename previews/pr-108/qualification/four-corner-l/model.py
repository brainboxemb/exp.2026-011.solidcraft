"""Four fixed front-corner placements using the minimal L-profile."""


class FrameBlock:
    WIDTH = 120.0
    DEPTH = 30.0
    HEIGHT = 80.0

    def build(self):
        return Box(self.WIDTH, self.DEPTH, self.HEIGHT)


class LBracket:
    WIDTH = 24.0
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
        return profile.extrude(
            self.WIDTH,
            direction=Direction.SYMMETRIC,
        )


class FourCornerL:
    def build(self):
        frame = FrameBlock()
        bracket = LBracket()

        # The neutral L occupies +X and -Z from this local corner. Its
        # attachment normal is +Y. The parent corner frame must rotate those
        # two in-plane directions to the two inward edges at each corner.
        mount = AnchorFrame(
            origin=(0, 0, 0),
            z=(0, 1, 0),
            x=(1, 0, 0),
        )

        top_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=mount,
        )
        top_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=mount,
        )
        bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=mount,
        )
        bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=mount,
        )

        return frame + top_left + top_right + bottom_right + bottom_left


FourCornerL()
