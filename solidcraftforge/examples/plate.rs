use solidcraftforge::solidcraft_adapter::SolidCraftAdapter;
use solidcraftforge::ScriptTransport;
use std::error::Error;
use std::path::PathBuf;

mod script {
    include!(concat!(env!("OUT_DIR"), "/plate_script.rs"));
}

fn main() -> Result<(), Box<dyn Error>> {
    let model = script::load()?;

    let mut cad = SolidCraftAdapter::new(ScriptTransport::default());
    cad.build(&model)?;

    let output = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../output/examples/plate/solidcraftforge");
    std::fs::create_dir_all(&output)?;
    cad.into_transport().write(output.join("solidcraft.json"))?;
    Ok(())
}
