//! Semantic CAD descriptions. Deliberately independent of SolidCraft, JSON and transport.
//!
//! These types express what to build. They never perform boolean operations or
//! compute a BRep; the actual CAD kernel always lives in SolidCraft.

use std::error::Error;
use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum DesignError {
    InvalidDimension(&'static str),
    InvalidPosition,
    HoleOutsideBase,
    IntersectingHoles,
    EmptyHoles,
    FilletOutsideBox,
    UnsupportedFeatureOrder,
    InvalidParameterName,
}

impl fmt::Display for DesignError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}
impl Error for DesignError {}

fn positive(value: f64, label: &'static str) -> Result<f64, DesignError> {
    if value.is_finite() && value > 0.0 {
        Ok(value)
    } else {
        Err(DesignError::InvalidDimension(label))
    }
}

/// A physical length, normalized to millimeters at the domain boundary.
/// The same type also represents signed coordinates (not only positive sizes).
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct Length(f64);

impl Length {
    pub fn mm(value: f64) -> Self { Self(value) }
    pub fn inches(value: f64) -> Self { Self(value * 25.4) }
    pub fn to_mm(self) -> f64 { self.0 }
}

/// A named CAD length parameter with an initial value.
/// This is design intent; the SolidCraft adapter decides how it is emitted.
#[derive(Debug, Clone, PartialEq)]
pub struct LengthParam {
    name: String,
    default: Length,
}

impl LengthParam {
    pub fn new(name: &str, default: Length) -> Result<Self, DesignError> {
        let mut chars = name.chars();
        let first_ok = chars.next().is_some_and(|c| c.is_ascii_alphabetic() || c == '_');
        if !first_ok || !chars.all(|c| c.is_ascii_alphanumeric() || c == '_') {
            return Err(DesignError::InvalidParameterName);
        }
        positive(default.to_mm(), "parameter default")?;
        Ok(Self { name: name.to_owned(), default })
    }

    pub fn name(&self) -> &str { &self.name }
    pub fn default_value(&self) -> Length { self.default }
}

/// A length used by a CAD feature: either a fixed value or a named parameter.
#[derive(Debug, Clone, PartialEq)]
pub enum LengthExpr {
    Fixed(Length),
    Parameter(LengthParam),
}

impl LengthExpr {
    pub fn value_mm(&self) -> f64 {
        match self {
            Self::Fixed(value) => value.to_mm(),
            Self::Parameter(param) => param.default_value().to_mm(),
        }
    }

    pub fn parameter(&self) -> Option<&LengthParam> {
        match self {
            Self::Fixed(_) => None,
            Self::Parameter(param) => Some(param),
        }
    }
}

impl From<f64> for LengthExpr {
    fn from(value: f64) -> Self { Self::Fixed(Length::mm(value)) }
}

impl From<Length> for LengthExpr {
    fn from(value: Length) -> Self { Self::Fixed(value) }
}

impl From<LengthParam> for LengthExpr {
    fn from(value: LengthParam) -> Self { Self::Parameter(value) }
}

/// Only a centered box is supported as the first experiment's base shape.
#[derive(Debug, Clone, PartialEq)]
pub struct Box3D {
    pub length: LengthExpr,
    pub width: LengthExpr,
    pub height: LengthExpr,
}

/// A through-hole described by its XY center and diameter, in millimeters.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Hole {
    pub x: f64,
    pub y: f64,
    pub diameter: f64,
}

impl Hole {
    pub fn at(x: f64, y: f64, diameter: f64) -> Result<Self, DesignError> {
        if !(x.is_finite() && y.is_finite()) {
            return Err(DesignError::InvalidPosition);
        }
        Ok(Self { x, y, diameter: positive(diameter, "hole diameter")? })
    }

    /// Supply explicit physical units (negative x/y offsets are valid).
    pub fn with_units(x: Length, y: Length, diameter: Length) -> Result<Self, DesignError> {
        Self::at(x.to_mm(), y.to_mm(), diameter.to_mm())
    }
}

/// A *semantic* edge selection, not a string or a list of SolidCraft pick points.
/// More general selectors need live topology queries before they can be added.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Edges {
    /// The four original upright edges of the base box.
    OuterVertical,
}

/// Semantic selection of a face. The first PoP supports the top of a base box;
/// no caller needs to specify a world-space XYZ point or a SolidCraft face ID.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Faces {
    Top,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Feature {
    EdgeFillet { selection: Edges, radius: f64 },
    ThroughHoles { on: Faces, holes: Vec<Hole> },
}

/// Engine-independent design intent, retained until an adapter builds it.
#[derive(Debug, Clone, PartialEq)]
pub struct Part {
    pub(crate) base: Box3D,
    pub(crate) name: String,
    pub(crate) features: Vec<Feature>,
}

