"""SCPF: compact Python CAD descriptions compiled to SolidCraft commands.

SolidCraft remains the sole geometry engine. No geometry is calculated here.
Supported proof of concept: CSG cube/sphere/cylinders and a filleted Plate
with a centered rectangular pattern of through cylinders.
"""
from .core import Box, Cube, Cylinder, Sphere, Polygon, Rectangle, Circle, Box3D, Cylinder3D, Sphere3D, Rectangle2D, Circle2D, Polygon2D, Shape, Parameter, Direction, X, Y, Z
from .compiler import compile_model, ModelError
from .runner import run_script

__all__ = [
    "Box", "Cube", "Cylinder", "Sphere", "Polygon", "Rectangle", "Circle", "Rectangle2D", "Circle2D", "Polygon2D", "Box3D", "Cylinder3D", "Sphere3D", "Shape", "Parameter", "Direction",
    "X", "Y", "Z", "compile_model", "run_script", "ModelError",
]
