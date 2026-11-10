class Enclosure:
    """Rebuild the SolidCraft plastic enclosure with native plastic features."""

    length = 80.0
    width = 50.0
    height = 30.0
    wall = 2.0

    def build(self):
        enclosure = Box(self.length, self.width, self.height)
        enclosure = enclosure.shell(self.wall, open=Faces.TOP)

        lip = Lip(width=1, height=2).attach(
            enclosure,
            parent=Anchor.TOP,
            offset=(Bounds.MIN + 1, Bounds.CENTER),
        )
        enclosure = enclosure + lip

        snap = SnapFit(
            length=14,
            thickness=1.5,
            width=6,
            catch_depth=1,
            catch_length=2,
            hook=(0, -1, 0),
        ).attach(
            enclosure,
            parent=Anchor.INNER_BOTTOM,
            offset=(Bounds.CENTER, Bounds.MAX - 6),
        )
        enclosure = enclosure + snap

        boss1 = Boss(d=7, h=12, hole_d=2.5).attach(
            enclosure,
            parent=Anchor.INNER_BOTTOM,
            offset=(Bounds.MIN + 10, Bounds.MIN + 10),
        )
        enclosure = enclosure + boss1

        boss2 = Boss(d=7, h=12, hole_d=2.5).attach(
            enclosure,
            parent=Anchor.INNER_BOTTOM,
            offset=(Bounds.MAX - 10, Bounds.MAX - 10),
        )
        enclosure = enclosure + boss2

        rest = Rest(width=16, length=24, height=3).attach(
            enclosure,
            parent=Anchor.INNER_BOTTOM,
        )
        enclosure + rest


Enclosure()
