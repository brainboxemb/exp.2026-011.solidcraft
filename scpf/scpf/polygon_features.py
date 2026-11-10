"""Polygon profiles and feature history translated to SolidCraft.

Shared with Bracket and other polygon-extruded bodies; no model-name dispatch.
"""
from math import isfinite
from .core import Shape, Edges, command_value, value_of
from .compiler import ModelError, _command, _collect, _param_commands, _require_positive

def _has_profile(shape):
    if shape.kind == "polygon":
        return True
    if shape.kind in ("fillet", "extrusion", "union"):
        return _has_profile(shape.data[0])
    return False


def compile_polygon_features(shape, name):
    """Compile a polygon extrusion and its ordered CAD modifiers.

    One closed planar polygon, one extrusion, optional edge fillet and
    zero or more native Hole features are supported. Coordinates are
    evaluated at the supplied parameter defaults; general parametric sketch
    constraints are intentionally not claimed.
    """
    # Native Hole features added with + are part of the ordered CAD history.
    native_holes = []
    while shape.kind == "union":
        base, feature = shape.data
        if feature.kind != "placed3d" or feature.data[0].kind != "hole":
            raise ModelError("polygon bodies support positioned Hole features")
        primitive, x, y, z = feature.data
        native_holes.append((primitive, x, y, z))
        shape = base
    native_holes.reverse()

    fillet = None
    if shape.kind == "fillet":
        shape, radius, edges = shape.data
        if edges is Edges.VERTICAL:
            raise ModelError("polygon fillet requires explicit 3D edge points")
        fillet = (radius, edges)

    if shape.kind != "extrusion":
        raise ModelError("profile features require a Polygon extrusion")
    polygon, distance, direction = shape.data
    if polygon.kind != "polygon":
        raise ModelError("extrude() requires a Polygon")
    points, sketch_plane = polygon.data
    _require_positive(distance, "extrusion distance")
    if direction not in ("positive", "negative"):
        raise ModelError("invalid extrusion direction")

    # Closed sketch uses real coordinates; SolidCraft may later support
    # symbolic point constraints, but this is not established here.
    concrete_points = []
    for point in points:
        coords = [value_of(v) for v in point]
        if not all(isfinite(x) for x in coords):
            raise ModelError("non-finite polygon coordinate")
        concrete_points.append(coords)

    # Avoid silently introducing invalid zero-length sketch edges.
    if len(set(tuple(x) for x in concrete_points)) != len(concrete_points):
        raise ModelError("duplicate polygon vertices")
    for p, q in zip(concrete_points, concrete_points[1:] + concrete_points[:1]):
        if p == q:
            raise ModelError("zero-length polygon edge")

    steps = [
        _command("sketch.create", plane=sketch_plane, name="Profile"),
        _command("sketch.line", points=concrete_points, closed=True,
                 ids=[chr(ord("a") + i) for i in range(len(points))]),
        _command("sketch.finish"),
        _command("solid.extrude", distance=command_value(distance),
                 direction=direction, body_name=name),
    ]
    if fillet is not None:
        radius, edges = fillet
        _require_positive(radius, "fillet radius")
        locations = []
        for point in edges:
            coords = [value_of(x) for x in point]
            if not all(isfinite(x) for x in coords):
                raise ModelError("non-finite edge selection")
            locations.append(coords)
        steps.append(_command("solid.fillet", edges=locations,
                              radius=value_of(radius)))

    for feature, x, y, z in native_holes:
        diameter, hole_depth = feature.data
        _require_positive(diameter, "hole diameter")
        params = dict(position=[value_of(x), value_of(y), value_of(z)],
                      diameter=command_value(diameter), targets=[name])
        from .core import Depth
        if hole_depth is not Depth.THROUGH_ALL:
            _require_positive(hole_depth, "hole depth")
            params["depth"] = command_value(hole_depth)
        steps.append(_command("solid.hole", **params))
    return _param_commands(_collect((distance, shape, native_holes))) + steps


