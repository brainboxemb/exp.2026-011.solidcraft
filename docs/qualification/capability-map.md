# CAD capability coverage and API references

Forge should not be judged only by the functions it already happens to expose.
We also need to know whether the API covers the important capabilities of its
native CAD engine and whether the resulting Python interface is coherent.

## Reference roles

**SolidCraft** is the capability truth. Forge should use native parametric
features and topology instead of becoming a second CAD kernel.

**PythonSCAD** is the primary Python API ergonomics reference. Its first-class
solids, operators and normal Python composition are useful checks for whether
Forge feels natural to script.

**BOSL2** is the main reference for anchors, attachables and local coordinate
frames. Forge does not need API compatibility, but it should be equally clear
about location versus orientation versus parent-relative placement.

**OpenSCAD** remains the minimal CSG/transform baseline. If a basic Forge
operation is harder to understand than its OpenSCAD equivalent, that is a
warning sign.

## Capability-based coverage

SolidCraft exposes hundreds of automation commands. Mirroring them would make
Forge a huge wrapper instead of a usable CAD API.

The capability map groups the engine into user-level areas:

- geometry fundamentals;
- sketches and parametric profiles;
- part features and face references;
- components, occurrences and relationships;
- advanced modelling;
- inspection and exchange.

For every capability we track what SolidCraft can do, what Forge exposes
today, whether the gap matters to current projects, and which external API is
the useful design reference.
