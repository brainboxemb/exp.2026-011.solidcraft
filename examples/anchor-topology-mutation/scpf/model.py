"""Qualification: a fixed AnchorTopology pick follows resized parent topology."""


class Board:
    width = 40.0
    height = 20.0
    DEPTH = 20.0

    def anchors(self):
        # Deliberately fixed pick coordinates from the baseline 40x20x20 board.
        # SolidCraft must retain the selected edge/face/corner after later
        # parameter changes; Forge does not recompute these points.
        return {
            "front_top_left_pick": AnchorTopology(
                edge=(-20.0, -10.0, 10.0),
                on=(0.0, -10.0, 10.0),
                corner=(-20.0, -10.0, 20.0),
                z=(0.0, -1.0, 0.0),
                x=(0.0, 0.0, -1.0),
            )
        }

    def build(self):
        return Box(self.width, self.DEPTH, self.height)


class Marker:
    SIZE = 10.0

    def build(self):
        # Center the cube on the component origin so rotation does not change
        # the expected bounding box around the selected topology corner.
        return Box(self.SIZE, self.SIZE, self.SIZE).move(z=-self.SIZE / 2)


class AnchorTopologyMutation:
    base_width = 40.0
    base_height = 20.0

    def build(self):
        board = Board(
            width=self.base_width,
            height=self.base_height,
        )
        marker = Marker().attach(
            board,
            parent="front_top_left_pick",
            child=AnchorFrame(),
        )
        return board + marker


AnchorTopologyMutation()
