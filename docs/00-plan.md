# 00 — Experiment plan

## Goal

Build a semantic **Rust CAD API** for SolidCraft. The user describes a part in CAD terms; the adapter decides how to construct it in SolidCraft.

CadQuery, vcad and µcad are interface-design references only.

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
