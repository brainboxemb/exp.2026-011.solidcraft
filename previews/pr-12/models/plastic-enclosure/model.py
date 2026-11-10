@dataclass
class PlasticEnclosure:
    """Rebuild the SolidCraft plastic enclosure with native plastic features."""

    length: float = 80
    width: float = 50
    height: float = 30
    wall: float = 2

    def build(self):
        enclosure = Box(self.length, self.width, self.height)
        enclosure = enclosure.shell(self.wall, open=Faces.TOP)

        lip = Lip(width=1, height=2).at(
            -(self.length / 2) + 1,
            0,
            self.height,
        )
        enclosure = enclosure + lip

        snap = SnapFit(
            length=14,
            thickness=1.5,
            width=6,
            catch_depth=1,
            catch_length=2,
            hook=(0, -1, 0),
        ).at(
            0,
            self.width / 2 - 6,
            self.wall,
        )
        enclosure = enclosure + snap

        boss1 = Boss(d=7, h=12, hole_d=2.5).at(
            -(self.length / 2) + 10,
            -(self.width / 2) + 10,
            self.wall,
        )
        enclosure = enclosure + boss1

        boss2 = Boss(d=7, h=12, hole_d=2.5).at(
            self.length / 2 - 10,
            self.width / 2 - 10,
            self.wall,
        )
        enclosure = enclosure + boss2

        rest = Rest(width=16, length=24, height=3).at(
            0,
            0,
            self.wall,
        )
        enclosure + rest


PlasticEnclosure()
