@dataclass
class SamplePlate:
    """Reconstructed from the saved SolidCraft Sample Plate design."""

    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        # Base: one XY rectangle, extruded upward, with four R6 corners.
        plate = Rectangle(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges="vertical")

        # The two mounting holes are ordinary circles on the XY plane.
        holes = Circle(d=8).at(12, 25) + Circle(d=8).at(68, 25)
        plate = plate - holes.extrude(self.thickness)

        # Another circle, positioned on top of the plate and joined.
        boss = Circle(d=24).at(40, 25, z=self.thickness)
        plate = plate + boss.extrude(14)

        # A circle on top of the boss, extruded down through both solids.
        bore = Circle(d=12).at(40, 25, z=self.thickness + 14)
        plate - bore.extrude(self.thickness + 14, direction="negative")


SamplePlate()
