class Base:
    def build(self):
        return Box(40, 30, 10)


class Block:
    def build(self):
        return Box(20, 20, 10)


class ParametricAttach:
    gap = 10.0

    def build(self):
        base = Base()
        block = Block().attach(
            base,
            parent=Anchor.RIGHT,
            child=Anchor.LEFT,
            gap=self.gap,
        )
        return base + block


ParametricAttach()
