use std::env;
use std::fs;
use std::path::{Path, PathBuf};

fn wrap_script(source: &Path, output: &Path, return_type: &str) {
    let script = fs::read_to_string(source).expect("read SolidCraftForge example script");
    let generated = format!(
        "pub fn load() -> Result<{return_type}, solidcraftforge::cad::DesignError> {{\n    Ok({{\n{script}\n    }})\n}}\n"
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
        "solidcraftforge::csg::Shape",
    );
    wrap_script(
        &examples.join("plate/solidcraftforge/model.rs"),
        &out.join("plate_script.rs"),
        "solidcraftforge::cad::Part",
    );
}
