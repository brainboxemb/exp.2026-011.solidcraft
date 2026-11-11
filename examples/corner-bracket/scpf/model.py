"""Fast CornerBracket variant: one native countersink per mounting hole.

Temporary GUI-performance experiment.  Unlike the production reference, the
counterbore/recess and the 0.2 mm hole-edge relief cuts are omitted.  The
larger countersink mouth is intentional; it is NOT an exact geometrical
replacement for a flat-bottom recessed screw-head seat.
"""

class CornerBracketFast:
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

    def build(self):
        w = self.wall_thickness
        h = self.horizontal_arm_length
        v = self.vertical_arm_length
        end = self.arm_end_chamfer
        outer = self.outer_corner_chamfer
        ef = self.elephant_foot_relief

        # One named polygon: the actual L profile, without print reliefs.
        # Each name identifies a vertex and the segment starting there.
        profile = Polygon2D([
            ("o_hor_tip", (h, 0)),
            ("o_hor_bevel", (h, w - end)),
            ("o_hor", (h - end, w)),
            ("o_corner", (-w + outer, w)),
            ("o_vert", (-w, w - outer)),
            ("o_vert_bevel", (-w, -v + end)),
            ("o_vert_end", (-w + end, -v)),
            ("v_tip", (0, -v)),
            ("i_corner", (0, 0)),
        ], plane="XZ", world=True)

        body = profile.extrude(self.bracket_width, direction=Direction.SYMMETRIC)

        # Round the inside, then remove printing relief from the two tip
        # edges (parallel to the extrusion direction).
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
        # Inner relief along both broad faces, independent of the 2D outline.
        body = body.chamfer(
            self.elephant_foot_relief,
            edges=Edges.from_profile("i_corner", sides="both"),
        )

        # A single 90-degree countersink avoids coincident circle/face cuts.
        # For 90 degrees, increasing the mouth diameter by 2*recess gives
        # the original head diameter at the intended nominal recess depth.
        # Note: this is a tapered opening, not a flat-bottom counterbore.
        through_d = self.bolt_diameter + self.bolt_clearance
        mouth_d = self.head_diameter + self.head_clearance + 2 * self.head_recess
        first = self.plywood_thickness + self.bolt_offset

        for x in (first, first + self.bolt_spacing):
            body = body + Hole(
                d=through_d,
                countersink_d=mouth_d,
                countersink_angle=90,
                direction=(0, 0, -1),
            ).at(x, self.bolt_y_offset, w)

        for z in (-first, -(first + self.bolt_spacing)):
            body = body + Hole(
                d=through_d,
                depth=w + 1.0,
                countersink_d=mouth_d,
                countersink_angle=90,
                direction=(1, 0, 0),
            ).at(-w, -self.bolt_y_offset, z)

        return body


CornerBracketFast()
