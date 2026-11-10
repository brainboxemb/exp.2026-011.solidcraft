@dataclass
class AnchoredHoles:
    """Two through holes, each 20 mm from the center along the Y axis."""

    width: float = 100
    depth: float = 60
    thickness: float = 10
    spacing: float = 40

    def build(self):
        plate = Rectangle2D(self.width, self.depth).extrude(self.thickness)
        holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
            count=2, spacing=self.spacing, axis=Axis.Y
        ).attach(plate, parent=Anchor.TOP)
        plate + holes


AnchoredHoles()
