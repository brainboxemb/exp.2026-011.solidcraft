"""Relative CAD placement and native edge references.

Anchor resolution is shared by Box and extruded Rectangle2D models.
It is not a geometry engine: SolidCraft owns actual face identity.
"""
from .core import Shape, _BoundOffset, value_of, command_value

def _is_centered_box(shape):
    while shape.kind in ("fillet", "shell", "union", "difference"):
        shape = shape.data[0]
    return shape.kind == "box"


def _base_rectangle(shape):
    """Get an XY rectangular plate's defining dimensions.

    For a feature chain, follow its original base; no bounding-box guesses.
    The result is valid for the supported base-rectangle feature family only.
    """
    if shape.kind == "rectangle":
        return shape.data, (0, 0, 0), None
    if shape.kind == "box":
        length, width, height = shape.data
        # Box uses the SolidCraft convention: centered in XY, bottom at Z=0.
        return (length, width), (-length / 2, -width / 2, 0), height
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
    if shape.kind in ("fillet", "shell"):
        return _base_rectangle(shape.data[0])
    if shape.kind in ("union", "difference"):
        return _base_rectangle(shape.data[0])
    raise ValueError("anchor target must be a supported extruded Rectangle2D")


def _shell_thickness(shape):
    """Return the active shell wall thickness in a supported feature chain."""
    if shape.kind == "shell":
        return shape.data[1]
    if shape.kind in ("fillet", "union", "difference"):
        return _shell_thickness(shape.data[0])
    return None


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


def _bound_offset(value, size, axis):
    """Resolve X/Y MIN/CENTER/MAX to an offset from the parent axis centre."""
    if not isinstance(value, _BoundOffset):
        return value
    if value.axis != axis:
        raise ValueError(f"{axis} offset cannot use {value.axis} bounds")
    if value.reference == "min":
        return _combine(-(size / 2), value.delta)
    if value.reference == "center":
        return value.delta
    if value.reference == "max":
        return _combine(size / 2, value.delta)
    raise ValueError(f"unknown bound reference {value.reference!r}")


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
    if value_of(z) != 0 or (not _is_centered_box(target)
                              and (value_of(x) != 0 or value_of(y) != 0)):
        raise ValueError("native references require an unshifted supported base")
    # The original rectangular base is not necessarily the highest face:
    # after a joined boss, Anchor.TOP must resolve to that boss's top.
    # A circular boss has no suitable pair of straight reference edges,
    # so a native Hole on its top uses a numeric face pick instead.
    on_boss = False
    if target.kind == "union":
        previous, boss = target.data
        if boss.kind == "anchored":
            boss_feature, boss_parent, boss_anchor, boss_child, boss_offset = boss.data
            if (boss_feature.kind == "cylinder" and boss_parent == previous
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
    elif parent_anchor is Anchor.INNER_BOTTOM:
        wall = _shell_thickness(target)
        if wall is None:
            raise ValueError("Anchor.INNER_BOTTOM requires a shelled body")
        face_z = _combine(z, wall)
    else:
        face_z = _combine(z, thickness / 2)
    if child.kind == "linear_pattern":
        feature, count, spacing, axis = child.data
        shifts = [((n - (count - 1) / 2) * spacing, axis)
                  for n in range(count)]
    else:
        feature, shifts = child, [(0, None)]
    if feature.kind not in (
            "cylinder", "hole", "lip", "snap_fit", "boss", "rest"):
        raise ValueError("unsupported anchored feature")
    if feature.kind == "hole":
        if parent_anchor not in (Anchor.TOP, Anchor.BOTTOM):
            raise ValueError("Hole must be placed on a planar exterior face")
        if child_anchor is not Anchor.BOTTOM:
            raise ValueError("Hole uses its entry point, not a volume center")
    if feature.kind in ("lip", "snap_fit", "boss", "rest"):
        if child_anchor is not Anchor.BOTTOM:
            raise ValueError("plastic features use their supporting point as Anchor.BOTTOM")
        if parent_anchor not in (Anchor.TOP, Anchor.BOTTOM, Anchor.INNER_BOTTOM):
            raise ValueError("plastic features require a supported planar anchor")
        height = None
    else:
        height = feature.data[0] if feature.kind == "cylinder" else None
    if feature.kind == "cylinder":
        if child_anchor is Anchor.BOTTOM:
            base_z = face_z
        elif child_anchor is Anchor.CENTER:
            base_z = _combine(face_z, -(height / 2))
        else:
            base_z = _combine(face_z, -height)
    else:
        base_z = face_z
    result = []
    offset_x = _bound_offset(offset[0], width, "X")
    offset_y = _bound_offset(offset[1], depth, "Y")
    for shift, axis in shifts:
        dx, dy = ((shift, 0) if axis is Axis.X else
                  ((0, shift) if axis is Axis.Y else (0, 0)))
        xx = _combine(x, width / 2, offset_x, dx)
        yy = _combine(y, depth / 2, offset_y, dy)
        # The edge samples are intentionally strictly within straight segments
        # on filleted rectangular faces (midpoints, not rounded corners).
        if not on_boss and parent_anchor in (Anchor.TOP, Anchor.BOTTOM) and child_anchor is Anchor.BOTTOM:
            refs = [
                {"edge": [value_of(x), value_of(y) + value_of(depth)/2, value_of(face_z)],
                 "distance": command_value(_combine(width / 2, offset_x, dx))},
                {"edge": [value_of(x) + value_of(width)/2, value_of(y), value_of(face_z)],
                 "distance": command_value(_combine(depth / 2, offset_y, dy))}
            ]
        else:
            refs = None
        # Native solid.hole uses a numeric authoring pick. For holes on the
        # joined circular boss no stable straight-edge references exist yet.
        # Do not pass unevaluated expressions as its position coordinates.
        if feature.kind in ("hole", "lip", "snap_fit", "boss", "rest") or refs:
            position = [value_of(xx), value_of(yy), value_of(base_z)]
        else:
            position = [command_value(xx), command_value(yy), command_value(base_z)]
        result.append((feature, position, refs))
    return result


