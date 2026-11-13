"""Four associative front-corner placements using the minimal L-profile."""


class FrameBlock:
    width = 120.0
    DEPTH = 30.0
    height = 80.0

    def build(self):
        return Box(self.width, self.DEPTH, self.height)


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
        # attachment normal faces FRONT. A half-width gap keeps the symmetric
        # extrusion fully outside the frame while its inner face stays flush.
        mount = AnchorFrame(
            origin=(0, 0, 0),
            z=FRONT,
            x=RIGHT,
        )

        top_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=mount,
            gap=LBracket.WIDTH / 2,
            angle=0,
        )
        top_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=mount,
            gap=LBracket.WIDTH / 2,
            angle=0,
        )
        bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=mount,
            gap=LBracket.WIDTH / 2,
            angle=0,
        )
        bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=mount,
            gap=LBracket.WIDTH / 2,
            angle=0,
        )

        return frame + top_left + top_right + bottom_right + bottom_left


FourCornerL()
