"""Eight reusable L-profiles: two on each XZ corner line."""


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
        return profile.extrude(
            self.THICKNESS,
            direction=Direction.SYMMETRIC,
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
        depth_position = self.frame_depth / 2 - LBracket.THICKNESS / 2

        def placed(x, z, angle, gap):
            return bracket.copy().attach(
                frame,
                parent=frame_xz,
                child=bracket_origin,
                offset=(x, z),
                gap=gap,
                angle=angle,
            )

        # Positive gap follows the frame normal (FRONT / -Y); negative gap
        # reaches the rear side. Each pair therefore belongs to one XZ corner.
        top_left_front = placed(-half_width, self.frame_height, 270, depth_position)
        top_left_rear = placed(-half_width, self.frame_height, 270, -depth_position)

        top_right_front = placed(half_width, self.frame_height, 180, depth_position)
        top_right_rear = placed(half_width, self.frame_height, 180, -depth_position)

        bottom_right_front = placed(half_width, 0, 90, depth_position)
        bottom_right_rear = placed(half_width, 0, 90, -depth_position)

        bottom_left_front = placed(-half_width, 0, 0, depth_position)
        bottom_left_rear = placed(-half_width, 0, 0, -depth_position)

        return (
            frame
            + top_left_front + top_left_rear
            + top_right_front + top_right_rear
            + bottom_right_front + bottom_right_rear
            + bottom_left_front + bottom_left_rear
        )


EightCornerBrackets()
