{
    let size = 50.0;
    let segments = 64;

    let body = Part::sphere("sphere", size / 1.5, segments)
        & centered_cube("cube", size, size, size);

    // Extend cutters past the target to avoid coincident end faces in the
    // legacy mesh-CSG backend.
    let radius = size / 1.5 / 2.0;
    let cutter_length = size * 1.2;
    let hole_x = centered_cylinder("hole_x", radius, cutter_length, segments)
        .rotate(0.0, 90.0, 0.0);
    let hole_y = centered_cylinder("hole_y", radius, cutter_length, segments)
        .rotate(90.0, 0.0, 0.0);
    let hole_z = centered_cylinder("hole_z", radius, cutter_length, segments);

    // Sequential cuts avoid an unnecessary union of three overlapping tools.
    body - hole_x - hole_y - hole_z
}
