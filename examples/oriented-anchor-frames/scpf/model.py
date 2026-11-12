class Frame:
    def build(self):
        return Box(100, 40, 60)


class Flag:
    def anchors(self):
        return {
            "mount_0": AnchorFrame(
                origin=(0, 0, 0),
                z=(0, -1, 0),
                x=(1, 0, 0),
            ),
            "mount_90": AnchorFrame(
                origin=(0, 0, 0),
                z=(0, -1, 0),
                x=(0, 0, -1),
            ),
            "mount_180": AnchorFrame(
                origin=(0, 0, 0),
                z=(0, -1, 0),
                x=(-1, 0, 0),
            ),
            "mount_270": AnchorFrame(
                origin=(0, 0, 0),
                z=(0, -1, 0),
                x=(0, 0, 1),
            ),
        }

    def build(self):
        profile = Polygon2D(
            [(0, 0), (30, 0), (30, 10), (0, 10)],
            plane="XZ",
            world=True,
        )
        return profile.extrude(
            10,
            direction=Direction.SYMMETRIC,
        )


class OrientedAnchorFrames:
    def build(self):
        frame = Frame()
        flag = Flag()

        top_left = flag.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_LEFT,
            child="mount_0",
        )
        top_right = flag.copy().attach(
            frame,
            parent=Anchor.FRONT_TOP_RIGHT,
            child="mount_90",
        )
        bottom_right = flag.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_RIGHT,
            child="mount_180",
        )
        bottom_left = flag.copy().attach(
            frame,
            parent=Anchor.FRONT_BOTTOM_LEFT,
            child="mount_270",
        )
        return frame + top_left + top_right + bottom_right + bottom_left


OrientedAnchorFrames()
