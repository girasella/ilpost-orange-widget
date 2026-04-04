param(
    [Parameter(Mandatory = $true)]
    [string]$Token
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Clean previous build artifacts
Write-Host "Cleaning dist/ and build/..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build

# Build source distribution and wheel
Write-Host "Building package..."
python -m build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Upload to PyPI
Write-Host "Uploading to PyPI..."
python -m twine upload dist/* --username __token__ --password $Token
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done."
