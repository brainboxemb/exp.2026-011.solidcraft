# Experiment 011 — agent guidance

Start with [README.md](README.md) and [docs/00-plan.md](docs/00-plan.md).

Keep the public Rust CAD domain independent from SolidCraft command names and transport details. The adapter may translate one semantic feature into several SolidCraft commands. SolidCraft remains the only geometry engine.

Do not claim working CAD until it has been run against a named SolidCraft version. Keep PartCAD, OpenSCAD migration and shared production tooling outside this experiment.
