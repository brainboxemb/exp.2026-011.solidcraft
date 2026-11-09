//! Technical script boundary. Users write only Rust CAD objects and expressions.
//! Imports, error propagation and SolidCraft command generation live here.

use crate::cad::{DesignError, Edges, Part};
use crate::csg::Shape;
use crate::solidcraft_adapter::SolidCraftAdapter;
use crate::{CadError, CommandTransport};

/// Automatically imported into a SolidCraftForge model.rs by the runner.
pub mod prelude {
    pub use crate::cad::{Edges, Faces, Hole, Length, Part};
    pub use crate::csg::{Cube, Cylinder, LengthUnits, ParamLength, Shape, Sphere, X, Y, Z};
    pub use super::Model;
}

#[derive(Debug, Clone, PartialEq)]
pub enum ScriptModel {
    Part(Part),
    Shape { name: String, shape: Shape },
}

/// Script-facing fluent part, carrying any design error to the runner.
/// No Result or ? is required in the user's model.rs.
pub struct Model {
    result: Result<Part, DesignError>,
}

impl Model {
    pub fn box3d(length: f64, width: f64, thickness: f64) -> Self {
        Self { result: Part::box3d(length, width, thickness) }
    }

    pub fn named(mut self, name: &str) -> Self {
        self.result = self.result.map(|part| part.named(name));
        self
    }

    pub fn fillet(mut self, edges: Edges, radius: f64) -> Self {
        self.result = self.result.and_then(|part| part.edges(edges).fillet(radius));
        self
    }

    pub fn subtract(
        mut self,
        cutters: Result<crate::cad::CylinderCut, DesignError>,
    ) -> Self {
        self.result = self.result.and_then(|part| cutters.and_then(|c| part.subtract(c)));
        self
    }
}

pub trait IntoScriptModel {
    fn into_script_model(self, name: &str) -> Result<ScriptModel, DesignError>;
}

impl IntoScriptModel for Model {
    fn into_script_model(self, _name: &str) -> Result<ScriptModel, DesignError> {
        self.result.map(ScriptModel::Part)
    }
}

impl IntoScriptModel for Part {
    fn into_script_model(self, _name: &str) -> Result<ScriptModel, DesignError> {
        Ok(ScriptModel::Part(self))
    }
}

impl IntoScriptModel for Shape {
    fn into_script_model(self, name: &str) -> Result<ScriptModel, DesignError> {
        Ok(ScriptModel::Shape { name: name.to_owned(), shape: self })
    }
}

impl ScriptModel {
    pub fn compile<T: CommandTransport>(
        &self,
        adapter: &mut SolidCraftAdapter<T>,
    ) -> Result<(), CadError> {
        match self {
            Self::Part(part) => adapter.build(part),
            Self::Shape { name, shape } => adapter.build_csg(shape, name),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::csg::{Cube, Cylinder};

    #[test]
    fn runner_accepts_part_and_shape_results() {
        let part = Part::box3d(10.0, 20.0, 3.0).unwrap();
        assert!(matches!(
            part.into_script_model("Ignored").unwrap(),
            ScriptModel::Part(_)
        ));

        let shape = Cube::new(10.0);
        assert!(matches!(
            shape.into_script_model("Cube").unwrap(),
            ScriptModel::Shape { name, .. } if name == "Cube"
        ));
    }

    #[test]
    fn script_builder_preserves_errors_for_runner() {
        let good = Model::box3d(100.0, 60.0, 10.0)
            .named("Plate")
            .fillet(Edges::OuterVertical, 2.0)
            .subtract(Cylinder::new(10.0, 8.0).rectangular_pattern(70.0, 30.0));
        assert!(matches!(good.into_script_model("Plate"), Ok(ScriptModel::Part(_))));

        let invalid = Model::box3d(10.0, 10.0, 5.0)
            .subtract(Cylinder::new(2.0, 8.0).rectangular_pattern(6.0, 6.0));
        assert!(invalid.into_script_model("Plate").is_err());
    }
}
