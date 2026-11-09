//! Emit an L-bracket SolidCraft command script, optionally run the CLI.
use solidcraft_facade_poc::{Direction, ScriptTransport, SolidCraft};
use std::error::Error;
use std::path::PathBuf;
use std::process::Command;

fn main() -> Result<(), Box<dyn Error>> {
    let mut cad = SolidCraft::new(ScriptTransport::default());
    cad.parameter("width", "60 mm")?
        .sketch("XZ", "Profile")?
        .closed_polygon(&[
            [0.0, 0.0], [40.0, 0.0], [40.0, 6.0],
            [6.0, 6.0], [6.0, 30.0], [0.0, 30.0],
        ])?
        .finish_sketch()?
        .extrude("width", Direction::Negative, "Bracket")?;

    let output = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../output");
    std::fs::create_dir_all(&output)?;
    let script_path = output.join("rust-bracket.json");
    cad.into_transport().write(&script_path)?;
    println!("Wrote {}", script_path.display());

    if std::env::args().any(|arg| arg == "--run") {
        let step_path = output.join("rust-bracket.step");
        let status = Command::new("solidcraft-cli")
            .arg("run")
            .arg(&script_path)
            .arg("--out")
            .arg(&step_path)
            .status()?;
        if !status.success() {
            return Err(format!("solidcraft-cli failed: {status}").into());
        }
        println!("Exported {}", step_path.display());
    }
    Ok(())
}
