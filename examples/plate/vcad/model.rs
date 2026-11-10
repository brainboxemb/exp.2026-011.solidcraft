{
    let length = 100.0;
    let width = 60.0;
    let thickness = 10.0;

    let body = Solid::cube(length, width, thickness)
        .translate(-length / 2.0, -width / 2.0, 0.0);

    let vertical_edges = EdgeQuery::Direction {
        axis: Vec3::new(0.0, 0.0, 1.0),
        tol_deg: 1.0,
    };
    let fillet = [BlendKey {
        t: 0.0,
        section: BlendSection {
            size: 2.0,
            shape: 1.0,
        },
    }];
    let body = body
        .edge_blend(&vertical_edges, &fillet)
        .expect("vertical R2 fillet");

    let cutter = |x: f64, y: f64| {
        Solid::cylinder(4.0, thickness + 2.0, 64)
            .translate(x, y, -1.0)
    };

    let body = body.try_difference(&cutter(-35.0, -15.0)).expect("hole 1");
    let body = body.try_difference(&cutter( 35.0, -15.0)).expect("hole 2");
    let body = body.try_difference(&cutter( 35.0,  15.0)).expect("hole 3");
    body.try_difference(&cutter(-35.0,  15.0)).expect("hole 4")
}
