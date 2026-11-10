@dataclass
class Plate:
    length: float = 100
    width: float = 60
    thickness: float = 10

    def build(self):
        # A Box is a native CAD solid; keep it as an object.
        body = Box(self.length, self.width, self.thickness)
        body = body.fillet(2, edges=Edges.VERTICAL)

        # Four native SolidCraft Hole features, relative to the box top.
        # Their nominal centres are (+/-35, +/-15) mm.
        for x, y in ((-35, -15), (35, -15), (35, 15), (-35, 15)):
            body = body.add(
                Hole(d=8, depth=Depth.THROUGH_ALL),
                on=Anchor.TOP, offset=(x, y))
        body


Plate()
