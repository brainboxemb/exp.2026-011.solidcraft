//! An intentionally small Rust facade over *SolidCraft commands*.
//!
//! This crate does not implement a CAD kernel. SolidCraft owns the geometry.
//! The first backend is a command script; future GUI/MCP backends implement
//! the same CommandTransport trait and return actual engine results.

pub mod cad;
pub mod solidcraft_adapter;

use serde_json::{json, Value};
use std::fmt;
use std::fs;
use std::path::Path;

#[derive(Debug)]
pub enum CadError {
    InvalidInput(&'static str),
    Io(std::io::Error),
    Json(serde_json::Error),
    Transport(String),
}

impl fmt::Display for CadError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidInput(message) => write!(f, "invalid input: {message}"),
            Self::Io(error) => write!(f, "I/O error: {error}"),
            Self::Json(error) => write!(f, "JSON error: {error}"),
            Self::Transport(message) => write!(f, "SolidCraft transport: {message}"),
        }
    }
}
impl std::error::Error for CadError {}

impl From<std::io::Error> for CadError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}
impl From<serde_json::Error> for CadError {
    fn from(error: serde_json::Error) -> Self {
        Self::Json(error)
    }
}

/// The protocol boundary. A live transport returns real SolidCraft results.
pub trait CommandTransport {
    fn execute(&mut self, command: &str, params: Value) -> Result<Value, CadError>;
}

/// Collect engine commands into a native SolidCraft JSON script.
#[derive(Debug, Default)]
pub struct ScriptTransport {
    commands: Vec<Value>,
}

impl CommandTransport for ScriptTransport {
    fn execute(&mut self, command: &str, params: Value) -> Result<Value, CadError> {
        self.commands.push(json!({"command": command, "params": params}));
        Ok(Value::Null) // Batch scripts do not provide per-command return IDs.
    }
}

impl ScriptTransport {
    pub fn document(&self) -> Value {
        json!({"commands": self.commands})
    }

    pub fn write(&self, path: impl AsRef<Path>) -> Result<(), CadError> {
        let data = serde_json::to_vec_pretty(&self.document())?;
        fs::write(path, data)?;
        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub enum Direction {
    Positive,
    Negative,
}

impl Direction {
    fn as_command_value(self) -> &'static str {
        match self {
            Self::Positive => "positive",
            Self::Negative => "negative",
        }
    }
}

/// A Rust client API that delegates all geometry to SolidCraft.
pub struct SolidCraft<B: CommandTransport> {
    transport: B,
}

impl<B: CommandTransport> SolidCraft<B> {
    pub fn new(transport: B) -> Self {
        Self { transport }
    }

    pub fn into_transport(self) -> B {
        self.transport
    }

    pub fn parameter(&mut self, name: &str, expression: &str) -> Result<&mut Self, CadError> {
        if name.trim().is_empty() || expression.trim().is_empty() {
            return Err(CadError::InvalidInput("parameter name and expression required"));
        }
        self.transport.execute(
            "parameters.change",
            json!({"name": name, "expression": expression}),
        )?;
        Ok(self)
    }

    pub fn sketch(&mut self, plane: &str, name: &str) -> Result<&mut Self, CadError> {
        if plane.trim().is_empty() || name.trim().is_empty() {
            return Err(CadError::InvalidInput("sketch plane and name required"));
        }
        self.transport.execute(
            "sketch.create",
            json!({"plane": plane, "name": name}),
        )?;
        Ok(self)
    }

    pub fn closed_polygon(&mut self, points: &[[f64; 2]]) -> Result<&mut Self, CadError> {
        if points.len() < 3 || points.iter().flatten().any(|x| !x.is_finite()) {
            return Err(CadError::InvalidInput("at least 3 finite 2D points are required"));
        }
        self.transport.execute(
            "sketch.line",
            json!({"points": points, "closed": true}),
        )?;
        Ok(self)
    }

    pub fn finish_sketch(&mut self) -> Result<&mut Self, CadError> {
        self.transport.execute("sketch.finish", json!({}))?;
        Ok(self)
    }

    pub fn extrude(
        &mut self,
        distance: &str,
        direction: Direction,
        body_name: &str,
    ) -> Result<&mut Self, CadError> {
        if distance.trim().is_empty() || body_name.trim().is_empty() {
            return Err(CadError::InvalidInput("extrusion distance and body name required"));
        }
        self.transport.execute(
            "solid.extrude",
            json!({
                "distance": distance,
                "direction": direction.as_command_value(),
                "body_name": body_name
            }),
        )?;
        Ok(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn emits_solidcraft_bracket_commands() {
        let mut cad = SolidCraft::new(ScriptTransport::default());
        cad.parameter("width", "60 mm").unwrap()
            .sketch("XZ", "Profile").unwrap()
            .closed_polygon(&[[0.0, 0.0], [40.0, 0.0], [40.0, 6.0],
                              [6.0, 6.0], [6.0, 30.0], [0.0, 30.0]]).unwrap()
            .finish_sketch().unwrap()
            .extrude("width", Direction::Negative, "Bracket").unwrap();
        let commands = cad.into_transport().document();
        let arr = commands["commands"].as_array().unwrap();
        assert_eq!(arr.len(), 5);
        assert_eq!(arr[0]["command"], "parameters.change");
        assert_eq!(arr[1]["params"]["plane"], "XZ");
        assert_eq!(arr[2]["command"], "sketch.line");
        assert_eq!(arr[2]["params"]["closed"], true);
        assert_eq!(arr[3]["command"], "sketch.finish");
        assert_eq!(arr[4]["params"]["distance"], "width");
    }

    #[test]
    fn rejects_invalid_geometry_before_command() {
        let mut cad = SolidCraft::new(ScriptTransport::default());
        assert!(cad.closed_polygon(&[[0.0, 0.0], [1.0, 1.0]]).is_err());
        assert!(cad.closed_polygon(&[[0.0, 0.0], [1.0, 0.0], [f64::NAN, 1.0]]).is_err());
        assert_eq!(cad.into_transport().document()["commands"].as_array().unwrap().len(), 0);
    }
}
