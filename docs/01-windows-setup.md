# 01 — Windows setup

Use the official current SolidCraft release. Initial target: **0.30.1**.

```powershell
Get-Command solidcraft-cli -ErrorAction SilentlyContinue
& "C:\Program Files\SolidCraft\solidcraft-cli.exe" --version
```

## Fast runtime test

```powershell
.\scripts\qualify-solidcraft.ps1 -SkipBuild -Snapshot
```

This uses the committed CAD fixture, so Rust is not required.

To compile the Rust API first:

```powershell
cargo test --manifest-path solidcraftforge/Cargo.toml --all-targets
.\scripts\qualify-solidcraft.ps1 -Snapshot
```

Results are written under ignored `output/`. Inspect STEP and the native `.sc` design before calling the CAD model qualified.
