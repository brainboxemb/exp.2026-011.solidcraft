"""Four reusable L-profiles centred on the four XZ corner lines."""


class FrameBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(
            self._width,
            self._depth,
            self._height,
        ).fillet(8, edges=Edges.VERTICAL)


class LBracket:
    ARM_LENGTH = 28.0
    WALL = 8.0
    THICKNESS = 4.0

    def build(self):
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
        # Symmetric depth makes the profile naturally centre on a corner line.
        return profile.extrude(
            self.THICKNESS,
            direction=Direction.SYMMETRIC,
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

        # Assembly-local XZ plane through Y=0. It survives the rounded outer
        # corners because placement is dimensional, not based on a sharp edge.
        frame_xz = AnchorFrame(
            origin=(0, 0, 0),
            z=Anchor.FRONT,
            x=Anchor.RIGHT,
        )
        bracket_origin = AnchorFrame(
            origin=(0, 0, 0),
            z=Anchor.FRONT,
            x=Anchor.RIGHT,
        )

        half_width = self.frame_width / 2

        top_left = bracket.copy().attach(
            frame,
            parent=frame_xz,
            child=bracket_origin,
            offset=(-half_width, self.frame_height),
            angle=270,
        )
        top_right = bracket.copy().attach(
            frame,
            parent=frame_xz,
            child=bracket_origin,
            offset=(half_width, self.frame_height),
            angle=180,
        )
        bottom_right = bracket.copy().attach(
            frame,
            parent=frame_xz,
            child=bracket_origin,
            offset=(half_width, 0),
            angle=90,
        )
        bottom_left = bracket.copy().attach(
            frame,
            parent=frame_xz,
            child=bracket_origin,
            offset=(-half_width, 0),
            angle=0,
        )

        return frame + top_left + top_right + bottom_right + bottom_left


FourCornerL()
