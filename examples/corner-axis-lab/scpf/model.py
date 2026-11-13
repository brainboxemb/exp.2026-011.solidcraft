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

        front_top_left = Marker(name="front_top_left").attach(
            parent,
            parent=Anchor.FRONT_TOP_LEFT,
            child=Anchor.BACK_TOP_RIGHT,
        )
        front_top_right = Marker(name="front_top_right").attach(
            parent,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=Anchor.BACK_TOP_RIGHT,
        )
        front_bottom_right = Marker(name="front_bottom_right").attach(
            parent,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child=Anchor.BACK_TOP_RIGHT,
        )
        front_bottom_left = Marker(name="front_bottom_left").attach(
            parent,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child=Anchor.BACK_TOP_RIGHT,
        )

        back_top_left = Marker(name="back_top_left").attach(
            parent,
            parent=Anchor.BACK_TOP_LEFT,
            child=Anchor.FRONT_TOP_RIGHT,
        )
        back_top_right = Marker(name="back_top_right").attach(
            parent,
            parent=Anchor.BACK_TOP_RIGHT,
            child=Anchor.FRONT_TOP_RIGHT,
        )
        back_bottom_right = Marker(name="back_bottom_right").attach(
            parent,
            parent=Anchor.BACK_BOTTOM_RIGHT,
            child=Anchor.FRONT_TOP_RIGHT,
        )
        back_bottom_left = Marker(name="back_bottom_left").attach(
            parent,
            parent=Anchor.BACK_BOTTOM_LEFT,
            child=Anchor.FRONT_TOP_RIGHT,
        )

        return (
            parent
            + front_top_left
            + front_top_right
            + front_bottom_right
            + front_bottom_left
            + back_top_left
            + back_top_right
            + back_bottom_right
            + back_bottom_left
        )


CornerAxisLab()
