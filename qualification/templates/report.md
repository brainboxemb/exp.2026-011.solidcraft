# SCPF Forge qualification

- Commit: `$source_commit`
- Target SolidCraft: `$solidcraft_version`
- Result schema: `$schema_version`

## Qualification cases

| Case | Overall | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
$case_rows

## Native visual evidence

$image_sections

## Result data

The machine-readable source of this report is `results.json`. Each native case
directory also contains its own `qualification-result.json`, together with the
SolidCraft measurements, saved models, STEP exports and PNG snapshots used as
evidence.

## Qualification model

- **Q1 — Python API:** public API validation and compiler invariants.
- **Q2 — Command contract:** generated SolidCraft command JSON is complete and inspectable.
- **Q3 — Native build:** SolidCraft accepts the command plan and saves an editable design.
- **Q4 — Native semantic validation:** body bounds, feature evidence and joint/anchor relationships are checked against independent expected geometry.
- **Q5 — Parametric mutation:** required saved designs re-solve correctly after parameter changes.
- **Q6 — Visual regression:** fixed front/right/isometric native views are compared with approved reference rasters and diff overlays are retained.

The report structure comes from `qualification/templates/report.md`; CI supplies
the result data but does not construct the document with inline shell markup.
