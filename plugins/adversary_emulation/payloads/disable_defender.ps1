$ErrorActionPreference = "Stop"

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
    Write-Error "This script requires administrator privileges. Please run as Administrator."
    exit 1
}
$InstallPath = "C:\Users\Public\defendnot"

switch -Wildcard ($env:PROCESSOR_ARCHITECTURE) {
    "AMD64"   { $arch = "x64" }
    "x86"     { $arch = "x86" }
    "ARM64"   { $arch = "ARM64" }
    default   {
        Write-Error "Unknown architecture: $($env:PROCESSOR_ARCHITECTURE)"
        exit 1
    }
}

$repo = "es3n1n/defendnot"
$apiReleaseUrl = "https://api.github.com/repos/$repo/releases/latest"
$headers = @{ 'User-Agent'="defendnot-install/1.0" }

try {
    $release = Invoke-RestMethod -Uri $apiReleaseUrl -Headers $headers
} catch {
    Write-Error "Failed to get latest release info: $_"
    exit 2
}

$zipAsset = $release.assets | Where-Object { $_.name -ieq "$arch.zip" }
if (-not $zipAsset) {
    Write-Error "Release does not contain asset for $arch"
    exit 3
}

$zipUrl = $zipAsset.browser_download_url
$zipPath = Join-Path $env:TEMP "defendnot-$arch.zip"

Write-Host "Downloading $($zipAsset.name)..."
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath

if (Test-Path $InstallPath) {
    Write-Host "Removing previous installation..."
    Remove-Item $InstallPath -Force -Recurse -ErrorAction SilentlyContinue
}

New-Item -Type Directory -Path $InstallPath -ErrorAction SilentlyContinue | Out-Null

Write-Host "Extracting to $InstallPath..."
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $InstallPath)
Remove-Item $zipPath

Write-Host "Installed to $InstallPath"
Write-Host "Starting..."
Write-Host "Args: $args"
& "$InstallPath\defendnot-loader.exe" @args
