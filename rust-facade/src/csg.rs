//! Small SolidCraft-independent CSG domain used by the scripting experiments.

use crate::cad::{DesignError, Length, LengthParam};
use serde_json::{json, Value};
use std::ops::{Add, BitAnd, BitOr, Div, Sub};

pub trait LengthUnits {
    fn mm(self) -> Length;
}

macro_rules! impl_mm {
    ($($t:ty),+ $(,)?) => {$(
        impl LengthUnits for $t {
            fn mm(self) -> Length { Length::mm(self as f64) }
        }
    )+};
}
impl_mm!(f64, f32, i32, i64, u32, u64, usize);

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ParamLength {
    name: &'static str,
    default: Length,
}

impl ParamLength {
    pub fn new(name: &'static str, default: Length) -> Self {
        Self { name, default }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct DimExpr {
    value_mm: f64,
    expression: Option<String>,
    parameters: Vec<ParamLength>,
}

impl DimExpr {
    fn fixed(value: Length) -> Self {
        Self { value_mm: value.to_mm(), expression: None, parameters: vec![] }
    }

    pub(crate) fn value_mm(&self) -> f64 { self.value_mm }

    pub(crate) fn command_value(&self) -> Value {
        match &self.expression {
            Some(expression) => json!(expression),
            None => json!(self.value_mm),
        }
    }

    pub(crate) fn negative_half_value(&self) -> Value {
        match &self.expression {
            Some(expression) => json!(format!("-({expression}) / 2")),
            None => json!(-self.value_mm / 2.0),
        }
    }

    pub(crate) fn parameters(&self) -> &[ParamLength] { &self.parameters }

    fn validate_positive(&self) -> Result<(), DesignError> {
        if self.value_mm.is_finite() && self.value_mm > 0.0 {
            Ok(())
        } else {
            Err(DesignError::InvalidDimension("CSG dimension"))
        }
    }
}

impl From<Length> for DimExpr {
    fn from(value: Length) -> Self { Self::fixed(value) }
}

impl From<ParamLength> for DimExpr {
    fn from(value: ParamLength) -> Self {
        Self {
            value_mm: value.default.to_mm(),
            expression: Some(value.name.to_owned()),
            parameters: vec![value],
        }
    }
}

impl Div<f64> for ParamLength {
    type Output = DimExpr;

    fn div(self, rhs: f64) -> Self::Output {
        DimExpr::from(self) / rhs
    }
}

impl Div<f64> for DimExpr {
    type Output = Self;

    fn div(mut self, rhs: f64) -> Self::Output {
        self.value_mm /= rhs;
        self.expression = Some(match self.expression {
            Some(expression) => format!("{expression} / {rhs}"),
            None => format!("{} / {rhs}", self.value_mm * rhs),
        });
        self
    }
}

pub fn parameter(name: &'static str, default: Length) -> Result<DimExpr, DesignError> {
    LengthParam::new(name, default)?;
    Ok(ParamLength::new(name, default).into())
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Axis {
    X,
    Y,
    Z,
}

impl Axis {
    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::X => "X",
            Self::Y => "Y",
            Self::Z => "Z",
        }
    }
}

pub const X: Axis = Axis::X;
pub const Y: Axis = Axis::Y;
pub const Z: Axis = Axis::Z;

#[derive(Debug, Clone, PartialEq)]
pub enum Shape {
    Cube { size: DimExpr },
    Sphere { radius: DimExpr },
    Cylinder { height: DimExpr, diameter: DimExpr, axis: Axis },
    Union(Vec<Shape>),
    Intersection(Box<Shape>, Box<Shape>),
    Difference(Box<Shape>, Box<Shape>),
}

pub struct Cube;
impl Cube {
    pub fn new(size: impl Into<DimExpr>) -> Shape {
        Shape::Cube { size: size.into() }
    }
}

pub struct Sphere;
impl Sphere {
    pub fn new(radius: impl Into<DimExpr>) -> Shape {
        Shape::Sphere { radius: radius.into() }
    }
}

#[derive(Debug, Clone)]
pub struct Cylinder {
    height: DimExpr,
    diameter: DimExpr,
}

impl Cylinder {
    pub fn new(height: impl Into<DimExpr>, diameter: impl Into<DimExpr>) -> Self {
        Self { height: height.into(), diameter: diameter.into() }
    }

