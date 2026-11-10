@dataclass
class Bracket:
    width: float = 60
    thickness: float = 6

    def build(self):
        profile = Polygon(
            [(0, 0), (40, 0), (40, self.thickness),
             (self.thickness, self.thickness),
             (self.thickness, 30), (0, 30)],
            plane="XZ",
        )
        body = profile.extrude(self.width, direction="negative")
        body = body.fillet(2, edges=[(40, -self.width / 2, self.thickness)])
        body.holes([(25, -15), (25, -45)], diameter=8, depth=self.thickness)


Bracket()
