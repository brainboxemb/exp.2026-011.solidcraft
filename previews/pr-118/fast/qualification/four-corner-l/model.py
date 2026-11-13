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

        # Placement belongs to this assembly. All four frames use the same
        # local origin and Z direction; only local X changes to express the
        # required clocking. The reusable CornerFoot itself remains neutral.
        bottom_frame = AnchorFrame(
            origin=(0, 0, 0),
            z=DOWN,
            x=FRONT,
        )

        front_left_origin = AnchorFrame(
            origin=(0, 0, 0),
            z=UP,
            x=FRONT,
        )
        front_right_origin = AnchorFrame(
            origin=(0, 0, 0),
            z=UP,
            x=LEFT,
        )
        back_right_origin = AnchorFrame(
            origin=(0, 0, 0),
            z=UP,
            x=BACK,
        )
        back_left_origin = AnchorFrame(
            origin=(0, 0, 0),
            z=UP,
            x=RIGHT,
        )

        half_width = self.frame_width / 2
        half_depth = self.frame_depth / 2

        # SolidCraft's BOTTOM frame uses local X along world -Y and local Y
        # along world -X. Express the four positions in that local (u, v)
        # frame; no extra joint angle is required.
        front_left = foot.copy().attach(
            frame,
            parent=bottom_frame,
            child=front_left_origin,
            offset=(half_depth, half_width),
        )
        front_right = foot.copy().attach(
            frame,
            parent=bottom_frame,
            child=front_right_origin,
            offset=(half_depth, -half_width),
        )
        back_right = foot.copy().attach(
            frame,
            parent=bottom_frame,
            child=back_right_origin,
            offset=(-half_depth, -half_width),
        )
        back_left = foot.copy().attach(
            frame,
            parent=bottom_frame,
            child=back_left_origin,
            offset=(-half_depth, half_width),
        )

        return frame + front_left + front_right + back_right + back_left


FourCornerL()
