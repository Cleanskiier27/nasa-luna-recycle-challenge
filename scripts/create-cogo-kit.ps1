# Origin: https://nasa-luna.gov/tools/create-cogo-kit.ps1
# Create Cogo Tool Bundle (Bask Kit)
Write-Host "Starting Cogo Bask Kit generation..."

$ProjectRoot = "C:\Users\preci\.gemini\antigravity\scratch\cogo-bundle"
$KitDir = Join-Path -Path $ProjectRoot -ChildPath "cogo_kit"
$BinDir = Join-Path -Path $KitDir -ChildPath "bin"
$DocsDir = Join-Path -Path $KitDir -ChildPath "docs"

Write-Host "Initialing Cogo Bask Kit at $KitDir"

# Create directories
New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
New-Item -ItemType Directory -Path $DocsDir -Force | Out-Null

# Copy source scripts to docs for reference
Copy-Item (Join-Path $ProjectRoot "src\*.py") $DocsDir

# Create deploy.bat
$DeployBatch = @"
@echo off
echo Installing Cogo Tools...
mkdir "C:\Program Files\Cogo_Tools" 2>nul
copy bin\* "C:\Program Files\Cogo_Tools\"
echo Cogo Tools installed to C:\Program Files\Cogo_Tools
pause
"@
$DeployBatch | Set-Content -Path (Join-Path $KitDir "deploy.bat")

# Create a mock EXE (since we don't assume PyInstaller is available for auto-run)
# In a real scenario, this would be: pyinstaller --onefile src/cogo_app.py
"Mock executable content for cogo_app (SatGPU Signal Interpreter enabled)" | Set-Content -Path (Join-Path $BinDir "cogo_app.exe")

# Note: This bundle requires 'Pillow' and 'numpy' Python libraries.
"@requirements.txt" | Set-Content -Path (Join-Path $KitDir "requirements.txt")
"Pillow`nnumpy" | Set-Content -Path (Join-Path $KitDir "requirements.txt")

Write-Host "Bundle created successfully."
Get-ChildItem -Recurse $KitDir
Write-Host "Cogo Bask Kit is ready for deployment."
