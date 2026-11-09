//! Script-facing CAD syntax. The runner imports the prelude, collects errors,
//! and compiles the final Shape; model.rs contains no plumbing.

use crate::cad::{CylinderCut, DesignError, Edges, Part};
use crate::csg::{self, Axis};
use crate::solidcraft_adapter::SolidCraftAdapter;
use crate::{CadError, CommandTransport};
use std::ops::{Add, BitAnd, BitOr, Sub};

pub mod prelude {
    pub use super::{Cube, Cylinder, Shape, Sphere};
    pub use crate::cad::Edges;
    pub use crate::csg::{X, Y, Z};
}

#[derive(Debug, Clone, PartialEq)]
pub enum ScriptModel {
    Part(Part),
    Csg { name: String, shape: csg::Shape },
}

#[derive(Debug, Clone)]
enum ShapeState {
    Part(Result<Part, DesignError>),
    Csg(csg::Shape),
    Error(DesignError),
}

/// The single public SolidCraftForge modeling result: features and CSG solids
/// share this type. Internally they retain separate CAD descriptions.
#[derive(Debug, Clone)]
pub struct Shape {
    state: ShapeState,
}

impl Shape {
    pub fn box3d(length: f64, width: f64, thickness: f64) -> Self {
        Self { state: ShapeState::Part(Part::box3d(length, width, thickness)) }
    }

    fn csg(shape: csg::Shape) -> Self {
        Self { state: ShapeState::Csg(shape) }
    }

    pub fn named(mut self, name: &str) -> Self {
        self.state = match self.state {
            ShapeState::Part(part) => ShapeState::Part(part.map(|p| p.named(name))),
            other => other,
        };
        self
    }

    pub fn fillet(mut self, edges: Edges, radius: f64) -> Self {
        self.state = match self.state {
            ShapeState::Part(part) => ShapeState::Part(
                part.and_then(|p| p.edges(edges).fillet(radius))
            ),
            _ => ShapeState::Error(DesignError::UnsupportedFeatureOrder),
        };
        self
    }

    pub fn subtract(mut self, cutters: Result<CylinderCut, DesignError>) -> Self {
        self.state = match self.state {
            ShapeState::Part(part) => ShapeState::Part(
                part.and_then(|p| cutters.and_then(|c| p.subtract(c)))
            ),
            _ => ShapeState::Error(DesignError::UnsupportedFeatureOrder),
        };
        self
    }
}

fn boolean(left: Shape, right: Shape, op: fn(csg::Shape, csg::Shape) -> csg::Shape) -> Shape {
    match (left.state, right.state) {
        (ShapeState::Csg(a), ShapeState::Csg(b)) => Shape::csg(op(a, b)),
        (ShapeState::Error(e), _) | (_, ShapeState::Error(e)) => Shape { state: ShapeState::Error(e) },
        _ => Shape { state: ShapeState::Error(DesignError::UnsupportedFeatureOrder) },
    }
}

impl BitAnd for Shape {
    type Output = Shape;
    fn bitand(self, rhs: Shape) -> Shape { boolean(self, rhs, |a,b| a & b) }
}
impl BitOr for Shape {
    type Output = Shape;
    fn bitor(self, rhs: Shape) -> Shape { boolean(self, rhs, |a,b| a | b) }
}
impl Add for Shape {
    type Output = Shape;
    fn add(self, rhs: Shape) -> Shape { boolean(self, rhs, |a,b| a + b) }
}
impl Sub for Shape {
    type Output = Shape;
    fn sub(self, rhs: Shape) -> Shape { boolean(self, rhs, |a,b| a - b) }
}

/// CSG primitives that return the same public Shape as feature CAD modeling.
pub struct Cube;
impl Cube {
    pub fn new(size: f64) -> Shape { Shape::csg(csg::Cube::new(size)) }
}

pub struct Sphere;
impl Sphere {
    pub fn new(radius: f64) -> Shape { Shape::csg(csg::Sphere::new(radius)) }
}

pub struct Cylinder(csg::Cylinder);
impl Cylinder {
    pub fn new(height: f64, diameter: f64) -> Self {
        Self(csg::Cylinder::new(height, diameter))
    }

    pub fn orient<const N: usize>(&self, axes: [Axis; N]) -> Shape {
        Shape::csg(self.0.orient(axes))
    }

    pub fn rectangular_pattern(self, spacing_x: f64, spacing_y: f64)
        -> Result<CylinderCut, DesignError>
    {
        self.0.rectangular_pattern(spacing_x, spacing_y)
    }
}

pub trait IntoScriptModel {
    fn into_script_model(self, name: &str) -> Result<ScriptModel, DesignError>;
}

impl IntoScriptModel for Shape {
    fn into_script_model(self, name: &str) -> Result<ScriptModel, DesignError> {
        match self.state {
            ShapeState::Part(result) => result.map(ScriptModel::Part),
            ShapeState::Csg(shape) => Ok(ScriptModel::Csg { name: name.to_owned(), shape }),
            ShapeState::Error(error) => Err(error),
        }
    }
}

impl ScriptModel {
    pub fn compile<T: CommandTransport>(
        &self,
        adapter: &mut SolidCraftAdapter<T>,
    ) -> Result<(), CadError> {
        match self {
            Self::Part(part) => adapter.build(part),
            Self::Csg { name, shape } => adapter.build_csg(shape, name),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn both_styles_return_the_same_public_shape() {
        let plate: Shape = Shape::box3d(100.0, 60.0, 10.0)
            .named("Plate")
            .fillet(Edges::OuterVertical, 2.0)
            .subtract(Cylinder::new(10.0, 8.0).rectangular_pattern(70.0, 30.0));
        assert!(matches!(plate.into_script_model("Plate"), Ok(ScriptModel::Part(_))));

        let cube: Shape = (Sphere::new(50.0 / 1.5) & Cube::new(50.0))
            - Cylinder::new(50.0, 50.0 / 1.5).orient([csg::X, csg::Y, csg::Z]);
        assert!(matches!(cube.into_script_model("CsgCube"), Ok(ScriptModel::Csg { .. })));
    }

    #[test]
    fn errors_reach_runner_without_question_marks_in_script() {
        let bad = Shape::box3d(10.0, 10.0, 5.0)
            .subtract(Cylinder::new(2.0, 8.0).rectangular_pattern(6.0, 6.0));
        assert!(bad.into_script_model("Plate").is_err());
    }
}
