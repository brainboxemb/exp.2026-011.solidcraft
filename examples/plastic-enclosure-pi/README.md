# Plastic Enclosure Pi

A separate practical SCPF example based on the supplied SolidCraft/MCP
electronics-enclosure sequence.

This project is intentionally separate from
[`history-policy`](../history-policy/): the history-policy example stays small
and demonstrates compiler behavior in isolation, while this example is a real
enclosure model that can grow independently.

## Source

[`source/enclosure_steps.json`](source/enclosure_steps.json) is the supplied
command-by-command SolidCraft reference.

The reference builds:

1. user parameters `width`, `depth`, `height`, `wall`;
2. a centered enclosure footprint;
3. extrusion by `height`;
4. 6 mm fillets on the four vertical edges;
5. an open-top shell with `wall` thickness;
6. a YZ sketch for the USB opening and a through-all cut;
7. four native screw bosses;
8. a final width change from 80 mm to 100 mm as an associative-rebuild demo.

The reference intentionally omits the rim lip because its source notes that it
waits for upstream SolidCraft issue #29.

## SCPF model

[`scpf/model.py`](scpf/model.py) expresses the same main design intent:

```python
class PlasticEnclosurePi:
    width = 80.0
    depth = 60.0
    height = 30.0
    wall = 2.0

    def build(self):
        enclosure = Box(self.width, self.depth, self.height)
        enclosure = enclosure.fillet(6.0, edges=Edges.VERTICAL)
        enclosure = enclosure.shell(self.wall, open=Faces.TOP)

        with Sketch(name="USB port", on=enclosure, plane="YZ") as usb:
            usb.add(Rectangle2D(12.0, 7.0), offset=(-6.0, 8.5))

        enclosure = enclosure - usb.extrude(Depth.THROUGH_ALL)
        ...
```

The four bosses remain semantic `Boss(...)` objects and therefore use native
SolidCraft plastic-boss features under the normal AUTO history policy.

This example also gives the explicit Sketch API a useful non-XY case:
`Sketch(..., plane="YZ")` plus a rectangular through-all cut.
