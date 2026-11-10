class CornerBracket:
    bracket_width = 24.0
    wall_thickness = 12.0
    horizontal_arm_length = 60.0
    vertical_arm_length = 60.0

    outer_corner_chamfer = 6.0
    arm_end_chamfer = 3.0
    side_edge_chamfer = 2.0

    elephant_foot_relief = 0.6
    inside_corner_radius = 4.0

    plywood_thickness = 12.0
    bolt_offset = 12.0
    bolt_spacing = 18.0
    bolt_y_offset = 0.0

    bolt_diameter = 5.0
    bolt_clearance = 0.4
    head_diameter = 10.0
    head_clearance = 0.4
    head_recess = 1.0
    bolt_hole_edge_relief = 0.2

    def build(self):
        w = self.wall_thickness
        h = self.horizontal_arm_length
        v = self.vertical_arm_length
        end = self.arm_end_chamfer
        outer = self.outer_corner_chamfer
        ef = self.elephant_foot_relief

        # Same X/Z outline as the OpenSCAD production model. The tiny
        # elephant-foot bevels at the two arm end faces belong to this profile.
        profile = Polygon2D(
            [
                (h - ef, 0),
                (h, ef),
                (h, w - end),
                (h - end, w),
                (-w + outer, w),
                (-w, w - outer),
                (-w, -v + end),
                (-w + end, -v),
                (-ef, -v),
                (0, -v + ef),
                (0, 0),
            ],
            plane="XZ",
        )

        body = profile.extrude(
            self.bracket_width,
            direction=Direction.SYMMETRIC,
        )

        # Round the concave plywood corner.
        body = body.fillet(
            self.inside_corner_radius,
            edges=[(0, 0, 0)],
        )

        # Bevel only the outside perimeter on both broad print faces.
        y0 = self.bracket_width / 2
        outer_edges = [
            (h, (ef + w - end) / 2),
            (h - end / 2, w - end / 2),
            ((h - end - w + outer) / 2, w),
            (-w + outer / 2, w - outer / 2),
            (-w, (w - outer - v + end) / 2),
            (-w + end / 2, -v + end / 2),
            ((-w + end - ef) / 2, -v),
        ]
        body = body.chamfer(
            self.side_edge_chamfer,
            edges=[
                (x, side * y0, z)
                for side in (-1, 1)
                for x, z in outer_edges
            ],
        )

        # One pick per broad face selects the complete tangent inside chain:
        # horizontal contact edge -> rounded corner -> vertical contact edge.
        body = body.chamfer(
            self.elephant_foot_relief,
            edges=[
                (h / 2, -y0, 0),
                (h / 2, y0, 0),
            ],
        )

        through_d = self.bolt_diameter + self.bolt_clearance
        head_d = self.head_diameter + self.head_clearance
        outside_relief_d = head_d + 2 * self.bolt_hole_edge_relief
        inside_relief_d = through_d + 2 * self.bolt_hole_edge_relief

        first = self.plywood_thickness + self.bolt_offset
        top_x = (first, first + self.bolt_spacing)
        vertical_z = (-first, -(first + self.bolt_spacing))

        # Two countersunk M5 holes through the horizontal arm.
        for x in top_x:
            hole = Hole(
                d=through_d,
                countersink_d=head_d,
                countersink_angle=90,
                countersink_recess=self.head_recess,
                direction=(0, 0, -1),
            ).at(x, self.bolt_y_offset, w)
            body = body + hole

            body = body + Hole(
                d=outside_relief_d,
                depth=self.bolt_hole_edge_relief,
                direction=(0, 0, -1),
            ).at(x, self.bolt_y_offset, w)
            body = body + Hole(
                d=inside_relief_d,
                depth=self.bolt_hole_edge_relief,
                direction=(0, 0, 1),
            ).at(x, self.bolt_y_offset, 0)

        # Two matching holes through the vertical arm.
        for z in vertical_z:
            hole = Hole(
                d=through_d,
                countersink_d=head_d,
                countersink_angle=90,
                countersink_recess=self.head_recess,
                direction=(1, 0, 0),
            ).at(-w, -self.bolt_y_offset, z)
            body = body + hole

            body = body + Hole(
                d=outside_relief_d,
                depth=self.bolt_hole_edge_relief,
                direction=(1, 0, 0),
            ).at(-w, -self.bolt_y_offset, z)
            body = body + Hole(
                d=inside_relief_d,
                depth=self.bolt_hole_edge_relief,
                direction=(-1, 0, 0),
            ).at(0, -self.bolt_y_offset, z)

        body


CornerBracket()
