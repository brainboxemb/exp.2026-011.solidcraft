"""First reusable HUB75 reference: two native component occurrences.

Based on the measured portrait-orientation panel in:
brainboxemb/2026-006-01.cad.HUB75-display-frame
v1.2/cad/components/hub75_panel.scad

Coordinate mapping for SCPF: X = panel width, Y = panel height,
Z = front-to-rear depth. The front is at Z=0; the original OpenSCAD
component uses X/Z for the front and Y for depth.

Only the outer envelope, six M3 mounting-hole centres, and a housing
material are modelled at this stage. This is NOT yet the full rear frame,
PCB, connectors, locator pins or an alternating-orientation assembly.
"""


class Hub75Panel:
    width = 159.70
    height = 319.71
    depth = 14.50

    # Source holes: X=7.85/151.85, Z=7.855/159.855/311.855 from
    # the drawing's lower-left corner. They become +/-72 and +/-152
    # once the panel is centred on the front plane.
    mount_x = 72.0
    mount_y = 152.0
    hole_diameter = 3.0

    def build(self):
        body = Box(self.width, self.height, self.depth)

        for x in (-self.mount_x, self.mount_x):
            for y in (-self.mount_y, 0, self.mount_y):
                body = body + Hole(
                    d=self.hole_diameter,
                    depth=self.depth + 0.5,
                    direction=(0, 0, -1),
                ).at(x, y, self.depth)

        # One gray housing material. Detailed PCB/front/connector colors
        # require separate native bodies in a later panel-model iteration.
        return body.with_material(
            "HUB75 housing", density_g_cm3=1.20, color="#B8B8B8"
        )


class TwoHub75Panels:
    pitch_x = 160.0  # nominal grid, NOT the 159.70 mm physical width

    def build(self):
        first = Hub75Panel()
        second = first.copy().move(x=self.pitch_x)
        # One Python model build, two native SolidCraft occurrences.
        # No boolean union and no duplicate editable feature history.
        return first + second


TwoHub75Panels()
