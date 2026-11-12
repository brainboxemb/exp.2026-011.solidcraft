class Block:
    def build(self):
        return Box(40, 30, 10)


class JointGap:
    gap = 10.0

    def build(self):
        left = Block()
        right = Block().attach(
            left,
            parent=Anchor.RIGHT,
            child=Anchor.LEFT,
            gap=self.gap,
        )
        return left + right


JointGap()
