use solidcraftforge::csg::LengthUnits;
use solidcraftforge::solidcraft_adapter::SolidCraftAdapter;
use solidcraftforge::ScriptTransport;
use std::error::Error;
use std::path::PathBuf;

mod cad_model {
    include!("../../examples/plate/solidcraftforge/model.rs");
}

fn main() -> Result<(), Box<dyn Error>> {
    let model = cad_model::Plate::new(100.mm(), 60.mm(), 10.mm())?;

    let mut cad = SolidCraftAdapter::new(ScriptTransport::default());
    cad.build(model.part())?;

    let output = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../output/examples/plate/solidcraftforge");
    std::fs::create_dir_all(&output)?;
    cad.into_transport().write(output.join("solidcraft.json"))?;
    Ok(())
}
