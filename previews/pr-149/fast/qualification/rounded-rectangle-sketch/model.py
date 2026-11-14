"""Qualification: RoundedRectangle2D in an explicit named Sketch."""


class RoundedRectangleSketch:
    base_width = 80.0
    base_depth = 60.0
    base_height = 5.0
    pad_width = 40.0
    pad_depth = 30.0
    radius = 5.0
    pad_height = 8.0

    def build(self):
        body = Box(self.base_width, self.base_depth, self.base_height)

        with Sketch(name="Rounded pad", on=body) as pad:
            pad.add(
                RoundedRectangle2D(
                    self.pad_width,
                    self.pad_depth,
                    self.radius,
                ),
                offset=(-20, -15),
            )

        return body + pad.extrude(self.pad_height)


RoundedRectangleSketch()
