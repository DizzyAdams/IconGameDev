# =============================================================================
# Epic/Fortnite Creative — Build Script (PowerShell / Windows)
# =============================================================================
# Usage:
#   .\epic\build.ps1           # validate all templates
#   .\epic\build.ps1 -Full     # validate + generate deployment artifacts
#   .\epic\build.ps1 -Publish  # do everything + package for submission
# =============================================================================

param(
    [switch]$Full,
    [switch]$Publish
)

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$EPIC_DIR = Join-Path $ROOT_DIR "epic"
$MAPS_DIR = Join-Path $EPIC_DIR "maps"
$BUILD_DIR = Join-Path $EPIC_DIR "build"
$SUBMISSION_DIR = Join-Path $EPIC_DIR "submission_pending"
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmm"

New-Item -ItemType Directory -Path $BUILD_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $SUBMISSION_DIR -Force | Out-Null

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Epic / Fortnite Creative — Build Pipeline" -ForegroundColor Cyan
Write-Host "  Timestamp: $TIMESTAMP" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# ── Step 1: Validate JSON ─────────────────────────────────────────────────
Write-Host "`n── Step 1/4: Validating JSON templates ──" -ForegroundColor Yellow
$validationFailed = $false
Get-ChildItem "$MAPS_DIR\*.json" | ForEach-Object {
    $name = $_.Name
    try {
        $null = Get-Content $_.FullName -Raw | ConvertFrom-Json
        Write-Host "  ✓ $name" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $name — invalid JSON" -ForegroundColor Red
        $validationFailed = $true
    }
}
if ($validationFailed) { Write-Host "ERROR: Invalid JSON detected." -ForegroundColor Red; exit 2 }

# ── Step 2: Check required fields ─────────────────────────────────────────
Write-Host "`n── Step 2/4: Checking required fields ──" -ForegroundColor Yellow
Get-ChildItem "$MAPS_DIR\*.json" | ForEach-Object {
    $name = $_.Name
    $data = Get-Content $_.FullName -Raw | ConvertFrom-Json
    $missing = @()
    @('template', 'version', 'display_name', 'description', 'game_settings') | ForEach-Object {
        if (-not $data.$_) { $missing += $_ }
    }
    if ($data.game_settings -and -not $data.game_settings.max_players) {
        $missing += "game_settings.max_players"
    }
    if ($missing.Count -gt 0) {
        Write-Host "  ✗ $name — missing: $($missing -join ', ')" -ForegroundColor Red
        $validationFailed = $true
    } else {
        Write-Host "  ✓ $name" -ForegroundColor Green
    }
}
if ($validationFailed) { exit 2 }

# ── Step 3: Build index ──────────────────────────────────────────────────
Write-Host "`n── Step 3/4: Generating template index ──" -ForegroundColor Yellow
$index = @()
Get-ChildItem "$MAPS_DIR\*.json" | ForEach-Object {
    $data = Get-Content $_.FullName -Raw | ConvertFrom-Json
    $index += [PSCustomObject]@{
        file         = $_.Name
        template     = $data.template
        display_name = $data.display_name
        tags         = $data.tags -join ', '
        max_players  = $data.game_settings.max_players
    }
}
$indexPath = Join-Path $BUILD_DIR "template_index.json"
$index | ConvertTo-Json | Set-Content $indexPath
Write-Host "  ✓ Generated $indexPath" -ForegroundColor Green

# ── Step 4: Summary ──────────────────────────────────────────────────────
Write-Host "`n── Step 4/4: Generating summary ──" -ForegroundColor Yellow
$total = (Get-ChildItem "$MAPS_DIR\*.json").Count
$summaryPath = Join-Path $BUILD_DIR "build_summary.txt"
@"
Epic/Fortnite Creative Build Summary
===================================
Timestamp: $TIMESTAMP
Templates validated: $total

Maps:
"@ | Set-Content $summaryPath

Get-ChildItem "$MAPS_DIR\*.json" | ForEach-Object {
    $data = Get-Content $_.FullName -Raw | ConvertFrom-Json
    "  - $($data.display_name) ($($data.template))" | Add-Content $summaryPath
}
"`nBuild: SUCCESS" | Add-Content $summaryPath
Write-Host "  ✓ Generated $summaryPath" -ForegroundColor Green

# ── Full mode ────────────────────────────────────────────────────────────
if ($Full -or $Publish) {
    Write-Host "`n── Full mode: Generating deployment artifacts ──" -ForegroundColor Yellow
    $pkgDir = Join-Path $BUILD_DIR "pkg_$TIMESTAMP"
    New-Item -ItemType Directory -Path $pkgDir -Force | Out-Null

    Get-ChildItem "$MAPS_DIR\*.json" | ForEach-Object {
        $name = $_.BaseName
        $mapDir = Join-Path $pkgDir $name
        New-Item -ItemType Directory -Path $mapDir -Force | Out-Null
        Copy-Item $_.FullName -Destination $mapDir

        $data = Get-Content $_.FullName -Raw | ConvertFrom-Json
        $manifest = [PSCustomObject]@{
            project_name  = $data.display_name
            template      = $data.template
            uefn_version  = ">=31.0"
            island_type   = $data.island.type
            max_players   = $data.game_settings.max_players
            game_mode     = $data.game_settings.game_mode
            generated     = $TIMESTAMP
            generator     = "IconGameDev Epic Pipeline"
        }
        $manifest | ConvertTo-Json | Set-Content (Join-Path $mapDir "uefn_project.json")
        Write-Host "  ✓ $name packaged" -ForegroundColor Green
    }

    if ($Publish) {
        $zipName = "epic_submission_$TIMESTAMP.zip"
        $zipPath = Join-Path $SUBMISSION_DIR $zipName
        Compress-Archive -Path "$pkgDir\*" -DestinationPath $zipPath
        Write-Host "`n  ✓ Submission package: $zipPath" -ForegroundColor Green
        Remove-Item -Recurse -Force $pkgDir
    }
}

Write-Host "`n==============================================" -ForegroundColor Cyan
Write-Host "  BUILD COMPLETE — all templates validated." -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
