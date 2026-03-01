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

function Get-PackageJsonObject {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PackageJsonPath
    )

    $raw = Get-Content -Raw -Path $PackageJsonPath
    return ($raw | ConvertFrom-Json)
}

function Test-IsExpoProject {
    param(
        [Parameter(Mandatory = $true)]
        [object]$PackageJson,
        [Parameter(Mandatory = $true)]
        [string]$AppRoot
    )

    $hasExpoDependency = $false
    if ($null -ne $PackageJson.dependencies -and ($PackageJson.dependencies.PSObject.Properties.Name -contains "expo")) {
        $hasExpoDependency = $true
    }
    if ($null -ne $PackageJson.devDependencies -and ($PackageJson.devDependencies.PSObject.Properties.Name -contains "expo")) {
        $hasExpoDependency = $true
    }

    $hasExpoConfigFile = (Test-Path -Path (Join-Path $AppRoot "app.json") -PathType Leaf) -or
        (Test-Path -Path (Join-Path $AppRoot "app.config.js") -PathType Leaf) -or
        (Test-Path -Path (Join-Path $AppRoot "app.config.ts") -PathType Leaf)

    return ($hasExpoDependency -or $hasExpoConfigFile)
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
$packageJson = Get-PackageJsonObject -PackageJsonPath $packageJsonPath
$isExpoProject = Test-IsExpoProject -PackageJson $packageJson -AppRoot $resolvedAppPath

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
        if ($isExpoProject) {
            Invoke-Step -Name "expo doctor" -Command "npx expo-doctor"
        } else {
            Write-Host "Skipping expo doctor: Expo project not detected."
        }
    } else {
        Write-Host "Skipping expo doctor."
    }

    Write-Host "React Native verification complete."
}
finally {
    Pop-Location
}
