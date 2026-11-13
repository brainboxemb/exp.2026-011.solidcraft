class Base:
    def build(self):
        return Box(40, 30, 20)


class Marker:
    def build(self):
        return Box(10, 10, 10)


class ParametricOffset:
    shift = 5.0

    def build(self):
        base = Base()
        marker = Marker().attach(
            base,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=Anchor.BACK_TOP_RIGHT,
            offset=(0, -self.shift),
        )
        return base + marker


ParametricOffset()
