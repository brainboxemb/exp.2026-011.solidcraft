use std::env;
use std::fs;
use std::path::{Path, PathBuf};

fn wrap_script(source: &Path, output: &Path, object_name: &str) {
    let script = fs::read_to_string(source).expect("read SCRF example script");
    let generated = format!(
        "use scrf::script::IntoScriptModel as _;\n\
         pub fn load() -> Result<scrf::script::ScriptModel, scrf::cad::DesignError> {{\n\
         \x20   let model = {{\n    use scrf::script::prelude::*;\n{script}\n\x20   }};\n\
         \x20   model.into_script_model(\"{object_name}\")\n\
         }}\n"
    );
    fs::write(output, generated).expect("write generated SolidCraftForge test harness");
    println!("cargo:rerun-if-changed={}", source.display());
}

fn main() {
    let manifest = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    let out = PathBuf::from(env::var("OUT_DIR").unwrap());
    let examples = manifest.join("../examples");

    wrap_script(
        &examples.join("csg-cube/solidcraftforge/model.rs"),
        &out.join("csg_cube_script.rs"),
        "CsgCube",
    );
    wrap_script(
        &examples.join("plate/solidcraftforge/model.rs"),
        &out.join("plate_script.rs"),
        "Plate",
    );
}
