# Named oriented AnchorFrame

## Nederlands — wat is een joint origin?

**Een joint origin op een bracket (beugel) is het digitale ankerpunt waarmee je het onderdeel vastzet.**
Je kunt dit het beste zien als een klein lokaal assenstelsel met een eigen X-, Y- en Z-as.

### 1. Eenvoudige uitleg: de basisassen

Elk onderdeel kan één of meer lokale bevestigingspunten hebben. Zo'n punt bestaat uit een positie en een richting.

- **Origin (het nulpunt):** het precieze punt op de beugel waar het lokale assenstelsel begint. Bijvoorbeeld het midden van een schroefgat.
- **Z-as (de normaal):** deze pijl bepaalt welke kant het bevestigingspunt op wijst. Denk aan de richting waarin een bout of schroef vanaf dat punt wegloopt.
- **X-as (de draaiing):** zodra de Z-as vastligt, kun je het onderdeel nog steeds om die Z-as draaien. De X-as legt die 'klokstand' vast.
- **Y-as (automatisch):** zodra Z en X bekend zijn, kan de software de derde as automatisch berekenen. De drie assen staan loodrecht op elkaar.

Een handige manier om dit te onthouden:

```text
origin = waar zit het punt?
Z      = welke kant kijkt het punt op?
X      = hoe is het rond die richting gedraaid?
Y      = volgt automatisch
```

### 2. API-definitie als JSON

In een algemene CAD-API kun je hetzelfde frame bijvoorbeeld zo beschrijven:

```json
{
  "joint_origin": {
    "name": "beugel_bevestigingspunt_1",
    "description": "Midden van het bovenste schroefgat",
    "origin": {
      "x": 10.0,
      "y": 25.0,
      "z": 0.0
    },
    "axes": {
      "z_direction": [0, 0, 1],
      "x_direction": [1, 0, 0],
      "y_direction": "auto_calculated"
    }
  }
}
```

Hoe je dit leest:

- **`origin`** — de positie van het nulpunt in millimeters.
- **`z_direction`** — de richting van de lokale Z-as. `[0, 0, 1]` betekent recht omhoog langs de globale +Z-as.
- **`x_direction`** — de richting van de lokale X-as. `[1, 0, 0]` betekent naar rechts langs de globale +X-as.
- **`y_direction`** — hoeft normaal niet handmatig te worden opgegeven; de software leidt deze af uit X en Z.

### 3. Dezelfde gedachte in Forge

Forge gebruikt hiervoor `AnchorFrame`.

Voor gewone 90°-richtingen hoef je geen vectoren te schrijven:

| Forge | Vector | Richting |
| --- | --- | --- |
| `RIGHT` | `(1, 0, 0)` | +X |
| `LEFT` | `(-1, 0, 0)` | -X |
| `BACK` | `(0, 1, 0)` | +Y |
| `FRONT` | `(0, -1, 0)` | -Y |
| `UP` | `(0, 0, 1)` | +Z |
| `DOWN` | `(0, 0, -1)` | -Z |

Voorbeeld:

```python
AnchorFrame(
    origin=(10, 25, 0),
    z=RIGHT,
    x=UP,
)
```

Dat betekent letterlijk:

- het bevestigingspunt zit op `(10, 25, 0)`;
- de lokale Z-as wijst naar rechts;
- de lokale X-as wijst omhoog;
- de lokale Y-as volgt automatisch uit die twee richtingen.

Voor een schuine of bijzondere richting mag je nog steeds een gewone vector gebruiken.

---

## English — what is a joint origin?

**A joint origin on a bracket is the digital attachment point used to connect the part.**
The easiest way to think about it is as a small local coordinate system with its own X, Y and Z axes.

### 1. Simple explanation: the local axes

Each component can expose one or more local attachment points. Such a point has both a position and an orientation.

- **Origin:** the exact point on the bracket where the local coordinate system starts, for example the centre of a screw hole.
- **Z axis (normal):** defines which way the attachment point faces. Think of the direction in which a bolt or screw would extend away from the surface.
- **X axis (clocking):** once Z is fixed, the part can still rotate around Z. The X axis fixes that remaining clock position.
- **Y axis (automatic):** once Z and X are known, the third axis can be calculated automatically. The three axes remain perpendicular.

A useful shorthand is:

```text
origin = where is the point?
Z      = which way does it face?
X      = how is it rotated around that direction?
Y      = calculated automatically
```

### 2. Generic API representation

The same frame can be represented in a CAD API like this:

```json
{
  "joint_origin": {
    "name": "bracket_mount_1",
    "description": "Centre of the upper screw hole",
    "origin": {
      "x": 10.0,
      "y": 25.0,
      "z": 0.0
    },
    "axes": {
      "z_direction": [0, 0, 1],
      "x_direction": [1, 0, 0],
      "y_direction": "auto_calculated"
    }
  }
}
```

How to read it:

- **`origin`** — the local attachment point in millimetres.
- **`z_direction`** — direction of the local Z axis. `[0, 0, 1]` means global +Z.
- **`x_direction`** — direction of the local X axis. `[1, 0, 0]` means global +X.
- **`y_direction`** — normally does not need to be supplied; it can be derived from X and Z.

### 3. The same idea in Forge

Forge represents this with `AnchorFrame`:

```python
AnchorFrame(
    origin=(10, 25, 0),
    z=RIGHT,
    x=UP,
)
```

For the six main directions, Forge exposes readable names instead of forcing the model author to write vectors manually:

`RIGHT`, `LEFT`, `FRONT`, `BACK`, `UP`, `DOWN`.

Arbitrary XYZ vectors remain valid for non-axis-aligned attachment frames.

## Qualification case

In this fixture the arm publishes a named frame called `tip`:

```python
def anchors(self):
    return {
        "tip": AnchorFrame(
            origin=(20, 0, 5),
            z=RIGHT,
            x=UP,
        ),
    }
```

The marker publishes the mating frame:

```python
def anchors(self):
    return {
        "mount": AnchorFrame(
            origin=(0, 0, 5),
            z=LEFT,
            x=UP,
        ),
    }
```

They are connected by name:

```python
marker = Marker().attach(
    arm,
    parent="tip",
    child="mount",
)
```

The arm occurrence is then rotated 90 degrees around global Z. The important part is that the `tip` frame belongs to the arm, so the frame rotates with the arm rather than becoming a frozen world-space XYZ point.

## Acceptance criteria

- the parent occurrence may rotate independently;
- the named frame rotates with the parent;
- the marker remains attached to the rotated frame;
- the marker keeps the authored Z/X orientation;
- Forge does not hard-code the rotated world position of the frame.

## Reference model

**BOSL2** uses the same general concept: an anchor is more than a point. It combines position with local orientation. BOSL2 represents the remaining rotation around the normal with `spin`; Forge keeps the local frame explicit with Z and X.
