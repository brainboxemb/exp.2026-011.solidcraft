use solidcraftforge::csg::LengthUnits;
use solidcraftforge::solidcraft_adapter::SolidCraftAdapter;
use solidcraftforge::ScriptTransport;
use std::error::Error;
use std::path::PathBuf;

mod cad_model {
    include!("../../examples/csg-cube/solidcraftforge/model.rs");
}

fn main() -> Result<(), Box<dyn Error>> {
    let model = cad_model::CsgCube::new(50.mm());

    let mut cad = SolidCraftAdapter::new(ScriptTransport::default());
    cad.build_csg(model.shape(), "CsgCube")?;

    let output = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../output/examples/csg-cube/solidcraftforge");
    std::fs::create_dir_all(&output)?;
    cad.into_transport().write(output.join("solidcraft.json"))?;
    Ok(())
}