/// Transitional fluent selection (inspired by CadQuery's `edges(...).fillet()`).
pub struct SelectedEdges {
    part: Part,
    selection: Edges,
}

impl SelectedEdges {
    pub fn fillet<R>(mut self, radius: R) -> Result<Part, DesignError>
    where
        R: Into<LengthExpr>,
    {
        let radius = positive(radius.into().value_mm(), "fillet radius")?;
        if radius * 2.0 >= self.part.base.length.value_mm().min(self.part.base.width.value_mm()) {
            return Err(DesignError::FilletOutsideBox);
        }
        self.part.features.push(Feature::EdgeFillet {
            selection: self.selection,
            radius,
        });
        Ok(self.part)
    }
}

/// A face selected by its meaning rather than by native topology identifiers.
pub struct SelectedFace {
    part: Part,
    face: Faces,
}

impl SelectedFace {
    /// Starts a 2D design-intent context. This is NOT `sketch.create`;
    /// no SolidCraft transport is used until a part is compiled by the adapter.
    pub fn workplane(self) -> Workplane {
        Workplane { part: self.part, face: self.face, circles: vec![] }
    }
}

/// Simple sketch feature builder on a semantic face.
pub struct Workplane {
    part: Part,
    face: Faces,
    circles: Vec<Hole>,
}

impl Workplane {
    pub fn circle(mut self, x: f64, y: f64, diameter: f64) -> Result<Self, DesignError> {
        self.circles.push(Hole::at(x, y, diameter)?);
        Ok(self)
    }

    pub fn circles(mut self, holes: &[Hole]) -> Result<Self, DesignError> {
        self.circles.extend_from_slice(holes);
        Ok(self)
    }

    /// A feature in CAD terms. Adapter handles plane attachment, sketch,
    /// circles, finish, and the subtractive extrusion.
    pub fn cut_through(self) -> Result<Part, DesignError> {
        self.part.through_holes_on(self.face, &self.circles)
    }
}

impl Part {
    /// A box centered around X/Y=(0,0), with its underside at Z=0.
    pub fn box3d<L, W, H>(length: L, width: W, height: H) -> Result<Self, DesignError>
    where
        L: Into<LengthExpr>,
        W: Into<LengthExpr>,
        H: Into<LengthExpr>,
    {
        let length = length.into();
        let width = width.into();
        let height = height.into();
        positive(length.value_mm(), "length")?;
        positive(width.value_mm(), "width")?;
        positive(height.value_mm(), "height")?;
        Ok(Self {
            base: Box3D { length, width, height },
            name: "Part".into(),
            features: vec![],
        })
    }

    pub fn named(mut self, name: &str) -> Self {
        if !name.trim().is_empty() {
            self.name = name.to_owned();
        }
        self
    }

    pub fn edges(self, selection: Edges) -> SelectedEdges {
        SelectedEdges { part: self, selection }
    }

    /// Select a face by a CAD concept, then describe a workplane operation.
    /// For now this is limited to the upper face of an original base box.
    pub fn faces(self, face: Faces) -> SelectedFace {
        SelectedFace { part: self, face }
    }

    /// Through-holes run from the top to the underside of the base box.
    /// This does not expose sketches, cuts, planes, or SolidCraft command IDs.
    pub fn through_holes(self, holes: &[Hole]) -> Result<Self, DesignError> {
        self.through_holes_on(Faces::Top, holes)
    }

    fn through_holes_on(mut self, face: Faces, holes: &[Hole]) -> Result<Self, DesignError> {
        // The face-pick point is guaranteed only before another cut changes
        // the base's upper face. Reject rather than silently picking a void.
        if self.features.iter().any(|f| matches!(f, Feature::ThroughHoles { .. })) {
            return Err(DesignError::UnsupportedFeatureOrder);
        }
        if holes.is_empty() {
            return Err(DesignError::EmptyHoles);
        }
        for (i, hole) in holes.iter().enumerate() {
            let radius = hole.diameter / 2.0;
            if hole.x.abs() + radius >= self.base.length.value_mm() / 2.0
                || hole.y.abs() + radius >= self.base.width.value_mm() / 2.0
            {
                return Err(DesignError::HoleOutsideBase);
            }
            for other in &holes[..i] {
                let min_distance = (hole.diameter + other.diameter) / 2.0;
                if (hole.x - other.x).hypot(hole.y - other.y) <= min_distance {
                    return Err(DesignError::IntersectingHoles);
                }
            }
        }
        self.features.push(Feature::ThroughHoles { on: face, holes: holes.to_vec() });
        Ok(self)
    }

