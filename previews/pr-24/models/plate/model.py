@dataclass
class Plate:
    length: float = 100
    width: float = 60
    thickness: float = 10

    def build(self):
        body = Box(self.length, self.width, self.thickness)
        body = body.fillet(2, edges=Edges.VERTICAL)

        # Explicit world positions keep this compact comparison model simple.
        for x, y in ((-35, -15), (35, -15), (35, 15), (-35, 15)):
            body = body + Hole(
                d=8, depth=Depth.THROUGH_ALL
            ).at(x, y, self.thickness)
        body


Plate()
