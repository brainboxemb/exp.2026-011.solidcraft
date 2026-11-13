"""Curated CAD capability map for completeness analysis.

The map is intentionally capability-based, not a mirror of SolidCraft's
hundreds of individual commands.
"""

REFERENCE_MODELS = [
    {
        "name": "SolidCraft",
        "role": "Native capability truth",
        "use": "What can remain editable and associative in the actual CAD engine?",
        "strength": "Parametric sketches/features, BRep topology, components, occurrences and joints.",
        "url": "https://docs.solidcraft.io/reference/commands.html",
    },
    {
        "name": "PythonSCAD",
        "role": "Primary Python API ergonomics reference",
        "use": "How should ordinary scripted modelling feel to a Python user?",
        "strength": "First-class solids, Python methods/operators, composability and the normal Python ecosystem.",
        "url": "https://pythonscad.org/tutorial/site/index.html",
    },
    {
        "name": "BOSL2",
        "role": "Attachment and local-frame reference",
        "use": "How can anchors, orientation and parent-relative placement stay understandable?",
        "strength": "Attachables, semantic anchors and explicit local orientation/spin concepts.",
        "url": "https://github.com/BelfrySCAD/BOSL2/wiki/Tutorial-Attachment-Overview",
    },
    {
        "name": "OpenSCAD",
        "role": "Minimal CSG and transform baseline",
        "use": "What is the smallest familiar vocabulary for primitives, transforms and booleans?",
        "strength": "Simple CSG, transformations, modules and a compact language reference.",
        "url": "https://openscad.org/documentation.html",
    },
]

CAPABILITY_GROUPS = [
    ("fundamentals", "1 · Geometry fundamentals"),
    ("sketches", "2 · Sketches and parametric profiles"),
    ("features", "3 · Part features and face references"),
    ("components", "4 · Components, occurrences and relationships"),
    ("advanced", "5 · Advanced modelling"),
    ("inspection", "6 · Inspection and exchange"),
]

SOLIDCRAFT_CAPABILITIES = [
    ("fundamentals", "Box / Cylinder / Sphere", "Native primitives; Cylinder also supports an axis vector.", "Q6 · Box, Cylinder and Sphere native-qualified for the current Forge subset.", "Core", "PythonSCAD + OpenSCAD", "Keep primitive constructors small and predictable."),
    ("fundamentals", "Cone / Torus", "Native primitives.", "Missing", "Later", "PythonSCAD + OpenSCAD", "Useful breadth, not needed for current frame work."),
    ("fundamentals", "Boolean join / cut / intersect", "Native solid operations.", "Q6", "Core", "PythonSCAD + OpenSCAD", "Operator syntax is a good fit."),
    ("fundamentals", "Translation", "Native primitive positions and occurrence moves.", "Q6 for CSG; component move also supported", "Core", "PythonSCAD + OpenSCAD", "Keep world movement distinct from local attachment offsets."),
    ("fundamentals", "General rotation / mirror / scale", "Occurrence rotation is native; SolidCraft has richer placement machinery.", "Partial rotation; mirror/scale gaps", "Core rotation; mirror/scale later", "PythonSCAD + OpenSCAD", "Prefer one general transform model over type-specific shortcuts."),

    ("sketches", "Lines / rectangles / circles / polygons / text", "Rich native sketch entities.", "Partial", "Core", "PythonSCAD + OpenSCAD", "Forge exposes only a useful subset today."),
    ("sketches", "Sketch constraints", "Native geometric constraints.", "Missing/very limited", "High", "SolidCraft", "Needed for genuinely editable sketches."),
    ("sketches", "Sketch dimensions and expressions", "Native dimensions and parameter expressions.", "Partial", "High", "SolidCraft", "Needed for a mature parametric API."),
    ("sketches", "Face workplanes / projections", "Native sketches can live on faces and reference/project geometry.", "Partial", "High", "SolidCraft", "Central to feature construction."),

    ("features", "Extrude", "Native new/join/cut/intersect, symmetric, two-sided and to/from-object extents.", "Q6 basic subset", "Core", "PythonSCAD/OpenSCAD + SolidCraft richness", "Expose advanced extents only from real use cases."),
    ("features", "Hole", "Native direction, through/to, countersink/counterbore, threads and edge references.", "Partial Q6", "Core", "SolidCraft", "Grow from user scenarios instead of wrapping every option at once."),
    ("features", "Fillet / chamfer / shell", "Native topology-based feature operations.", "Partial; dedicated gaps remain", "High", "PythonSCAD", "Important mechanical/workshop operations."),
    ("features", "Patterns", "Native solid and sketch rectangular/circular patterns.", "Partial hole pattern", "High", "PythonSCAD + OpenSCAD", "General pattern API remains a gap."),
    ("features", "Materials / appearance", "Native material and appearance support.", "Partial", "Useful", "PythonSCAD", "Important for readable assemblies, not core geometry."),

    ("components", "Components and repeated occurrences", "Native component definitions and occurrence copies.", "Q6 basic", "Core", "PythonSCAD objects + SolidCraft components", "One definition, many physical placements."),
    ("components", "Occurrence local/world placement", "Native local/world translation, axis-angle and matrices.", "Partial", "Core", "PythonSCAD + OpenSCAD", "Forge should expose a smaller coherent transform API."),
    ("components", "Parent/child relation via a face", "Native face/topology references can remain associative.", "Partial", "Core", "SolidCraft + BOSL2", "Conceptually comes before custom anchors or joints."),
    ("components", "Local attachment frame / joint origin", "Native face, circle, edge, corner, point, plane or axis origins plus orientation.", "Partial Anchor/AnchorFrame/AnchorTopology", "Core", "BOSL2", "Key capability behind robust anchors."),
    ("components", "Rigid / planar relationships", "Native persistent component relationships and editable values.", "Partial", "Needed after basic parent/child placement", "BOSL2 conceptually; SolidCraft technically", "Keep joint terminology in the advanced/native layer."),
    ("components", "Motion joints / limits / kinematics", "Native degrees of freedom, limits and motion solving.", "Missing", "Later", "SolidCraft", "Not needed for current static assemblies."),

    ("advanced", "Revolve", "Native parametric revolve.", "Missing", "High", "PythonSCAD + OpenSCAD", "Common mechanical modelling operation."),
    ("advanced", "Sweep", "Native sweep with path orientation, twist, scale and rails.", "Missing", "Later", "PythonSCAD + OpenSCAD", "Useful, not a prerequisite for current projects."),
    ("advanced", "Loft", "Native multi-section loft with optional rails.", "Internal/special-case use only", "Later", "PythonSCAD + OpenSCAD", "Expose only when a real scenario needs it."),
    ("advanced", "Threads / emboss / sheet metal", "Native specialized features exist.", "Missing", "Later/out of current scope", "SolidCraft", "Track capability without wrapping everything."),

    ("inspection", "Measurements / topology / interference", "Native inspection and topology queries are extensive.", "Used by qualification; little public modelling API", "High for verification", "SolidCraft", "Qualification should consume this even if the modelling API stays small."),
    ("inspection", "Import / export / linked components", "Native exchange and component-linking workflows.", "CLI/project workflow only", "Later", "SolidCraft", "Separate workflow capability from modelling API."),
]
