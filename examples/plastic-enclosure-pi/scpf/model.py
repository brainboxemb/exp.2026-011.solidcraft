class PlasticEnclosurePi:
    # SolidCraft 0.8 Raspberry Pi 4 video: board 85 × 56, case +10 mm.
    width = 95.0
    depth = 66.0
    height = 24.0
    wall = 2.0

    def build(self):
        enclosure = Box(self.width, self.depth, self.height)
        enclosure = enclosure.fillet(5.0, edges=Edges.VERTICAL)
        enclosure = enclosure.shell(self.wall, open=Faces.TOP)

        # The video rounds one upper rim edge, R1.
        enclosure = enclosure.fillet(
            1.0, edges=[(0, self.depth / 2, self.height)]
        )

        # Board mounting holes: one corner 3.5 mm in from board edges,
        # then a 58 × 49 mm rectangular pattern. Native screw bosses.
        for x, y in (
            (-39.0, -24.5),
            (19.0, -24.5),
            (-39.0, 24.5),
            (19.0, 24.5),
        ):
            boss = Boss(d=6.0, h=4.0, hole_d=2.5).attach(
                enclosure, parent=Anchor.INNER_BOTTOM, offset=(x, y)
            )
            enclosure = enclosure + boss

        # Front (-Y): USB-C and two micro-HDMI openings.
        # Local XZ coordinates are (world X, world Z). A negative
        # extrusion points into the case from the front face.
        with Sketch(
            name="Pi ports", on=enclosure, plane="XZ",
            origin=(0, -(self.depth / 2), 0),
        ) as ports:
            for x, half_width in ((-31.3, 5.0), (-16.5, 4.0), (-3.0, 4.0)):
                ports.add(
                    Rectangle2D(half_width * 2, 4.0),
                    offset=(x - half_width, 7.5),
                )
        enclosure = enclosure - ports.extrude(
            self.wall, direction=Direction.NEGATIVE
        )

        # Right (+X) end: the combined USB-A and Ethernet window.
        # Local YZ coordinates are (world Y, world Z).
        with Sketch(
            name="USB and Ethernet", on=enclosure, plane="YZ",
            origin=(self.width / 2, 0, 0),
        ) as end_ports:
            end_ports.add(Rectangle2D(50.0, 14.0), offset=(-25.0, 8.0))
        enclosure = enclosure - end_ports.extrude(
            self.wall, direction=Direction.NEGATIVE
        )

        # Five separate slots, spaced 7 mm along X, through the floor.
        with Sketch(
            name="Floor vents", on=enclosure, plane="XY",
            origin=(0, 0, self.wall),
        ) as vents:
            for i in range(5):
                vents.add(
                    Rectangle2D(5.0, 28.0),
                    offset=(-22.0 + i * 7.0, -16.5),
                )
        enclosure = enclosure - vents.extrude(
            self.wall, direction=Direction.NEGATIVE
        )
        enclosure


PlasticEnclosurePi()
