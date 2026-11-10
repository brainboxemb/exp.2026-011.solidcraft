class PlasticEnclosurePi:
    width = 80.0
    depth = 60.0
    height = 30.0
    wall = 2.0

    def build(self):
        enclosure = Box(self.width, self.depth, self.height)
        enclosure = enclosure.fillet(6.0, edges=Edges.VERTICAL)
        enclosure = enclosure.shell(self.wall, open=Faces.TOP)

        with Sketch(name="USB port", on=enclosure, plane="YZ") as usb:
            usb.add(
                Rectangle2D(12.0, 7.0),
                offset=(-6.0, 8.5),
            )

        enclosure = enclosure - usb.extrude(Depth.THROUGH_ALL)

        for x, y in (
            (-30.0, -20.0),
            (30.0, -20.0),
            (30.0, 20.0),
            (-30.0, 20.0),
        ):
            boss = Boss(d=7.0, h=12.0, hole_d=2.5).attach(
                enclosure,
                parent=Anchor.INNER_BOTTOM,
                offset=(x, y),
            )
            enclosure = enclosure + boss

        enclosure


PlasticEnclosurePi()
