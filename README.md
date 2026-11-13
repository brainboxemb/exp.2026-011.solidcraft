# SCPF — SolidCraft Python Forge

**Repository:** `brainboxemb/lib.py.solidcraft.forge` (previously `lib.py.solidcraft`).
**Python package and command:** still `scpf`; no code-level rename required.
**Companion native-command library:** [SCPC](https://github.com/brainboxemb/lib.py.solidcraft.cmd), with package/command `scpc`.

`lib.py.solidcraft.forge` owns the **reusable Python API, native command compiler, runner and unit tests** for the [SolidCraft](https://github.com/tangency-labs/solidcraft) CAD engine.

SCPF models are plain Python classes with a `build()` method. The package
compiles these to **native SolidCraft command JSON**. The SolidCraft engine,
not SCPF, creates and saves the actual editable CAD geometry and feature history.

## Install and test this library

From this repository root, in the active Python/Conda environment:

```powershell
python -m pip install -e ./scpf
python -m unittest discover -s scpf/tests -v
```

There is no mandatory `main()` or `show()`. The tiny
[examples and SCPF cheatsheet](https://brainboxemb.github.io/lib.py.solidcraft.forge/)
are generated from source, command-compiled, **rendered by native SolidCraft**
and regression-checked in CI.
The library website also provides a [full, multi-chapter API Guide](https://brainboxemb.github.io/lib.py.solidcraft.forge/guide/) covering geometry, transforms, native features, reusable components and verification.
[Why SCPF delegates geometry to SolidCraft](scpf/docs/architecture.md) explains the code structure, native component placement and verification.

SolidCraft compatibility: **0.30.1 tested**; older versions are refused by the native-version guard, newer ones generate a warning. See the
[SCPF API guide](scpf/README.md) for parameters, placement, sketches, features,
reusable components, and GUI/CLI execution.

## Reusable component parameters

Component parameters are implicit. Public lower-case numeric fields become
editable native parameters when the component owns that value:

```python
@component
class Bracket:
    width = 24.0
    inside_corner_radius = 4.0
```

When a parent `Parameter` or expression is passed into a child input, Forge
reuses that existing symbolic dependency instead of creating a duplicate
component parameter:

```python
bracket = Bracket(
    width=self.bracket_width,
    inside_corner_radius=self.corner_radius,
)
```

The naming contract is the same everywhere: public `lower_case` values are
editable, `_private_lower_case` values are Forge/build-time inputs, and
`UPPER_CASE` values are fixed constants. There is no separate component
parameter publication switch.

## CAD projects live in another repository

**[2026-011-02.cad.solidcraft](https://github.com/brainboxemb/2026-011-02.cad.solidcraft)** contains the actual models and native output:

- [Corner Bracket](https://github.com/brainboxemb/2026-011-02.cad.solidcraft/tree/main/models/corner-bracket)
- [HUB75 panel and component occurrences](https://github.com/brainboxemb/2026-011-02.cad.solidcraft/tree/main/models/hub75-panel)
- [Raspberry Pi enclosure](https://github.com/brainboxemb/2026-011-02.cad.solidcraft/tree/main/models/plastic-enclosure-pi)
- [Other CAD models](https://github.com/brainboxemb/2026-011-02.cad.solidcraft/tree/main/models)

The CAD project uses [vcs2l](https://github.com/ros-infrastructure/vcs2l)
and an exact Git commit in `dependencies.repos` to import the library under
`ext/scpf`. Its `bootstrap.ps1` installs `ext/scpf/scpf` editable.
No Git submodules or manual `PYTHONPATH` setup are required.

Native renders and the CAD model catalog are published on the
[CAD results website](https://brainboxemb.github.io/2026-011-02.cad.solidcraft/).

## Migration status

This repository was renamed from `exp.2026-011.solidcraft` on 2026-11-11,
preserving its issues, pull requests and history. The CAD repository is
separate and has passed its first Python, native SolidCraft and Pages build
checks. Only the small, independent API fixtures remain under `examples/` on
`main`. Historical CAD models and the old results website remain in Git history
in Git history. The **CAD project** is the current owner, while the
library's `gh-pages` branch now publishes only three tiny API examples and
the cheatsheet (no duplicate native CAD gallery).

The migration is tracked in [issue #25](https://github.com/brainboxemb/lib.py.solidcraft.forge/issues/25).

## License

The package exposes SolidCraft's native command interface; SolidCraft itself is
an independent open-source CAD application. See the respective repositories for
their current license information.
