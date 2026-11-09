part!(Plate(length: Length, width: Length, thickness: Length) -> Part {
    let holes = [
        Hole::with_units((-35).mm(), (-15).mm(), 8.mm())?,
        Hole::with_units( 35.mm(), (-15).mm(), 8.mm())?,
        Hole::with_units( 35.mm(),  15.mm(), 8.mm())?,
        Hole::with_units((-35).mm(),  15.mm(), 8.mm())?,
    ];

    Part::box3d(length, width, thickness)?
        .named("Plate")
        .edges(Edges::OuterVertical)
        .fillet(2.mm())?
        .faces(Faces::Top)
        .workplane()
        .circles(&holes)?
        .cut_through()
});

build!(Plate(100.mm(), 60.mm(), 10.mm()));
