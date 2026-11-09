//! Minimal user-facing example of the semantic CAD API.
//!
//! Run from the repository root:
//!   cargo run --manifest-path rust-facade/Cargo.toml --example plate
//!   cargo run --manifest-path rust-facade/Cargo.toml --example plate -- --run
use solidcraft_facade_poc::cad::{Edges, Faces, Hole, Length, LengthParam, Part};
use solidcraft_facade_poc::solidcraft_adapter::SolidCraftAdapter;
use solidcraft_facade_poc::ScriptTransport;
use std::error::Error;
use std::path::PathBuf;
use std::process::Command;

fn main() -> Result<(), Box<dyn Error>> {
    // Domain-level description: no sketches, JSON, transport or feature IDs.
    let holes = [
        Hole::at(-35.0, -15.0, 8.0)?,
        Hole::at(35.0, -15.0, 8.0)?,
        Hole::at(35.0, 15.0, 8.0)?,
        Hole::at(-35.0, 15.0, 8.0)?,
    ];
    let plate = Part::box3d(
        LengthParam::new("plate_length", Length::mm(100.0))?,
        LengthParam::new("plate_width", Length::mm(60.0))?,
        LengthParam::new("thickness", Length::mm(10.0))?,
    )?
        .named("Plate")
        .edges(Edges::OuterVertical).fillet(2.0)?
        .faces(Faces::Top).workplane().circles(&holes)?.cut_through()?;

    // Only the adapter decides how to build that design using SolidCraft.
    let mut cad = SolidCraftAdapter::new(ScriptTransport::default());
    cad.build(&plate)?;

    let output = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../output");
    std::fs::create_dir_all(&output)?;
    let script_path = output.join("cad-plate.json");
    cad.into_transport().write(&script_path)?;
    println!("Wrote {}", script_path.display());

    if std::env::args().any(|arg| arg == "--run") {
        let step = output.join("cad-plate.step");
        let status = Command::new("solidcraft-cli")
            .arg("run")
            .arg(&script_path)
            .arg("--out")
            .arg(&step)
            .status()?;
        if !status.success() {
            return Err(format!("SolidCraft CLI failed: {status}").into());
        }
        println!("Requested STEP export: {}", step.display());
    }
    Ok(())
}
