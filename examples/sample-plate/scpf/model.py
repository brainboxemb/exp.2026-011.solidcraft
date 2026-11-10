@dataclass
class SamplePlate:
    """80 x 50 x 8 plate, rounded corners, two holes and a raised boss."""

    width: float = 80
    depth: float = 50
    thickness: float = 8

    def build(self):
        # Source feature 1-3: XY footprint, extrusion, four R6 corners.
        plate = Rectangle(self.width, self.depth).extrude(self.thickness)
        plate = plate.fillet(6, edges="vertical")

        # Source features 4-5: two through-holes, each diameter 8.
        plate = plate.holes([(12, 25), (68, 25)],
                            diameter=8, depth=self.thickness)

        # Source features 6-7: circular boss starts on top of base.
        plate = plate.boss(center=(40, 25), diameter=24, height=14)

        # Source features 8-9: bore from boss top through base.
        plate.bore(center=(40, 25), diameter=12)


SamplePlate()
