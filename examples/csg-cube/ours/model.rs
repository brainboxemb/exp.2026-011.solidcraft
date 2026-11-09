{
    let size = parameter("size", 50.mm())?;

    let body = Sphere::new(size.clone() / 1.5) & Cube::new(size.clone());
    let holes = Cylinder::new(size.clone(), size / 1.5).orient([X, Y, Z]);

    Ok(body - holes)
}
