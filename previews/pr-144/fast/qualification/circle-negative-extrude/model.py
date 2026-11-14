"""Qualification: explicitly sketched Circle2D extrusion in negative Z."""


class NegativeCircleExtrude:
    diameter = 20.0
    height = 30.0

    def build(self):
        with Sketch(plane="XY") as sketch:
            Circle2D(d=self.diameter)
        return sketch.extrude(
            self.height,
            direction=Direction.NEGATIVE,
        )


NegativeCircleExtrude()
