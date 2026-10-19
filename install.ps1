# Install the rawpy-based ARW loader for GIMP 3.2 on Windows.
# Run: powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = 'Stop'

$Src = $PSScriptRoot
$HomeDir = Join-Path $env:LOCALAPPDATA 'gimp-arw'
$PluginDir = Join-Path $env:APPDATA 'GIMP\3.2\plug-ins\file-arw-rawpy'
$VenvPy = Join-Path $HomeDir 'venv\Scripts\python.exe'

New-Item -ItemType Directory -Force $HomeDir, $PluginDir | Out-Null

if (-not (Test-Path $VenvPy)) {
    # python.org launcher first, then whatever python is on PATH
    $candidates = @('py -3.14', 'py -3', 'python')
    $exe = $null
    foreach ($c in $candidates) {
        $parts = $c -split ' '
        $exe = $parts[0]
        $pyArgs = @($parts | Select-Object -Skip 1)
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { $exe = $null; continue }
        & $exe @pyArgs -c 'import sys; assert sys.version_info >= (3, 9)' 2>$null
        if ($LASTEXITCODE -eq 0) { break }
        $exe = $null
    }
    if (-not $exe) { throw 'Python 3.9+ not found; install it from https://www.python.org/downloads/' }
    & $exe @pyArgs -m venv (Join-Path $HomeDir 'venv')
    if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
}
& $VenvPy -m pip install -q --upgrade rawpy numpy tifffile
if ($LASTEXITCODE -ne 0) { throw 'pip install failed' }

Copy-Item (Join-Path $Src 'arw2tiff.py') $HomeDir -Force
Copy-Item (Join-Path $Src 'file-arw-rawpy.py') $PluginDir -Force
Get-ChildItem (Join-Path $HomeDir 'arw2tiff.py'), $PluginDir -Recurse -File | Unblock-File

# command-line helper: arw2tiff photo.ARW -> photo.tif
$BinDir = Join-Path $HomeDir 'bin'
New-Item -ItemType Directory -Force $BinDir | Out-Null
Set-Content (Join-Path $BinDir 'arw2tiff.cmd') -Encoding ascii -Value (
    '@"%LOCALAPPDATA%\gimp-arw\venv\Scripts\python.exe" "%LOCALAPPDATA%\gimp-arw\arw2tiff.py" %*')

Write-Host 'Installed. Restart GIMP, then File > Open any .ARW.'
Write-Host "CLI: $BinDir\arw2tiff.cmd (add $BinDir to PATH if needed)"
