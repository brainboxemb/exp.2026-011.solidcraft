//! Compiles semantic CAD intent into native SolidCraft commands.
//!
//! The domain model knows nothing of sketch creation, extrusion or transport.
//! Only this adapter knows SolidCraft's feature-building sequence.
//! Current supported subset: box, its *original* outside vertical-edge fillet,
//! and circular through-holes along Z.

use crate::cad::{Edges, Faces, Feature, LengthExpr, Part};
use crate::csg::{Axis, Shape};
use crate::{CadError, CommandTransport};
use serde_json::json;

/// Same high-level model can be translated by different command transports.
pub struct SolidCraftAdapter<T: CommandTransport> {
    transport: T,
}

fn command_length(value: &LengthExpr) -> serde_json::Value {
    match value {
        LengthExpr::Fixed(value) | LengthExpr::Auto(value) => json!(value.to_mm()),
        LengthExpr::Parameter(param) => json!(param.name()),
    }
}

fn half_coordinate(value: &LengthExpr, negative: bool) -> serde_json::Value {
    match value {
        LengthExpr::Fixed(value) | LengthExpr::Auto(value) => {
            let half = value.to_mm() / 2.0;
            json!(if negative { -half } else { half })
        }
        LengthExpr::Parameter(param) => {
            if negative {
                json!(format!("-{} / 2", param.name()))
            } else {
                json!(format!("{} / 2", param.name()))
            }
        }
    }
}

impl<T: CommandTransport> SolidCraftAdapter<T> {
    pub fn new(transport: T) -> Self {
        Self { transport }
    }

    pub fn into_transport(self) -> T {
        self.transport
    }

    pub fn build_csg(&mut self, shape: &Shape, name: &str) -> Result<(), CadError> {
        shape.validate().map_err(|_| CadError::InvalidInput("invalid CSG model"))?;

        let mut parameters = vec![];
        shape.collect_parameters(&mut parameters);
        for parameter in parameters {
            self.transport.execute(
                "parameters.add",
                json!({
                    "name": parameter.name(),
                    "expression": format!("{}", parameter.default_value().to_mm()),
                    "unit": "mm"
                }),
            )?;
        }

        self.emit_csg_new(shape, name)
    }

    fn emit_csg_new(&mut self, shape: &Shape, target: &str) -> Result<(), CadError> {
        match shape {
            Shape::Cube { .. } | Shape::Sphere { .. } | Shape::Cylinder { .. } => {
                self.emit_csg_primitive(shape, target, "new")
            }
            Shape::Intersection(left, right) => {
                self.emit_csg_new(left, target)?;
                self.emit_csg_apply(right, target, "intersect")
            }
            Shape::Difference(left, right) => {
                self.emit_csg_new(left, target)?;
                self.emit_csg_apply(right, target, "cut")
            }
            Shape::Union(items) => {
                let (first, rest) = items.split_first()
                    .ok_or(CadError::InvalidInput("empty CSG union"))?;
                self.emit_csg_new(first, target)?;
                for item in rest {
                    self.emit_csg_apply(item, target, "join")?;
                }
                Ok(())
            }
        }
    }

    fn emit_csg_apply(&mut self, shape: &Shape, target: &str, operation: &str) -> Result<(), CadError> {
        match shape {
            Shape::Cube { .. } | Shape::Sphere { .. } | Shape::Cylinder { .. } => {
                self.emit_csg_primitive(shape, target, operation)
            }
            Shape::Union(items) if operation == "cut" || operation == "join" => {
                for item in items {
                    self.emit_csg_apply(item, target, operation)?;
                }
                Ok(())
            }
            _ => Err(CadError::InvalidInput("unsupported nested CSG expression")),
        }
    }

    fn emit_csg_primitive(&mut self, shape: &Shape, target: &str, operation: &str) -> Result<(), CadError> {
        let mut params = match shape {
            Shape::Cube { size } => json!({
                "length": size.command_value(),
                "width": size.command_value(),
                "height": size.command_value(),
                "center": [0, 0, 0],
                "operation": operation
            }),
            Shape::Sphere { radius } => json!({
                "radius": radius.command_value(),
                "center": [0, 0, 0],
                "operation": operation
            }),
            Shape::Cylinder { height, diameter, axis } => {
                let half = height.negative_half_value();
                let base = match axis {
                    Axis::X => json!([half, 0, 0]),
                    Axis::Y => json!([0, half, 0]),
                    Axis::Z => json!([0, 0, half]),
                };
                json!({
                    "height": height.command_value(),
                    "diameter": diameter.command_value(),
                    "base": base,
                    "axis": axis.as_str(),
                    "operation": operation
                })
            }
            _ => return Err(CadError::InvalidInput("expected CSG primitive")),
        };

        if operation == "new" {
            params["body_name"] = json!(target);
        } else {
            params["targets"] = json!([target]);
        }

        let command = match shape {
            Shape::Cube { .. } => "solid.box",
            Shape::Sphere { .. } => "solid.sphere",
            Shape::Cylinder { .. } => "solid.cylinder",
            _ => unreachable!(),
        };
        self.transport.execute(command, params)?;
        Ok(())
    }

