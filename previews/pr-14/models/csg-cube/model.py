@dataclass
class CsgCube:
    size: float = 50

    def build(self):
        body = Sphere(self.size / 1.5) & Box(self.size, self.size, self.size)
        holes = Cylinder(d=self.size / 1.5, h=self.size).orient(X, Y, Z)
        body - holes


CsgCube()
