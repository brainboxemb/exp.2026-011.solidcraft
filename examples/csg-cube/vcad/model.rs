{
    let size = 50.0;
    let segments = 64;

    let body = Part::sphere("sphere", size / 1.5, segments)
        & centered_cube("cube", size, size, size);

    let radius = size / 1.5 / 2.0;
    let hole_x = centered_cylinder("hole_x", radius, size, segments)
        .rotate(0.0, 90.0, 0.0);
    let hole_y = centered_cylinder("hole_y", radius, size, segments)
        .rotate(90.0, 0.0, 0.0);
    let hole_z = centered_cylinder("hole_z", radius, size, segments);

    body - (hole_x + hole_y + hole_z)
}
