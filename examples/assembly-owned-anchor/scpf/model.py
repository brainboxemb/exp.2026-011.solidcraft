"""Qualification: an assembly-owned named anchor remains associative."""


class Base:
    width = 40.0
    height = 20.0
    DEPTH = 30.0

    def build(self):
        return Box(self.width, self.DEPTH, self.height)


class Companion:
    SIZE = 10.0

    def build(self):
        return Box(self.SIZE, self.SIZE, self.SIZE)


class Marker:
    def build(self):
        return Box(10, 10, 10)


class AssemblyOwnedAnchor:
    base_width = 40.0
    base_height = 20.0

    def build(self):
        base = Base(
            width=self.base_width,
            height=self.base_height,
            name="base",
        )
        companion = Companion(name="companion").move(x=70)

        frame = (base + companion).with_anchor(
            "inspection_corner",
            base,
            Anchor.FRONT_TOP_RIGHT,
        )
        datum = frame.anchor("inspection_corner")

        marker = Marker().attach(
            datum.target,
            parent=datum.reference,
            child=Anchor.BACK_TOP_RIGHT,
            offset=datum.offset,
        )
        return frame + marker


AssemblyOwnedAnchor()
