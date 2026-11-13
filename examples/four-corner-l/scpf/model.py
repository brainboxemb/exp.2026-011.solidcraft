"""Four reusable L-profile feet mounted under one rectangular frame."""


class FrameBlock:
    _width = 120.0
    _depth = 80.0
    HEIGHT = 60.0

    def build(self):
        return Box(self._width, self._depth, self.HEIGHT)


class CornerFoot:
    ARM_LENGTH = 28.0
    WALL = 8.0
    HEIGHT = 30.0

    def build(self):
        # Neutral reusable component.
        #
        # The local origin is the outside top corner of the foot.
        # The L-shaped footprint extends in local +X/+Y and the foot extends
        # downwards in local -Z. It has no knowledge of the frame or of which
        # of the four frame corners it will occupy.
        footprint = Polygon2D(
            [
                (0, 0),
                (self.ARM_LENGTH, 0),
                (self.ARM_LENGTH, self.WALL),
                (self.WALL, self.WALL),
                (self.WALL, self.ARM_LENGTH),
                (0, self.ARM_LENGTH),
            ],
            plane="XY",
        )
        return footprint.extrude(
            self.HEIGHT,
            direction=Direction.NEGATIVE,
        )


class FourCornerL:
    frame_width = 120.0
    frame_depth = 80.0

    def build(self):
        frame = FrameBlock(
            _width=self.frame_width,
            _depth=self.frame_depth,
        )
        foot = CornerFoot()

        # The assembly chooses the attachment point and orientation.
        # CornerFoot itself stays completely placement-agnostic.
        foot_origin = AnchorFrame(
            origin=(0, 0, 0),
            z=UP,
            x=RIGHT,
        )

        half_width = self.frame_width / 2
        half_depth = self.frame_depth / 2

        # SolidCraft's native BOTTOM frame uses local X along world -Y and
        # local in-plane Y along world -X.  offset=(u, v) is deliberately
        # expressed in that local frame, not as world X/Y coordinates.
        foot_origin_reversed = AnchorFrame(
            origin=(0, 0, 0),
            z=UP,
            x=LEFT,
        )

        front_left = foot.copy().attach(
            frame,
            parent=Anchor.BOTTOM,
            child=foot_origin,
            offset=(half_depth, half_width),
            angle=90,
        )
        front_right = foot.copy().attach(
            frame,
            parent=Anchor.BOTTOM,
            child=foot_origin,
            offset=(half_depth, -half_width),
            angle=180,
        )
        back_right = foot.copy().attach(
            frame,
            parent=Anchor.BOTTOM,
            child=foot_origin_reversed,
            offset=(-half_depth, -half_width),
            angle=90,
        )
        back_left = foot.copy().attach(
            frame,
            parent=Anchor.BOTTOM,
            child=foot_origin,
            offset=(-half_depth, half_width),
            angle=0,
        )

        return frame + front_left + front_right + back_right + back_left


FourCornerL()
