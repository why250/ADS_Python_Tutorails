# 1. Define Paths (Using single quotes to handle spaces safely)
$ADS_PATH = 'C:\Program Files\Keysight\ADS2025_Update2\tools\python'
$ADS_PYTHON = Join-Path $ADS_PATH 'python.exe'
$WHEEL_DIR = Join-Path $ADS_PATH 'wheelhouse'
$VENV_NAME = "ads_venv"

Write-Host "--- Starting ADS Python Environment Setup ---" -ForegroundColor Cyan

# 2. Environment Check
if (-not (Test-Path $ADS_PYTHON)) {
    Write-Host "ERROR: ADS Python not found at: $ADS_PYTHON" -ForegroundColor Red
    return
}

# 3. Create Virtual Environment
Write-Host "Creating virtual environment [$VENV_NAME]..." -ForegroundColor Yellow
# Using Start-Process to ensure it uses the correct 3.12 executable
Start-Process -FilePath $ADS_PYTHON -ArgumentList "-m venv $VENV_NAME" -Wait

# 4. Install ADS Libraries
Write-Host "Installing ADS Wheels (this may take a minute)..." -ForegroundColor Yellow
$LOCAL_PIP = Join-Path (Get-Location) "$VENV_NAME\Scripts\python.exe"

# Navigate to wheelhouse and install locally to bypass proxy issues
Push-Location $WHEEL_DIR
try {
    # --no-index ensures pip only looks at the local --find-links folder
    # --proxy "" bypasses any system VPN/SOCKS settings
    # Revised Step 4: No proxy needed since we are using --no-index for local files
& $LOCAL_PIP -m pip install -r venv_requirements.txt --find-links . --no-index
}
catch {
    Write-Host "Installation failed. Please check if venv_requirements.txt exists in $WHEEL_DIR" -ForegroundColor Red
}
finally {
    Pop-Location
}

# 5. Verification
Write-Host "`n--- Setup Complete! ---" -ForegroundColor Green
Write-Host "To activate this environment, run:"
Write-Host ".\$VENV_NAME\Scripts\activate" -ForegroundColor White

Write-Host "`nInstalled Packages:"
& $LOCAL_PIP -m pip list