# Qualify the semantic Rust CAD API against *your installed* SolidCraft on Windows.
# No downloads or changes to GUI state; all generated evidence is gitignored.
[CmdletBinding()]
param(
    [string]$CliPath = '',
    [switch]$Snapshot,
    [switch]$SkipBuild
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root 'output'
$scriptFile = Join-Path $out 'cad-plate.json'
$nativeFile = Join-Path $out 'cad-plate.sc'
$stepFile = Join-Path $out 'cad-plate.step'
$evalFile = Join-Path $out 'cad-plate-eval.json'
$resultsFile = Join-Path $out 'cad-plate-results.json'
$nativeEvalFile = Join-Path $out 'cad-plate-native-eval.json'
$pngFile = Join-Path $out 'cad-plate.png'

if (-not $CliPath) {
    $found = Get-Command solidcraft-cli -ErrorAction SilentlyContinue
    if ($found) { $CliPath = $found.Source }
    else {
        $fallback = Join-Path $env:ProgramFiles 'SolidCraft\solidcraft-cli.exe'
        if (Test-Path -LiteralPath $fallback) { $CliPath = $fallback }
    }
}
if (-not $CliPath -or -not (Test-Path -LiteralPath $CliPath)) {
    throw 'SolidCraft CLI not found. Install official SolidCraft or pass -CliPath "C:\Program Files\SolidCraft\solidcraft-cli.exe".'
}

function Invoke-Checked([string]$Label, [scriptblock]$Action) {
    Write-Host "-- $Label"
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE" }
}

New-Item -ItemType Directory -Path $out -Force | Out-Null
Write-Host "SolidCraft CLI: $CliPath"
Invoke-Checked 'SolidCraft version' { & $CliPath --version }
if (-not $SkipBuild) {
    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        throw 'Rust cargo is not on PATH. Install Rust or use -SkipBuild with an existing output/cad-plate.json.'
    }
    Invoke-Checked 'Rust domain / adapter tests' {
        & cargo test --manifest-path (Join-Path $root 'rust-facade\Cargo.toml') --all-targets
    }
    Invoke-Checked 'Generate semantic CAD script' {
        & cargo run --manifest-path (Join-Path $root 'rust-facade\Cargo.toml') --bin cad_plate
    }
}
if (-not (Test-Path -LiteralPath $scriptFile)) { throw "Missing generated script: $scriptFile" }
Invoke-Checked 'Evaluate generated model' {
    & $CliPath eval $scriptFile --json-out $evalFile
}
Invoke-Checked 'Export STEP, native design and detailed results' {
    & $CliPath run $scriptFile --param-check strict --results --json-out $resultsFile --save $nativeFile --out $stepFile
}
Invoke-Checked 'Re-evaluate saved native design' {
    & $CliPath eval $nativeFile --json-out $nativeEvalFile
}
if ($Snapshot) {
    Invoke-Checked 'Generate snapshot' {
        & $CliPath snapshot $nativeFile --out $pngFile --no-grid --no-axes
    }
}
foreach ($file in @($evalFile, $resultsFile, $nativeFile, $nativeEvalFile, $stepFile)) {
    if (-not (Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).Length -eq 0) {
        throw "Expected non-empty result missing: $file"
    }
}
$null = Get-Content -LiteralPath $evalFile -Raw | ConvertFrom-Json
$null = Get-Content -LiteralPath $resultsFile -Raw | ConvertFrom-Json
$null = Get-Content -LiteralPath $nativeEvalFile -Raw | ConvertFrom-Json
Write-Host "SolidCraft commands executed; output saved under $out"
Write-Host 'Inspect STEP and native .sc in SolidCraft for actual geometry, hole placement and parametric history.'
