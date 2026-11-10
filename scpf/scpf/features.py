"""Ordered CAD features -> native SolidCraft commands.

Works on Box, Rectangle2D/Circle2D/Polygon2D extrusions. Every feature
is compiled from its operation, not from a named example such as Plate.
"""
from math import isfinite
from .core import Shape, Edges, Faces, Depth, Anchor, Parameter, value_of, command_value
from .history import History
from .compiler import ModelError, _command, _collect, _param_commands, _require_positive
from .placement import (
    _anchored_features, _base_rectangle, _combine, _shell_thickness,
)
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
    if shape.kind in ("fillet", "shell", "union", "difference"):
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


def _face_point(base, face):
    """Return a stable authoring pick on a named face of a rectangular base."""
    if base.get("profile") != "rectangle":
        raise ModelError("named Faces currently require a rectangular base")
    x, y, z = (value_of(v) for v in base["origin"])
    width = value_of(base["width"])
    depth = value_of(base["depth"])
    height = value_of(base["thickness"])
    points = {
        Faces.TOP: [x + width / 2, y + depth / 2, z + height],
        Faces.BOTTOM: [x + width / 2, y + depth / 2, z],
        Faces.LEFT: [x, y + depth / 2, z + height / 2],
        Faces.RIGHT: [x + width, y + depth / 2, z + height / 2],
        Faces.FRONT: [x + width / 2, y, z + height / 2],
        Faces.BACK: [x + width / 2, y + depth, z + height / 2],
    }
    return points[face]


def _shell_command(base, thickness, faces, name):
    _require_positive(thickness, "shell thickness")
    return _command(
        "solid.shell",
        faces=[_face_point(base, face) for face in faces],
        thickness=command_value(thickness),
        body=name,
    )


def _vector(values, label):
    concrete = [value_of(v) for v in values]
    if len(concrete) != 3 or not all(isfinite(v) for v in concrete):
        raise ModelError(f"{label} must be a finite 3D direction")
    if concrete == [0, 0, 0]:
        raise ModelError(f"{label} cannot be the zero vector")
    return concrete


def _plastic_feature_command(feature, position, name):
    """Compile one native SolidCraft plastic feature at an explicit face pick."""
    point = [value_of(v) for v in position]
    if not all(isfinite(v) for v in point):
        raise ModelError("plastic feature position must be finite")

    if feature.kind == "lip":
        width, height = feature.data
        _require_positive(width, "lip width")
        _require_positive(height, "lip height")
        return _command(
            "plastic.lip",
            face=point,
            width=command_value(width),
            height=command_value(height),
            body=name,
        )

    if feature.kind == "snap_fit":
        length, thickness, width, catch_depth, catch_length, hook, direction = feature.data
        for value, label in (
            (length, "snap-fit length"),
            (thickness, "snap-fit thickness"),
            (width, "snap-fit width"),
            (catch_depth, "snap-fit catch depth"),
            (catch_length, "snap-fit catch length"),
        ):
            _require_positive(value, label)
        params = dict(
            position=point,
            hook=_vector(hook, "snap-fit hook"),
            length=command_value(length),
            thickness=command_value(thickness),
            width=command_value(width),
            catch_depth=command_value(catch_depth),
            catch_length=command_value(catch_length),
            body=name,
        )
        if direction is not None:
            params["direction"] = _vector(direction, "snap-fit direction")
        return _command("plastic.snap_fit", **params)

    if feature.kind == "boss":
        diameter, height, hole_diameter, direction = feature.data
        _require_positive(diameter, "boss diameter")
        _require_positive(height, "boss height")
        params = dict(
            position=point,
            diameter=command_value(diameter),
            height=command_value(height),
            body=name,
        )
        if hole_diameter is not None:
            _require_positive(hole_diameter, "boss hole diameter")
            params["hole_diameter"] = command_value(hole_diameter)
        if direction is not None:
            params["direction"] = _vector(direction, "boss direction")
        return _command("plastic.boss", **params)

    if feature.kind == "rest":
        width, height, length, along, direction = feature.data
        _require_positive(width, "rest width")
        _require_positive(height, "rest height")
        params = dict(
            position=point,
            width=command_value(width),
            height=command_value(height),
            body=name,
        )
        if length is not None:
            _require_positive(length, "rest length")
            params["length"] = command_value(length)
        if along is not None:
            params["along"] = _vector(along, "rest along")
        if direction is not None:
            params["direction"] = _vector(direction, "rest direction")
        return _command("plastic.rest", **params)

    raise ModelError(f"unsupported plastic feature {feature.kind}")


