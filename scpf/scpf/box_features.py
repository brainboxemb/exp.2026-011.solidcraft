"""Native SolidCraft feature compilation for axis-aligned Box bodies.

The implementation is intentionally feature-oriented: Box, Fillet and Hole.
A model name such as Plate never determines compiler behavior.
"""
from .core import Shape, Edges, Depth, command_value, value_of
from .compiler import ModelError, _command, _param_commands, _collect, _require_positive
from .sketch_features import _anchored_features


def _is_box_feature(node):
    if not isinstance(node, Shape):
        return False
    if node.kind == "box":
        return True
    if node.kind in ("fillet", "union", "difference"):
        return _is_box_feature(node.data[0])
    return False


def _compile_body(node, name):
    if node.kind == "box":
        length, width, thickness = node.data
        l = _require_positive(length, "box length")
        w = _require_positive(width, "box width")
        _require_positive(thickness, "box height")
        # Native editable footprint, as used by the reviewed Plate fixture.
        from .csg import _half
        return [
            _command("sketch.create", plane="XY", name=f"{name} footprint"),
            _command("sketch.rectangle.two_point",
                     p0=[_half(length, True), _half(width, True)],
                     p1=[_half(length), _half(width)]),
            _command("sketch.finish"),
            _command("solid.extrude", distance=command_value(thickness),
                     body_name=name),
        ], (length, width, thickness)

    if node.kind == "fillet":
        body, radius, edges = node.data
        steps, dims = _compile_body(body, name)
        if edges is not Edges.VERTICAL:
            raise ModelError("Box fillet currently supports vertical edges")
        l, w, h = (value_of(v) for v in dims)
        r = _require_positive(radius, "fillet radius")
        if r * 2 >= min(l, w):
            raise ModelError("fillet radius exceeds box dimensions")
        picks = [[x, y, h / 2]
                 for x, y in ((-l/2, -w/2), (l/2, -w/2),
                              (l/2, w/2), (-l/2, w/2))]
        steps.append(_command("solid.fillet", edges=picks,
                              radius=value_of(radius), body=name))
        return steps, dims

    if node.kind in ("union", "difference"):
        body, feature = node.data
        steps, dims = _compile_body(body, name)
        if feature.kind == "anchored":
            child, target, _, _, _ = feature.data
            if target != body:
                raise ModelError("Hole must refer to the body being modified")
            try:
                features = _anchored_features(feature)
            except (TypeError, ValueError) as exc:
                raise ModelError(str(exc)) from exc
            for primitive, position, references in features:
                if primitive.kind != "hole":
                    raise ModelError("Box attachments currently require Hole")
                diameter, hole_depth = primitive.data
                _require_positive(diameter, "hole diameter")
                params = dict(position=position, diameter=command_value(diameter),
                              targets=[name])
                if hole_depth is not Depth.THROUGH_ALL:
                    _require_positive(hole_depth, "hole depth")
                    params["depth"] = command_value(hole_depth)
                if references:
                    params["references"] = references
                steps.append(_command("solid.hole", **params))
            return steps, dims
        if feature.kind == "placed3d" and feature.data[0].kind == "hole":
            hole, x, y, z = feature.data
            diameter, hole_depth = hole.data
            _require_positive(diameter, "hole diameter")
            params = dict(position=[value_of(x), value_of(y), value_of(z)],
                          diameter=command_value(diameter), targets=[name])
            if hole_depth is not Depth.THROUGH_ALL:
                _require_positive(hole_depth, "hole depth")
                params["depth"] = command_value(hole_depth)
            steps.append(_command("solid.hole", **params))
            return steps, dims
        raise ModelError("Box feature operation requires an attached/placed Hole")

    raise ModelError(f"unsupported Box operation: {node.kind}")


def compile_box_features(shape, name):
    steps, _ = _compile_body(shape, name)
    return _param_commands(_collect(shape)) + steps
