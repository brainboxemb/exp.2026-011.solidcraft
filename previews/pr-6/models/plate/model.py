@dataclass
class Plate:
    length: float = 100
    width: float = 60
    thickness: float = 10

    def build(self):
        body = Box(self.length, self.width, self.thickness).fillet(
            2, edges=Edges.VERTICAL
        )
        holes = Cylinder(d=8, h=self.thickness).pattern(x=70, y=30)
        body - holes


Plate()
