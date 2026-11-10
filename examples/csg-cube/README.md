# CSG Cube — Python SCPF comparison

The Python [SCPF model](scpf/model.py) intersects a sphere with a cube
and subtracts three perpendicular cylindrical bores. Nominal size: 50 mm.

The [reviewed native commands](scpf/reference.json) are regression
fixtures for the SolidCraft Python compiler.

```powershell
python -m scpf examples/csg-cube/scpf/model.py --out output/csg-cube.json
code output/csg-cube.json
```

CadQuery, µcad, vcad and PythonSCAD examples remain available for
modeling-syntax comparisons. SolidCraft is the SCPF geometry engine.
