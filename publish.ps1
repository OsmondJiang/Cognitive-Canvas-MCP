# Cognitive Canvas MCP Server - PyPI Publishing Script
# This script builds and publishes your MCP server to PyPI

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("test", "prod")]
    [string]$Target = "test",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$LocalTestOnly = $false
)

Write-Host "Cognitive Canvas MCP Server - Publishing Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (!(Test-Path "pyproject.toml")) {
    Write-Host "[ERROR] pyproject.toml not found. Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Step 1: Check dependencies
Write-Host "`n[STEP 1] Checking dependencies..." -ForegroundColor Yellow

$requiredPackages = @("build", "twine")
foreach ($package in $requiredPackages) {
    $installed = pip list | Select-String $package
    if (!$installed) {
        Write-Host "[INFO] Installing $package..." -ForegroundColor Blue
        pip install $package
    } else {
        Write-Host "[OK] $package is already installed" -ForegroundColor Green
    }
}

# Step 2: Clean previous builds
if (!$SkipBuild) {
    Write-Host "`n[STEP 2] Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path "dist") {
        Remove-Item -Path "dist" -Recurse -Force
        Write-Host "[OK] Cleaned dist directory" -ForegroundColor Green
    }
    if (Test-Path "build") {
        Remove-Item -Path "build" -Recurse -Force
        Write-Host "[OK] Cleaned build directory" -ForegroundColor Green
    }
    if (Test-Path "*.egg-info") {
        Remove-Item -Path "*.egg-info" -Recurse -Force
        Write-Host "[OK] Cleaned egg-info directories" -ForegroundColor Green
    }
}

# Step 3: Build the package
if (!$SkipBuild) {
    Write-Host "`n[STEP 3] Building the package..." -ForegroundColor Yellow
    python -m build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Build failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Package built successfully" -ForegroundColor Green
    
    # Show what was built
    Write-Host "`n[INFO] Built files:" -ForegroundColor Cyan
    Get-ChildItem -Path "dist" | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
}

# Step 4: Local testing (if requested)
if ($LocalTestOnly) {
    Write-Host "`n[STEP 4] Local testing only..." -ForegroundColor Yellow
    
    # Find the wheel file
    $wheelFile = Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1
    if ($wheelFile) {
        Write-Host "[INFO] To test locally, run:" -ForegroundColor Cyan
        Write-Host "  pip install `"$($wheelFile.FullName)`"" -ForegroundColor White
        Write-Host "  cognitive-canvas" -ForegroundColor White
        Write-Host "`n[SUCCESS] Build completed! Ready for manual testing." -ForegroundColor Green
    } else {
        Write-Host "[ERROR] No wheel file found in dist directory" -ForegroundColor Red
    }
    exit 0
}

# Step 5: Upload to PyPI
Write-Host "`n[STEP 5] Publishing to PyPI..." -ForegroundColor Yellow

if ($Target -eq "test") {
    Write-Host "[INFO] Uploading to Test PyPI..." -ForegroundColor Blue
    Write-Host "[NOTE] You'll need to create an account at https://test.pypi.org if you haven't already" -ForegroundColor Cyan
    twine upload --repository testpypi dist/*
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[SUCCESS] Successfully published to Test PyPI!" -ForegroundColor Green
        Write-Host "[LINK] Check your package at: https://test.pypi.org/project/cognitive-canvas-mcp/" -ForegroundColor Cyan
        Write-Host "`n[INFO] To test installation from Test PyPI:" -ForegroundColor Yellow
        Write-Host "  pip install --index-url https://test.pypi.org/simple/ cognitive-canvas-mcp" -ForegroundColor White
    } else {
        Write-Host "[ERROR] Upload to Test PyPI failed!" -ForegroundColor Red
        exit 1
    }
    
} elseif ($Target -eq "prod") {
    Write-Host "[WARNING] You are about to publish to PRODUCTION PyPI!" -ForegroundColor Red
    Write-Host "[NOTE] You'll need to create an account at https://pypi.org if you haven't already" -ForegroundColor Cyan
    $confirm = Read-Host "Are you sure you want to continue? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Host "[INFO] Uploading to Production PyPI..." -ForegroundColor Blue
        twine upload dist/*
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n[SUCCESS] Successfully published to PyPI!" -ForegroundColor Green
            Write-Host "[LINK] Your package is now available at: https://pypi.org/project/cognitive-canvas-mcp/" -ForegroundColor Cyan
            Write-Host "`n[INFO] Users can now install with:" -ForegroundColor Yellow
            Write-Host "  pip install cognitive-canvas-mcp" -ForegroundColor White
        } else {
            Write-Host "[ERROR] Upload to PyPI failed!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[CANCELLED] Publication cancelled by user" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "`n[COMPLETE] All done!" -ForegroundColor Green
