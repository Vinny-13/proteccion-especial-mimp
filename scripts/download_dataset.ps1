[CmdletBinding()]
param(
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $repo "data/source/proteccion_especial_raw.csv"
}

$url = "https://www.datosabiertos.gob.pe/sites/default/files/1.3.1%20BdD_Proteccion%20Especial_10.csv"
$parent = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $parent | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $OutputPath
Write-Output "Dataset descargado en $OutputPath"
