param(
    [Parameter(Mandatory = $true)]
    [string]$AppPath,
    [switch]$SkipTests,
    [switch]$SkipLint,
    [switch]$SkipTypecheck,
    [switch]$SkipExpoDoctor,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-ScriptsFromPackageJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PackageJsonPath
    )

    $raw = Get-Content -Raw -Path $PackageJsonPath
    $pkg = $raw | ConvertFrom-Json
    if ($null -eq $pkg.scripts) {
        return @{}
    }
    return $pkg.scripts.PSObject.Properties.Name
}

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
        throw "${Name} failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path -Path $AppPath -PathType Container)) {
    throw "AppPath does not exist or is not a directory: $AppPath"
}

$resolvedAppPath = (Resolve-Path $AppPath).Path
$packageJsonPath = Join-Path $resolvedAppPath "package.json"
if (-not (Test-Path -Path $packageJsonPath -PathType Leaf)) {
    throw "No package.json found at: $packageJsonPath"
}

$scriptNames = Get-ScriptsFromPackageJson -PackageJsonPath $packageJsonPath

Push-Location $resolvedAppPath
try {
    if (-not $SkipTests) {
        if ($scriptNames -contains "test") {
            Invoke-Step -Name "tests" -Command "npm test -- --watchAll=false"
        } else {
            Write-Host "Skipping tests: no test script in package.json."
        }
    } else {
        Write-Host "Skipping tests."
    }

    if (-not $SkipLint) {
        if ($scriptNames -contains "lint") {
            Invoke-Step -Name "lint" -Command "npm run lint"
        } else {
            Write-Host "Skipping lint: no lint script in package.json."
        }
    } else {
        Write-Host "Skipping lint."
    }

    if (-not $SkipTypecheck) {
        if ($scriptNames -contains "typecheck") {
            Invoke-Step -Name "typecheck" -Command "npm run typecheck"
        } else {
            Write-Host "Skipping typecheck: no typecheck script in package.json."
        }
    } else {
        Write-Host "Skipping typecheck."
    }

    if (-not $SkipExpoDoctor) {
        Invoke-Step -Name "expo doctor" -Command "npx expo-doctor"
    } else {
        Write-Host "Skipping expo doctor."
    }

    Write-Host "React Native verification complete."
}
finally {
    Pop-Location
}
