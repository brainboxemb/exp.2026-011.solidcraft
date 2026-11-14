@dataclass
class AnchoredHoles:
    """Two through holes, each 20 mm from the center along the Y axis."""

    width: float = 100
    depth: float = 60
    thickness: float = 10
    spacing: float = 40

    def build(self):
        with Sketch(name="Base", plane="XY") as sketch:
            Rectangle2D(self.width, self.depth)
        plate = sketch.extrude(self.thickness)
        holes = Hole(d=8, depth=Depth.THROUGH_ALL).pattern(
            count=2, spacing=self.spacing, axis=Axis.Y
        ).on(plate, face=Faces.TOP)
        plate + holes


AnchoredHoles()
