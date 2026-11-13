"""Eight reusable three-face flightcase corners on a rectangular frame."""


class FrameBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class FlightcaseCorner:
    ARM_LENGTH = 28.0
    THICKNESS = 4.0

    def build(self):
        arm = self.ARM_LENGTH
        wall = self.THICKNESS
        overlap = 1.0

        # Local mount point is (0, 0, 0).
        #
        # +X and +Z run inward along the two visible frame edges.
        # +Y points outward from the front/rear face.
        #
        # The plates overlap by 1 mm around the local corner. Their external
        # envelope is still exactly x=[-4,28], y=[-28,4], z=[-4,28], but the
        # native union has real volume at every join instead of zero-thickness
        # edge contact.
        face_plate = Box(
            arm + overlap,
            wall + overlap,
            arm + overlap,
        ).move(
            x=(arm - overlap) / 2,
            y=(wall - overlap) / 2,
            z=(arm - overlap) / 2,
        )
        horizontal_plate = Box(
            arm + overlap,
            arm + overlap,
            wall + overlap,
        ).move(
            x=(arm - overlap) / 2,
            y=(overlap - arm) / 2,
            z=(overlap - wall) / 2,
        )
        side_plate = Box(
            wall + overlap,
            arm + overlap,
            arm + overlap,
        ).move(
            x=(overlap - wall) / 2,
            y=(overlap - arm) / 2,
            z=(arm - overlap) / 2,
        )

        return face_plate + horizontal_plate + side_plate


class EightFlightcaseCorners:
    frame_width = 120.0
    frame_depth = 80.0
    frame_height = 60.0

    def build(self):
        frame = FrameBlock(
            _width=self.frame_width,
            _depth=self.frame_depth,
            _height=self.frame_height,
        )
        corner = FlightcaseCorner()

        mount = AnchorFrame(
            origin=(0, 0, 0),
            z=FRONT,
            x=UP,
        )

        front_top_left = corner.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=mount,
        )
        front_top_right = corner.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=mount,
        )
        front_bottom_right = corner.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=mount,
        )
        front_bottom_left = corner.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=mount,
        )

        rear_top_left = corner.copy().attach(
            frame,
            parent=Anchor.BACK_TOP_LEFT,
            child=mount,
        )
        rear_top_right = corner.copy().attach(
            frame,
            parent=Anchor.BACK_TOP_RIGHT,
            child=mount,
        )
        rear_bottom_right = corner.copy().attach(
            frame,
            parent=Anchor.BACK_BOTTOM_RIGHT,
            child=mount,
        )
        rear_bottom_left = corner.copy().attach(
            frame,
            parent=Anchor.BACK_BOTTOM_LEFT,
            child=mount,
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


EightFlightcaseCorners()
