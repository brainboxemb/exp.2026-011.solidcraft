# 01 — Windows setup

## Choose the SolidCraft release deliberately

As checked on 9 November 2026:

- Chocolatey Community has `solidcraft` **0.19.0**. It works as an installation option, but is behind the current stable release **0.30.1**.
- The official [SolidCraft releases](https://github.com/tangency-labs/solidcraft/releases/latest) offer Windows x64 MSI and portable ZIP. **Prefer the official current stable MSI or portable ZIP** for this experiment.
- `scraftpybind` was generated against SolidCraft CLI **0.20.0**. We must verify its commands against the chosen version.

If Chocolatey installation is specifically wanted:

```powershell
choco info solidcraft
choco install solidcraft -y
```

The package is third-party community maintained and currently older; do not assume `choco upgrade` provides the latest upstream release.

## Check local executables

```powershell
Get-Command solidcraft -ErrorAction SilentlyContinue
Get-Command solidcraft-cli -ErrorAction SilentlyContinue
```

The GUI and CLI are different executables. A GUI installation does not prove `solidcraft-cli` is on the `PATH`. When required, use the CLI from the downloaded official package and add its containing folder to the current session's `PATH`.

## Python dependency

Use Python 3.11 or later and Git. From this experiment repository:

```powershell
.\scripts\bootstrap.ps1
$env:PYTHONPATH = (Resolve-Path .\ext\scraftcnc).Path
python --version
```

The bootstrap is deliberately limited to cloning and checking out the recorded upstream revision. It will not install global packages or silently reset local edits.

## Offline upstream tests

The upstream tests expect their own repository as the working directory:

```powershell
Push-Location .\ext\scraftcnc
try {
    python -m unittest -v tests.test_scraftpybind
} finally {
    Pop-Location
}
```

Offline transport tests do not require SolidCraft. Some upstream tests also run live when the CLI is available.

## First local model

```powershell
python .\examples\plate.py --target headless --out .\output\plate.step
```

For interactive inspection, open the SolidCraft GUI normally (its control port is enabled by default unless disabled in Preferences). In another PowerShell window set `PYTHONPATH` again, then run:

```powershell
python .\examples\plate.py --target 0 --out .\output\plate-gui.step
```

The `0` asks the upstream binding to discover the GUI's port from `current.port`. The experiment example sets `SOLIDCRAFT_CONTROL_DIR` to `$env:LOCALAPPDATA\SolidCraft\control` on Windows, which is necessary because upstream `scraftpybind` 0.2.0 otherwise looks for Linux's token directory. You may instead explicitly launch the GUI with `--control 8080` and run `--target 8080`.

The GUI token is private. Do not paste its contents in logs or commit it to Git.

Run **our fixture's** offline tests without the external dependency or SolidCraft:

```powershell
python -m unittest discover -s tests -v
```

Record the installed SolidCraft version and result in the experiment evidence. Do not label this workflow qualified before running it locally.
