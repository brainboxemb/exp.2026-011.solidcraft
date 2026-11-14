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
<p>In the <code>lib.py.solidcraft.forge</code> repository and an active Python environment:</p>
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
<p>For a live GUI run, open SolidCraft, enable
<em>Preferences → Assistant → Let AI agents connect</em>, and use:</p>
""" + code("""python -m scpf model.py --connect --new""") + """
<p><code>--new</code> asks SolidCraft to replace the active design with a new,
empty one before the model batch is sent. Leave it off when you deliberately
want to add commands to the current design. Neither form saves the design.
The CAD project also provides a separate native CLI qualification workflow.</p>
<h2 id="next">Where to continue</h2>
<p>Continue with <a href="../mental-model/">How to think about Forge</a>.
That chapter introduces parts, components, occurrences, assemblies, anchors
and attachments without assuming CAD experience. The later chapters then
describe the Python API in detail.</p>""",
    },
    {
        "slug": "mental-model",
        "title": "How to think about Forge",
        "summary": "The small set of concepts you need before learning the API.",
        "body": """
<h2 id="goal">Start with the thing you want to build</h2>
<p>You do not need to think in SolidCraft commands, transformation matrices or
joint internals to use Forge. Start by asking a simpler question:
<strong>what are the physical parts, and how are they related?</strong></p>
<p>For a small frame with four corner brackets, for example, you might have:</p>
<ul>
<li>two side boards;</li>
<li>a top and bottom board;</li>
<li>one reusable corner-bracket design;</li>
<li>eight placed copies of that bracket.</li>
</ul>
<p>Forge turns that description into native SolidCraft geometry and assembly
relationships.</p>

<h2 id="model">Model: one thing you can build</h2>
<p>A <strong>model</strong> is a Python class with a <code>build()</code>
method. It describes one piece of geometry or one composed result.</p>
""" + code("""class Plate:
    width = 100.0
    height = 60.0
    thickness = 10.0

    def build(self):
        return Box(self.width, self.height, self.thickness)""") + """
<p>The public dimensions can become editable CAD parameters. You normally do
not need to write SolidCraft commands yourself.</p>

<h2 id="component">Component: a reusable physical part</h2>
<p>A <strong>component</strong> is a model that represents a reusable part.
Think of a bracket, panel, beam or PCB enclosure. If you need the same part
five times, you still want one definition of the part.</p>
""" + code("""@component
class Bracket:
    def build(self):
        return Box(40, 20, 10)""") + """
<p>Changing the component definition changes what every occurrence of that
part represents.</p>

<h2 id="occurrence">Occurrence: one placed copy of a component</h2>
<p>An <strong>occurrence</strong> is one use of a component inside a larger
design. It has its own position and orientation, while sharing the same
component definition.</p>
""" + code("""first = Bracket()
second = first.copy().move(x=80)""") + """
<p>This is similar to putting two identical purchased brackets on a workbench:
they are two physical instances of the same part design.</p>

<h2 id="assembly">Assembly: parts that belong together</h2>
<p>An <strong>assembly</strong> combines component occurrences into a larger
construction. An assembly is not one fused blob of geometry. The parts remain
separate, reusable objects with relationships between them.</p>
""" + code("""@assembly
class Frame:
    def build(self):
        left = SideBoard()
        right = left.copy().move(x=800)
        return left + right""") + """
<p>An assembly can itself expose useful attachment locations for something
that will be mounted to the complete frame.</p>

<h2 id="anchor">Anchor: a meaningful place and direction</h2>
<p>An <strong>anchor</strong> tells Forge where a relationship belongs.
A simple anchor can mean “the right face” or “the front-top-left corner”.
More advanced anchors can also describe orientation.</p>
""" + code("""parent=Anchor.FRONT_TOP_LEFT
child=Anchor.BACK_TOP_RIGHT""") + """
<p>This is more useful than saying “put it at X=412, Y=-6, Z=362”, because a
semantic anchor can keep referring to the same face or corner when dimensions
change.</p>
<div class="notice"><strong>Important:</strong> an anchor should be thought of
as a local attachment reference, not merely a world XYZ point. For oriented
attachments, its local directions matter too.</div>

<h2 id="attachment">Attachment: the relationship between two anchors</h2>
<p><code>attach()</code> says that one component occurrence belongs relative
to another one. You choose a parent anchor and a child anchor; Forge converts
that relationship into the appropriate native SolidCraft representation.</p>
""" + code("""bracket = Bracket().attach(
    side,
    parent=Anchor.FRONT_TOP_LEFT,
    child=Anchor.BACK_TOP_RIGHT,
)""") + """
<p>From a user point of view, the important statement is simply:
“attach this bracket here using this side of the bracket.” You should not need
to design the underlying SolidCraft joint yourself.</p>

<h2 id="relationship-values">Gap, offset and orientation are different ideas</h2>
<p>Once two anchors are related, additional values may refine that
relationship. Keep these concepts separate:</p>
<table><thead><tr><th>Concept</th><th>Meaning</th></tr></thead><tbody>
<tr><td><code>gap</code></td><td>Distance along the attachment normal</td></tr>
<tr><td><code>offset=(u,v)</code></td><td>Displacement inside the local attachment plane</td></tr>
<tr><td>orientation / frame</td><td>Which way the attached part faces</td></tr>
<tr><td>world move</td><td>Explicit placement in assembly X/Y/Z coordinates</td></tr>
</tbody></table>
<p>These are intentionally not interchangeable. A local attachment offset is
not automatically a world-X or world-Z movement.</p>

