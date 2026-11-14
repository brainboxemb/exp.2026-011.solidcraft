"""Qualification: attach(angle=...) is a native joint clocking value."""


class Base:
    WIDTH = 60.0
    DEPTH = 60.0
    HEIGHT = 10.0

    def build(self):
        return Box(self.WIDTH, self.DEPTH, self.HEIGHT)


class Arm:
    LENGTH = 30.0
    WIDTH = 10.0
    HEIGHT = 6.0

    def build(self):
        return Box(self.LENGTH, self.WIDTH, self.HEIGHT)


class AttachAngle:
    def build(self):
        base = Base()
        arm = Arm().attach(
            base,
            parent=Anchor.TOP,
            child=Anchor.BOTTOM,
            angle=90,
        )
        return base + arm


AttachAngle()
