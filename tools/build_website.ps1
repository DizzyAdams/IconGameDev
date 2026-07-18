param(
  [int]$Batch = 500,
  [string]$OutFile = "website\catalog\pack_index.json",
  [string]$Catalog = "marketplace-content\catalog\PACK_CATALOG.json",
  [switch]$Stats
)
$ErrorActionPreference = 'SilentlyContinue'
Import-Module -Name Microsoft.PowerShell.Utility

$packs = Get-Content -Path $Catalog -Raw | ConvertFrom-Json | Select-Object -ExpandProperty packs
if (-not $packs) { throw "Pack catalog is empty or malformed: $Catalog" }
$count = $packs.Count
$outDir = Split-Path -Path $OutFile -Parent
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
if ($Batch -lt 1 -or $Batch -gt $count) { $Batch = $count }
$slice = $packs | Select-Object -First $Batch
$slice | ConvertTo-Json -Depth 8 | Set-Content -Path $OutFile -Encoding UTF8
$content = Get-Content -Path $OutFile -Raw | ConvertFrom-Json
if ($Stats) {
  Write-Host "Shipped $($content.Count) pack records to $OutFile"
} else {
  Write-Host "Site build updated from $Catalog using $Batch pack(s)."
  Write-Host "Output -> $OutFile"
  Write-Host "Total packs available: $count"
}
