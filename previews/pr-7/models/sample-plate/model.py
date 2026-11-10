@dataclass
class SamplePlate:
    """Reconstruct the nominal geometry of a saved SolidCraft design."""

    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        # An XY sketch becomes a solid base.
        plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges=Edges.VERTICAL)

        # Two mounting holes follow the original sketch-and-cut history.
        holes = Circle2D(d=8).at(12, 25) + Circle2D(d=8).at(68, 25)
        plate = plate - holes.extrude(self.thickness)

        # Match the source SolidCraft feature history:
        # two more sketches, one for the joined boss and one for the cut bore.
        # Sketch planes remain linked to thickness by a native expression.
        cx, cy = self.width / 2, self.depth / 2

        boss_profile = Circle2D(d=24).at(cx, cy, self.thickness)
        plate = plate + boss_profile.extrude(14)

        bore_profile = Circle2D(d=12).at(cx, cy, self.thickness + 14)
        plate - bore_profile.extrude(
            self.thickness + 14, direction=Direction.NEGATIVE
        )


SamplePlate()
