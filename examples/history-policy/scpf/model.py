class HistoryPolicyBoss:
    size = 50.0

    def build(self):
        body = Box(self.size, self.size, 6.0)

        native = Boss(d=12.0, h=10.0, hole_d=4.0).attach(
            body,
            parent=Anchor.TOP,
            offset=(X.MIN + 15.0, Y.CENTER),
        )
        body = body + native

        with behavior(history=History.SKETCH):
            sketched = Boss(d=12.0, h=10.0, hole_d=4.0).attach(
                body,
                parent=Anchor.TOP,
                offset=(X.MAX - 15.0, Y.CENTER),
            )
        body = body + sketched

        with Sketch(name="Explicit pad", on=body, parent=Anchor.TOP) as sketch:
            sketch.add(Circle2D(d=10.0), offset=(0.0, -15.0))

        explicit = sketch.extrude(6.0)
        body + explicit


HistoryPolicyBoss()
