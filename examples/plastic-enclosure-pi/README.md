# Plastic Enclosure Pi — Raspberry Pi 4 video reconstruction

A practical SCPF example kept separate from [`history-policy`](../history-policy/).

## Upstream sources

**Video implementation (authoritative for this example):**
[`tangency-labs/solidcraft/examples/demo/enclosure_ui_mcp.py`, `run_pi()`, lines 558–705](https://github.com/tangency-labs/solidcraft/blob/main/examples/demo/enclosure_ui_mcp.py#L558-L705).

Useful locations in that script:

- [Lines 567–617](https://github.com/tangency-labs/solidcraft/blob/main/examples/demo/enclosure_ui_mcp.py#L567-L617): parameters, 95 × 66 mm rectangle, 24 mm extrusion, R5 corners, 2 mm shell and R1 rim.
- [Lines 619–659](https://github.com/tangency-labs/solidcraft/blob/main/examples/demo/enclosure_ui_mcp.py#L619-L659): one annular Ø6/Ø2.5 standoff, 4 mm extrusion, rectangular 58 × 49 mm pattern.
- [Lines 661–689](https://github.com/tangency-labs/solidcraft/blob/main/examples/demo/enclosure_ui_mcp.py#L661-L689): three side connector openings, the USB/Ethernet end opening, and five floor ventilation slots.
- [Lines 492–530](https://github.com/tangency-labs/solidcraft/blob/main/examples/demo/enclosure_ui_mcp.py#L492-L530): `Pi 4` engraved lettering and PETG material settings.
- [Lines 697–704](https://github.com/tangency-labs/solidcraft/blob/main/examples/demo/enclosure_ui_mcp.py#L697-L704): final height change 24 → 32 mm.

The script uses the `--story pi` path for the 0.8 Raspberry Pi 4 demo.
Its UI operations (clicks and camera movements) are not part of our CAD model.

**Different demo — not the Raspberry Pi video:** the supplied
[`source/enclosure_steps.json`](source/enclosure_steps.json) is an 80 × 60 × 30 mm
generic electronics enclosure (R6 fillets, USB sketch and four bosses). It is
retained only for comparison.

## Current SCPF implementation

[`scpf/model.py`](scpf/model.py) now describes:

1. 95 × 66 × 24 mm shell, 2 mm wall, R5 vertical corners, and R1 top rim.
2. Four Ø6 mm bosses with Ø2.5 mm holes at the source's initial 58 × 49 mm pattern locations.
3. Three openings on the front (-Y) face (USB-C and two micro-HDMI).
4. One 50 × 14 mm combined USB/Ethernet opening at the right (+X) end.
5. Five separate 5 × 28 mm floor ventilation slots at 7 mm spacing along X.
6. `Pi 4` engraving, 6 mm DejaVu Sans Bold, depth 0.6 mm.
7. PETG design-owned material, density 1.27 g/cm³, color `#2a8696`.
8. CI replay of the final 24 → 32 mm height parameter edit.

### Differences / outstanding verification

The original video creates **one annular sketch and then a native feature pattern**.
The current SCPF prototype instead emits **four native Boss features**. The visible
geometry is the target, but the editable feature-history is not yet identical.

The original recording creates a 28 × 5 mm slot and patterns it 7 mm along its 28 mm length, which overlaps cuts. Our model uses separate 5 × 28 mm slots for the intended five vents; this is a deliberate correction, **not** an exact feature-history match.

The lettering and PETG material are compiled as native SolidCraft operations.
The final height change is checked by the native CI workflow, not baked into the
initial Python object's 24 mm height. Native execution and visual equivalence
still require qualification.
