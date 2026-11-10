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

        # The adapter places a circle sketch on the plate's top face,
        # then makes a native join extrusion (Boss).
        boss = Cylinder(d=24, h=14).attach(
            plate, parent=Anchor.TOP, child=Anchor.BOTTOM)
        plate = plate + boss

        # Cut from the top down through both boss and plate (Bore).
        bore = Cylinder(d=12, h=self.thickness + 14).attach(
            plate, parent=Anchor.BOTTOM, child=Anchor.BOTTOM)
        plate - bore


SamplePlate()
