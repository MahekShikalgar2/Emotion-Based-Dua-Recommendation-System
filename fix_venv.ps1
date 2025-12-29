# Fix Virtual Environment and Reinstall Dependencies
# Run this script to fix broken virtual environment and TensorFlow issues

Write-Host "🔧 Fixing Virtual Environment..." -ForegroundColor Cyan

# Step 1: Deactivate current venv if active
Write-Host "`n1. Deactivating current virtual environment..." -ForegroundColor Yellow
if ($env:VIRTUAL_ENV) {
    deactivate
}

# Step 2: Remove broken virtual environment
Write-Host "`n2. Removing broken virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
    Write-Host "   ✅ Old .venv removed" -ForegroundColor Green
}

# Step 3: Create new virtual environment
Write-Host "`n3. Creating new virtual environment..." -ForegroundColor Yellow
python -m venv .venv
Write-Host "   ✅ New .venv created" -ForegroundColor Green

# Step 4: Activate virtual environment
Write-Host "`n4. Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"
Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green

# Step 5: Upgrade pip
Write-Host "`n5. Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "   ✅ pip upgraded" -ForegroundColor Green

# Step 6: Install dependencies
Write-Host "`n6. Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
Write-Host "   Installing TensorFlow, OpenCV, PyQt5, NumPy, Pandas..." -ForegroundColor Gray
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All dependencies installed successfully!" -ForegroundColor Green
    Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Train the model: cd EmotionRecognition && python model\train_model.py" -ForegroundColor White
    Write-Host "   2. Run GUI: cd EmotionRecognition\ui && python main_ui.py" -ForegroundColor White
} else {
    Write-Host "`n❌ Installation failed. Check error messages above." -ForegroundColor Red
    Write-Host "`n💡 If you see Windows Long Path errors, run enable_long_paths.ps1 as Administrator" -ForegroundColor Yellow
}

