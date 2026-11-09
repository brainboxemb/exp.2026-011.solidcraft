{
    let size = 50.0;
    let segments = 64;
    let half = size / 2.0;

    let body = Solid::sphere(size / 1.5, segments)
        & Solid::cube(size, size, size).translate(-half, -half, -half);

    let radius = size / 1.5 / 2.0;
    let cutter_length = size * 1.2;
    let cutter_half = cutter_length / 2.0;

    let hole_x = Solid::cylinder(radius, cutter_length, segments)
        .translate(0.0, 0.0, -cutter_half)
        .rotate(0.0, 90.0, 0.0);
    let hole_y = Solid::cylinder(radius, cutter_length, segments)
        .translate(0.0, 0.0, -cutter_half)
        .rotate(90.0, 0.0, 0.0);
    let hole_z = Solid::cylinder(radius, cutter_length, segments)
        .translate(0.0, 0.0, -cutter_half);

    body - hole_x - hole_y - hole_z
}
