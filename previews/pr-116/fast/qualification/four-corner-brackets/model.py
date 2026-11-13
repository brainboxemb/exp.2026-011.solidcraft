"""Four real HUB75 CornerBracket occurrences on the front corners."""


class FrameBlock:
    _width = 120.0
    _depth = 80.0
    _height = 60.0

    def build(self):
        return Box(self._width, self._depth, self._height)


class Hub75CornerBracket:
    arm_width = 24.0
    arm_height = 12.0
    horizontal_arm_length = 60.0
    vertical_arm_length = 60.0

    outer_corner_chamfer = 6.0
    arm_end_chamfer = 3.0
    side_edge_chamfer = 2.0
    elephant_foot_relief = 0.6
    inside_corner_radius = 4.0

    def build(self):
        w = self.arm_height
        h = self.horizontal_arm_length
        v = self.vertical_arm_length
        end = self.arm_end_chamfer
        outer = self.outer_corner_chamfer

        # Same neutral XZ profile used by the real HUB75 wood-frame model.
        points = [
            ("i_corner", (0, 0)),
            ("o_hor_tip", (h, 0)),
            ("o_hor_bevel", (h, w - end)),
            ("o_hor", (h - end, w)),
            ("o_corner", (-w + outer, w)),
            ("o_vert", (-w, w - outer)),
            ("o_vert_bevel", (-w, -v + end)),
            ("o_vert_end", (-w + end, -v)),
            ("v_tip", (0, -v)),
        ]

        body = Polygon2D(
            points,
            plane="XZ",
            world=True,
        ).extrude(
            self.arm_width,
            direction=Direction.SYMMETRIC,
        )

        body = body.fillet(
            self.inside_corner_radius,
            edges=Edges.from_vertices("i_corner"),
        )
        body = body.chamfer(
            self.elephant_foot_relief,
            edges=Edges.from_vertices("o_hor_tip", "v_tip"),
        )
        body = body.chamfer(
            self.side_edge_chamfer,
            edges=Edges.from_profile("o_*", sides="both"),
        )
        body = body.chamfer(
            self.elephant_foot_relief,
            edges=Edges.from_profile("i_corner", sides="both"),
        )
        return body


class FourHub75CornerBrackets:
    frame_width = 120.0
    frame_depth = 80.0
    frame_height = 60.0

    def build(self):
        frame = FrameBlock(
            _width=self.frame_width,
            _depth=self.frame_depth,
            _height=self.frame_height,
        )
        bracket = Hub75CornerBracket()

        # These are the same mount-A / mount-B datums used by the real
        # HUB75 wood-frame assembly. The component remains placement-neutral.
        w = Hub75CornerBracket.arm_height
        front_mount_a = AnchorFrame(
            origin=(0, 0, -w),
            z=BACK,
            x=DOWN,
        )
        front_mount_b = AnchorFrame(
            origin=(w, 0, 0),
            z=BACK,
            x=DOWN,
        )
        # Positive gap moves the symmetric bracket to the outside of the
        # FRONT face: its rear broad face lands exactly on the cabinet face.
        gap = Hub75CornerBracket.arm_width / 2

        top_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child=front_mount_a,
            gap=gap,
        )
        top_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=front_mount_b,
            gap=gap,
        )
        bottom_right = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=front_mount_a,
            gap=gap,
        )
        bottom_left = bracket.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=front_mount_b,
            gap=gap,
        )

        return frame + top_left + top_right + bottom_right + bottom_left


FourHub75CornerBrackets()
