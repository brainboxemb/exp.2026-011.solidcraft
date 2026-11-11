"""Long-form, source-maintained API guide pages for the library website.

This is educational documentation, not executable API fixtures. Claims about
supported operations must match scpf/scpf/*.py and scpf/tests/*.py.
"""
from html import escape


def code(source):
    return '<pre><code>' + escape(source.strip()) + '</code></pre>'


GUIDES = [
    {
        "slug": "getting-started",
        "title": "Getting started",
        "summary": "From a Python class to editable SolidCraft geometry.",
        "body": """
<h2 id="what">What SCPF does</h2>
<p>SCPF is a Python interface and compiler for <strong>native SolidCraft commands</strong>.
It is not a replacement CAD kernel. You describe a model using ordinary Python;
SolidCraft executes the generated commands and owns the final geometry and
feature history.</p>
<h2 id="install">Install the library</h2>
<p>In the <code>lib.py.solidcraft</code> repository and an active Python environment:</p>
""" + code("""python -m pip install -e ./scpf
python -m unittest discover -s scpf/tests -v""") + """
<h2 id="first-model">Your first model</h2>
<p>Define one class, give it numeric dimensions, and return the body from
<code>build()</code>. No <code>main()</code> or <code>show()</code> is necessary.</p>
""" + code("""from scpf import Box, Edges

class Plate:
    length = 100.0
    width = 60.0
    thickness = 10.0

    def build(self):
        plate = Box(self.length, self.width, self.thickness)
        return plate.fillet(2, edges=Edges.VERTICAL)

Plate()""") + """
<h2 id="run">Compile, inspect, then execute</h2>
<p>Save the model as <code>model.py</code>. Compilation alone does not open SolidCraft.
The JSON is a native command plan, not a mesh or STEP file.</p>
""" + code("""python -m scpf model.py --out output/model.json
python -m json.tool output/model.json""") + """
<p>For a live GUI run, open an <strong>empty design</strong> in SolidCraft,
enable <em>Preferences → Assistant → Let AI agents connect</em>, and use:</p>
""" + code("""python -m scpf model.py --connect""") + """
<p>This sends commands to the active document; it does not save the design.
The CAD project also provides a separate native CLI qualification workflow.</p>
<h2 id="next">Where to continue</h2>
<p>Read <a href="../model-objects/">Model objects</a> to understand the difference
between a shape definition and a placed component occurrence. The
<a href="../transformations/">Transformations</a> chapter covers coordinate axes,
rotation and the common “my panel is lying flat” problem.</p>""",
    },
    {
        "slug": "model-objects",
        "title": "Model objects and parameters",
        "summary": "What a class, Shape, component and occurrence mean.",
        "body": """
<h2 id="class">A model is a normal Python class</h2>
<p>Numeric class attributes become editable SolidCraft parameters when SCPF
compiles a plain model class. <code>build()</code> returns geometry. A call to
the class at the bottom of the file selects the root model.</p>
""" + code("""from scpf import Box

class Plate:
    length = 100.0
    width = 60.0
    thickness = 10.0

    def build(self):
        return Box(self.length, self.width, self.thickness)

Plate(width=80)""") + """
<p>The override changes the value of <code>width</code> in this instance.
Arithmetic such as <code>self.length / 2</code> is preserved symbolically
for supported expressions; general Python computations are not automatically
made parametric.</p>
<h2 id="shape">Shape versus component occurrence</h2>
<p><strong>Shape</strong> describes geometry or a feature expression
(<code>Box</code>, <code>Hole</code>, an extrusion). A <strong>component
occurrence</strong> is one placed instance of a shared, editable model definition.
Do not confuse a new occurrence with a new feature history.</p>
""" + code("""from scpf import Box, component

class Block:
    def build(self):
        return Box(40, 20, 10)

BlockComponent = component(Block)
first = BlockComponent()
second = first.copy().move(x=50)
assembly = first + second""") + """
<p>The two occurrences share the same <code>Block</code> definition.
<code>copy()</code> does not duplicate its features.</p>
<h2 id="groups">Groups are actual native parent components</h2>
""" + code("""blocks = (first + second).group("Blocks")""") + """
<p>Grouping changes the browser hierarchy, not the geometry's orientation.
At present one shared definition cannot be split among different groups.</p>
<h2 id="limits">Important boundaries</h2>
<p>Associative attachment is supported for a limited set of rectangular
component faces. General mates, arbitrary face queries and rotational
constraints are not implemented as a complete assembly solver.</p>""",
    },
    {
        "slug": "geometry",
        "title": "Geometry, sketches and Boolean operations",
        "summary": "Solids, 2D profiles, extrusions and the CSG operators.",
        "body": """
<h2 id="solids">Start with a solid</h2>
<p><code>Box(length, width, height)</code> is centred in X/Y, with its lower
face at Z=0. <code>Cylinder(d=…, h=…)</code> starts at its bottom face.
A sphere is specified by radius. These initial coordinate assumptions matter
when locating holes or placing multiple components.</p>
""" + code("""from scpf import Box, Cylinder, Sphere

plate = Box(80, 50, 8)
pin = Cylinder(d=8, h=20).at(10, 10, 8)
ball = Sphere(12)""") + """
<h2 id="profiles">Draw a 2D profile, then extrude it</h2>
<p>A <code>Rectangle2D</code> is a planar profile rather than a 3D body.
<code>Polygon2D</code> can be placed on the XY, XZ or YZ plane.</p>
""" + code("""from scpf import Rectangle2D, Polygon2D

plate = Rectangle2D(80, 50).extrude(8)
side_profile = Polygon2D(
    [(0, 0), (40, 0), (40, 8), (8, 8), (8, 30), (0, 30)],
    plane="XZ",
    world=True,
)""") + """
<p>A profile's plane affects where its axes go; changing the camera
does not rotate its geometry. Use a supported extrusion direction to
create 3D material.</p>
<h2 id="boolean">Add, subtract and intersect</h2>
""" + code("""body = Box(50, 50, 20)
tool = Cylinder(d=12, h=22).at(0, 0, 0)
joined = body + tool       # union, where supported
cut = body - tool          # difference, where supported
shared = body & tool       # intersection, where supported""") + """
<p>The supported compiler path depends on the operands. Native feature
history and CSG trees are not interchangeable for every operation.
For manufacturing features such as holes, prefer the native
<a href="../features/">feature operations</a>.</p>""",
    },
    {
        "slug": "transformations",
        "title": "Transformations and orientation",
        "summary": "Coordinate systems, movement, rotation, copies and what is not yet supported.",
        "body": """
<h2 id="axes">First choose the coordinate system</h2>
<p>SolidCraft models are three-dimensional: X, Y and Z are axes, not
synonyms for left, up and front in every project. The conventional
<code>Box</code> base is in XY and its height extends along +Z.
A portrait HUB75 module may be authored with its large face in XY, then
placed upright in the assembly's XZ plane.</p>
<p>Differentiate <strong>definition coordinates</strong> (how one component
is built) from <strong>assembly coordinates</strong> (where an occurrence
is placed). A camera rotation is only a change of view; it does not
change any of these coordinates.</p>
<h2 id="move">Move: translation</h2>
""" + code("""from scpf import Box

body = Box(40, 20, 10)
shifted = body.move(x=10, y=0, z=25)""") + """
<p>For supported CSG shapes, <code>move()</code> translates the full CSG
expression. A feature-based Plate body cannot always be freely moved
using the same method. Component occurrences have their own placement
<code>move()</code>, which adds the requested displacement.</p>
""" + code("""from scpf import component

class Panel:
    def build(self):
        return Box(160, 320, 14.5)

PanelComponent = component(Panel)
first = PanelComponent()
right = first.copy().move(x=160)""") + """
<h2 id="rotate">Rotate: axis and angle on a component occurrence</h2>
<p>In the current implementation, <code>rotate()</code> belongs to a
<strong>component occurrence</strong> and accepts an XYZ direction tuple and
an angle in degrees. It rotates the placement about the component's local origin.
The shared component definition is not modified.</p>
""" + code("""upside_down = first.copy().rotate(axis=(0, 0, 1), degrees=180)
upright = first.copy().rotate(axis=(1, 0, 0), degrees=90)""") + """
<p>The first rotates about Z; the second rotates about X. A rotation
around X can convert a face authored in XY into a vertical XZ face.
The direction of the depth axis changes too.</p>
<h2 id="absolute">Critical: rotate sets an orientation; it does not compose</h2>
""" + code("""# NOT two successive rotations in current SCPF:
panel = first.rotate(axis=(1, 0, 0), degrees=90)
panel = panel.rotate(axis=(0, 1, 0), degrees=180)""") + """
<p>The second call <strong>replaces</strong> the first occurrence rotation.
It does not apply a second rotation on top of the first. A model that
appears to lie flat after a second rotation can be caused by this rule.
SCPF currently supports one absolute axis-angle orientation per occurrence,
not chained Euler rotations.</p>
<p>If an orientation needs multiple conceptual turns, compute and pass
<strong>one final axis-angle pose</strong>; test it against the intended
geometry. Do not assume two <code>rotate()</code> calls combine.</p>
<h2 id="named-axes">Are rotate(Z, 180) or rotate(Y, 180) available?</h2>
<p><strong>No, not yet.</strong> The exported <code>X</code>,
<code>Y</code> and <code>Z</code> tokens are used in other APIs, including
bounds and <code>orient()</code>. Occurrence rotation currently requires
<code>rotate(axis=(0,0,1), degrees=180)</code>. The shorter form is
a possible future API change, not an existing feature.</p>
<h2 id="orient">Cylinder orient is a different operation</h2>
""" + code("""from scpf import Cylinder, X, Y, Z

tool = Cylinder(d=10, h=30).orient(X, Y, Z)""") + """
<p><code>orient()</code> is currently restricted to
<strong>Cylinder</strong> shapes and their supported CSG compilation.
It does not mean arbitrary model rotation. Do not substitute
<code>orient(Z)</code> for a component occurrence's
<code>rotate(axis=(0,0,1), degrees=…)</code>.</p>
<h2 id="copies">Copies and ordering</h2>
<p><code>copy()</code> inherits the source occurrence's placement;
<code>move()</code> changes its translation; <code>rotate()</code>
sets its absolute orientation. If a source occurrence is already moved,
copying and moving it again needs care to avoid double offsets.
For predictable arrays, start with a master at the origin.</p>
<h2 id="json">How to verify the generated native command</h2>
<p>Unit tests compile a tiny model and inspect the
<code>occurrence.move</code> command. For SolidCraft 0.30.1 a rotation uses a relative native
<code>matrix</code>, <strong>not</strong> the later absolute
<code>to</code> parameter (which that version silently ignores).
The input matrix is conventional affine form with translation in the
last column. The following is an <strong>illustrative command fragment</strong>:</p>
""" + code("""{
  "command": "occurrence.move",
  "params": {
    "occurrence": "Panel:2",
    "matrix": [
      [-1, 0, 0, 160],
      [0, -1, 0, 0],
      [0, 0, 1, 0],
      [0, 0, 0, 1]
    ]
  }
}""") + """
<p>Saved SolidCraft document transforms use a transposed matrix with the\ntranslation in the last row. Compiler tests confirm the command shape, but native CAD evaluation
and an actual geometry screenshot are still necessary to verify
that a full assembly is physically upright.</p>
<h2 id="limitations">Current support summary</h2>
<table><thead><tr><th>Operation</th><th>Scope</th><th>Limit</th></tr></thead><tbody>
<tr><td><code>move(x,y,z)</code></td><td>Occurrences, supported CSG shapes</td><td>Not arbitrary feature bodies</td></tr>
<tr><td><code>rotate(axis=…,degrees=…)</code></td><td>Component occurrences</td><td>Absolute single axis-angle</td></tr>
<tr><td><code>orient(X,Y,Z)</code></td><td>Cylinder shapes</td><td>Not general components</td></tr>
<tr><td>Chained rotations</td><td>Not implemented</td><td>Second rotate replaces first</td></tr>
<tr><td><code>rotate(Z,180)</code></td><td>Not implemented</td><td>Use explicit XYZ axis tuple</td></tr>
</tbody></table>""",
    },
    {
        "slug": "features",
        "title": "Features and references",
        "summary": "Native holes, fillets, shells and relative positioning.",
        "body": """
<h2 id="features">A feature changes an existing body</h2>
<p>A native feature is different from subtracting arbitrary CSG geometry.
SCPF can retain named sketches and operations in SolidCraft history.
For exact results, supported body types and selection constraints matter.</p>
<h2 id="hole">Holes</h2>
""" + code("""from scpf import Box, Hole, Depth, Anchor

plate = Box(100, 60, 10)
hole = Hole(d=8, depth=Depth.THROUGH_ALL)
plate = plate + hole.attach(plate, parent=Anchor.TOP)""") + """
<p>A <code>Hole</code> is a native hole feature: adding it to the shape
means adding the operation that <em>removes</em> material.
<code>Anchor.TOP</code> indicates its entry face, not a surface normal
you can use as an arbitrary coordinate transform.</p>
<h2 id="fillet">Fillets and chamfers</h2>
""" + code("""from scpf import Box, Edges
body = Box(80, 50, 15)
rounded = body.fillet(3, edges=Edges.VERTICAL)""") + """
<p>Edge selection can use supported named selectors or explicit pick
coordinates. Named profile segment IDs are available for
<code>Polygon2D</code> workflows. A topological edge cannot
always be inferred reliably from a visual camera position.</p>
<h2 id="shell">Shells</h2>
""" + code("""from scpf import Box, Faces
case = Box(80, 50, 30).shell(2, open=Faces.TOP)""") + """
<p><code>Faces.TOP</code> chooses the face to open. It is different
from <code>Anchor.TOP</code>, which chooses a relative placement reference.
See the source and regression tests for the supported feature chains.</p>
<h2 id="anchors">Position without hard-coded global offsets</h2>
""" + code("""from scpf import X, Y, Boss, Anchor

boss = Boss(d=7, h=12, hole_d=2.5).attach(
    case, parent=Anchor.INNER_BOTTOM,
    offset=(X.MIN + 10, Y.MAX - 10),
)""") + """
<p><code>X.MIN</code> and <code>Y.MAX</code> refer to the parent
bounds and are not rotation-axis constants. Anchoring support
currently focuses on rectangular bases and a documented set of faces.
Do not assume every curved or lofted surface supports it.</p>""",
    },
    {
        "slug": "components",
        "title": "Components and assemblies",
        "summary": "Reusable definitions, occurrence transforms, grouping and attachments.",
        "body": """
<h2 id="definition">One definition, several occurrences</h2>
""" + code("""from scpf import Box, component

class Beam:
    length = 100.0
    def build(self):
        return Box(self.length, 20, 20)

BeamComponent = component(Beam)
left = BeamComponent()
right = left.copy().move(x=120)
assembly = (left + right).group("Beams")""") + """
<p>SolidCraft receives one reusable definition and multiple occurrences.
A group is a native parent component in the browser, not a Boolean
fusion of its children.</p>
<h2 id="placement">Occurrence placement</h2>
<p>Copying a model reuses its source placement. Placing an already shifted
master and shifting the copy may produce an unintended offset. For regular
arrays, use a central master at the origin, then distribute copies by their
intended world-space offsets.</p>
""" + code("""center = BeamComponent()
array = center
for x in (-240, -120, 120, 240):
    array = array + center.copy().move(x=x)""") + """
<h2 id="attach">Face-to-face attachment</h2>
""" + code("""right = BeamComponent().attach(
    left, parent=Anchor.RIGHT, child=Anchor.LEFT
)""") + """
<p>Supported rectangular faces can form a rigid native attachment.
A general mating constraint solver, arbitrary face-to-face offset and
multiple levels of independent shared parent groups are not yet available.</p>
<h2 id="verify">What to test in an assembly</h2>
<p>Check the native command list for one <code>component.create</code>
per shared definition, expected <code>occurrence.copy</code> counts,
and full poses for rotated occurrences. Separately verify native SolidCraft
geometry and its bounding dimensions before trusting an assembly image.</p>""",
    },
    {
        "slug": "verification",
        "title": "Verification and API boundaries",
        "summary": "Python unit tests, native JSON plans and mechanical evidence.",
        "body": """
<h2 id="unit">Unit tests for Python behavior</h2>
<p>The library's tests under <code>scpf/tests/</code> cover model
objects, feature compilation, reusable components and rotation validation.
For example, an occurrence rotation test checks that the compiler emits
one <code>occurrence.move</code> with the expected pose.</p>
""" + code("""python -m unittest discover -s scpf/tests -v""") + """
<h2 id="json">Test compiled native commands</h2>
<p>Compare the generated command structure with explicit expectations,
not only with a count of operations. Tests should check component names,
absolute positions, the orientation axis and angle, and feature ordering.
A regression can preserve a known good JSON fixture when command ordering
is part of the contract.</p>
<h2 id="native">Native geometric verification</h2>
<p>The CAD model repository runs a separate SolidCraft CLI workflow for
native geometry, editable history, STEP output, measurements and screenshots.
A valid Python object or syntactically valid command plan is not evidence
that the final solid occupies the correct plane or has no collision.</p>
<h2 id="changes">Keep implementation and docs in sync</h2>
<p>When new shorthand syntax (such as <code>rotate(Z, 180)</code>) or
chained rotation is implemented, add tests for the exact generated
native commands <em>before</em> documenting it as supported.
Until then, describe the current limit explicitly.</p>""",
    },
]
