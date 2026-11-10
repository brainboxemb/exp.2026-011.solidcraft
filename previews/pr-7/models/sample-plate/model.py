@dataclass
class SamplePlate:
    """Build the sample plate from object-level CAD intent."""

    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges=Edges.VERTICAL)

        holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
            count=2,
            spacing=self.width - 24,
            axis=Axis.X,
        ).attach(plate, parent=Anchor.TOP)
        plate = plate + holes

        boss = Cylinder(d=24, h=14).attach(
            plate,
            parent=Anchor.TOP,
            child=Anchor.BOTTOM,
        )
        plate = plate + boss

        bore = Hole(d=12, depth=Depth.THROUGH_ALL).attach(
            plate,
            parent=Anchor.TOP,
        )
        plate + bore


SamplePlate()
