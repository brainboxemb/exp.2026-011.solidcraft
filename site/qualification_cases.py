"""Qualification case metadata for the Forge library site.

Keep this deliberately explicit.  A qualification case is documentation of a
contract between the public Forge API, Forge's compiler model and native
SolidCraft behaviour.  The site and site tests both consume this table.
"""

REFERENCE_URLS = {
    "SolidCraft": "https://docs.solidcraft.io/guide/assemblies.html",
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


QUALIFICATION_GROUPS = [
    ("fundamentals", "1 · Basic geometry", "Primitives, profiles, CSG and simple reusable reference geometry."),
    ("features", "2 · Parent/child features and faces", "Features that belong to an existing object and use a meaningful parent face."),
    ("parameters", "3 · Parameters and dependencies", "Editable values, component-local parameters and inherited symbolic dependencies."),
    ("components", "4 · Components and occurrences", "Reusable physical parts and more than one placed occurrence."),
    ("anchors", "5 · Anchors and local frames", "Richer component references: faces, corners, topology and oriented local frames."),
    ("associativity", "6 · Associative relationships", "Editable distances and local offsets that must keep their meaning after parameter changes."),
]


QUALIFICATION_CASES = [
    {
        "slug": "simple-box",
        "group": "fundamentals",
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
        "group": "features",
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
        "slug": "parameter-scope",
        "q5_required": True,
        "group": "parameters",
        "title": "Implicit component parameters and shared dependencies",
        "intent": "Verify that public component defaults become editable native parameters automatically, while parent Parameters/Expressions are reused rather than duplicated in the child.",
        "forge_api": "plain reusable class fields; Panel(width=self.shared_width); Panel(width=self.shared_width / 2)",
        "forge_model": "Local numeric defaults become component-local Parameters; inherited Parameter/Expression inputs become external bindings to the existing parent dependency.",
        "lowering": "Local component parameters are namespaced (for example Panel_width); inherited names such as shared_width remain unprefixed and are emitted once even when several child definitions use them.",
        "native_expectation": "The saved SolidCraft design exposes Panel_width, Panel_2_width and shared_width; changing shared_width updates both directly-bound children and the derived half-width child without rerunning Python.",
        "mutation": "Change shared_width from 80 to 100 mm in the saved native design; widths must change from [40,40,60,80,80] to [40,50,60,100,100].",
        "references": [
            ("PythonSCAD", "Primary API reference: normal Python objects/defaults should remain natural; users should not need a separate parameter-publication switch."),
            ("SolidCraft", "Native parameters and expressions are the source of truth for saved-design editability and rebuild behaviour."),
        ],
    },
    {
        "slug": "components",
        "group": "components",
        "title": "Place one component relative to another",
        "intent": "Verify reuse of one component definition while a child occurrence is placed relative to a meaningful face of the parent.",
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
        "q5_required": True,
        "group": "associativity",
        "title": "Editable distance between attached components",
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
        "q5_required": True,
        "group": "associativity",
        "title": "Editable local offset at an attachment",
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
        "q5_required": True,
        "group": "anchors",
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
        "q5_required": True,
        "group": "anchors",
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
        "slug": "four-corner-l",
        "q5_required": True,
        "group": "anchors",
        "title": "One L-profile on all four front corners",
        "intent": "Verify that one directional L-profile and one child AnchorFrame are oriented correctly at all four front corners, then remain attached when the parent width and height change in the saved native design.",
        "forge_api": "Anchor.FRONT_TOP_LEFT/RIGHT and FRONT_BOTTOM_LEFT/RIGHT; one AnchorFrame(origin=(0,0,0), z=(0,-1,0), x=(1,0,0)) with angle=0",
        "forge_model": "One parametric rectangular parent plus four occurrences of one LBracket definition; every child uses the same local attachment frame and differs only by the selected parent corner.",
        "lowering": "Four rigid joint.create commands: parent corners use topology-backed edge/on/corner origins; each child supplies the same point/z/x local frame and an explicit zero joint angle.",
        "native_expectation": "The four 40x40 L bounding boxes occupy the four inward front-corner quadrants and keep the same local clock cycle after the parent grows from 120x80 to 160x120 mm.",
        "mutation": "After the fixed baseline is proven, change FrameBlock_width from 120 to 160 mm and FrameBlock_height from 80 to 120 mm in the saved .sc design; all four brackets and solved joint origins must follow their corners without rerunning Python.",
        "references": [
            ("BOSL2", "A single child-local frame should be reusable while the selected parent anchor supplies the different local corner orientations."),
            ("SolidCraft", "A corner joint origin retains the selected face/edge/corner topology and defines a local frame at that corner."),
        ],
    },
    {
        "slug": "custom-anchor",
        "group": "anchors",
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
        "q5_required": True,
        "group": "anchors",
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
        "group": "fundamentals",
        "title": "Primitive CSG",
        "intent": "Qualify direct primitive/CSG modelling independently of feature-history geometry: Sphere and Box union, translated primitives, one ordinary Cylinder cut and intersection.",
        "forge_api": "Sphere(); Box(...).move(...); Cylinder(...).move(...); + / - / &",
        "forge_model": "A Shape CSG tree rooted in Sphere so Forge deliberately selects the direct CSG compiler instead of the feature-history Box compiler.",
        "lowering": "solid.sphere(new), solid.box(join), one Z-axis solid.cylinder(cut), then solid.box(intersect).",
        "native_expectation": "SolidCraft accepts the complete CSG command path, produces one valid clipped body and evaluates the native timeline without errors.",
        "mutation": "No saved-design mutation in this case; it isolates primitive CSG lowering. Parametric edits are covered by dedicated Q5 cases.",
        "references": [
            ("OpenSCAD", "Closest to ordinary union()/difference()/intersection() with translate()/rotate() around primitives."),
            ("PythonSCAD", "Useful comparison for Python objects and operators while Forge still delegates all geometry to SolidCraft."),
        ],
    },
    {
        "slug": "bracket",
        "group": "fundamentals",
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