<h2 id="parameters">Parameters: dimensions you expect to edit later</h2>
<p>A parameter is a value that should remain meaningful after the Python model
has been compiled. If a frame width changes from 800 to 900 mm, an attached
part should ideally follow its semantic anchor rather than keep an old
hard-coded coordinate.</p>
<p>This is why Forge qualification tests do more than check the initial
picture: important cases also edit the saved SolidCraft parameters and verify
that relationships still solve correctly.</p>

<h2 id="solidcraft">What SolidCraft does underneath</h2>
<p>Forge is a description and compilation layer. SolidCraft remains the CAD
engine. Forge may lower your intent to sketches, extrusions, component
occurrences, joint origins or native joints, but those are implementation
details unless you are debugging or extending Forge.</p>
<p>The later chapters explain those details where they are useful. For normal
model writing, keep the simpler hierarchy in mind:</p>
""" + code("""model
  └─ component definition
       └─ occurrences
            └─ assembly
                 └─ anchors
                      └─ attachments""") + """
<h2 id="next">Where to go next</h2>
<p>Read <a href="../model-objects/">Model objects and parameters</a> for the
Python rules behind models and components, then
<a href="../components/">Components and assemblies</a> for placement,
anchors and attachments.</p>""",
    },
    {
        "slug": "model-objects",
        "title": "Model objects and parameters",
        "summary": "What a class, Shape, component and occurrence mean.",
        "body": """
<h2 id="class">A model is a normal Python class</h2>
<p>Numeric class attributes become editable SolidCraft parameters when SCPF
compiles a plain model class. <code>build()</code> returns geometry. If a file
contains exactly one public class with <code>build()</code>, that class is the
root automatically; no trailing constructor call or launcher file is needed.</p>
""" + code("""from scpf import Box

class Plate:
    length = 100.0
    width = 60.0
    thickness = 10.0

    def build(self):
        return Box(self.length, self.width, self.thickness)""") + """
<p>Run that source file directly with
<code>python -m scpf plate.py --connect</code>. The same rule lets a reusable
component file serve as its standalone model while assemblies import the exact
same class. If a file contains several public model classes, SCPF deliberately
does not guess: finish the script with an explicit call such as
<code>Assembly()</code> to choose the root.</p>
<p>An explicit final call is also how you override root parameters for a
particular run, for example <code>Plate(width=80)</code>. Arithmetic such as
<code>self.length / 2</code> is preserved symbolically for supported
expressions; general Python computations are not automatically made
parametric.</p>
<h2 id="parameter-intent">Parameter intent is visible in the name</h2>
<p>SCPF distinguishes three kinds of numeric class attributes. This keeps a
Python build setting from looking like a native editable CAD parameter.</p>
""" + code("""class Display:
    PANEL_COUNT = 5          # fixed constant
    _panel_pitch = 160.0     # Forge/build-time input
    opening_width = 844.0    # native model parameter""") + """
