@dataclass
class Bracket:
    """Minimal L-profile qualification fixture.

    Deliberately no holes, fillets or secondary features: this fixture exists
    to verify profile geometry, XZ extrusion and later assembly relationships
    without unrelated feature behavior obscuring the result.
    """

    width: float = 24
    arm_length: float = 40
    arm_height: float = 12

    def build(self):
        profile = Polygon2D(
            [
                (0, 0),
                (self.arm_length, 0),
                (self.arm_length, self.arm_height),
                (self.arm_height, self.arm_height),
                (self.arm_height, self.arm_length),
                (0, self.arm_length),
            ],
            plane="XZ",
        )
        return profile.extrude(self.width, direction=Direction.SYMMETRIC)


Bracket()
