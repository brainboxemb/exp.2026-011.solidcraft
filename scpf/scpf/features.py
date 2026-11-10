"""Ordered CAD features -> native SolidCraft commands.

Works on Box, Rectangle2D/Circle2D/Polygon2D extrusions. Every feature
is compiled from its operation, not from a named example such as Plate.
"""
from math import isfinite
from .core import Shape, Edges, Depth, Anchor, Parameter, value_of, command_value
from .compiler import ModelError, _command, _collect, _param_commands, _require_positive
from .placement import _anchored_features, _base_rectangle, _combine
from .sketches import compile_base, _circle_profiles


def _is_feature_tree(shape):
    if not isinstance(shape, Shape):
        return False
    if shape.kind == "box":
        return True
    if shape.kind == "extrusion":
        profile = shape.data[0]
        if profile.kind == "positioned":
            profile = profile.data[0]
        return profile.kind in ("rectangle", "circle", "polygon")
    if shape.kind in ("fillet", "union", "difference"):
        return _is_feature_tree(shape.data[0])
    return False


def _hole_command(feature, position, name, refs=None):
    if feature.kind != "hole":
        raise ModelError("native hole operation requires Hole")
    diameter, depth = feature.data
    _require_positive(diameter, "hole diameter")
    params = dict(position=[value_of(v) for v in position],
                  diameter=command_value(diameter), targets=[name])
    if depth is not Depth.THROUGH_ALL:
        _require_positive(depth, "hole depth")
        params["depth"] = command_value(depth)
    if refs:
        params["references"] = refs
    return _command("solid.hole", **params)


def _fillet_command(base, radius, edges, name):
    r = _require_positive(radius, "fillet radius")
    if edges is Edges.VERTICAL:
        if base["profile"] != "rectangle":
            raise ModelError("vertical-edge selection requires a rectangular base")
        w, d, h = (value_of(base[k]) for k in ("width", "depth", "thickness"))
        if r * 2 >= min(w, d):
            raise ModelError("fillet radius exceeds rectangular base dimensions")
        x, y, z = (value_of(v) for v in base["origin"])
        if z != 0:
            raise ModelError("vertical fillet of shifted base not supported")
        picks = [[x + dx, y + dy, h / 2]
                 for dx, dy in ((0, 0), (w, 0), (w, d), (0, d))]
        return _command("solid.fillet", edges=picks, radius=r, body=name)
    picks = [[value_of(v) for v in point] for point in edges]
    if not all(isfinite(v) for point in picks for v in point):
        raise ModelError("fillet edge selection must be finite")
    return _command("solid.fillet", edges=picks, radius=r)


def _attached_commands(shape, original, feature, name, *, feature_name=None):
    child, target, parent_anchor, child_anchor, offset = feature.data
    if target != original:
        raise ModelError("attached feature must target the body being modified")
    try:
        resolved = _anchored_features(feature)
    except (ValueError, TypeError) as exc:
        raise ModelError(str(exc)) from exc
    operations = []
    for primitive, position, refs in resolved:
        if primitive.kind == "hole":
            operations.append(_hole_command(primitive, position, name, refs))
            continue
        height, diameter = primitive.data
        _require_positive(height, "cylinder height")
        _require_positive(diameter, "cylinder diameter")
        if child.kind != "cylinder":
            params = dict(height=command_value(height),
                          diameter=command_value(diameter), base=position,
                          axis="Z",
                          operation="join" if shape.kind == "union" else "cut",
                          targets=[name])
            if refs:
                params["references"] = refs
            operations.append(_command("solid.cylinder", **params))
            continue
        (_, _), (_, _, origin_z), thickness = _base_rectangle(target)
        if shape.kind == "union" and child_anchor is Anchor.BOTTOM:
            sketch_z = thickness if parent_anchor is Anchor.TOP else origin_z
            direction = "positive"
        elif shape.kind == "difference" and child_anchor is Anchor.BOTTOM:
            anchor_z = origin_z if parent_anchor is Anchor.BOTTOM else thickness
            sketch_z = (height if value_of(anchor_z) == 0
                        else _combine(anchor_z, height))
            direction = "negative"
        else:
            raise ModelError("single attached Cylinder requires a bottom-anchored join/cut")
        # Name by CAD feature intent; no example/model-specific switch.
        label = feature_name or ("Boss" if shape.kind == "union" else "Cut")
        plane = dict(plane="XY", name=label)
        if value_of(sketch_z):
            plane["offset"] = command_value(sketch_z)
        operations.extend([
            _command("sketch.create", **plane),
            _command("sketch.circle.center",
                     center=position[:2], diameter=command_value(diameter)),
            _command("sketch.finish"),
            _command("solid.extrude", distance=command_value(height),
                     direction=direction,
                     operation="join" if shape.kind == "union" else "cut",
                     targets=[name]),
        ])
    return operations


