from scpf import assembly


class Parent:
    width = 80.0
    depth = 30.0
    height = 60.0

    def build(self):
        return Box(self.width, self.depth, self.height)


class Helper:
    def build(self):
        return Box(1, 1, 1)


class Marker:
    def build(self):
        return Box(8, 8, 8)


@assembly
class NormalizedFrame:
    def build(self):
        parent = Parent(name="parent")
        helper = Helper(name="helper").attach(parent, as_built=True)
        frame = parent + helper

        for name, anchor, rotation in (
            ("front_top_left", Anchor.FRONT_TOP_LEFT, 180),
            ("front_top_right", Anchor.FRONT_TOP_RIGHT, -90),
            ("front_bottom_right", Anchor.FRONT_BOTTOM_RIGHT, 0),
            ("front_bottom_left", Anchor.FRONT_BOTTOM_LEFT, 90),
            ("back_top_left", Anchor.BACK_TOP_LEFT, -90),
            ("back_top_right", Anchor.BACK_TOP_RIGHT, 180),
            ("back_bottom_right", Anchor.BACK_BOTTOM_RIGHT, 90),
            ("back_bottom_left", Anchor.BACK_BOTTOM_LEFT, 0),
        ):
            frame = frame.with_anchor(
                name,
                parent,
                anchor,
                rotation=rotation,
            )

        return frame


class NormalizedCornerAnchorLab:
    def build(self):
        frame = NormalizedFrame()
        result = frame

        for name in (
            "front_top_left",
            "front_top_right",
            "front_bottom_right",
            "front_bottom_left",
            "back_top_left",
            "back_top_right",
            "back_bottom_right",
            "back_bottom_left",
        ):
            anchor = frame.anchor(name)
            child = (
                Anchor.BACK_TOP_RIGHT
                if name.startswith("front_")
                else Anchor.FRONT_TOP_RIGHT
            )
            marker = Marker(name=name).attach(
                anchor.target,
                parent=anchor.reference,
                child=child,
            )
            result = result + marker

        return result


NormalizedCornerAnchorLab()
