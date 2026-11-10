"""Generic sketch-based solid operations for SCPF.

A 2D Rectangle or Circle sketch can be extruded into a SolidCraft body;
additional extruded Circle sketches can be joined (+) or cut (-).
This module recognizes CAD operations, never example names such as Boss
or Bore. SolidCraft is the only BRep engine.
"""
from .core import Parameter, Shape, command_value, value_of


def _circle_profiles(shape, dx=0, dy=0, z=0):
    """Return circles from planar shapes and their placements.

    Each circle is (x, y, z, diameter). A union in a 2D sketch is a
    collection of profiles, not a 3D Boolean operation.
    """
    if shape.kind == "positioned":
        base, x, y, dz = shape.data
        if base.kind == "positioned":
            raise ValueError("nested at() placement is not yet supported")
        return _circle_profiles(base, value_of(x), value_of(y), dz)
    if shape.kind == "circle":
        (diameter,) = shape.data
        return [(dx, dy, z, diameter)]
    if shape.kind == "union":
        left, right = shape.data
        return _circle_profiles(left) + _circle_profiles(right)
    raise ValueError("Expected Circle or union of Circle profiles")


def _rectangle_profile(shape):
    if shape.kind == "rectangle":
        return shape.data, (0, 0, 0)
    if shape.kind == "positioned":
        child, x, y, z = shape.data
        if child.kind != "rectangle":
            raise ValueError("Unsupported positioned profile")
        return child.data, (x, y, z)
    raise ValueError("Base shape must be a Rectangle")


def _to_commands(shape, body_name):
    # The imported compiler utilities are generic and centralized.
    from .compiler import ModelError, _command, _require_positive

    if shape.kind == "extrusion":
        profile, distance, direction = shape.data
        if direction not in ("positive", "negative"):
            raise ModelError("Invalid extrusion direction")
        _require_positive(distance, "extrusion distance")
        try:
            (width, depth), (x, y, z) = _rectangle_profile(profile)
        except ValueError as exc:
            raise ModelError("First extrusion must use Rectangle") from exc
        _require_positive(width, "rectangle width")
        _require_positive(depth, "rectangle depth")
        steps = []
        plane = {"plane": "XY", "name": "Base"}
        if value_of(z) != 0 or isinstance(z, Parameter):
            plane["offset"] = command_value(z)
        steps.append(_command("sketch.create", **plane))
        steps.append(_command("sketch.rectangle.two_point",
                              p0=[command_value(x), command_value(y)],
                              p1=[command_value(width), command_value(depth)]))
        steps.append(_command("sketch.finish"))
        steps.append(_command("solid.extrude",
                              distance=command_value(distance),
                              direction=direction, body_name=body_name))
        return steps, {"width": width, "depth": depth, "thickness": distance,
                       "origin": (x, y, z)}

    if shape.kind == "fillet":
        original, radius, edges = shape.data
        steps, base = _to_commands(original, body_name)
        if edges != "vertical":
            raise ModelError("Rectangular plate supports vertical edges only")
        r = _require_positive(radius, "fillet radius")
        w = value_of(base["width"])
        d = value_of(base["depth"])
        t = value_of(base["thickness"])
        x, y, z = (value_of(v) for v in base["origin"])
        if r * 2 >= min(w, d):
            raise ModelError("Fillet radius too large")
        if z != 0:
            raise ModelError("Fillet of shifted base not supported yet")
        edges = [[x+xx, y+yy, t/2] for xx, yy in
                 ((0,0), (w,0), (w,d), (0,d))]
        return steps + [
            _command("solid.fillet", edges=edges, radius=r, body=body_name)
        ], base

    if shape.kind in ("union", "difference"):
        original, cutter = shape.data
        steps, base = _to_commands(original, body_name)
        if cutter.kind != "extrusion":
            raise ModelError("Boolean feature must use an extruded 2D sketch")
        profiles, distance, direction = cutter.data
        try:
            circles = _circle_profiles(profiles)
        except ValueError as exc:
            raise ModelError("Boolean sketch requires Circle profiles") from exc
        if not circles:
            raise ModelError("Circle sketch is empty")
        depths = [value_of(z) for _, _, z, _ in circles]
        if not all(z == depths[0] for z in depths):
            raise ModelError("A sketch cannot mix circles on different Z planes")
        if shape.kind == "union" and direction != "positive":
            raise ModelError("Joining circles must extrude upward")
        if shape.kind == "difference" and direction not in ("positive", "negative"):
            raise ModelError("Invalid cutter direction")
        sketch_names = ("Holes", "Boss", "Bore")
        previous_sketches = [s.get("params", {}).get("name") for s in steps
                             if s["command"] == "sketch.create"]
        if "Boss" in previous_sketches:
            sketch_name = "Bore"
        elif shape.kind == "union":
            sketch_name = "Boss"
        else:
            sketch_name = "Holes"
        plane = {"plane": "XY", "name": sketch_name}
        z = circles[0][2]
        if value_of(z) != 0:
            plane["offset"] = command_value(z)
        steps.append(_command("sketch.create", **plane))
        for x, y, _, diameter in circles:
            _require_positive(diameter, "circle diameter")
            steps.append(_command("sketch.circle.center",
                                  center=[x, y],
                                  diameter=command_value(diameter)))
        steps.append(_command("sketch.finish"))
        steps.append(_command("solid.extrude",
                              distance=command_value(distance),
                              direction=direction,
                              operation="join" if shape.kind == "union" else "cut",
                              targets=[body_name]))
        return steps, base
    raise ModelError(f"Unsupported sketch-feature geometry: {shape.kind}")


def _is_rectangular_feature(node):
    if not isinstance(node, Shape):
        return False
    if node.kind == "rectangle":
        return True
    if node.kind in ("positioned", "extrusion", "fillet"):
        return _is_rectangular_feature(node.data[0])
    if node.kind in ("union", "difference"):
        return _is_rectangular_feature(node.data[0])
    return False


def compile_sketch_features(shape, name):
    from .compiler import _collect, _param_commands
    steps, _ = _to_commands(shape, name)
    return _param_commands(_collect(shape)) + steps
