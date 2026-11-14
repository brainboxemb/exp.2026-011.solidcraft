"""Qualification: Rectangle2D in an explicit named Sketch."""


class RectangleSketch:
    base_width = 80.0
    base_depth = 60.0
    base_height = 5.0
    pad_width = 40.0
    pad_depth = 30.0
    pad_height = 8.0

    def build(self):
        body = Box(self.base_width, self.base_depth, self.base_height)

        with Sketch(name="Rectangle pad", on=body) as pad:
            pad.add(
                Rectangle2D(self.pad_width, self.pad_depth),
                offset=(-20, -15),
            )

        return body + pad.extrude(self.pad_height)


RectangleSketch()