def _circle_boolean_commands(shape, cutter, name, *, feature_name=None):
    profiles, distance, direction = cutter.data
    try:
        circles = _circle_profiles(profiles)
    except ValueError as exc:
        raise ModelError("boolean sketch requires Circle2D profiles") from exc
    if not circles:
        raise ModelError("empty circular cutter sketch")
    z_values = [value_of(z) for _, _, z, _ in circles]
    if len(set(z_values)) != 1:
        raise ModelError("a sketch cannot mix circles on different Z planes")
    if shape.kind == "union" and direction != "positive":
        raise ModelError("joining circles must extrude upward")
    label = feature_name or ("Join" if shape.kind == "union" else "Cut")
    plane = dict(plane="XY", name=label)
    z = circles[0][2]
    if value_of(z):
        plane["offset"] = command_value(z)
    result = [_command("sketch.create", **plane)]
    for x, y, _, diameter in circles:
        _require_positive(diameter, "circle diameter")
        result.append(_command("sketch.circle.center",
                               center=[command_value(x), command_value(y)],
                               diameter=command_value(diameter)))
    result.extend([
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(distance),
                 direction=direction,
                 operation="join" if shape.kind == "union" else "cut",
                 targets=[name]),
    ])
    return result


def _to_commands(shape, name):
    if shape.kind in ("box", "extrusion"):
        return compile_base(shape, name)
    if shape.kind == "fillet":
        original, radius, edges = shape.data
        steps, base = _to_commands(original, name)
        return steps + [_fillet_command(base, radius, edges, name)], base
    if shape.kind in ("union", "difference"):
        original, added = shape.data
        steps, base = _to_commands(original, name)
        feature_name = None
        if added.kind == "labeled":
            added, feature_name = added.data
        if added.kind == "anchored":
            return steps + _attached_commands(
                shape, original, added, name, feature_name=feature_name), base
        if added.kind == "placed3d" and added.data[0].kind == "hole":
            hole, x, y, z = added.data
            return steps + [_hole_command(hole, (x, y, z), name)], base
        if added.kind == "hole":
            raise ModelError("Hole must be positioned with .on() or .at()")
        if added.kind in ("cylinder", "placed3d"):
            if added.kind == "placed3d":
                primitive, x, y, z = added.data
            else:
                primitive, x, y, z = added, 0, 0, 0
            if primitive.kind != "cylinder":
                raise ModelError("boolean primitive requires Cylinder")
            height, diameter = primitive.data
            _require_positive(height, "cylinder height")
            _require_positive(diameter, "cylinder diameter")
            return steps + [
                _command("solid.cylinder",
                         height=command_value(height),
                         diameter=command_value(diameter),
                         base=[command_value(x), command_value(y), command_value(z)],
                         axis="Z", operation="join" if shape.kind == "union" else "cut",
                         targets=[name]),
            ], base
        if added.kind == "extrusion":
            return steps + _circle_boolean_commands(
                shape, added, name, feature_name=feature_name), base
        raise ModelError(f"unsupported CAD feature {added.kind}")
    raise ModelError(f"unsupported CAD solid {shape.kind}")


def compile_features(shape, name):
    """Compile native commands with deterministic, source-oriented parameters."""
    steps, _ = _to_commands(shape, name)
    # On an extruded polygon the sweep distance is the first independent
    # dimension of the feature. Keep it before coordinates of its profile.
    # XY rectangular footprints instead list their plan dimensions first.
    root = shape
    while root.kind in ("fillet", "union", "difference"):
        root = root.data[0]
    if root.kind == "extrusion" and root.data[0].kind == "polygon":
        parameters = _collect((root.data[1], shape))
    else:
        parameters = _collect(shape)
    return _param_commands(parameters) + steps
