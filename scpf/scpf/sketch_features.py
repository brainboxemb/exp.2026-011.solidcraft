"""Generic sketch-based solid operations for SCPF.

A 2D Rectangle or Circle sketch can be extruded into a SolidCraft body;
additional extruded Circle sketches can be joined (+) or cut (-).
This module recognizes CAD operations, never example names such as Boss
or Bore. SolidCraft is the only BRep engine.
"""
from .core import Parameter, Shape, Edges, command_value, value_of


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


def _base_rectangle(shape):
    """Get an XY rectangular plate's defining dimensions.

    For a feature chain, follow its original base; no bounding-box guesses.
    The result is valid for the supported base-rectangle feature family only.
    """
    if shape.kind == "rectangle":
        return shape.data, (0, 0, 0), None
    if shape.kind == "positioned":
        child, x, y, z = shape.data
        if child.kind == "rectangle":
            return child.data, (x, y, z), None
    if shape.kind == "extrusion":
        child, height, direction = shape.data
        dimensions, origin, old_height = _base_rectangle(child)
        if old_height is not None or direction != "positive":
            raise ValueError("anchoring requires one positive XY base extrusion")
        return dimensions, origin, height
    if shape.kind == "fillet":
        return _base_rectangle(shape.data[0])
    if shape.kind in ("union", "difference"):
        return _base_rectangle(shape.data[0])
    raise ValueError("anchor target must be a supported extruded Rectangle2D")


def _combine(*terms):
    """Compose symbolic coordinates using the same named model dimensions."""
    from .core import Expression, Parameter, parameters_in, number_text
    numeric = sum(value_of(x) for x in terms)
    used = parameters_in(*terms)
    if not used:
        return numeric
    symbolic = []
    literal = 0
    for term in terms:
        if isinstance(term, (Parameter, Expression)):
            symbolic.append(f"({command_value(term)})")
        else:
            literal += value_of(term)
    expression = " + ".join(symbolic)
    if literal:
        expression += f" + ({number_text(literal)} mm)"
    return Expression(numeric, expression, used)


def _anchored_cylinders(shape):
    """Resolve attached cylinders against the original base plate dimensions.

    Resolving a relation into named-parameter expressions is currently an
    SCPF compile-time operation, NOT a persistent native face constraint.
    """
    from .core import Anchor, Axis
    if shape.kind != "anchored":
        raise ValueError("expected an anchored cylinder")
    child, target, parent_anchor, child_anchor, offset = shape.data
    (width, depth), (x, y, z), thickness = _base_rectangle(target)
    if thickness is None:
        raise ValueError("anchor target must be a 3D rectangular plate")
    center_x = _combine(x, width / 2)
    center_y = _combine(y, depth / 2)
    if parent_anchor is Anchor.TOP:
        parent_z = _combine(z, thickness)
    elif parent_anchor is Anchor.CENTER:
        parent_z = _combine(z, thickness / 2)
    elif parent_anchor is Anchor.BOTTOM:
        parent_z = z
    else:
        raise ValueError("unsupported anchor")
    if child.kind == "linear_pattern":
        cylinder, count, spacing, axis = child.data
        shifts = [((i - (count - 1)/2) * value_of(spacing), axis)
                  for i in range(count)]
    elif child.kind == "cylinder3d":
        cylinder = child
        shifts = [(0, None)]
    else:
        raise ValueError("only Cylinder patterns are supported")
    height, diameter = cylinder.data
    if child_anchor is Anchor.BOTTOM:
        base_z = parent_z
    elif child_anchor is Anchor.CENTER:
        base_z = _combine(parent_z, -(height / 2))
    else:
        base_z = _combine(parent_z, -height)
    result = []
    for shift, axis in shifts:
        dx, dy = (shift, 0) if axis is Axis.X else ((0, shift) if axis is Axis.Y else (0, 0))
        result.append((cylinder,
                       (_combine(center_x, offset[0], dx),
                        _combine(center_y, offset[1], dy),
                        base_z)))
    return result


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
        if edges is not Edges.VERTICAL:
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
        # Anchored cylinders resolve to SolidCraft named-parameter coordinates.
        if cutter.kind == "anchored":
            try:
                cylinders = _anchored_cylinders(cutter)
            except (ValueError, TypeError) as exc:
                raise ModelError(str(exc)) from exc
            for primitive, position in cylinders:
                height, diameter = primitive.data
                _require_positive(height, "cylinder height")
                _require_positive(diameter, "cylinder diameter")
                steps.append(_command(
                    "solid.cylinder", height=command_value(height),
                    diameter=command_value(diameter),
                    base=[command_value(dim) for dim in position],
                    axis="Z", operation="join" if shape.kind == "union" else "cut",
                    targets=[body_name]))
            return steps, base
        # A native 3D cylinder does not require a 2D sketch or extrusion.
        if cutter.kind in ("cylinder3d", "placed3d"):
            if cutter.kind == "placed3d":
                primitive, x, y, z = cutter.data
            else:
                primitive, x, y, z = cutter, 0, 0, 0
            if primitive.kind != "cylinder3d":
                raise ModelError("Only cylinders can join/cut this feature chain")
            height, diameter = primitive.data
            _require_positive(height, "cylinder height")
            _require_positive(diameter, "cylinder diameter")
            return steps + [
                _command("solid.cylinder",
                         height=command_value(height),
                         diameter=command_value(diameter),
                         base=[command_value(x), command_value(y), command_value(z)],
                         axis="Z",
                         operation="join" if shape.kind == "union" else "cut",
                         targets=[body_name])
            ], base
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