def _attached_hole_commands(child, target, parent_anchor, resolved, name):
    """Compile Hole intent as one editable sketch plus one cut feature."""
    feature = child.data[0] if child.kind == "linear_pattern" else child
    if feature.kind != "hole":
        raise ModelError("expected Hole feature")
    if parent_anchor is not Anchor.TOP:
        raise ModelError("Hole.attach() currently starts drilling from Anchor.TOP")

    diameter, depth = feature.data
    _require_positive(diameter, "hole diameter")
    (_, _), (_, _, origin_z), thickness = _base_rectangle(target)
    base_top = thickness if value_of(origin_z) == 0 else _combine(origin_z, thickness)
    entry_z = base_top
    on_base_top = True

    # If the current body ends in a centered Cylinder attached to its top,
    # the next Hole starts on that boss top. Keep the symbolic height so the
    # generated Bore sketch remains parametrically tied to the base thickness.
    if target.kind == "union":
        previous, attached = target.data
        if attached.kind == "anchored":
            boss, boss_parent, boss_parent_anchor, boss_child_anchor, boss_offset = attached.data
            if (boss.kind == "cylinder" and boss_parent == previous
                    and boss_parent_anchor is Anchor.TOP
                    and boss_child_anchor is Anchor.BOTTOM
                    and all(value_of(v) == 0 for v in boss_offset)):
                boss_height, _ = boss.data
                entry_z = (base_top + boss_height
                           if isinstance(boss_height, (int, float))
                           else _combine(base_top, boss_height))
                on_base_top = False

    if depth is Depth.THROUGH_ALL:
        if on_base_top:
            # Preserve the editable Sample Plate convention: XY/base-plane
            # sketch and positive cut through the plate thickness.
            sketch_z = origin_z
            distance = thickness
            direction = "positive"
        else:
            # A bore starting on a joined boss is sketched at its entry face
            # and cuts back through the complete current height.
            sketch_z = entry_z
            distance = (entry_z if value_of(origin_z) == 0
                        else _combine(entry_z, -value_of(origin_z)))
            direction = "negative"
    else:
        _require_positive(depth, "hole depth")
        sketch_z = entry_z
        distance = depth
        direction = "negative"

    label = "Holes" if child.kind == "linear_pattern" else (
        "Bore" if not on_base_top else "Hole")
    plane = {"plane": "XY", "name": label}
    if value_of(sketch_z):
        plane["offset"] = command_value(sketch_z)

    operations = [_command("sketch.create", **plane)]
    for primitive, position, _refs in resolved:
        hole_diameter, _ = primitive.data
        operations.append(_command(
            "sketch.circle.center",
            center=position[:2],
            diameter=command_value(hole_diameter),
        ))
    operations.extend([
        _command("sketch.finish"),
        _command("solid.extrude",
                 distance=command_value(distance),
                 direction=direction,
                 operation="cut",
                 targets=[name],
                 name=label),
    ])
    return operations


def _sketch_boss_commands(feature, position, name, *, feature_name=None):
    """Experimental sketch-based lowering for a semantic Boss object."""
    diameter, height, hole_diameter, direction = feature.data
    _require_positive(diameter, "boss diameter")
    _require_positive(height, "boss height")
    if direction is not None and [value_of(v) for v in direction] != [0, 0, 1]:
        raise ModelError("sketch-based Boss prototype currently supports +Z only")

    x, y, z = position
    label = feature_name or "Boss"
    plane = dict(plane="XY", name=label)
    if value_of(z):
        plane["offset"] = command_value(z)

    commands = [
        _command("sketch.create", **plane),
        _command(
            "sketch.circle.center",
            center=[command_value(x), command_value(y)],
            diameter=command_value(diameter),
        ),
        _command("sketch.finish"),
        _command(
            "solid.extrude",
            distance=command_value(height),
            direction="positive",
            operation="join",
            targets=[name],
            name=label,
        ),
    ]

    if hole_diameter is not None:
        _require_positive(hole_diameter, "boss hole diameter")
        top = _combine(z, height)
        hole_label = f"{label} hole"
        hole_plane = dict(plane="XY", name=hole_label)
        if value_of(top):
            hole_plane["offset"] = command_value(top)
        commands.extend([
            _command("sketch.create", **hole_plane),
            _command(
                "sketch.circle.center",
                center=[command_value(x), command_value(y)],
                diameter=command_value(hole_diameter),
            ),
            _command("sketch.finish"),
            _command(
                "solid.extrude",
                distance=command_value(height),
                direction="negative",
                operation="cut",
                targets=[name],
                name=hole_label,
            ),
        ])
    return commands


