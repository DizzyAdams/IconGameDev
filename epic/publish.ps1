# =============================================================================
# Epic/Fortnite Creative — Publish Script (PowerShell / Windows)
# =============================================================================
# Usage:
#   .\epic\publish.ps1                  # generate submission package
#   .\epic\publish.ps1 -DryRun          # preview without creating ZIP
#   .\epic\publish.ps1 -ExportUEFN      # generate ready-to-import UEFN files
# =============================================================================

param(
    [switch]$DryRun,
    [switch]$ExportUEFN
)

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$EPIC_DIR = Join-Path $ROOT_DIR "epic"
$MAPS_DIR = Join-Path $EPIC_DIR "maps"
$SUBMISSION_DIR = Join-Path $EPIC_DIR "submission_pending"
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmm"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Epic / Fortnite Creative — Publish Pipeline" -ForegroundColor Cyan
Write-Host "  Timestamp: $TIMESTAMP" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# ── Step 1: Pre-flight checks ────────────────────────────────────────────
Write-Host "`n── Step 1/4: Pre-flight checks ──" -ForegroundColor Yellow
$maps = Get-ChildItem "$MAPS_DIR\*.json"
if ($maps.Count -eq 0) {
    Write-Host "  ERROR: No map templates found in $MAPS_DIR" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Found $($maps.Count) map templates" -ForegroundColor Green

# ── Step 2: Validate ─────────────────────────────────────────────────────
Write-Host "`n── Step 2/4: Validating templates ──" -ForegroundColor Yellow
$valid = 0
$invalid = 0
foreach ($map in $maps) {
    try {
        $null = Get-Content $map.FullName -Raw | ConvertFrom-Json
        $valid++
    } catch {
        Write-Host "  ✗ $($map.Name) — INVALID" -ForegroundColor Red
        $invalid++
    }
}
if ($invalid -gt 0) { Write-Host "  ERROR: $invalid invalid templates" -ForegroundColor Red; exit 2 }
Write-Host "  ✓ $valid templates valid" -ForegroundColor Green

# ── Step 3: Manifest ─────────────────────────────────────────────────────
Write-Host "`n── Step 3/4: Generating submission manifest ──" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $SUBMISSION_DIR -Force | Out-Null

$manifestPath = Join-Path $SUBMISSION_DIR "submission_manifest_$TIMESTAMP.json"
$manifest = [PSCustomObject]@{
    submission_id       = "epic-$TIMESTAMP"
    timestamp           = $TIMESTAMP
    project             = "IconGameDev"
    platform            = "fortnite_creative"
    engine              = "uefn"
    total_maps          = $maps.Count
    creator             = "IconGameDev"
    default_language    = "pt-BR"
    languages_supported = @("pt-BR", "en-US")
    rating              = "E10+ (Everyone 10+)"
    maps                = @()
}

foreach ($map in $maps) {
    $data = Get-Content $map.FullName -Raw | ConvertFrom-Json
    $manifest.maps += [PSCustomObject]@{
        file         = $map.Name
        template     = $data.template
        display_name = $data.display_name
        game_mode    = $data.game_settings.game_mode
        max_players  = $data.game_settings.max_players
        tags         = $data.tags
    }
}

$manifest | ConvertTo-Json -Depth 5 | Set-Content $manifestPath
Write-Host "  ✓ Manifest: $manifestPath" -ForegroundColor Green

# ── Step 4: Submission package ───────────────────────────────────────────
if (-not $DryRun) {
    Write-Host "`n── Step 4/4: Creating submission package ──" -ForegroundColor Yellow
    
    $pkgDir = Join-Path $SUBMISSION_DIR "pkg_$TIMESTAMP"
    New-Item -ItemType Directory -Path $pkgDir -Force | Out-Null

    # Copy all maps + manifest + guide
    Get-ChildItem "$MAPS_DIR\*.json" | Copy-Item -Destination $pkgDir
    Copy-Item $manifestPath -Destination $pkgDir
    $guidePath = Join-Path $EPIC_DIR "SUBMISSION_GUIDE.md"
    if (Test-Path $guidePath) { Copy-Item $guidePath -Destination $pkgDir }

    # Create ZIP
    $zipName = "fortnite_submission_$TIMESTAMP.zip"
    $zipPath = Join-Path $SUBMISSION_DIR $zipName
    Compress-Archive -Path "$pkgDir\*" -DestinationPath $zipPath -Force
    $zipInfo = Get-Item $zipPath

    Write-Host "  ✓ Package: $zipPath" -ForegroundColor Green
    Write-Host "  ✓ Size: $([math]::Round($zipInfo.Length / 1KB, 1)) KB"

    # ── Optional: UEFN export ──
    if ($ExportUEFN) {
        $uefnDir = Join-Path $SUBMISSION_DIR "uefn_export_$TIMESTAMP"
        New-Item -ItemType Directory -Path $uefnDir -Force | Out-Null
        foreach ($map in $maps) {
            $data = Get-Content $map.FullName -Raw | ConvertFrom-Json
            $uefn = [PSCustomObject]@{
                ProjectName  = $data.template
                DisplayName  = $data.display_name
                Description  = $data.description
                Tags         = $data.tags
                MapSettings  = [PSCustomObject]@{
                    IslandType     = $data.island.type
                    GameMode       = $data.game_settings.game_mode
                    MaxPlayers     = $data.game_settings.max_players
                    AllowBuilding  = ($data.game_settings.build_permission -ne "none")
                    StormEnabled   = $data.island.allow_storm
                }
            }
            $uefnPath = Join-Path $uefnDir "$($map.BaseName)_uefn_import.json"
            $uefn | ConvertTo-Json -Depth 5 | Set-Content $uefnPath
        }
        Write-Host "  ✓ UEFN export: $uefnDir" -ForegroundColor Green
    }

    # Cleanup
    Remove-Item -Recurse -Force $pkgDir

    Write-Host "`n==============================================" -ForegroundColor Cyan
    Write-Host "  ✓ PUBLISH READY" -ForegroundColor Green
    Write-Host "  Package: $zipName" -ForegroundColor White
    Write-Host "  Upload to: https://create.fortnite.com/publish" -ForegroundColor White
    Write-Host "==============================================" -ForegroundColor Cyan
} else {
    Write-Host "`n── Dry-run mode — no files created ──" -ForegroundColor Yellow
    Write-Host "  Would create submission package with $($maps.Count) maps."
}
