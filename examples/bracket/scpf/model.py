@dataclass
class Bracket:
    width: float = 60
    thickness: float = 6

    def build(self):
        profile = Polygon2D(
            [(0, 0), (40, 0), (40, self.thickness),
             (self.thickness, self.thickness),
             (self.thickness, 30), (0, 30)],
            plane="XZ",
        )
        body = profile.extrude(self.width, direction=Direction.NEGATIVE)
        body = body.fillet(2, edges=[(40, -self.width / 2, -self.thickness)])
        # Native Hole features on the upper face (world Z = 0).
        # The XZ profile grows towards negative Z in SolidCraft.
        for y in (-15, -45):
            body = body.add(
                Hole(d=8, depth=self.thickness), at=(25, y, 0))
        body


Bracket()
