"""Lower reusable SCPF model instances to native SolidCraft components."""
import re

from .compiler import ModelError
from .model_objects import Assembly, ModelInstance
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

    by_definition = {}
    for instance in assembly.instances:
        by_definition.setdefault(instance.definition.key, []).append(instance)

    for key, instances in by_definition.items():
        definition = instances[0].definition
        component_name = names[key]

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
        commands.append(_command(
            "component.create",
            name=component_name,
            grounded=False,
        ))
        commands.extend(geometry_commands)
        commands.append(_command("component.activate", component="root"))

        first = instances[0]
        if any(first.translation):
            commands.append(_command(
                "occurrence.move",
                occurrence=f"{component_name}:1",
                translate=list(first.translation),
            ))

        for instance in instances[1:]:
            params = {"component": component_name}
            if any(instance.translation):
                params["translate"] = list(instance.translation)
            commands.append(_command("occurrence.copy", **params))

    if not commands:
        raise ModelError(f"{name} contains no component instances")
    return {"commands": commands}