    pub fn orient<const N: usize>(&self, axes: [Axis; N]) -> Shape {
        let mut shapes: Vec<Shape> = axes.into_iter()
            .map(|axis| Shape::Cylinder {
                height: self.height.clone(),
                diameter: self.diameter.clone(),
                axis,
            })
            .collect();

        match shapes.len() {
            1 => shapes.pop().unwrap(),
            _ => Shape::Union(shapes),
        }
    }
}

fn union(left: Shape, right: Shape) -> Shape {
    let mut items = match left {
        Shape::Union(items) => items,
        other => vec![other],
    };
    match right {
        Shape::Union(mut rhs) => items.append(&mut rhs),
        other => items.push(other),
    }
    Shape::Union(items)
}

impl BitAnd for Shape {
    type Output = Shape;
    fn bitand(self, rhs: Shape) -> Self::Output {
        Shape::Intersection(Box::new(self), Box::new(rhs))
    }
}

impl BitOr for Shape {
    type Output = Shape;
    fn bitor(self, rhs: Shape) -> Self::Output { union(self, rhs) }
}

impl Add for Shape {
    type Output = Shape;
    fn add(self, rhs: Shape) -> Self::Output { union(self, rhs) }
}

impl Sub for Shape {
    type Output = Shape;
    fn sub(self, rhs: Shape) -> Self::Output {
        Shape::Difference(Box::new(self), Box::new(rhs))
    }
}

impl Shape {
    pub(crate) fn validate(&self) -> Result<(), DesignError> {
        match self {
            Self::Cube { size } => size.validate_positive(),
            Self::Sphere { radius } => radius.validate_positive(),
            Self::Cylinder { height, diameter, .. } => {
                height.validate_positive()?;
                diameter.validate_positive()
            }
            Self::Union(items) => {
                if items.is_empty() {
                    return Err(DesignError::InvalidDimension("empty CSG union"));
                }
                for item in items { item.validate()?; }
                Ok(())
            }
            Self::Intersection(left, right) | Self::Difference(left, right) => {
                left.validate()?;
                right.validate()
            }
        }
    }

    pub(crate) fn collect_parameters(&self, out: &mut Vec<LengthParam>) {
        fn add(expr: &DimExpr, out: &mut Vec<LengthParam>) {
            for parameter in expr.parameters() {
                if !out.iter().any(|p| p.name() == parameter.name) {
                    out.push(
                        LengthParam::new(parameter.name, parameter.default)
                            .expect("validated CAD parameter"),
                    );
                }
            }
        }

        match self {
            Self::Cube { size } => add(size, out),
            Self::Sphere { radius } => add(radius, out),
            Self::Cylinder { height, diameter, .. } => {
                add(height, out);
                add(diameter, out);
            }
            Self::Union(items) => {
                for item in items { item.collect_parameters(out); }
            }
            Self::Intersection(left, right) | Self::Difference(left, right) => {
                left.collect_parameters(out);
                right.collect_parameters(out);
            }
        }
    }
}


#[macro_export]
macro_rules! part {
    ($name:ident($($param:ident : Length),* $(,)?) $body:block) => {
        #[allow(non_snake_case)]
        pub fn $name($($param: $crate::cad::Length),*) -> $crate::csg::Shape {
            $(let $param = $crate::csg::ParamLength::new(stringify!($param), $param);)*
            $body
        }
    };
}

#[macro_export]
macro_rules! root {
    ($expr:expr) => {
        pub fn model() -> $crate::csg::Shape {
            $expr
        }
    };
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn csg_cube_model_is_pure_domain_intent() {
        let size = parameter("size", 50.mm()).unwrap();
        let body = Sphere::new(size.clone() / 1.5) & Cube::new(size.clone());
        let holes = Cylinder::new(size.clone(), size / 1.5).orient([X, Y, Z]);
        let model = body - holes;

        model.validate().unwrap();
        let mut parameters = vec![];
        model.collect_parameters(&mut parameters);
        assert_eq!(parameters.len(), 1);
        assert_eq!(parameters[0].name(), "size");
    }
}
