"""Four vertical L-profiles centred on the four rounded side corners."""


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


class LProfile:
    ARM_LENGTH = 28.0
    THICKNESS = 4.0
    PROFILE_HEIGHT = 16.0

    def build(self):
        # A real angle profile around a vertical corner. Local +X/+Y is the
        # inside of the case; material sits just outside those two faces.
        profile = Polygon2D(
            [
                (0, 0),
                (self.ARM_LENGTH, 0),
                (self.ARM_LENGTH, -self.THICKNESS),
                (-self.THICKNESS, -self.THICKNESS),
                (-self.THICKNESS, self.ARM_LENGTH),
                (0, self.ARM_LENGTH),
            ],
            plane="XY",
        )
        return profile.extrude(
            self.PROFILE_HEIGHT,
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
        profile = LProfile()

        frame_xy = AnchorFrame(
            origin=(0, 0, 0),
            z=Anchor.UP,
            x=Anchor.RIGHT,
        )
        profile_origin = AnchorFrame(
            origin=(0, 0, 0),
            z=Anchor.UP,
            x=Anchor.RIGHT,
        )

        half_width = self.frame_width / 2
        half_depth = self.frame_depth / 2
        centre_height = (
            self.frame_height - LProfile.PROFILE_HEIGHT
        ) / 2

        front_left = profile.copy().attach(
            frame,
            parent=frame_xy,
            child=profile_origin,
            offset=(-half_width, -half_depth),
            gap=centre_height,
            angle=180,
        )
        front_right = profile.copy().attach(
            frame,
            parent=frame_xy,
            child=profile_origin,
            offset=(half_width, -half_depth),
            gap=centre_height,
            angle=270,
        )
        rear_right = profile.copy().attach(
            frame,
            parent=frame_xy,
            child=profile_origin,
            offset=(half_width, half_depth),
            gap=centre_height,
            angle=0,
        )
        rear_left = profile.copy().attach(
            frame,
            parent=frame_xy,
            child=profile_origin,
            offset=(-half_width, half_depth),
            gap=centre_height,
            angle=90,
        )

        return frame + front_left + front_right + rear_right + rear_left


FourCornerL()
