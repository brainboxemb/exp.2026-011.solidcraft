{
    let size = 50.0;
    let half = size / 2.0;

    let body = Solid::sphere(size / 1.5, 64)
        & Solid::cube(size, size, size).translate(-half, -half, -half);

    let radius = size / 1.5 / 2.0;
    let hole_x = Solid::cylinder(radius, size, 64)
        .translate(0.0, 0.0, -half)
        .rotate(0.0, 90.0, 0.0);
    let hole_y = Solid::cylinder(radius, size, 64)
        .translate(0.0, 0.0, -half)
        .rotate(-90.0, 0.0, 0.0);
    let hole_z = Solid::cylinder(radius, size, 64)
        .translate(0.0, 0.0, -half);

    body - (hole_x + hole_y + hole_z)
}
