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

        # Hole is a native SolidCraft feature; + adds the feature to the model.
        # Two holes at (12, 25) and (68, 25), centered on the plate.
        holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
            count=2, spacing=self.width - 24, axis=Axis.X
        ).on(plate, Anchor.TOP)
        plate = plate + holes

        # Object-level attachment; adapter builds native Boss sketch + join.
        boss = Cylinder(d=24, h=14).attach(
            plate, parent=Anchor.TOP, child=Anchor.BOTTOM)
        plate = plate + boss

        # A native through-hole is placed on the joined boss's top face.
        bore = Hole(d=12, depth=Depth.THROUGH_ALL).on(plate, Anchor.TOP)
        plate + bore


SamplePlate()
