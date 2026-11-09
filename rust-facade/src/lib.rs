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
