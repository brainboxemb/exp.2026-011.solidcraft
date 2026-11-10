# Execute a SolidCraft command script and open the resulting native design.
# Usage: .\scripts\open-solidcraft-json.ps1 -Script "examples/plate/scpf/solidcraft.json"
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Script,

    [string]$Output,

    [string]$Cli,

    [string]$Gui,

    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

function Resolve-Executable {
    param([string]$Override, [string]$Name, [string]$Installed)
    if ($Override) {
        if (-not (Test-Path -LiteralPath $Override -PathType Leaf)) {
            throw "Executable does not exist: $Override"
        }
        return (Resolve-Path -LiteralPath $Override).Path
    }
    $found = Get-Command $Name -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
    if (Test-Path -LiteralPath $Installed -PathType Leaf) { return $Installed }
    throw "Cannot find $Name. Pass -$(if ($Name -eq 'solidcraft-cli') { 'Cli' } else { 'Gui' }) explicitly."
}

$source = (Resolve-Path -LiteralPath $Script -ErrorAction Stop).Path
if (-not $Output) {
    $Output = [System.IO.Path]::ChangeExtension($source, ".sc")
}
$outputFile = [System.IO.Path]::GetFullPath($ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Output))
if ($outputFile -eq $source) { throw "Output cannot overwrite the input JSON script." }

$target = Split-Path -Parent $outputFile
New-Item -ItemType Directory -Path $target -Force | Out-Null

$cliExe = Resolve-Executable -Override $Cli -Name "solidcraft-cli" -Installed "$env:ProgramFiles\SolidCraft\solidcraft-cli.exe"
Write-Host "Running SolidCraft command script: $source"
& $cliExe run $source --param-check strict --save $outputFile
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $outputFile -PathType Leaf)) {
    throw "SolidCraft command execution failed. No valid design was opened."
}
Write-Host "Saved native SolidCraft design: $outputFile"

if (-not $NoOpen) {
    $guiExe = Resolve-Executable -Override $Gui -Name "solidcraft" -Installed "$env:ProgramFiles\SolidCraft\solidcraft.exe"
    Start-Process -FilePath $guiExe -ArgumentList ('"' + $outputFile + '"')
}
