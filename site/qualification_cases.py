"""Qualification case metadata for the Forge library site.

Keep this deliberately explicit.  A qualification case is documentation of a
contract between the public Forge API, Forge's compiler model and native
SolidCraft behaviour.  The site and site tests both consume this table.
"""

REFERENCE_URLS = {
    "BOSL2": "https://github.com/BelfrySCAD/BOSL2/wiki/Tutorial-Attachment-Overview",
    "OpenSCAD": "https://openscad.org/documentation.html",
    "PythonSCAD": "https://github.com/pythonscad/pythonscad",
}


QUALIFICATION_LEVELS = [
    ("Q1", "Python API", "Public API validation, symbolic values and compiler invariants."),
    ("Q2", "Command contract", "Generated SolidCraft command JSON is complete and inspectable."),
    ("Q3", "Native build", "SolidCraft 0.30.1 accepts the command plan and saves an editable design."),
    ("Q4", "Native measurement", "Timeline and actual body measurements match the expected result."),
    ("Q5", "Parametric mutation", "A saved design re-solves correctly after parameters.change."),
    ("Q6", "Visual artifact", "A native snapshot makes orientation and placement reviewable."),
]


QUALIFICATION_CASES = [
    {
        "slug": "simple-box",
        "title": "Parameterized Box",
        "intent": "Establish the smallest model/parameter contract: three public Python fields create one editable native box.",
        "forge_api": "class fields -> Parameter; Box(length, width, height); build()",
        "forge_model": "One root Shape with symbolic length, width and height; no occurrence or assembly layer.",
        "lowering": "parameters.add for the public dimensions, followed by the native sketch/extrude commands used for Box.",
        "native_expectation": "One rectangular solid with the requested 40 x 30 x 10 mm dimensions and an error-free timeline.",
        "mutation": "Not required in this fixture; parameter-expression preservation is covered by focused Q1 tests and more specific native mutation cases.",
        "references": [
            ("OpenSCAD", "cube([40,30,10]) is the constructive-geometry baseline; Forge differs by preserving editable SolidCraft history."),
        ],
    },
    {
        "slug": "anchored-holes",
        "title": "Face-relative hole pattern",
        "intent": "Verify a 2D profile, native extrusion, patterned holes and placement on a selected face.",
        "forge_api": "Rectangle2D(...).extrude(...); Hole(...).pattern(...).on(..., face=Faces.TOP)",
        "forge_model": "A feature-based plate plus a patterned Hole feature anchored to the plate's TOP face.",
        "lowering": "Native sketch/extrude commands followed by native hole/pattern placement commands; Forge does not subtract hand-built cylinders.",
        "native_expectation": "One plate with two through holes at the requested Y spacing and no feature errors.",
        "mutation": "No saved-design mutation in this fixture; geometry and feature placement are measured at Q4.",
        "references": [
            ("OpenSCAD", "Comparable geometry would normally use difference() and repeated cylinders; Forge intentionally prefers SolidCraft hole features."),
        ],
    },
    {
        "slug": "components",
        "title": "Rigid component attachment",
        "intent": "Verify reuse of one component definition and a rigid face-to-face relationship between two occurrences.",
        "forge_api": "copy()/reusable model semantics; attach(parent=Anchor.RIGHT, child=Anchor.LEFT)",
        "forge_model": "Two ModelInstance occurrences sharing one ModelDefinition; the second carries an Attachment to the first.",
        "lowering": "One component definition, one copied occurrence and joint.create(type='rigid') using the RIGHT and LEFT native references.",
        "native_expectation": "Two identical blocks touch face-to-face and retain one shared editable component definition.",
        "mutation": "No mutation in this base case; parametric joint distance and moving anchor geometry are isolated below.",
        "references": [
            ("BOSL2", "Comparable to attach(RIGHT, LEFT): the relationship is described by parent and child attachment references."),
        ],
    },
    {
        "slug": "parametric-attach",
        "title": "Parametric normal gap",
        "intent": "Verify that distance along the attachment normal remains a native editable joint parameter.",
        "forge_api": "attach(..., gap=self.gap)",
        "forge_model": "Rigid Attachment with a symbolic gap expression; anchor identities are unchanged.",
        "lowering": "joint.create(type='rigid', offset='gap'); gap is not flattened into occurrence.move.",
        "native_expectation": "The child sits 10 mm away from the parent's RIGHT face along the joint normal.",
        "mutation": "Change gap from 10 to 30 mm in the saved .sc design; the child must move another 20 mm without rerunning Python.",
        "references": [
            ("BOSL2", "Conceptually similar to an attachment displacement along the local anchor normal rather than a world-axis translate."),
        ],
    },
    {
        "slug": "parametric-offset",
        "title": "Parametric in-plane joint offset",
        "intent": "Verify the existing local (u,v) attachment-plane offset and make its coordinate semantics explicit.",
        "forge_api": "attach(..., offset=(u, v))",
        "forge_model": "Attachment stores two symbolic local planar values; these are not world X/Y/Z coordinates.",
        "lowering": "A non-zero/symbolic local offset becomes joint.create(type='planar', values=[u,v,angle]).",
        "native_expectation": "The marker moves within the selected corner anchor's local attachment plane.",
        "mutation": "Change shift from 5 to 10 mm in the saved design; the marker must follow the same local axis by another 5 mm.",
        "references": [
            ("BOSL2", "Important reference: attach() operates in the local coordinate system at the parent anchor, not blindly in world coordinates."),
            ("OpenSCAD", "A raw translate([x,y,z]) is world/object transform syntax and therefore is not equivalent to this local joint offset."),
        ],
    },
    {
        "slug": "parametric-anchor",
        "title": "Face anchor follows parent geometry",
        "intent": "Verify that a standard face anchor remains tied to changing parent topology.",
        "forge_api": "Anchor.RIGHT / Anchor.LEFT with parent parameter propagation",
        "forge_model": "The attachment references the parent's semantic RIGHT face, not a frozen absolute X coordinate.",
        "lowering": "joint.create uses a native face reference derived from the parent occurrence; the parent width remains a SolidCraft parameter.",
        "native_expectation": "The attached block stays on the parent's right face.",
        "mutation": "Change base_width from 40 to 80 mm in the saved design; the block follows the moved RIGHT face.",
        "references": [
            ("BOSL2", "BOSL2 cardinal anchors similarly express a meaningful side of the parent instead of an absolute coordinate."),
        ],
    },
    {
        "slug": "corner-anchor",
        "title": "Topology-backed corner anchor",
        "intent": "Verify a corner reference that follows both parent width and height changes.",
        "forge_api": "Anchor.FRONT_TOP_RIGHT paired with child Anchor.BACK_TOP_RIGHT",
        "forge_model": "A standard corner Anchor is resolved to an edge/on/corner native topology reference rather than a free point.",
        "lowering": "joint.create receives SolidCraft edge/on/corner picks so the saved design can re-find the corner after geometry changes.",
        "native_expectation": "The marker sits on the front-top-right corner of the base.",
        "mutation": "Change the base from 40x20 to 80x40 mm; the marker must follow both the new right side and new top.",
        "references": [
            ("BOSL2", "BOSL2 supports side/edge/corner anchors; its anchor also carries orientation, which is a useful design reference for Forge."),
        ],
    },
    {
        "slug": "custom-anchor",
        "title": "Named oriented AnchorFrame",
        "intent": "Verify that a reusable component can publish a named attachment datum with both position and orientation.",
        "forge_api": "anchors() -> {'tip': AnchorFrame(origin=..., z=..., x=...)}; attach(parent='tip', child='mount')",
        "forge_model": "AnchorFrame is explicitly a local frame: origin plus Z axis and X axis. It is not merely a named point.",
        "lowering": "For the rotated parent occurrence Forge materializes/uses the native joint-origin path so SolidCraft owns the occurrence rotation.",
        "native_expectation": "After the arm rotates 90 degrees about Z, the marker remains attached to the rotated tip with the authored frame orientation.",
        "mutation": "No parameter mutation; this fixture isolates occurrence rotation plus named-frame attachment.",
        "references": [
            ("BOSL2", "Closest conceptual match: an anchor defines position, local Z direction and spin/orientation information."),
        ],
    },
    {
        "slug": "xz-anchor",
        "title": "Anchors on XZ-profile extrusion",
        "intent": "Verify standard corner anchors on geometry authored as an XZ polygon and extruded in Y.",
        "forge_api": "Polygon2D(..., plane='XZ', world=True).extrude(...); standard corner Anchors",
        "forge_model": "Forge recovers rectangular bounds/topology from the XZ profile while preserving symbolic width and height.",
        "lowering": "Corner attachments lower to native topology references on the extruded board; no special HUB75-specific placement logic is involved.",
        "native_expectation": "Left and right markers attach to their respective front-top corners with mirrored spatial results.",
        "mutation": "Change board width/height from 40x20 to 80x40 mm; both markers follow their own corners.",
        "references": [
            ("OpenSCAD", "The profile/extrusion resembles polygon()+linear_extrude(), but Forge retains native SolidCraft parameters and attachment topology."),
            ("BOSL2", "Mirrored corner anchors are a useful check that local anchor frames, not a single global direction assumption, control attachment."),
        ],
    },
    {
        "slug": "primitive-csg",
        "title": "Primitive CSG and orientation",
        "intent": "Qualify the direct CSG path independently of feature-history geometry: Sphere and Box union, translated primitives, three-axis Cylinder.orient() cuts and intersection.",
        "forge_api": "Sphere(); Box(...).move(...); Cylinder(...).orient(X, Y, Z); + / - / &",
        "forge_model": "A Shape CSG tree rooted in Sphere so Forge deliberately selects the direct CSG compiler rather than the feature-history Box compiler.",
        "lowering": "solid.sphere(new), solid.box(join), three centered solid.cylinder(cut) commands for X/Y/Z, then solid.box(intersect).",
        "native_expectation": "One valid clipped solid remains after union, three orthogonal bores and intersection; SolidCraft must accept every CSG operation with an error-free evaluated timeline.",
        "mutation": "No saved-design mutation in this case; it isolates primitive CSG lowering and orientation. Parameter mutation belongs in the parameter-specific cases.",
        "references": [
            ("OpenSCAD", "This is closest to ordinary union()/difference()/intersection() with translate()/rotate() around primitives."),
            ("PythonSCAD", "Useful comparison for first-class solid objects and Python operators while Forge still delegates geometry to SolidCraft."),
        ],
    },
    {
        "slug": "bracket",
        "title": "Minimal L-profile",
        "intent": "Provide a deliberately simple reusable L-shaped reference component for later attachment/orientation qualification.",
        "forge_api": "Polygon2D(..., plane='XZ').extrude(width, direction=Direction.SYMMETRIC)",
        "forge_model": "One symbolic L profile extruded symmetrically through its width; no holes, fillets, anchors or secondary features.",
        "lowering": "Native XZ sketch/polygon plus symmetric extrusion. No assembly commands are present yet.",
        "native_expectation": "A clean 40 mm L profile with 12 mm arms and 24 mm symmetric extrusion width.",
        "mutation": "Not yet an attachment mutation case. This component is intentionally the geometry baseline for upcoming multi-orientation anchor tests.",
        "references": [
            ("OpenSCAD", "Equivalent baseline is a 2D L polygon followed by linear_extrude(center=true)."),
            ("BOSL2", "Later attachment cases can reuse this simple shape while testing anchor/orient semantics independently of bracket feature complexity."),
        ],
    },
]
