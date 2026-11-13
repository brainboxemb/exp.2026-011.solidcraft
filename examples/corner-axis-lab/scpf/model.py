class Parent:
    width = 80.0
    depth = 30.0
    height = 60.0

    def build(self):
        return Box(self.width, self.depth, self.height)


class Marker:
    def build(self):
        return Box(8, 8, 8)


class CornerAxisLab:
    def build(self):
        parent = Parent()

        top_left = Marker(name="top_left").attach(
            parent,
            parent=Anchor.FRONT_TOP_LEFT,
            child=Anchor.BACK_TOP_RIGHT,
        )
        top_right = Marker(name="top_right").attach(
            parent,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=Anchor.BACK_TOP_RIGHT,
        )
        bottom_right = Marker(name="bottom_right").attach(
            parent,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=Anchor.BACK_TOP_RIGHT,
        )
        bottom_left = Marker(name="bottom_left").attach(
            parent,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=Anchor.BACK_TOP_RIGHT,
        )

        return parent + top_left + top_right + bottom_right + bottom_left


CornerAxisLab()
