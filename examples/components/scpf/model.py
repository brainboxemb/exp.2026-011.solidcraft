class Block:
    length = 40.0
    width = 30.0
    height = 10.0

    def build(self):
        Box(self.length, self.width, self.height)


class TwoBlocks:
    def build(self):
        left = Block()
        right = Block().attach(
            left,
            parent=Anchor.RIGHT,
            child=Anchor.LEFT,
        )

        left + right


TwoBlocks()
