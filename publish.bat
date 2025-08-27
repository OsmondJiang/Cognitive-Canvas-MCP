@echo off
echo.
echo Cognitive Canvas MCP Server - Quick Publish
echo ===========================================
echo.

REM Check if pyproject.toml exists
if not exist "pyproject.toml" (
    echo [ERROR] pyproject.toml not found. Please run this from the project root directory.
    pause
    exit /b 1
)

echo [STEP 1] Installing build dependencies...
pip install build twine

echo.
echo [STEP 2] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

echo.
echo [STEP 3] Building package...
python -m build

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Package built successfully!
echo.
echo [MENU] Choose publishing target:
echo   1) Test PyPI (recommended for first time)
echo   2) Production PyPI
echo   3) Local test only
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo [INFO] Publishing to Test PyPI...
    echo [NOTE] You'll need an account at https://test.pypi.org
    twine upload --repository testpypi dist/*
    echo.
    echo [LINK] Check your package at: https://test.pypi.org/project/cognitive-canvas-mcp/
    echo [INFO] To test: pip install --index-url https://test.pypi.org/simple/ cognitive-canvas-mcp
) else if "%choice%"=="2" (
    echo.
    echo [WARNING] Publishing to PRODUCTION PyPI!
    set /p confirm="Are you sure? (y/N): "
    if /i "%confirm%"=="y" (
        echo [INFO] Publishing to Production PyPI...
        twine upload dist/*
        echo.
        echo [SUCCESS] Published! Available at: https://pypi.org/project/cognitive-canvas-mcp/
        echo [INFO] Users can install with: pip install cognitive-canvas-mcp
    ) else (
        echo [CANCELLED] Publication cancelled
    )
) else if "%choice%"=="3" (
    echo.
    echo [INFO] For local testing, run:
    for %%f in (dist\*.whl) do echo   pip install "%%f"
    echo   cognitive-canvas
    echo.
    echo [SUCCESS] Build completed!
) else (
    echo [ERROR] Invalid choice
)

echo.
pause