def _attached_commands(shape, original, feature, name, *, feature_name=None):
    child, target, parent_anchor, child_anchor, offset = feature.data
    if target != original:
        raise ModelError("attached feature must target the body being modified")
    try:
        resolved = _anchored_features(feature)
    except (ValueError, TypeError) as exc:
        raise ModelError(str(exc)) from exc

    attached_primitive = child.data[0] if child.kind == "linear_pattern" else child
    if attached_primitive.kind == "hole":
        return _attached_hole_commands(
            child, target, parent_anchor, resolved, name)
    if attached_primitive.kind in ("lip", "snap_fit", "boss", "rest"):
        if shape.kind != "union":
            raise ModelError("plastic features are added with +")
        if (
            attached_primitive.kind == "boss"
            and attached_primitive.history is History.SKETCH
        ):
            operations = []
            for primitive, position, _refs in resolved:
                operations.extend(
                    _sketch_boss_commands(
                        primitive,
                        position,
                        name,
                        feature_name=feature_name,
                    )
                )
            return operations
        return [
            _plastic_feature_command(primitive, position, name)
            for primitive, position, _refs in resolved
        ]

    operations = []
    for primitive, position, refs in resolved:
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
                     targets=[name],
                     name=label),
        ])
    return operations


def _explicit_sketch_commands(shape, original, feature, name):
    """Compile the first explicit Sketch prototype to a named native sketch."""
    sketch_name, target, parent_anchor, profiles, distance, direction = feature.data
    if target != original:
        raise ModelError("explicit Sketch must target the body being modified")
    if shape.kind not in ("union", "difference"):
        raise ModelError("explicit Sketch extrusion must be added or subtracted")

    (width, depth), (x, y, z), thickness = _base_rectangle(target)
    if thickness is None:
        raise ModelError("explicit Sketch prototype requires a rectangular solid")

    if parent_anchor is Anchor.TOP:
        plane_z = _combine(z, thickness)
    elif parent_anchor is Anchor.BOTTOM:
        plane_z = z
    elif parent_anchor is Anchor.INNER_BOTTOM:
        wall = _shell_thickness(target)
        if wall is None:
            raise ModelError("Anchor.INNER_BOTTOM requires a shelled body")
        plane_z = _combine(z, wall)
    elif parent_anchor is Anchor.CENTER:
        plane_z = _combine(z, thickness / 2)
    else:
        raise ModelError("unsupported explicit Sketch anchor")

    plane = dict(plane="XY", name=sketch_name)
    if value_of(plane_z):
        plane["offset"] = command_value(plane_z)
    commands = [_command("sketch.create", **plane)]

    for profile, offset in profiles:
        if profile.kind != "circle":
            raise ModelError("explicit Sketch prototype supports Circle2D only")
        diameter = profile.data[0]
        _require_positive(diameter, "sketch circle diameter")
        cx = _combine(x, width / 2, offset[0])
        cy = _combine(y, depth / 2, offset[1])
        commands.append(
            _command(
                "sketch.circle.center",
                center=[command_value(cx), command_value(cy)],
                diameter=command_value(diameter),
            )
        )

    commands.extend([
        _command("sketch.finish"),
        _command(
            "solid.extrude",
            distance=command_value(distance),
            direction=direction,
            operation="join" if shape.kind == "union" else "cut",
            targets=[name],
            name=sketch_name,
        ),
    ])
    return commands


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
                 targets=[name],
                 name=label),
    ])
    return result


def _to_commands(shape, name):
    if shape.kind in ("box", "extrusion"):
        return compile_base(shape, name)
    if shape.kind == "shell":
        original, thickness, faces = shape.data
        steps, base = _to_commands(original, name)
        return steps + [_shell_command(base, thickness, faces, name)], base
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
        if added.kind == "explicit_sketch_extrusion":
            return steps + _explicit_sketch_commands(
                shape, original, added, name
            ), base
        if added.kind == "placed3d" and added.data[0].kind in (
                "lip", "snap_fit", "boss", "rest"):
            if shape.kind != "union":
                raise ModelError("plastic features are added with +")
            feature, x, y, z = added.data
            return steps + [
                _plastic_feature_command(feature, (x, y, z), name)
            ], base
        if added.kind == "placed3d" and added.data[0].kind == "hole":
            hole, x, y, z = added.data
            return steps + [_hole_command(hole, (x, y, z), name)], base
        if added.kind == "hole":
            raise ModelError("Hole must be positioned with .attach() or .at()")
        if added.kind in ("lip", "snap_fit", "boss", "rest"):
            raise ModelError(
                f"{added.kind} must be positioned with .attach() or .at()"
            )
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
    while root.kind in ("fillet", "shell", "union", "difference"):
        root = root.data[0]
    if root.kind == "extrusion" and root.data[0].kind == "polygon":
        parameters = _collect((root.data[1], shape))
    else:
        parameters = _collect(shape)
    return _param_commands(parameters) + steps
