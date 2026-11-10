@dataclass
class SamplePlate:
    """Reproduce the four editable sketches in the original SolidCraft sample."""

    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges=Edges.VERTICAL)

        # Original source history uses a HoleS SKETCH and one extruded cut.
        holes = (
            Circle2D(d=8).at(12, self.depth / 2)
            + Circle2D(d=8).at(self.width - 12, self.depth / 2)
        )
        plate = plate.cut(holes.extrude(self.thickness), name="Holes")

        # Original source history uses a BOSS SKETCH and joined extrusion.
        boss = Circle2D(d=24).at(
            self.width / 2, self.depth / 2, self.thickness
        )
        plate = plate.add(boss.extrude(14), name="Boss")

        # Original source history uses a BORE SKETCH and downward cut.
        bore = Circle2D(d=12).at(
            self.width / 2, self.depth / 2, self.thickness + 14
        )
        plate.cut(
            bore.extrude(self.thickness + 14, direction=Direction.NEGATIVE),
            name="Bore",
        )


SamplePlate()
