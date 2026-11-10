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

        # Consecutive points describe the seven outer edges to bevel.
        # These are also used by the sketch: one source of geometry.
        outer_path_xz = [
            (h, ef),
            (h, w - end),
            (h - end, w),
            (-w + outer, w),
            (-w, w - outer),
            (-w, -v + end),
            (-w + end, -v),
            (-ef, -v),
        ]
        # SolidCraft's XZ sketch local vertical axis points toward world -Z.
        outline_xz = [
            (h - ef, 0),
            *outer_path_xz,
            (0, -v + ef),
            (0, 0),
        ]
        profile = Polygon2D([(x, -z) for x, z in outline_xz], plane="XZ")
        body = profile.extrude(self.bracket_width, direction=Direction.SYMMETRIC)
        body = body.fillet(self.inside_corner_radius, edges=[(0, 0, 0)])

        y0 = self.bracket_width / 2
        # SolidCraft's chamfer command currently selects an edge by a
        # point on it. Derive those points from the sketch path instead
        # of duplicating seven coordinate formulas in the model.
        outer_edges = [
            ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            for a, b in zip(outer_path_xz, outer_path_xz[1:])
        ]
        body = body.chamfer(
            self.side_edge_chamfer,
            edges=[
                (x, side * y0, z)
                for side in (-1, 1)
                for x, z in outer_edges
            ],
        )
        body = body.chamfer(
            self.elephant_foot_relief,
            edges=[(h / 2, -y0, 0), (h / 2, y0, 0)],
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

        body


CornerBracketFast()
