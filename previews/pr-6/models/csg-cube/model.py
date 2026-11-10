@dataclass
class CsgCube:
    size: float = 50

    def build(self):
        body = Sphere(self.size / 1.5) & Cube(self.size)
        holes = Cylinder(d=self.size / 1.5, h=self.size).orient(X, Y, Z)
        body - holes


CsgCube()
