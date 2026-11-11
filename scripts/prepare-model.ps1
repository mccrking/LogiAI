$ErrorActionPreference = 'Stop'
$logiaiRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $logiaiRoot
try {
    New-Item -ItemType Directory -Force -Path 'data', 'models' | Out-Null
    docker build --target trainer -t logiai-trainer:1.0 .
    if ($LASTEXITCODE -ne 0) { throw 'Construction du conteneur de préparation impossible.' }
    docker run --rm --mount "type=bind,source=$logiaiRoot/data,target=/app/data" --mount "type=bind,source=$logiaiRoot/models,target=/app/models" logiai-trainer:1.0
    if ($LASTEXITCODE -ne 0) { throw 'Préparation du modèle impossible.' }
} finally {
    Pop-Location
}
