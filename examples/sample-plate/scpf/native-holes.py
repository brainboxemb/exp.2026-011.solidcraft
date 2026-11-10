@dataclass
class SamplePlateNativeHoles:
    """A shorter SolidCraft-native feature history, with editable Hole features."""

    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges=Edges.VERTICAL)

        plate = plate.add(
            Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
                count=2, spacing=self.width - 24, axis=Axis.X),
            on=Anchor.TOP,
        )
        plate = plate.add(Cylinder(d=24, h=14), on=Anchor.TOP)
        plate = plate.add(Hole(d=12, depth=Depth.THROUGH_ALL), on=Anchor.TOP)
        plate


SamplePlateNativeHoles()
