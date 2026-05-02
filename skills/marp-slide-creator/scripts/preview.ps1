#!/usr/bin/env pwsh
# preview.ps1 - Export Marp slides as PNGs for AI review
# Usage: .\scripts\preview.ps1 -SlidePath slides/my-deck/my-deck.md -Theme themes/azure-clarity.css

param(
    [Parameter(Mandatory=$true)]
    [string]$SlidePath,

    [Parameter(Mandatory=$true)]
    [string]$Theme,

    [string]$Scale = "1",

    [switch]$AllowLocalFiles,

    [switch]$Cleanup
)

$ErrorActionPreference = "Stop"

# Resolve paths
$slideDir  = Split-Path $SlidePath -Parent
$slideBase = [System.IO.Path]::GetFileNameWithoutExtension($SlidePath)
$outputBase = Join-Path $slideDir "assets" "preview.png"

# Ensure assets dir exists
$assetsDir = Join-Path $slideDir "assets"
if (-not (Test-Path $assetsDir)) {
    New-Item -ItemType Directory -Path $assetsDir | Out-Null
}

Write-Host "Exporting slides as PNG..." -ForegroundColor Cyan
Write-Host "  Slide : $SlidePath"
Write-Host "  Theme : $Theme"
Write-Host "  Output: $outputBase"
Write-Host ""

# Run Marp CLI
$marpArgs = @(
    "-y", "@marp-team/marp-cli",
    "--no-stdin",
    "--theme", $Theme,
    "--images", "png",
    "--image-scale", $Scale,
    $SlidePath,
    "-o", $outputBase
)
if ($AllowLocalFiles) { $marpArgs += "--allow-local-files" }

npx @marpArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "Marp CLI failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

# List generated files
$pngs = Get-ChildItem -Path $assetsDir -Filter "preview.*.png" | Sort-Object Name
Write-Host ""
Write-Host "Generated $($pngs.Count) slide PNG(s):" -ForegroundColor Green
$pngs | ForEach-Object { Write-Host "  $($_.FullName)" }

Write-Host ""
Write-Host "Review complete." -ForegroundColor Green
if ($Cleanup) {
    Remove-Item "$assetsDir\preview.*.png" -Force
    Write-Host "Preview PNGs cleaned up." -ForegroundColor Yellow
} else {
    Write-Host "Run the following to clean up:" -ForegroundColor Yellow
    Write-Host "  Remove-Item `"$assetsDir\preview.*.png`""
    Write-Host "Or re-run with -Cleanup flag."
}
