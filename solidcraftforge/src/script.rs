//! Technical boundary between a SolidCraftForge script and the SolidCraft adapter.
//!
//! User-facing model files do not call this module. The external runner wraps the
//! script's final expression and converts the resulting CAD object into this
//! common representation.

use crate::cad::Part;
use crate::csg::Shape;
use crate::solidcraft_adapter::SolidCraftAdapter;
use crate::{CadError, CommandTransport};

#[derive(Debug, Clone, PartialEq)]
pub enum ScriptModel {
    Part(Part),
    Shape { name: String, shape: Shape },
}

pub trait IntoScriptModel {
    fn into_script_model(self, name: &str) -> ScriptModel;
}

impl IntoScriptModel for Part {
    fn into_script_model(self, _name: &str) -> ScriptModel {
        ScriptModel::Part(self)
    }
}

impl IntoScriptModel for Shape {
    fn into_script_model(self, name: &str) -> ScriptModel {
        ScriptModel::Shape {
            name: name.to_owned(),
            shape: self,
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
            Self::Shape { name, shape } => adapter.build_csg(shape, name),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cad::Part;
    use crate::csg::{Cube, LengthUnits};

    #[test]
    fn runner_accepts_part_and_shape_results() {
        let part = Part::box3d(10.0, 20.0, 3.0).unwrap();
        assert!(matches!(
            part.into_script_model("Ignored"),
            ScriptModel::Part(_)
        ));

        let shape = Cube::new(10.mm());
        assert!(matches!(
            shape.into_script_model("Cube"),
            ScriptModel::Shape { name, .. } if name == "Cube"
        ));
    }
}
