# Windows setup — Python SCPF

Use the official SolidCraft CLI and Python 3.12 (the version used in CI).
Open PowerShell in the repository root.

```powershell
# Check installed executables
python --version
Get-Command solidcraft-cli -ErrorAction SilentlyContinue

# Install SCPF
python -m pip install -e ./scpf

# Run its regression tests
python -m unittest discover -s scpf/tests -v

# Translate a Python example into real SolidCraft commands
python -m scpf examples/sample-plate/scpf/model.py --out output/sample-plate.json

# Review the exact command document
code output/sample-plate.json

# Execute it in native SolidCraft and save the editable design
solidcraft-cli run output/sample-plate.json --param-check strict --results --save output/sample-plate.sc --out output/sample-plate.step

# Validate the saved design
solidcraft-cli eval output/sample-plate.sc --json-out output/sample-plate-measurements.json
```

Alternatively, with a new empty SolidCraft document and external Assistant
control enabled:

```powershell
python -m scpf examples/sample-plate/scpf/model.py --connect
```

Commands using `--out` generate files and do not modify the GUI;
`--connect` sends commands to the open design. Outputs live in ignored
`output/`.
