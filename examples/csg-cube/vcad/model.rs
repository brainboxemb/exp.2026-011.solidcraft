{
    let size = 50.0;
    let segments = 64;
    let half = size / 2.0;

    let sphere = Solid::sphere(size / 1.5, segments);
    let cube = Solid::cube(size, size, size).translate(-half, -half, -half);
    let body = sphere
        .try_intersection(&cube)
        .expect("sphere/cube intersection");

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

    let body = body.try_difference(&hole_x).expect("X cylinder cut");
    let body = body.try_difference(&hole_y).expect("Y cylinder cut");
    body.try_difference(&hole_z).expect("Z cylinder cut")
}
