# 00 — Experiment plan

## Goal

Build a semantic **Rust CAD API** for SolidCraft. The user describes a part in CAD terms; the adapter decides how to construct it in SolidCraft.

CadQuery, vcad, µcad and PythonSCAD are interface-design references only. We compare five implementations: SolidCraftForge, CadQuery, µcad, vcad and PythonSCAD.

## Architecture

```text
CAD domain → SolidCraft adapter → script / GUI / MCP → SolidCraft engine
```

## Current scope

- centered box
- typed lengths
- outside vertical-edge fillet
- semantic top-face selection
- workplane
- circular through-holes
- SolidCraft script transport

## Qualification

| Case | Requirement |
|---|---|
| API-01 | CAD types remain independent from SolidCraft JSON |
| API-02 | CAD features expand into the expected native command sequence |
| API-03 | units and invalid dimensions are checked |
| API-04 | top-face workplane works in SolidCraft 0.30.1 |
| API-05 | exported geometry has intended dimensions, holes and fillets |
| API-06 | native `.sc` history remains editable after save/reopen |
| API-07 | runtime failures identify the failing native command |
| API-08 | same CAD domain can later use GUI or MCP transport |

Do not implement a second geometry engine or claim general topology selection before runtime qualification.

## Generated model evidence

The source branch keeps the example scripts and reviewed SolidCraft command
fixtures. Generated binary geometry is not committed alongside source.

After **all five** implementations have qualified for each comparison example,
publish the results together to a separate orphan branch named
`generated-examples`. Do not create or update that branch from an incomplete
or failing comparison run. Do not use a branch named `output`.

Expected directory layout:

```text
generated-examples (orphan branch)
├── plate/
│   ├── solidcraftforge/
│   ├── cadquery/
│   ├── microcad/
│   ├── vcad/
│   └── pythonscad/
└── csg-cube/
    ├── solidcraftforge/
    ├── cadquery/
    ├── microcad/
    ├── vcad/
    └── pythonscad/
```

Each implementation directory retains generated geometry in its actually
supported format (STEP, STL, and native `.sc` where available), a preview
when rendering succeeds, measurements and relevant diagnostics. Do not invent
STEP files for mesh-only results. In particular, vcad's CSG cube currently
falls back to a mesh after some boolean operations; the geometry and the
loss of BRep must both be recorded, not silently treated as a STEP success.

GitHub Pages can then present these same results for visual inspection.
The page must make unavailable previews and missing formats explicit.
Workflow artifacts remain useful as temporary evidence before publication.
