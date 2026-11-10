# Plastic Enclosure Pi — video reconstruction

This is a separate practical SCPF example, independent of the small
[`history-policy`](../history-policy/) demonstration.

## Correct source

The supplied [`source/enclosure_steps.json`](source/enclosure_steps.json) describes
**another** enclosure (80 × 60 × 30 mm, R6, USB port and four bosses). It
does not describe the Raspberry Pi 4 video. Keep it for comparison, not as the
implementation target.

The Raspberry Pi 4 video is scripted in upstream SolidCraft
[`examples/demo/enclosure_ui_mcp.py`](https://github.com/tangency-labs/solidcraft/blob/main/examples/demo/enclosure_ui_mcp.py),
function `run_pi` (`--story pi`).

## Implemented video steps

1. Parameters: `board_w = 85 mm`, `board_d = 56 mm`,
   `height = 24 mm`, `wall = 2 mm`.
2. Centered XY rectangle dimensioned as `board_w + 10 mm = 95 mm` by
   `board_d + 10 mm = 66 mm`.
3. Extrude to `height = 24 mm`.
4. Fillet the four vertical edges, **R5 mm**.
5. Shell from the top face, **2 mm wall**, leaving the top open.

The current Python model deliberately stops after Shell, so the saved geometry
can be compared with this point in the video before proceeding.

## Next steps in the video (not yet implemented)

The 0.8 video next rounds the upper rim by 1 mm, builds an annular M2.5
standoff and patterns it over 58 × 49 mm, makes connector and ventilation
cuts, adds `Pi 4` text and PETG material, then changes height from 24 to 32 mm.

These are **not** the USB sketch or four native bosses from the older JSON.
