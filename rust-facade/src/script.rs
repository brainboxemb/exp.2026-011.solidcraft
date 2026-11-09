use crate::cad::{DesignError, Part};
use crate::csg::Shape;

#[derive(Debug, Clone, PartialEq)]
pub enum BuiltModel {
    Csg(Shape),
    Feature(Part),
}

pub trait IntoBuiltModel {
    fn into_built_model(self) -> Result<BuiltModel, DesignError>;
}

impl IntoBuiltModel for Shape {
    fn into_built_model(self) -> Result<BuiltModel, DesignError> {
        Ok(BuiltModel::Csg(self))
    }
}

impl IntoBuiltModel for Part {
    fn into_built_model(self) -> Result<BuiltModel, DesignError> {
        Ok(BuiltModel::Feature(self))
    }
}

impl IntoBuiltModel for Result<Shape, DesignError> {
    fn into_built_model(self) -> Result<BuiltModel, DesignError> {
        self.map(BuiltModel::Csg)
    }
}

impl IntoBuiltModel for Result<Part, DesignError> {
    fn into_built_model(self) -> Result<BuiltModel, DesignError> {
        self.map(BuiltModel::Feature)
    }
}

#[macro_export]
macro_rules! build {
    ($expr:expr) => {
        pub fn model() -> Result<$crate::script::BuiltModel, $crate::cad::DesignError> {
            $crate::script::IntoBuiltModel::into_built_model($expr)
        }
    };
}