    pub fn build(&mut self, part: &Part) -> Result<(), CadError> {
        let base = &part.base;
        let name = &part.name;
        let hx = base.length.value_mm() / 2.0;
        let hy = base.width.value_mm() / 2.0;

        // Named CAD dimensions become native design parameters before any
        // feature refers to them. The public CAD API does not expose this command.
        for dimension in [&base.length, &base.width, &base.height] {
            if let Some(param) = dimension.parameter() {
                self.transport.execute(
                    "parameters.add",
                    json!({
                        "name": param.name(),
                        "expression": format!("{}", param.default_value().to_mm()),
                        "unit": "mm"
                    }),
                )?;
            }
        }

        // One semantic Box3D becomes four SolidCraft feature commands.
        self.transport.execute(
            "sketch.create",
            json!({"plane": "XY", "name": format!("{name} footprint")}),
        )?;
        self.transport.execute(
            "sketch.rectangle.two_point",
            json!({
                "p0": [
                    half_coordinate(&base.length, true),
                    half_coordinate(&base.width, true)
                ],
                "p1": [
                    half_coordinate(&base.length, false),
                    half_coordinate(&base.width, false)
                ]
            }),
        )?;
        self.transport.execute("sketch.finish", json!({}))?;
        self.transport.execute(
            "solid.extrude",
            json!({"distance": command_length(&base.height), "body_name": name}),
        )?;

        // Each geometric feature may require one or many SolidCraft steps.
        for feature in &part.features {
            match feature {
                Feature::EdgeFillet { selection: Edges::OuterVertical, radius } => {
                    // The first PoP knows only the analytic *base box* topology.
                    // Its four upright edges are selected at their midpoints.
                    // No claim of general topology selection is made here.
                    let z = base.height.value_mm() / 2.0;
                    let edges = [
                        [-hx, -hy, z], [hx, -hy, z],
                        [hx, hy, z], [-hx, hy, z],
                    ];
                    self.transport.execute(
                        "solid.fillet",
                        json!({"edges": edges, "radius": radius, "body": name}),
                    )?;
                }
                Feature::ThroughHoles { on: Faces::Top, holes } => {
                    // A semantic face selection becomes a native SolidCraft
                    // face attachment. The on-face point is the center of this
                    // known base box's top face, BEFORE any subtractive cuts.
                    // Use a point-only face pick. SolidCraft 0.30.1 rejects
                    // {body, face} without an exact face index. For this
                    // single-body PoP the top-centre point is unambiguous,
                    // so SolidCraft can resolve and capture the face itself.
                    self.transport.execute(
                        "sketch.create",
                        json!({
                            "plane": {
                                "face": [0.0, 0.0, base.height.value_mm()]
                            },
                            "name": format!("{name} top-face holes")
                        }),
                    )?;
                    for hole in holes {
                        self.transport.execute(
                            "sketch.circle.center",
                            json!({
                                "center": [hole.x, hole.y],
                                "diameter": hole.diameter
                            }),
                        )?;
                    }
                    self.transport.execute("sketch.finish", json!({}))?;
                    self.transport.execute(
                        "solid.extrude",
                        json!({
                            "distance": command_length(&base.height),
                            "direction": "negative",
                            "operation": "cut",
                            "targets": [name]
                        }),
                    )?;
                }
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cad::Hole;
    use crate::ScriptTransport;

    #[test]
    fn semantic_design_expands_to_multiple_native_commands() {
        let model = Part::box3d(100.0, 60.0, 10.0).unwrap()
            .named("Plate")
            .edges(Edges::OuterVertical).fillet(2.0).unwrap()
            .through_holes(&[
                Hole::at(-35.0, -15.0, 8.0).unwrap(),
                Hole::at(35.0, 15.0, 8.0).unwrap(),
            ]).unwrap();

        let mut adapter = SolidCraftAdapter::new(ScriptTransport::default());
        adapter.build(&model).unwrap();
        let script = adapter.into_transport().document();
        let commands = script["commands"].as_array().unwrap();
        assert_eq!(commands.len(), 13);
        assert_eq!(commands[0]["command"], "parameters.add");
        assert_eq!(commands[1]["command"], "parameters.add");
        assert_eq!(commands[2]["command"], "parameters.add");
        assert_eq!(commands[3]["command"], "sketch.create");
        assert_eq!(commands[4]["command"], "sketch.rectangle.two_point");
        assert_eq!(commands[6]["command"], "solid.extrude");
        assert_eq!(commands[7]["command"], "solid.fillet");
        assert_eq!(commands[7]["params"]["edges"].as_array().unwrap().len(), 4);
        assert_eq!(commands[8]["command"], "sketch.create");
        assert_eq!(commands[8]["params"]["plane"]["face"], json!([0.0, 0.0, 10.0]));
        assert_eq!(commands[9]["command"], "sketch.circle.center");
        assert_eq!(commands[10]["command"], "sketch.circle.center");
        assert_eq!(commands[11]["command"], "sketch.finish");
        assert_eq!(commands[12]["params"]["operation"], "cut");
        assert_eq!(commands[12]["params"]["targets"][0], "Plate");
    }

    /// The adapter must not swallow a transport error and keep issuing commands.
    struct FailingTransport { calls: usize }

    impl CommandTransport for FailingTransport {
        fn execute(&mut self, _command: &str, _params: serde_json::Value)
            -> Result<serde_json::Value, CadError>
        {
            self.calls += 1;
            if self.calls == 2 {
                Err(CadError::Transport("simulated failure".into()))
            } else {
                Ok(serde_json::Value::Null)
            }
        }
    }

    #[test]
    fn face_workplane_expands_to_native_attached_sketch() {
        let model = Part::box3d(80.0, 40.0, 5.0).unwrap()
            .named("Workplane sample")
            .faces(Faces::Top).workplane()
            .circle(-15.0, 0.0, 4.0).unwrap()
            .circle(15.0, 0.0, 4.0).unwrap()
            .cut_through().unwrap();
        let mut adapter = SolidCraftAdapter::new(ScriptTransport::default());
        adapter.build(&model).unwrap();
        let script = adapter.into_transport().document();
        let commands = script["commands"].as_array().unwrap();
        assert_eq!(commands[7]["command"], "sketch.create");
        assert_eq!(commands[7]["params"]["plane"]["face"], json!([0.0, 0.0, 5.0]));
        assert_eq!(commands[8]["command"], "sketch.circle.center");
        assert_eq!(commands[9]["command"], "sketch.circle.center");
        assert_eq!(commands[11]["command"], "solid.extrude");
        assert_eq!(commands[11]["params"]["direction"], "negative");
    }

    #[test]
    fn named_box_dimensions_emit_parameters_and_expressions() {
        use crate::cad::{Length, LengthParam};
        let model = Part::box3d(
            LengthParam::new("plate_length", Length::mm(100.0)).unwrap(),
            LengthParam::new("plate_width", Length::mm(60.0)).unwrap(),
            LengthParam::new("thickness", Length::mm(10.0)).unwrap(),
        ).unwrap();
        let mut adapter = SolidCraftAdapter::new(ScriptTransport::default());
        adapter.build(&model).unwrap();
        let script = adapter.into_transport().document();
        let commands = script["commands"].as_array().unwrap();
        assert_eq!(commands[0]["command"], "parameters.add");
        assert_eq!(commands[0]["params"]["name"], "plate_length");
        assert_eq!(commands[0]["params"]["unit"], "mm");
        assert_eq!(commands[3]["command"], "sketch.create");
        assert_eq!(commands[4]["params"]["p0"], json!(["-plate_length / 2", "-plate_width / 2"]));
        assert_eq!(commands[6]["params"]["distance"], "thickness");
    }

    #[test]
    fn csg_cube_compiles_to_native_primitives_without_temporary_combine_bodies() {
        use crate::csg::{parameter, Cube, Cylinder, LengthUnits, Sphere, X, Y, Z};

        let size = parameter("size", 50.mm()).unwrap();
        let model = (Sphere::new(size.clone() / 1.5) & Cube::new(size.clone()))
            - Cylinder::new(size.clone(), size / 1.5).orient([X, Y, Z]);

        let mut adapter = SolidCraftAdapter::new(ScriptTransport::default());
        adapter.build_csg(&model, "CsgCube").unwrap();
        let script = adapter.into_transport().document();
        let commands = script["commands"].as_array().unwrap();

        assert_eq!(commands.len(), 6);
        assert_eq!(commands[0]["command"], "parameters.add");
        assert_eq!(commands[1]["command"], "solid.sphere");
        assert_eq!(commands[2]["command"], "solid.box");
        assert_eq!(commands[2]["params"]["operation"], "intersect");
        assert_eq!(commands[3]["params"]["axis"], "X");
        assert_eq!(commands[4]["params"]["axis"], "Y");
        assert_eq!(commands[5]["params"]["axis"], "Z");
        assert!(commands.iter().all(|c| c["command"] != "solid.combine"));
    }

    #[test]
    fn failure_stops_compilation_of_command_sequence() {
        let model = Part::box3d(10.0, 10.0, 3.0).unwrap();
        let mut adapter = SolidCraftAdapter::new(FailingTransport { calls: 0 });
        assert!(adapter.build(&model).is_err());
        assert_eq!(adapter.into_transport().calls, 2);
    }
}
