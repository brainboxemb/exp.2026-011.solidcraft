# Fetch pinned upstream scraftpybind; do not vendor third-party code here.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$externalRoot = Join-Path $repoRoot 'ext'
$checkout = Join-Path $externalRoot 'scraftcnc'
$upstream = 'https://github.com/waynegramlich/scraftcnc.git'
$revision = 'eef7b7c96e2c829f82271827c7c16fb7ad95668b'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required on PATH.'
}
New-Item -ItemType Directory -Path $externalRoot -Force | Out-Null

if (-not (Test-Path $checkout)) {
    & git clone $upstream $checkout
    if ($LASTEXITCODE -ne 0) { throw 'Failed to clone scraftcnc.' }
}
elseif (-not (Test-Path (Join-Path $checkout '.git'))) {
    throw "Found $checkout but it is not a Git checkout."
}

$actual = (& git -C $checkout remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $actual -notin @($upstream, 'git@github.com:waynegramlich/scraftcnc.git')) {
    throw "Unexpected upstream origin: $actual"
}
$dirty = & git -C $checkout status --porcelain
if ($LASTEXITCODE -ne 0) { throw 'Failed to inspect the upstream checkout.' }
if ($dirty) { throw 'Upstream checkout has local changes; refusing to replace them.' }

# Fetch may check for newer upstream refs, but the checkout stays on the exact
# pinned revision. Do not follow a floating branch.
& git -C $checkout fetch origin
if ($LASTEXITCODE -ne 0) { throw 'Failed to fetch upstream.' }
& git -C $checkout checkout --detach $revision
if ($LASTEXITCODE -ne 0) { throw "Unable to check out pinned revision $revision" }

Write-Host "scraftcnc pinned at $revision"
Write-Host 'In this session:'
Write-Host '  $env:PYTHONPATH = (Resolve-Path .\ext\scraftcnc).Path'