<table><thead><tr><th>Name</th><th>Meaning</th><th>SolidCraft parameter</th></tr></thead><tbody>
<tr><td><code>UPPER_CASE</code></td><td>Fixed constant</td><td>No</td></tr>
<tr><td><code>_lower_case</code></td><td>Forge/build-time input</td><td>No</td></tr>
<tr><td><code>lower_case</code></td><td>Editable model parameter</td><td>Yes</td></tr>
</tbody></table>
<p>If a public lower-case parameter is consumed only as a concrete Python
value—for example through <code>pv()</code>—Forge emits a
<code>ModelParameterWarning</code>. The same warning is emitted when a
parameter remains native in some geometry but is also flattened into a
concrete component <code>move()</code> or rotation. Such a parameter is only
partly associative: editing it in SolidCraft would update only part of the
model. Either preserve the symbolic placement or rename an intentionally
build-time input with a leading underscore.</p>
<h2 id="shared-parameters">Share one model parameter across child components</h2>
<p>Passing a parent parameter into several component inputs keeps one native
SolidCraft parameter instead of creating component-specific duplicates.</p>
""" + code("""bottom = BottomBoard(corner_radius=self.corner_radius)
roof = RoofBoard(corner_radius=self.corner_radius)
bracket = Bracket(
    bracket_width=self.bracket_width,
    inside_corner_radius=self.corner_radius,
)""") + """
<p>Here the wooden fillets and bracket inside fillet all depend on the same
<code>corner_radius</code>. Passing the parent parameter into the child input
reuses that existing native dependency rather than creating a duplicate child
parameter.</p>
<p>If a reusable component owns a public lower-case numeric default itself,
that default automatically becomes an editable, namespaced component
parameter. No extra publication or alias declaration is needed.</p>
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
<code>copy()</code> does not duplicate its features. The compiler creates
all native occurrences in place first, then sends their individual
placement commands to SolidCraft. This keeps rotations and offsets
independent.</p>
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
        "slug": "parameters-associativity",
        "title": "Parameters and associativity",
        "summary": "Understand which values stay editable and which relationships must follow later dimension changes.",
        "body": """
<h2 id="scenario">The practical question</h2>
<p>Suppose a frame is 800 mm wide today, but you expect to change it to
900 mm later. You want two things to happen:</p>
<ul>
<li>the frame geometry becomes wider;</li>
<li>parts attached to the right side move with that side.</li>
</ul>
<p>The first is a <strong>parameter</strong> problem. The second is an
<strong>associativity</strong> problem. They are related, but they are not the
same thing.</p>

<h2 id="parameter">Parameter: a value that should remain editable</h2>
<p>For a plain Forge model, public lower-case numeric attributes are intended
to become editable SolidCraft parameters:</p>
""" + code("""class Frame:
    width = 800.0
    height = 400.0
    wood_thickness = 12.0""") + """
<p>Those values are part of the model's design intent. They are different from
temporary Python calculations used only while building the command plan.</p>

<h2 id="intent">Make parameter intent visible in the name</h2>
<table><thead><tr><th>Python name</th><th>Meaning</th><th>Native editable parameter?</th></tr></thead><tbody>
<tr><td><code>width = 800.0</code></td><td>Design dimension</td><td>Yes</td></tr>
<tr><td><code>_panel_pitch = 160.0</code></td><td>Forge/build-time helper</td><td>No</td></tr>
<tr><td><code>PANEL_COUNT = 5</code></td><td>Fixed constant</td><td>No</td></tr>
</tbody></table>
<p>This naming convention prevents a Python implementation detail from looking
like a promise that the value remains editable in the saved CAD design.</p>

<h2 id="expressions">Derived dimensions should remain symbolic where possible</h2>
<p>Simple arithmetic on parameters can stay symbolic:</p>
""" + code("""class Frame:
    width = 800.0

    def build(self):
        half_width = self.width / 2
        return SideBoard().move(x=half_width)""") + """
<p>However, not every Python operation can or should become a CAD expression.
If Forge needs a concrete number for Python control flow, it may use
<code>pv()</code>. At that moment the value is being evaluated during the
Forge run.</p>

<h2 id="flattening">A parameter can be accidentally flattened</h2>
<p>This is the important trap: geometry may remain parameterized while one
placement is calculated only once in Python.</p>
""" + code("""x = pv(self.width) / 2
right = SideBoard().move(x=x)""") + """
<p>If the saved SolidCraft parameter later changes, that one-time placement
cannot automatically know that it should move too. Forge emits
<code>ModelParameterWarning</code> for supported cases where a public parameter
is partly flattened in this way.</p>
<div class="notice"><strong>Rule of thumb:</strong> if you expect a relationship
to update after editing the saved SolidCraft design, the relationship itself
must be represented natively or symbolically. Keeping only the source
dimension parametric is not enough.</div>

<h2 id="associativity">Associativity: relationships that survive edits</h2>
<p>An associative model expresses <em>why</em> geometry belongs somewhere.
For example:</p>
""" + code("""block = Block().attach(
    base,
    parent=Anchor.RIGHT,
    child=Anchor.LEFT,
)""") + """
<p>If the parent width changes, the semantic <code>RIGHT</code> face should
move and the child should follow it. The attachment is therefore more useful
than calculating the original right-face X coordinate once.</p>

<h2 id="gap">Parametric relationship values</h2>
<p>A relationship value can itself be a parameter:</p>
""" + code("""class Mount:
    gap = 10.0

    def build(self):
        return Block().attach(
            base,
            parent=Anchor.RIGHT,
            child=Anchor.LEFT,
            gap=self.gap,
        )""") + """
<p>For supported attachments, Forge keeps the gap as a native joint value.
Changing the saved <code>gap</code> parameter can then re-solve the
relationship without rerunning Python.</p>

<h2 id="shared">Share one design parameter across components</h2>
<p>Several reusable parts may depend on one assembly-level design value. Pass
the symbolic parent parameter into those components instead of creating
unrelated duplicates:</p>
""" + code("""bottom = BottomBoard(corner_radius=self.corner_radius)
roof = RoofBoard(corner_radius=self.corner_radius)
bracket = CornerBracket(
    inside_corner_radius=self.corner_radius,
)""") + """
<p>All three uses express one design decision: the same corner radius.</p>

<h2 id="build-time">Not every useful value should be parametric</h2>
<p>Some values genuinely belong only to the Forge build process. Examples can
include a loop count, an intermediate lookup, a temporary placement used to
construct a non-associative reference model or a choice between two source
branches.</p>
<p>Use an underscore or constant when the model is intentionally rebuilt from
Python after changing that value. Do not pretend every Python number is a
native CAD parameter.</p>

<h2 id="verification">How Forge proves associativity</h2>
<p>Initial geometry is not enough evidence. A parametric qualification case
should:</p>
<ol>
<li>build and save the native SolidCraft design;</li>
<li>measure the initial result;</li>
<li>change the native parameter with <code>parameters.change</code>;</li>
<li>evaluate the saved design again without rerunning the Python model;</li>
<li>measure that the dependent geometry or attachment moved correctly.</li>
</ol>
<p>This is qualification level Q5 in the Forge test system.</p>

<h2 id="example">Example: wood thickness and a bracket</h2>
<p>If a bracket must stay aligned when <code>wood_thickness</code> changes,
there are two independent questions:</p>
<ul>
<li>does SolidCraft still know the new board geometry?</li>
<li>is the bracket relationship expressed in a way that follows that geometry
and preserves any intended local correction?</li>
</ul>
<p>Changing the parameter successfully while the bracket remains frozen is
therefore a failed associative use case, even if the board itself updates.</p>

<h2 id="decision">A simple decision guide</h2>
<table><thead><tr><th>You want...</th><th>Use...</th></tr></thead><tbody>
<tr><td>A dimension editable in SolidCraft</td><td>Public model parameter</td></tr>
<tr><td>A fixed source/build constant</td><td><code>UPPER_CASE</code></td></tr>
<tr><td>A Python-only helper/input</td><td><code>_lower_case</code></td></tr>
<tr><td>A child to follow a face/corner after edits</td><td>Associative anchor + attachment</td></tr>
<tr><td>A relationship distance editable later</td><td>Supported symbolic/native relationship value</td></tr>
</tbody></table>
""",
    },
    {
        "slug": "geometry",
        "title": "Geometry, sketches and Boolean operations",
        "summary": "Solids, 2D profiles, extrusions and the CSG operators.",
        "body": """
<h2 id="solids">Start with a solid</h2>
<p><code>Box(length, width, height)</code> is centred in X/Y, with its lower
face at Z=0. <code>Cylinder(d=…, h=…, axis=Axis.Z)</code> starts at its
base point. Use <code>Axis.X</code> or <code>Axis.Y</code> for the other
native principal directions. A sphere is specified by radius. These initial coordinate assumptions matter
when locating holes or placing multiple components.</p>
""" + code("""from scpf import (
    BOTTOM, FRONT, LEFT, RIGHT,
    Axis, Box, Cylinder, Sphere,
)

plate = Box(80, 50, 8)
board = Box(80, 50, 12).at(
    0, 0, 0,
    anchor=FRONT + BOTTOM,
).fillet(
    4,
    edges=[BOTTOM + LEFT, BOTTOM + RIGHT],
)
pin = Cylinder(d=8, h=20, axis=Axis.Z).at(10, 10, 8)
side_pin = Cylinder(d=8, h=20, axis=Axis.X).at(-10, 0, 0)
ball = Sphere(12)

body = Sphere(20) & Box(30, 30, 30)
centered_bore = Cylinder(d=8, h=30, axis=Axis.X).at(body)""") + """
<p><code>at(x, y, z)</code> uses absolute coordinates. Passing another
Shape instead uses shape-relative placement. The first supported relation is
CENTER-to-CENTER, so <code>Cylinder(...).at(body)</code> derives the native
cylinder base from its axis and height instead of requiring a manual
<code>-h/2</code> offset.</p>
<h2 id="profiles">Draw a 2D profile, then extrude it</h2>
<p>A <code>Rectangle2D</code> is a planar profile rather than a 3D body. 2D geometry is authored inside an explicit <code>Sketch</code> scope. <code>Polygon2D</code> can be created on the XY, XZ or YZ plane.</p>
""" + code("""from scpf import Sketch, Rectangle2D, Polygon2D

with Sketch(plane="XY") as plate_sketch:
    Rectangle2D(80, 50)
plate = plate_sketch.extrude(8)

with Sketch(plane="XZ") as side_sketch:
    Polygon2D(
        [(0, 0), (40, 0), (40, 8), (8, 8), (8, 30), (0, 30)],
        plane="XZ",
        world=True,
    )
side = side_sketch.extrude(10)""") + """
<p>A sketch plane affects where its axes go; changing the camera does not rotate its geometry. Leave the <code>with Sketch(...)</code> scope, then call <code>sketch.extrude(...)</code> to create 3D material. Direct <code>Rectangle2D(...).extrude(...)</code> syntax is intentionally not supported.</p>
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
""" + code("""from scpf import X, Y, Z

upside_down = first.copy().rotate(Z, 180)
upright = first.copy().rotate(X, 90)

# Explicit XYZ tuple form remains valid:
sideways = first.copy().rotate(axis=(0, 1, 0), degrees=90)""") + """
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
<p>For a final orientation involving several conceptual turns, give SCPF
<strong>one axis-angle orientation</strong>. SolidCraft performs the
native rotation; SCPF does not build its own rotation matrices.
Verify the saved native geometry to check which direction is up.</p>
<h2 id="named-axes">Named axis rotation</h2>
<p>The exported <code>X</code>, <code>Y</code> and <code>Z</code> tokens can
be passed directly to occurrence rotation. Prefer
<code>rotate(Y, 90)</code> when a principal-axis turn is all that is needed.
The explicit <code>axis=(x,y,z), degrees=…</code> form remains available for
arbitrary axis-angle placement.</p>
<h2 id="copies">Copies are independent placements</h2>
<p>One <strong>component definition</strong> describes the shape and its
editable features. Every <strong>occurrence</strong> says where one copy
belongs in the assembly. Several occurrences reuse the same definition.</p>
""" + code("""first = PanelComponent().move(z=160).rotate(axis=(1, 0, 0), degrees=90)
second = first.copy().move(x=160)
screen = first + second""") + """
<p>In Python, <code>copy()</code> inherits the desired placement:
<code>second</code> keeps the 90° rotation and adds 160 mm to X.
In the generated command sequence, however, SCPF makes both native
occurrences <strong>at the origin</strong> before moving either one.
It then asks SolidCraft to place each one. This prevents a copy from
accidentally inheriting an already-applied native rotation or offset.</p>
<h2 id="json">What SCPF actually sends to SolidCraft</h2>
<p>The sequence below is deliberately simple: create one component,
copy it once, then ask SolidCraft to place both occurrences. The
editable shape features are omitted here for clarity.</p>
""" + code("""{
  "commands": [
    {"command":"component.create","params":{"name":"Panel"}},
    {"command":"occurrence.copy","params":{"component":"Panel"}},
    {"command":"occurrence.move","params":{
      "occurrence":"Panel:1",
      "translate":[0,0,160],
      "axis":[1,0,0],
      "angle":"90 deg",
      "move_grounded":true
    }},
    {"command":"occurrence.move","params":{
      "occurrence":"Panel:2",
      "translate":[160,0,160],
      "axis":[1,0,0],
      "angle":"90 deg"
    }}
  ]
}""") + """
<p>SolidCraft 0.30.1 understands the native <code>translate</code>,
<code>axis</code> and <code>angle</code> parameters. SCPF does
<strong>not</strong> calculate transformation matrices. The newer
<code>to</code> placement field is not supported by 0.30.1; using it
previously left a panel flat without reporting an error.</p>
<p>Passing a command-plan test is not enough to prove the CAD is right.
The CAD project's native tests also inspect the rotations and
positions saved in SolidCraft's own design, and front/rear screenshots
help verify the result visually. A camera change does not rotate
the actual panel geometry.</p>
<h2 id="limitations">Current support summary</h2>
<table><thead><tr><th>Operation</th><th>Scope</th><th>Limit</th></tr></thead><tbody>
<tr><td><code>move(x,y,z)</code></td><td>Occurrences, supported CSG shapes</td><td>Not arbitrary feature bodies</td></tr>
<tr><td><code>rotate(X,90)</code> / explicit axis tuple</td><td>Component occurrences</td><td>Absolute single axis-angle</td></tr>
<tr><td>Chained rotations</td><td>Not implemented</td><td>Second rotate replaces first</td></tr>
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
""" + code("""from scpf import Box, Hole, Depth, Faces

plate = Box(100, 60, 10)
hole = Hole(d=8, depth=Depth.THROUGH_ALL)
plate = plate + hole.on(plate, face=Faces.TOP)""") + """
<p>A <code>Hole</code> is a native hole feature: adding it to the shape
means adding the operation that <em>removes</em> material.
<code>Faces.TOP</code> selects its entry face. Simple feature placement
uses <code>on()</code>; assembly attachment uses explicit anchors.</p>
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
<p><code>Faces.TOP</code> chooses the face to open and is also the same
surface-selection vocabulary used by <code>feature.on(...)</code>.
<code>Anchor</code> is reserved for explicit component attachment in
assemblies. See the source and regression tests for supported feature chains.</p>
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
        "summary": "Describe reusable parts, placed copies and how they belong together.",
        "body": """
<h2 id="scenario">Start from a real build</h2>
<p>Suppose you are making a wooden display frame with eight identical corner
brackets. You do <strong>not</strong> want to model eight unrelated brackets.
You want to describe:</p>
<ul>
<li>what one bracket looks like;</li>
<li>where eight physical copies of that bracket are used;</li>
<li>which boards and brackets together form the frame;</li>
<li>how each bracket is related to the frame.</li>
</ul>
<p>Those four questions correspond directly to Forge's component, occurrence,
assembly and attachment concepts.</p>

<h2 id="component">Component: the reusable part design</h2>
<p>A <strong>component</strong> describes one kind of physical part. A bracket,
panel, side board or PCB enclosure is a good component candidate when you may
use it more than once or want to edit it independently.</p>
""" + code("""from scpf import Box, component

@component
class CornerBracket:
    width = 24.0

    def build(self):
        return Box(40, self.width, 40)""") + """
<p>This defines the bracket design. It does not mean that only one bracket
exists in the final assembly.</p>

<h2 id="occurrence">Occurrence: one physical use of that component</h2>
<p>Every placed copy is an <strong>occurrence</strong>. Eight brackets in the
frame means eight occurrences, while all eight still share one component
definition.</p>
""" + code("""first = CornerBracket()
second = first.copy().move(x=100)""") + """
<p>Think of buying eight identical metal brackets: there is one product design,
but eight physical pieces. This distinction matters because changing the
component definition should not require rebuilding eight independent models.</p>

<h2 id="assembly">Assembly: the construction made from parts</h2>
<p>An <strong>assembly</strong> describes how component occurrences form a
larger object. The parts remain separate; an assembly is not automatically a
Boolean union.</p>
""" + code("""from scpf import assembly

@assembly
class Frame:
    def build(self):
        left = SideBoard()
        right = left.copy().move(x=800)
        return left + right""") + """
<p>The assembly can later grow to include top/bottom boards, panels and corner
brackets without turning those parts into one inseparable solid.</p>

<h2 id="move-or-attach">Move or attach?</h2>
<p>Use <code>move()</code> when you deliberately know an occurrence's assembly
position. Use <code>attach()</code> when the important fact is a
<strong>relationship between parts</strong>.</p>
<table><thead><tr><th>Question</th><th>Prefer</th></tr></thead><tbody>
<tr><td>“Put this reference object 200 mm to the right.”</td><td><code>move()</code></td></tr>
<tr><td>“Keep this bracket on the top-left corner of the side board.”</td><td><code>attach()</code></td></tr>
<tr><td>“Make five copies on a fixed pitch.”</td><td><code>copy().move(...)</code></td></tr>
<tr><td>“This child must follow a parent face when its size changes.”</td><td><code>attach()</code></td></tr>
</tbody></table>

<h2 id="simple-attachment">Attachment: describe why the child belongs there</h2>
""" + code("""bracket = CornerBracket().attach(
    side_board,
    parent=Anchor.FRONT_TOP_LEFT,
    child=Anchor.BACK_TOP_RIGHT,
)""") + """
<p>The parent anchor says <em>where on the side board</em> the relationship
belongs. The child anchor says <em>which part of the bracket</em> is placed
there. Forge then maps that intent to SolidCraft.</p>
<p>From the user's point of view this is the important API contract. Native
SolidCraft joints are an implementation detail unless you are debugging or
extending Forge.</p>

<h2 id="component-vs-assembly-knowledge">Where should knowledge live?</h2>
<p>A reusable component should know facts that are intrinsic to that part.
An assembly should know facts that only make sense in one construction.</p>
<table><thead><tr><th>Knowledge</th><th>Best owner</th></tr></thead><tbody>
<tr><td>Bracket width, hole positions, intrinsic mounting face</td><td>Component</td></tr>
<tr><td>“This is the frame's front-top-left mounting point”</td><td>Assembly</td></tr>
<tr><td>One sensor connector's local orientation</td><td>Component anchor</td></tr>
<tr><td>Which of eight brackets is used in one frame corner</td><td>Assembly</td></tr>
</tbody></table>
<p>This separation keeps generic components reusable instead of filling them
with names and coordinates that only make sense in one project.</p>

<h2 id="component-parameters">Component parameter visibility</h2>
<p>Public lower-case numeric component defaults are editable automatically.
Forge namespaces component-local parameter names when necessary, so normal
component code stays simple:</p>
""" + code("""@component
class CornerBracket:
    width = 24.0
    inside_corner_radius = 4.0

    def build(self):
        ...""") + """
<p>When a parent <code>Parameter</code> or expression is passed into a child
input, that existing dependency stays symbolic. For example,
<code>CornerBracket(inside_corner_radius=self.corner_radius)</code> reuses the
parent design's <code>corner_radius</code>; it does not create a separate
<code>CornerBracket_inside_corner_radius</code> parameter.</p>
<h2 id="placement">Occurrence placement</h2>
<p><code>copy()</code> in Python retains the source's intended position
and orientation. <code>move()</code> then adds the given displacement.
For example, moving a copy by X=120 after its source already sits at X=50
makes the copy's intended X position 170. This is normal Python-side behavior.
When compiling, SCPF first creates all native occurrences at the origin and
asks SolidCraft to position each one <em>once</em>. No previous native
transform needs to be undone, and no inverse matrix is calculated.</p>
""" + code("""center = BeamComponent()
array = center
for x in (-240, -120, 120, 240):
    array = array + center.copy().move(x=x)""") + """
<h2 id="attach">Component attachment</h2>
""" + code("""right = BeamComponent().attach(
    left, parent=Anchor.RIGHT, child=Anchor.LEFT
)

marker = Marker().attach(
    frame,
    parent=Anchor.FRONT_TOP_RIGHT,
    child=Anchor.BACK_TOP_RIGHT,
)""") + """
<p><code>attach()</code> is the public Forge relationship between reusable
components. <code>Anchor</code> selects the attachment reference: a supported
face, or one of the eight rectangular corners such as
<code>FRONT_TOP_RIGHT</code>. Corner anchors compile to native SolidCraft
edge/corner origins, so they follow dimension changes in a saved design.</p>
<h2 id="attach-offset">Associative in-plane attachment offset</h2>
<p><code>attach(offset=(u, v))</code> moves the child within the attachment
plane. Numeric values and parameter expressions are both supported. Forge
lowers a non-zero or symbolic in-plane offset to a native planar joint and
keeps <code>u</code> and <code>v</code> as SolidCraft joint values, so they are
re-evaluated when their parameters change.</p>
""" + code("""wood = Parameter("wood_thickness", 18)

bracket = Bracket().attach(
    side,
    parent=Anchor.FRONT_TOP_LEFT,
    child=mount,
    offset=(0, -wood + 12),
    gap=-12,
)""") + """
<p><code>offset</code> is independent of <code>gap</code>: the two offset
values move in the attachment plane, while <code>gap</code> remains the normal
distance between the two references. On a rectangular corner origin, the
second planar value follows the selected vertical corner edge; its sign is
defined by that corner frame rather than by world Z.</p>
<h2 id="assembly-anchor">Assembly-owned named anchors</h2>
<p>When a datum belongs to the meaning of an assembly rather than to a generic
component, keep it on the assembly with <code>with_anchor()</code>. The anchor
stores the target occurrence plus its attachment reference. Consumers resolve
it by name with <code>anchor()</code>.</p>
""" + code("""frame = (left + right + bottom).with_anchor(
    "front_top_left",
    left,
    AnchorTopology(
        edge=(-6, 0, 181),
        on=(0, 0, 181),
        corner=(-6, 0, 362),
        z=(0, 0, -1),
        x=(1, 0, 0),
    ),
)

parent = frame.anchor("front_top_left")
bracket = CornerBracket().attach(
    parent.target,
    parent=parent.reference,
    child=bracket_reference,
)""") + """
<p>This keeps a generic <code>Board</code> or <code>CornerBracket</code> free
of application-specific anchor names while a higher-level frame can expose
semantic datums such as <code>front_top_left</code>.</p>
<p>An assembly anchor may also carry its own symbolic
<code>offset=(u, v)</code>. Consumers can combine that semantic offset with a
fixed local correction and pass the result to <code>attach(offset=...)</code>.
This is useful when an assembly datum follows a frame parameter such as wall
thickness while the reusable part keeps a fixed mounting correction.</p>
<h2 id="anchor-frame">AnchorFrame: point plus orientation</h2>
<p>An <code>AnchorFrame</code> describes one local attachment coordinate frame.
<code>origin</code> gives the local point; <code>z</code> gives the attachment
normal and <code>x</code> fixes the rotation around that normal. Use it when a
single point or rectangular <code>Anchor</code> is not enough to describe how
the occurrence must be oriented.</p>
""" + code("""from scpf import Anchor, AnchorFrame

mount = AnchorFrame(
    origin=(0, 0, -12),
    z=(0, 1, 0),
    x=(0, 0, -1),
)

bracket = CornerBracket().attach(
    side_board,
    parent=Anchor.FRONT_TOP_LEFT,
    child=mount,
)""") + """
<p>There are two ownership patterns. If the datum is an intrinsic part of a
reusable component, expose it with <code>anchors()</code> and refer to it by
name. If the frame exists only because of a particular assembly or mounting
choice, construct the <code>AnchorFrame</code> in that assembly and pass it
directly to <code>attach()</code>. This keeps application knowledge out of the
generic component definition.</p>
""" + code("""@component
class Sensor:
    def anchors(self):
        return {
            "connector": AnchorFrame(
                origin=(12, 0, 4),
                z=(1, 0, 0),
                x=(0, 0, 1),
            )
        }

    def build(self):
        return Box(24, 12, 8)

sensor = Sensor().attach(panel, child="connector")""") + """
<p>For an unrotated occurrence, Forge lowers an <code>AnchorFrame</code>
directly into the native <code>joint.create</code> reference as
<code>point</code>, <code>z</code> and <code>x</code>; it does not create a
persistent visible <code>joint.origin</code>. Named frames on explicitly
rotated occurrences currently use the native origin fallback so SolidCraft
owns the transform. A direct <code>AnchorFrame</code> on an explicitly rotated
occurrence is not supported yet.</p>
<h2 id="anchor-topology">AnchorTopology: follow an edge or corner</h2>
<p><code>AnchorTopology</code> is a named component datum that stays attached to native SolidCraft topology. <code>edge</code> picks an edge, <code>on</code> selects its adjacent planar face and <code>corner</code> optionally chooses one endpoint. The coordinates are selection picks; SolidCraft keeps the selected edge, face and endpoint by topology name as the design changes.</p>
""" + code("""from scpf import AnchorTopology, Box, component

@component
class Board:
    def anchors(self):
        return {
            "mount": AnchorTopology(
                edge=(-20, 50, 5),
                on=(-20, 50, 10),
                corner=(-20, 0, 5),
                z=(0, 1, 0),
                x=(0, 0, 1),
            )
        }

    def build(self):
        return Box(40, 100, 20)""") + """
<p>This is useful for references such as the straight tangent edge beside a fillet: if dimensions move that edge, the joint can follow it without freezing the original XYZ point. The current implementation supports named or direct <code>AnchorTopology</code> values on non-rotated occurrences. A direct topology anchor is useful when the datum belongs only to one assembly rather than to the reusable component. SCPF deliberately does not transform topology picks itself.</p>
<p>SolidCraft joints remain an internal implementation detail; Forge does not
expose a separate public Joint object.</p>
<h2 id="verify">What to test in an assembly</h2>
<p>Check the native command list for one <code>component.create</code>
per shared definition, expected <code>occurrence.copy</code> counts,
and native <code>translate</code>, <code>axis</code> and <code>angle</code>
parameters for rotated occurrences. Separately verify native SolidCraft
geometry and its bounding dimensions before trusting an assembly image.</p>""",
    },
    {
        "slug": "anchors-attachments",
        "title": "Anchors and attachments",
        "summary": "Describe where parts connect, which way they face and which relationship should remain associative.",
        "body": """
<h2 id="why">Why anchors exist</h2>
<p>If you place every part with absolute X/Y/Z coordinates, the model may look
correct once but becomes fragile as soon as dimensions change. An
<strong>anchor</strong> gives a part a meaningful attachment reference such as
“right face”, “front-top-left corner” or a named mounting frame.</p>
<p>The important idea is not the coordinate value itself. The important idea is
<strong>what place on the part this coordinate represents</strong> and, for
oriented attachments, <strong>which way the local attachment frame points</strong>.</p>

<h2 id="parent-child">An attachment relates two anchors</h2>
<p><code>attach()</code> always describes a relationship between a parent
reference and a child reference:</p>
""" + code("""bracket = Bracket().attach(
    frame,
    parent=Anchor.FRONT_TOP_LEFT,
    child=Anchor.BACK_TOP_RIGHT,
)""") + """
<p>Read this as:</p>
<ul>
<li>find the parent's front-top-left attachment reference;</li>
<li>take the child's back-top-right attachment reference;</li>
<li>place the child so those references form the requested relationship.</li>
</ul>
<p>You should not need to calculate the final world coordinates yourself.</p>

<h2 id="standard">Standard anchors</h2>
<p>For simple rectangular parts, Forge provides semantic anchors for common
faces and corners:</p>
""" + code("""Anchor.LEFT
Anchor.RIGHT
Anchor.TOP
Anchor.BOTTOM
Anchor.FRONT
Anchor.BACK

Anchor.FRONT_TOP_LEFT
Anchor.FRONT_TOP_RIGHT
Anchor.FRONT_BOTTOM_LEFT
Anchor.FRONT_BOTTOM_RIGHT
Anchor.BACK_TOP_LEFT
Anchor.BACK_TOP_RIGHT
Anchor.BACK_BOTTOM_LEFT
Anchor.BACK_BOTTOM_RIGHT""") + """
<p>These names describe the part from its own local coordinate system. A corner
anchor should continue to mean the same corner when a parameter changes the
part's width or height.</p>

<h2 id="local-frame">An anchor is more than a world point</h2>
<p>A reliable attachment needs a local frame. Conceptually that frame contains:</p>
<ul>
<li>an origin — where the attachment is;</li>
<li>a normal/direction — which way it faces;</li>
<li>a rotation reference around that normal.</li>
</ul>
<p>This is why the same numeric adjustment can behave differently at different
corners if it is interpreted in the anchor's local coordinate system. A local
attachment offset is not automatically a world-X, world-Y or world-Z move.</p>
<div class="notice"><strong>Design rule:</strong> Forge should make the coordinate
space explicit. The user should never have to guess whether an offset is local
to the anchor or global to the assembly.</div>

<h2 id="gap-offset">Gap and offset describe different parts of the relationship</h2>
<table><thead><tr><th>Value</th><th>Meaning</th><th>Coordinate space</th></tr></thead><tbody>
<tr><td><code>gap</code></td><td>Distance away from/toward the parent along the attachment normal</td><td>Local normal</td></tr>
<tr><td><code>offset=(u,v)</code></td><td>Movement within the attachment plane</td><td>Local anchor plane</td></tr>
<tr><td><code>move(x,y,z)</code></td><td>Explicit occurrence translation</td><td>Assembly/world axes</td></tr>
<tr><td>orientation</td><td>Which way the child faces</td><td>Anchor/component frame</td></tr>
</tbody></table>
<p>Keeping these concepts separate is important for parametric models. If an
offset is local, Forge should preserve it as a local relationship instead of
flattening it into one-time global coordinates.</p>

<h2 id="anchorframe">AnchorFrame: define a custom oriented mounting frame</h2>
<p>Use <code>AnchorFrame</code> when the attachment location is not one of the
standard faces/corners, or when the orientation must be stated explicitly.</p>
""" + code("""mount = AnchorFrame(
    origin=(0, 0, -12),
    z=BACK,
    x=DOWN,
)""") + """
<p>Here:</p>
<ul>
<li><code>origin</code> is the component-local mounting point;</li>
<li><code>z</code> is the local attachment direction;</li>
<li><code>x</code> fixes the rotation around that direction.</li>
<li>For principal axes, use <code>RIGHT</code>, <code>LEFT</code>,
<code>FRONT</code>, <code>BACK</code>, <code>UP</code> or
<code>DOWN</code> instead of spelling the vector manually.</li>
</ul>
<p>This is conceptually close to BOSL2's attachable model: a useful anchor has
both a location and local orientation. Forge does not need to copy BOSL2's API,
but that mental model is a good check for clear semantics.</p>

<h2 id="topology">AnchorTopology: follow real model topology</h2>
<p>Sometimes a datum should follow a real edge/corner in SolidCraft instead of
remaining at a free local coordinate. <code>AnchorTopology</code> describes
selection picks for an edge, adjacent face and optional endpoint.</p>
""" + code("""mount = AnchorTopology(
    edge=(-20, 50, 5),
    on=(-20, 50, 10),
    corner=(-20, 0, 5),
)""") + """
<p>Those coordinates are used to identify native topology. The intention is
that SolidCraft keeps following that selected edge/corner when the underlying
dimensions change.</p>

<h2 id="ownership">Who should own an anchor?</h2>
<p>An anchor belongs where its meaning originates:</p>
<table><thead><tr><th>Example</th><th>Owner</th></tr></thead><tbody>
<tr><td>A sensor connector position that is intrinsic to the sensor</td><td>Component</td></tr>
<tr><td>The top-left mounting datum of one particular frame assembly</td><td>Assembly</td></tr>
<tr><td>A generic rectangular face or corner</td><td>Standard <code>Anchor</code></td></tr>
</tbody></table>
<p>This prevents a generic component from accumulating project-specific names
and offsets.</p>

<h2 id="parametric">What should happen when dimensions change?</h2>
<p>A good associative attachment is judged by its behaviour after an edit, not
only by its initial picture. For example:</p>
<ol>
<li>a frame width changes from 800 to 900 mm;</li>
<li>the semantic top-right corner moves;</li>
<li>the child attached to that corner follows it;</li>
<li>its local gap/offset still mean the same thing;</li>
<li>no Python recompilation is needed for a saved-design parameter edit where
the relationship is supported natively.</li>
</ol>
<p>This is why Forge qualification cases explicitly edit saved SolidCraft
parameters and measure the native result.</p>

<h2 id="current-boundaries">Current API boundaries</h2>
<p>Forge currently supports standard rectangular anchors, named
<code>AnchorFrame</code> values, topology-backed references and native rigid or
planar attachment lowering for documented cases. It is not yet a general mate
solver for arbitrary faces and every possible 3D relationship.</p>
<p>When we add a new attachment capability, its coordinate space and
associativity must first be described here, then implemented and qualified in
an isolated use scenario before it is used in a larger CAD project.</p>
""",
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
one <code>occurrence.move</code> with the expected native parameters.</p>
""" + code("""python -m unittest discover -s scpf/tests -v""") + """
<h2 id="json">Test compiled native commands</h2>
<p>Compare the generated command structure with explicit expectations,
not only with a count of operations. Tests should check component names,
requested positions, the orientation axis and angle, and feature ordering.
A regression can preserve a known good JSON fixture when command ordering
is part of the contract.</p>
<h2 id="native">Native geometric verification</h2>
<p>The CAD model repository runs a separate SolidCraft CLI workflow for
native geometry, editable history, STEP output, measurements and screenshots.
Read the <strong>saved SolidCraft occurrence transforms</strong>, not just
whether a command ran successfully. A valid Python object or syntactically valid command plan is not evidence
that the final solid occupies the correct plane or has no collision.</p>
<h2 id="changes">Keep implementation and docs in sync</h2>
<p>When placement syntax changes, add tests for the exact generated native
commands before documenting it as supported. Named principal-axis rotation
is supported; chained rotations are still not.</p>
<p>For a plain-language explanation of the implementation and its
boundaries, read
<a href="https://github.com/brainboxemb/lib.py.solidcraft.forge/blob/main/scpf/docs/architecture.md">How SCPF works (without building a second CAD engine)</a>.</p>""",
    },
]
