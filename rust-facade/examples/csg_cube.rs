use solidcraft_facade_poc::solidcraft_adapter::SolidCraftAdapter;
use solidcraft_facade_poc::ScriptTransport;
use std::error::Error;
use std::path::PathBuf;

mod cad_model {
    use solidcraft_facade_poc::csg::{Cube, Cylinder, LengthUnits, Shape, Sphere, X, Y, Z};
    use solidcraft_facade_poc::{part, root};

    include!("../../examples/csg-cube/ours/model.rs");
}

fn main() -> Result<(), Box<dyn Error>> {
    let model = cad_model::model();
    let mut cad = SolidCraftAdapter::new(ScriptTransport::default());
    cad.build_csg(&model, "CsgCube")?;

    let output = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../output/examples/csg-cube/ours");
    std::fs::create_dir_all(&output)?;
    cad.into_transport().write(output.join("solidcraft.json"))?;
    Ok(())
}
