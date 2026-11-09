{
    let size = 50.0;
    let segments = 64;

    let body = Part::sphere("sphere", size / 1.5, segments)
        & centered_cube("cube", size, size, size);

    // Extend the cutters past the body. The resulting geometry is identical,
    // but avoids coincident cutter end faces in vcad's mesh-CSG backend.
    let radius = size / 1.5 / 2.0;
    let cutter_length = size * 1.2;
    let hole_x = centered_cylinder("hole_x", radius, cutter_length, segments)
        .rotate(0.0, 90.0, 0.0);
    let hole_y = centered_cylinder("hole_y", radius, cutter_length, segments)
        .rotate(90.0, 0.0, 0.0);
    let hole_z = centered_cylinder("hole_z", radius, cutter_length, segments);

    body - (hole_x + hole_y + hole_z)
}
