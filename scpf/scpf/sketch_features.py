"""Generic sketch-based solid operations for SCPF.

A 2D Rectangle or Circle sketch can be extruded into a SolidCraft body;
additional extruded Circle sketches can be joined (+) or cut (-).
This module recognizes CAD operations, never example names such as Boss
or Bore. SolidCraft is the only BRep engine.
"""
from .core import Parameter, Shape, Edges, Depth, command_value, value_of


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
            text = str(command_value(term))
            symbolic.append(text if text.startswith("(") and text.endswith(")")
                            else f"({text})")
        else:
            literal += value_of(term)
    expression = " + ".join(symbolic)
    if literal:
        expression += f" + ({number_text(literal)} mm)"
    return Expression(numeric, expression, used)


def _anchored_features(shape):
    """Resolve relative placement and retain two native reference edges.

    Only rectangular XY bases are currently supported. For a face on the
    original base plate, two perpendicular straight edges locate the center.
    Native references follow those edges after a parameter edit. The numeric
    pick points are merely initial selectors, not the dimensional relationship.
    """
    from .core import Anchor, Axis, Depth
    if shape.kind != "anchored":
        raise ValueError("expected an anchored feature")
    child, target, parent_anchor, child_anchor, offset = shape.data
    (width, depth), (x, y, z), thickness = _base_rectangle(target)
    if thickness is None:
        raise ValueError("anchor target must be an extruded Rectangle2D")
    if value_of(x) != 0 or value_of(y) != 0 or value_of(z) != 0:
        raise ValueError("native reference edges require an unshifted base for now")
    # The original rectangular base is not necessarily the highest face:
    # after a joined boss, Anchor.TOP must resolve to that boss's top.
    # A circular boss has no suitable pair of straight reference edges,
    # so a native Hole on its top uses a numeric face pick instead.
    on_boss = False
    if target.kind == "union":
        previous, boss = target.data
        if boss.kind == "anchored":
            boss_feature, boss_parent, boss_anchor, boss_child, boss_offset = boss.data
            if (boss_feature.kind == "cylinder3d" and boss_parent == previous
                    and boss_anchor is Anchor.TOP and boss_child is Anchor.BOTTOM
                    and all(value_of(v) == 0 for v in boss_offset)):
                boss_height, boss_diameter = boss_feature.data
                _require_positive_local = value_of(boss_height) > 0 and value_of(boss_diameter) > 0
                if not _require_positive_local:
                    raise ValueError("invalid attached boss")
                on_boss = True
            # Other joins (including attached Hole features) do not raise
            # the top surface; the rectangular top remains the reference.
    if parent_anchor is Anchor.TOP:
        face_z = _combine(thickness, boss_height) if on_boss else thickness
    elif parent_anchor is Anchor.BOTTOM:
        face_z = z
    else:
        face_z = _combine(z, thickness / 2)
    if child.kind == "linear_pattern":
        feature, count, spacing, axis = child.data
        shifts = [((n - (count - 1) / 2) * spacing, axis)
                  for n in range(count)]
    else:
        feature, shifts = child, [(0, None)]
    if feature.kind not in ("cylinder3d", "hole"):
        raise ValueError("anchoring currently supports Cylinder and Hole")
    if feature.kind == "hole":
        if parent_anchor not in (Anchor.TOP, Anchor.BOTTOM):
            raise ValueError("Hole must be placed on a planar exterior face")
        if child_anchor is not Anchor.BOTTOM:
            raise ValueError("Hole uses its entry point, not a volume center")
    height = feature.data[0] if feature.kind == "cylinder3d" else None
    if feature.kind == "cylinder3d":
        if child_anchor is Anchor.BOTTOM:
            base_z = face_z
        elif child_anchor is Anchor.CENTER:
            base_z = _combine(face_z, -(height / 2))
        else:
            base_z = _combine(face_z, -height)
    else:
        base_z = face_z
    result = []
    for shift, axis in shifts:
        dx, dy = ((shift, 0) if axis is Axis.X else
                  ((0, shift) if axis is Axis.Y else (0, 0)))
        xx = _combine(x, width / 2, offset[0], dx)
        yy = _combine(y, depth / 2, offset[1], dy)
        # The edge samples are intentionally strictly within straight segments
        # on filleted rectangular faces (midpoints, not rounded corners).
        if not on_boss and parent_anchor in (Anchor.TOP, Anchor.BOTTOM) and child_anchor is Anchor.BOTTOM:
            refs = [
                {"edge": [value_of(x), value_of(y) + value_of(depth)/2, value_of(face_z)],
                 "distance": command_value(_combine(width / 2, offset[0], dx))},
                {"edge": [value_of(x) + value_of(width)/2, value_of(y), value_of(face_z)],
                 "distance": command_value(_combine(depth / 2, offset[1], dy))}
            ]
        else:
            refs = None
        # Native solid.hole uses a numeric authoring pick. For holes on the
        # joined circular boss no stable straight-edge references exist yet.
        # Do not pass unevaluated expressions as its position coordinates.
        if feature.kind == "hole" or refs:
            position = [value_of(xx), value_of(yy), value_of(base_z)]
        else:
            position = [command_value(xx), command_value(yy), command_value(base_z)]
        result.append((feature, position, refs))
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
        if cutter.kind == "anchored":
            try:
                features = _anchored_features(cutter)
            except (ValueError, TypeError) as exc:
                raise ModelError(str(exc)) from exc
            child, target, parent_anchor, child_anchor, offset = cutter.data
            if target != original:
                raise ModelError("attached feature target must be the current body")
            for feature, position, refs in features:
                if feature.kind == "hole":
                    # A Hole is added as a CAD feature, not positive material.
                    # Keep legacy subtraction syntax valid for old scripts.
                    diameter, depth = feature.data
                    _require_positive(diameter, "hole diameter")
                    params = dict(
                        position=position, diameter=command_value(diameter),
                        targets=[body_name])
                    if depth is not Depth.THROUGH_ALL:
                        _require_positive(depth, "hole depth")
                        params["depth"] = command_value(depth)
                    if refs:
                        params["references"] = refs
                    steps.append(_command("solid.hole", **params))
                else:
                    height, diameter = feature.data
                    _require_positive(height, "cylinder height")
                    _require_positive(diameter, "cylinder diameter")
                    # A single attached cylinder is a user-facing object, but
                    # its native SolidCraft construction is a circle sketch
                    # plus an extrusion. Leave linear patterns on the existing
                    # direct-cylinder path until sketch pattern support exists.
                    if child.kind == "cylinder3d":
                        from .core import Anchor
                        (_, _), (_, _, origin_z), thickness = _base_rectangle(target)
                        if shape.kind == "union" and child_anchor is Anchor.BOTTOM:
                            sketch_z = thickness if parent_anchor is Anchor.TOP else origin_z
                            direction = "positive"
                        elif shape.kind == "difference" and child_anchor is Anchor.BOTTOM:
                            # The cylinder starts at its bottom; cut downwards
                            # from its top to retain the full cutter extent.
                            anchor_z = origin_z if parent_anchor is Anchor.BOTTOM else thickness
                            sketch_z = height if value_of(anchor_z) == 0 else _combine(anchor_z, height)
                            direction = "negative"
                        else:
                            raise ModelError(
                                "attached sketch cylinders currently support a bottom-anchored "
                                "join or cut; use a direct cylinder for other placements")
                        sketch_names = [s["params"].get("name") for s in steps
                                        if s["command"] == "sketch.create"]
                        feature_name = ("Boss" if shape.kind == "union" else
                                        ("Bore" if "Boss" in sketch_names else "Holes"))
                        plane = dict(plane="XY", name=feature_name)
                        if value_of(sketch_z):
                            plane["offset"] = command_value(sketch_z)
                        steps.extend([
                            _command("sketch.create", **plane),
                            _command("sketch.circle.center",
                                     center=position[:2], diameter=command_value(diameter)),
                            _command("sketch.finish"),
                            _command("solid.extrude", distance=command_value(height),
                                     direction=direction,
                                     operation="join" if shape.kind == "union" else "cut",
                                     targets=[body_name]),
                        ])
                    else:
                        params = dict(
                            height=command_value(height),
                            diameter=command_value(diameter), base=position,
                            axis="Z",
                            operation="join" if shape.kind == "union" else "cut",
                            targets=[body_name])
                        if refs:
                            params["references"] = refs
                        steps.append(_command("solid.cylinder", **params))
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
