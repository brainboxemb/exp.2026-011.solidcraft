"""SCPF: compact Python CAD descriptions compiled to SolidCraft commands.

SolidCraft remains the sole geometry engine. No geometry is calculated here.
Supported proof of concept: CSG cube/sphere/cylinders and a filleted Plate
with a centered rectangular pattern of through cylinders.
"""
from .core import Box, Cube, Cylinder, Sphere, Polygon, Shape, Parameter, X, Y, Z
from .compiler import compile_model, ModelError
from .runner import run_script

__all__ = [
    "Box", "Cube", "Cylinder", "Sphere", "Polygon", "Shape", "Parameter",
    "X", "Y", "Z", "compile_model", "run_script", "ModelError",
]
