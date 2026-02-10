# Quick ngrok download and extraction script
Write-Host "🔽 Downloading ngrok..." -ForegroundColor Cyan

# Download
$url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$output = "$PSScriptRoot\ngrok.zip"

# Use faster method
Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing

Write-Host "📦 Extracting ngrok..." -ForegroundColor Cyan

# Quick extraction with Python
python -c "import zipfile; z = zipfile.ZipFile('ngrok.zip'); z.extractall('.'); z.close()"

Write-Host "✅ ngrok ready!" -ForegroundColor Green

# Verify
if (Test-Path ".\ngrok.exe") {
    Write-Host "✅ ngrok.exe found" -ForegroundColor Green
    .\ngrok.exe version
} else {
    Write-Host "❌ Windows Defender may have blocked ngrok." -ForegroundColor Red
    Write-Host "📝 Please temporarily disable Windows Defender Real-time protection:" -ForegroundColor Yellow
    Write-Host "   1. Open Windows Security" -ForegroundColor Yellow
    Write-Host "   2. Virus and threat protection" -ForegroundColor Yellow
    Write-Host "   3. Turn OFF Real-time protection (temporarily)" -ForegroundColor Yellow
    Write-Host "   4. Run this script again" -ForegroundColor Yellow
}

Remove-Item ngrok.zip -ErrorAction SilentlyContinue
