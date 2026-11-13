class Arm:
    def anchors(self):
        return {
            "tip": AnchorFrame(
                origin=(20, 0, 5),
                z=(1, 0, 0),
                x=(0, 0, 1),
            ),
        }

    def build(self):
        return Box(40, 10, 10)


class Marker:
    def anchors(self):
        return {
            "mount": AnchorFrame(
                origin=(0, 0, 5),
                z=(-1, 0, 0),
                x=(0, 0, 1),
            ),
        }

    def build(self):
        return Box(10, 10, 10)


class CustomAnchor:
    def build(self):
        arm = Arm().rotate(Axis.Z, 90)
        marker = Marker().attach(
            arm,
            parent="tip",
            child="mount",
        )
        return arm + marker


CustomAnchor()
