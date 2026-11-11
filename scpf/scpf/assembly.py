"""Lower reusable SCPF model instances to native SolidCraft components."""
import re

from .compiler import ModelError
from .model_objects import Assembly, ModelInstance, _anchor_point
from .compiler import compile_model


_IDENTIFIER = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def _command(command_name, **params):
    return {"command": command_name, "params": params}


def _component_slug(name):
    text = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_")
    if not text:
        text = "component"
    if text[0].isdigit():
        text = "_" + text
    return text


def _rewrite_value(value, mapping):
    if isinstance(value, str):
        return _IDENTIFIER.sub(lambda m: mapping.get(m.group(0), m.group(0)), value)
    if isinstance(value, list):
        return [_rewrite_value(item, mapping) for item in value]
    if isinstance(value, tuple):
        return [_rewrite_value(item, mapping) for item in value]
    if isinstance(value, dict):
        return {key: _rewrite_value(item, mapping) for key, item in value.items()}
    return value


def _namespace_commands(commands, component_name):
    """Make design-wide SolidCraft parameter names unique per component definition."""
    local_names = [
        command["params"]["name"]
        for command in commands
        if command["command"] == "parameters.add"
    ]
    prefix = _component_slug(component_name)
    mapping = {name: f"{prefix}_{name}" for name in local_names}

    result = []
    for command in commands:
        params = dict(command["params"])
        if command["command"] == "parameters.add":
            params["name"] = mapping[params["name"]]
        else:
            params = _rewrite_value(params, mapping)
        result.append({"command": command["command"], "params": params})
    return result


def _as_assembly(value):
    if isinstance(value, ModelInstance):
        return Assembly((value,))
    if isinstance(value, Assembly):
        return value
    raise TypeError("assembly result must contain reusable model instances")


def _definition_names(assembly):
    """Assign stable component names in first-occurrence order."""
    names = {}
    class_counts = {}
    for instance in assembly.instances:
        key = instance.definition.key
        if key in names:
            continue
        base = instance.definition.class_name
        count = class_counts.get(base, 0) + 1
        class_counts[base] = count
        names[key] = base if count == 1 else f"{base} {count}"
    return names


def compile_assembly(value, name):
    """Compile a root assembly into reusable components and occurrences."""
    assembly = _as_assembly(value)
    names = _definition_names(assembly)
    commands = []
    occurrence_names = {}

    # Named groups are actual empty native components, not just labels in
    # Python. Child component definitions are created under their parent.
    # Native "component.create(parent=...)" makes the browser expandable.
    group_names = list(dict.fromkeys(
        instance.group_name
        for instance in assembly.instances
        if instance.group_name is not None
    ))
    if set(group_names) & set(names.values()):
        raise ModelError("assembly group name conflicts with a component name")
    for group_name in group_names:
        commands.append(_command(
            "component.create",
            name=group_name,
            activate=False,
            grounded=(assembly.instances[0].group_name == group_name),
        ))

    by_definition = {}
    for instance in assembly.instances:
        by_definition.setdefault(instance.definition.key, []).append(instance)

    for key, instances in by_definition.items():
        definition = instances[0].definition
        component_name = names[key]
        parent_names = {instance.group_name for instance in instances}
        if len(parent_names) != 1:
            raise ModelError(
                f"{component_name}: one reusable definition cannot currently "
                "be placed under multiple assembly parents"
            )
        parent_name = instances[0].group_name

        compiled = compile_model(
            definition.shape,
            _component_slug(component_name),
        )["commands"]
        compiled = _namespace_commands(compiled, component_name)
        parameter_commands = [
            command for command in compiled
            if command["command"] == "parameters.add"
        ]
        geometry_commands = [
            command for command in compiled
            if command["command"] != "parameters.add"
        ]

        commands.extend(parameter_commands)
        first_is_root = (
            instances[0] is assembly.instances[0] and parent_name is None
        )
        create_params = {"name": component_name, "grounded": first_is_root}
        if parent_name is not None:
            create_params["parent"] = parent_name
        commands.append(_command("component.create", **create_params))
        commands.extend(geometry_commands)
        commands.append(_command("component.activate", component="root"))

        first = instances[0]
        first_occurrence = f"{component_name}:1"
        occurrence_names[id(first)] = first_occurrence
        if first.rotation is not None:
            axis, angle = first.rotation
            commands.append(_command(
                "occurrence.move",
                occurrence=first_occurrence,
                to={
                    "position": list(first.translation),
                    "axis": list(axis),
                    "angle": f"{angle:g} deg",
                },
                move_grounded=first_is_root,
            ))
        elif any(first.translation):
            commands.append(_command(
                "occurrence.move",
                occurrence=first_occurrence,
                translate=list(first.translation),
                move_grounded=first_is_root,
            ))

        for index, instance in enumerate(instances[1:], start=2):
            params = {"component": component_name}
            if any(instance.translation):
                params["translate"] = list(instance.translation)
            commands.append(_command("occurrence.copy", **params))
            new_occurrence = f"{component_name}:{index}"
            occurrence_names[id(instance)] = new_occurrence
            if instance.rotation is not None:
                axis, angle = instance.rotation
                commands.append(_command(
                    "occurrence.move",
                    occurrence=new_occurrence,
                    to={
                        "position": list(instance.translation),
                        "axis": list(axis),
                        "angle": f"{angle:g} deg",
                    },
                ))

    for instance in assembly.instances:
        attachment = instance.attachment
        if attachment is None:
            continue
        child_occurrence = occurrence_names.get(id(instance))
        parent_occurrence = occurrence_names.get(id(attachment.target))
        if child_occurrence is None or parent_occurrence is None:
            raise ModelError("component attach target must be part of the assembly")

        parent_local = _anchor_point(attachment.target, attachment.parent)
        child_local = _anchor_point(instance, attachment.child)
        parent_face = [
            parent_local[i] + attachment.target.translation[i]
            for i in range(3)
        ]
        child_face = [
            child_local[i] + instance.translation[i]
            for i in range(3)
        ]
        commands.append(_command(
            "joint.create",
            type="rigid",
            name=f"Attach {child_occurrence} to {parent_occurrence}",
            a={"occurrence": parent_occurrence, "face": parent_face},
            b={"occurrence": child_occurrence, "face": child_face},
        ))

    if not commands:
        raise ModelError(f"{name} contains no component instances")
    return {"commands": commands}
