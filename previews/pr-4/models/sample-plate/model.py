@dataclass
class SamplePlate:
    """Reconstruct the nominal geometry of a saved SolidCraft design."""

    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        # An XY sketch becomes a solid base.
        plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges="vertical")

        # Two mounting holes follow the original sketch-and-cut history.
        holes = Circle2D(d=8).at(12, 25) + Circle2D(d=8).at(68, 25)
        plate = plate - holes.extrude(self.thickness)

        # Direct 3D primitives; SolidCraft emits solid.cylinder, not a sketch.
        boss = Cylinder3D(d=24, h=14).at(40, 25, self.thickness)
        plate = plate + boss

        # Its base is at z=0; the full 22 mm height is removed.
        bore = Cylinder3D(d=12, h=self.thickness + 14).at(40, 25, 0)
        plate - bore


SamplePlate()
