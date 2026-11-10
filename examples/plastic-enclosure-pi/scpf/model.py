class PlasticEnclosurePi:
    # Raspberry Pi 4 video: board 85 × 56 mm, plus 10 mm in both directions.
    width = 95.0
    depth = 66.0
    height = 24.0
    wall = 2.0

    def build(self):
        enclosure = Box(self.width, self.depth, self.height)
        enclosure = enclosure.fillet(5.0, edges=Edges.VERTICAL)
        enclosure = enclosure.shell(self.wall, open=Faces.TOP)
        enclosure


PlasticEnclosurePi()
