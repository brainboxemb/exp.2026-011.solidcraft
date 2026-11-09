use vcad_kernel::Solid;

// vcad's public Rust API is the comparison point here.
// The three orthogonal-cylinder transform details still need to be pinned to a
// specific vcad revision before this reference becomes an executable fixture.

fn csg_cube(size: f64) -> Solid {
    let body = Solid::sphere(size / 1.5 / 2.0, 32)
        & Solid::cube(size, size, size);

    // TODO: construct the X/Y/Z cylinders using vcad's current transform API.
    let holes = todo!("three orthogonal cylinders, diameter = size / 1.5");

    body - holes
}

let model = csg_cube(50.0);
