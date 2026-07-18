# bulk-build.ps1 - Build all marketplace packs
$ErrorActionPreference = "Stop"
$root = "C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content"

# Step 1: Generate textures
Write-Host "=== Generating textures ===" -ForegroundColor Cyan
python "$root\scripts\generate-skin-textures.py"
python "$root\scripts\generate-anime-textures.py"
python "$root\scripts\generate-texture-pack.py"
python "$root\scripts\generate-texture-packs.py"
python "$root\scripts\generate-all-skin-packs.py"

# Step 2: Build .mcpacks
Write-Host "=== Building .mcpacks ===" -ForegroundColor Cyan
python "$root\scripts\build-all.py"

# Step 3: Verify
Write-Host "=== Output ===" -ForegroundColor Cyan
Get-ChildItem "$root\dist\*.mcpack" | ForEach-Object {
    $size = [math]::Round($_.Length / 1KB)
    Write-Host "  $($_.Name) ($size KB)" -ForegroundColor Green
}
Write-Host "Done!" -ForegroundColor Cyan
