class Base:
    width = 40.0

    def build(self):
        return Box(self.width, 30, 10)


class Block:
    def build(self):
        return Box(20, 20, 10)


class ParametricAnchor:
    base_width = 40.0

    def build(self):
        base = Base(width=self.base_width)
        block = Block().attach(
            base,
            parent=Anchor.RIGHT,
            child=Anchor.LEFT,
        )
        return base + block


ParametricAnchor()