    /// Length-typed constructor. The legacy box3d(f64,..) remains mm shorthand.
    pub fn box_with_units(length: Length, width: Length, height: Length) -> Result<Self, DesignError> {
        Self::box3d(length, width, height)
    }

    pub fn dimensions(&self) -> (f64, f64, f64) {
        (self.base.length.value_mm(), self.base.width.value_mm(), self.base.height.value_mm())
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn feature_count(&self) -> usize {
        self.features.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fluent_design_is_engine_independent() {
        let part = Part::box3d(100.0, 60.0, 10.0).unwrap()
            .named("Plate")
            .edges(Edges::OuterVertical).fillet(2.0).unwrap()
            .through_holes(&[
                Hole::at(-35.0, -15.0, 8.0).unwrap(),
                Hole::at(35.0, 15.0, 8.0).unwrap(),
            ]).unwrap();

        assert_eq!(part.name(), "Plate");
        assert_eq!(part.dimensions(), (100.0, 60.0, 10.0));
        assert_eq!(part.feature_count(), 2);
        assert!(matches!(part.features[0], Feature::EdgeFillet { .. }));
        assert!(matches!(part.features[1], Feature::ThroughHoles { on: Faces::Top, .. }));
    }

    #[test]
    fn reject_invalid_dimensions() {
        assert!(Part::box3d(0.0, 10.0, 1.0).is_err());
        assert!(Part::box3d(f64::NAN, 10.0, 1.0).is_err());
        assert!(Hole::at(f64::INFINITY, 0.0, 1.0).is_err());
        assert!(Part::box3d(20.0, 10.0, 1.0).unwrap()
            .edges(Edges::OuterVertical).fillet(5.0).is_err());
    }

    #[test]
    fn unit_typed_constructors_convert_to_mm() {
        let part = Part::box_with_units(
            Length::mm(100.0), Length::inches(2.0), Length::mm(10.0)
        ).unwrap();
        assert_eq!(part.dimensions(), (100.0, 50.8, 10.0));
        let hole = Hole::with_units(
            Length::inches(-1.0), Length::mm(0.0), Length::mm(8.0)
        ).unwrap();
        assert_eq!(hole.x, -25.4);
        assert_eq!(hole.diameter, 8.0);
        assert!(Part::box_with_units(
            Length::mm(f64::NAN), Length::mm(10.0), Length::mm(2.0)
        ).is_err());
    }

    #[test]
    fn selected_top_face_workplane_is_semantic() {
        let part = Part::box3d(100.0, 60.0, 10.0).unwrap()
            .named("Plate")
            .faces(Faces::Top).workplane()
            .circle(-35.0, -15.0, 8.0).unwrap()
            .circle(35.0, 15.0, 8.0).unwrap()
            .cut_through().unwrap();

        assert!(matches!(
            &part.features[0],
            Feature::ThroughHoles { on: Faces::Top, holes } if holes.len() == 2
        ));
        assert_eq!(part.name(), "Plate");
        assert_eq!(part.feature_count(), 1);
    }

    #[test]
    fn unsupported_second_face_cut_is_rejected() {
        let part = Part::box3d(100.0, 60.0, 10.0).unwrap()
            .faces(Faces::Top).workplane()
            .circle(0.0, 0.0, 8.0).unwrap()
            .cut_through().unwrap();

        assert!(matches!(
            part.faces(Faces::Top).workplane()
                .circle(10.0, 10.0, 3.0).unwrap().cut_through(),
            Err(DesignError::UnsupportedFeatureOrder)
        ));
    }

    #[test]
    fn named_box_dimensions_remain_domain_parameters() {
        let length = LengthParam::new("plate_length", Length::mm(100.0)).unwrap();
        let width = LengthParam::new("plate_width", Length::mm(60.0)).unwrap();
        let thickness = LengthParam::new("thickness", Length::mm(10.0)).unwrap();
        let part = Part::box3d(length, width, thickness).unwrap();
        assert_eq!(part.dimensions(), (100.0, 60.0, 10.0));
        assert_eq!(part.base.length.parameter().unwrap().name(), "plate_length");
        assert_eq!(part.base.height.parameter().unwrap().name(), "thickness");
        assert!(LengthParam::new("not a parameter", Length::mm(1.0)).is_err());
    }

    #[test]
    fn reject_holes_that_cannot_fit() {
        let base = Part::box3d(20.0, 10.0, 5.0).unwrap();
        assert!(base.clone().through_holes(&[]).is_err());
        assert!(base.clone().through_holes(&[
            Hole::at(8.0, 0.0, 6.0).unwrap()
        ]).is_err());
        assert!(base.through_holes(&[
            Hole::at(0.0, 0.0, 5.0).unwrap(),
            Hole::at(2.0, 0.0, 5.0).unwrap(),
        ]).is_err());
    }
}
