class Parent:
    width = 80.0
    depth = 30.0
    height = 60.0

    def build(self):
        return Box(self.width, self.depth, self.height)


class LBracket:
    arm_width = 24.0
    arm_height = 12.0
    horizontal_arm_length = 50.0
    vertical_arm_length = 40.0

    def build(self):
        w = self.arm_height
        h = self.horizontal_arm_length
        v = self.vertical_arm_length
        profile = Polygon2D(
            [
                (0, 0),
                (h, 0),
                (h, w),
                (-w, w),
                (-w, -v),
                (0, -v),
            ],
            plane="XZ",
            world=True,
        )
        return profile.extrude(
            self.arm_width,
            direction=Direction.SYMMETRIC,
        )


class RigidAnchorLab:
    def build(self):
        parent = Parent()

        # Assembly-owned child mount reference on the actual broad face of the
        # bracket. The reusable LBracket itself knows nothing about mounting.
        child_mount = AnchorFrame(
            origin=(0, -LBracket.arm_width / 2, 0),
            z=(0, 1, 0),
            x=(0, 0, -1),
        )

        bracket = LBracket().attach(
            parent,
            parent=Anchor.FRONT_TOP_RIGHT,
            child=child_mount,
            gap=0,
            angle=0,
        )
        return parent + bracket


RigidAnchorLab()
