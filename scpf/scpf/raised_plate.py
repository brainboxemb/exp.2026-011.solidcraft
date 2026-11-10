"""Compile a raised XY plate with holes, a boss and a central bore.

Reconstructed from the feature history of a saved SolidCraft design.
This translator preserves native commands; it does not calculate geometry.
"""
from .core import Parameter, Shape, value_of, command_value, number_text


def compile_raised_plate(shape, name):
    from .compiler import ModelError, _collect, _command, _param_commands, _require_positive

    if shape.kind != "bore":
        raise ModelError("raised plate must finish with a bore")
    shape, bore_center, bore_diameter, bore_depth = shape.data
    if shape.kind != "boss":
        raise ModelError("raised plate requires a boss")
    shape, boss_center, boss_diameter, boss_height = shape.data
    if shape.kind != "holes":
        raise ModelError("raised plate requires mounting holes")
    shape, hole_centers, hole_diameter, hole_depth, plane = shape.data
    if plane != "XY" or len(hole_centers) != 2:
        raise ModelError("raised plate requires two XY mounting holes")
    if shape.kind != "fillet":
        raise ModelError("raised plate requires four corner fillets")
    shape, fillet_radius, edges = shape.data
    if edges != "vertical":
        raise ModelError("raised plate requires vertical fillets")
    if shape.kind != "extrusion":
        raise ModelError("raised plate requires an extrusion")
    rectangle, thickness, direction = shape.data
    if rectangle.kind != "rectangle" or direction != "positive":
        raise ModelError("raised plate requires an XY Rectangle extruded upward")
    width, depth = rectangle.data

    w = _require_positive(width, "plate width")
    d = _require_positive(depth, "plate depth")
    t = _require_positive(thickness, "plate thickness")
    radius = _require_positive(fillet_radius, "fillet radius")
    if radius * 2 >= min(w, d):
        raise ModelError("fillet radius exceeds plate")
    _require_positive(hole_diameter, "mounting hole diameter")
    if _require_positive(hole_depth, "mounting hole depth") < t:
        raise ModelError("mounting holes must pass through base")
    boss_d = _require_positive(boss_diameter, "boss diameter")
    boss_h = _require_positive(boss_height, "boss height")
    bore_d = _require_positive(bore_diameter, "bore diameter")
    if bore_d >= boss_d:
        raise ModelError("central bore must fit inside the boss")
    if bore_depth is not None and _require_positive(bore_depth, "bore depth") < t + boss_h:
        raise ModelError("central bore must pass through boss and base")
    bx, by = (value_of(v) for v in boss_center)
    if tuple(value_of(v) for v in bore_center) != (bx, by):
        raise ModelError("central bore must share the boss centre")
    if bx - boss_d/2 < 0 or bx + boss_d/2 > w or by - boss_d/2 < 0 or by + boss_d/2 > d:
        raise ModelError("boss is outside the base")
    for x, y in hole_centers:
        xx, yy = value_of(x), value_of(y)
        if not (0 < xx < w and 0 < yy < d):
            raise ModelError("mounting hole is outside the base")

    parameters = _param_commands(_collect((width, depth, thickness, shape,
                                           hole_centers, bore_depth)))
    corner_edges = [[x, y, t/2] for x, y in
                    [(0, 0), (w, 0), (w, d), (0, d)]]
    if isinstance(thickness, Parameter):
        upper_plane = f"{thickness.name} + {number_text(boss_h)} mm"
    else:
        upper_plane = t + boss_h
    through_depth = (command_value(bore_depth) if bore_depth is not None
                     else upper_plane)

    commands = [
        _command("sketch.create", plane="XY", name="Base"),
        _command("sketch.rectangle.two_point", p0=[0, 0],
                 p1=[command_value(width), command_value(depth)]),
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(thickness),
                 direction="positive", body_name=name),
        _command("solid.fillet", edges=corner_edges, radius=radius, body=name),
        _command("sketch.create", plane="XY", name="Holes"),
    ]
    commands += [
        _command("sketch.circle.center", center=[value_of(x), value_of(y)],
                 diameter=value_of(hole_diameter))
        for x, y in hole_centers
    ]
    commands += [
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(hole_depth),
                 direction="positive", operation="cut", targets=[name]),
        _command("sketch.create", plane="XY", offset=command_value(thickness),
                 name="Boss"),
        _command("sketch.circle.center", center=[bx, by], diameter=boss_d),
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(boss_height),
                 direction="positive", operation="join", targets=[name]),
        _command("sketch.create", plane="XY", offset=upper_plane, name="Bore"),
        _command("sketch.circle.center", center=[bx, by], diameter=bore_d),
        _command("sketch.finish"),
        _command("solid.extrude", distance=through_depth,
                 direction="negative", operation="cut", targets=[name]),
    ]
    return parameters + commands
