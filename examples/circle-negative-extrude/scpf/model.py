"""Qualification: direct Circle2D extrusion in the negative Z direction."""


class NegativeCircleExtrude:
    diameter = 20.0
    height = 30.0

    def build(self):
        return Circle2D(d=self.diameter).extrude(
            self.height,
            direction=Direction.NEGATIVE,
        )


NegativeCircleExtrude()
