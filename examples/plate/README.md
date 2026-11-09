# Plate fillet / feature comparison

This case tests the feature-style operations that matter for Experiment 011:

- a 100 × 60 × 10 mm plate;
- R2 fillets on the four **vertical outside edges**;
- four Ø8 through-holes at (±35, ±15) mm;
- final bounding box 100 × 60 × 10 mm;
- reference volume about 57,955.04 mm³.

The fillet is the main reason this example exists. In plain OpenSCAD a true
edge fillet is not a native modeling feature; it usually requires constructive
geometry such as hulls, Minkowski operations or cutters.

## Variants

- `solidcraftforge/model.rs` — ordinary Rust `Plate` type; the script ends with `Plate::new(...)`.
- `solidcraftforge/solidcraft.json` — reviewed native SolidCraft command sequence.
- `cadquery/model.py` — native BRep edge fillet via `.edges("|Z").fillet(2)`.
- `vcad/model.rs` — native BRep selective edge blend using a direction query.
- `pythonscad/model.py` — PythonSCAD's native mesh fillet with an edge-selection mask.
- `microcad/model.mu` — µcad 0.6.0 has no native 3D fillet operation. It uses
  an explicitly constructed rounded 2D footprint followed by extrusion, which
  is geometrically equivalent for this particular plate but is **not** a general
  fillet feature. The 0.6.0 `RoundedRect` builtin parses but does not export
  successfully, so the example uses rectangles plus corner circles.

Execution and export plumbing stays outside these model files.
