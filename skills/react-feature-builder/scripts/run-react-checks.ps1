param(
    [Parameter(Mandatory = $true)]
    [string]$AppPath,
    [string]$TestPattern = "",
    [switch]$SkipTests,
    [switch]$SkipBuild,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    if ($WhatIf) {
        Write-Host "[WhatIf] ${Name}: $Command"
        return
    }

    Write-Host "Running ${Name}: $Command"
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path -Path $AppPath -PathType Container)) {
    throw "AppPath does not exist or is not a directory: $AppPath"
}

$resolvedAppPath = (Resolve-Path $AppPath).Path
Push-Location $resolvedAppPath

try {
    if (-not $SkipTests) {
        if ([string]::IsNullOrWhiteSpace($TestPattern)) {
            Invoke-Step -Name "tests" -Command "npm test -- --watchAll=false"
        } else {
            Invoke-Step -Name "targeted tests" -Command "npm test -- --watchAll=false $TestPattern"
        }
    } else {
        Write-Host "Skipping tests."
    }

    if (-not $SkipBuild) {
        Invoke-Step -Name "build" -Command "npm run build"
    } else {
        Write-Host "Skipping build."
    }

    Write-Host "Verification complete."
} finally {
    Pop-Location
}
