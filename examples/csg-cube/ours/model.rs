part!(CsgCube(size: Length) {
    let body = Sphere::new(size / 1.5) & Cube::new(size);
    let holes = Cylinder::new(size, size / 1.5).orient([X, Y, Z]);

    body - holes
});

root!(CsgCube(50.mm()));
