# Download and extract ngrok
Write-Host "Downloading ngrok..." -ForegroundColor Cyan

$url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
Invoke-WebRequest -Uri $url -OutFile "ngrok.zip" -UseBasicParsing

Write-Host "Extracting ngrok..." -ForegroundColor Cyan
python -c "import zipfile; z = zipfile.ZipFile('ngrok.zip'); z.extractall('.'); z.close()"

Write-Host "Done!" -ForegroundColor Green

if (Test-Path ".\ngrok.exe") {
    Write-Host "SUCCESS - ngrok.exe is ready" -ForegroundColor Green
    .\ngrok.exe version
} else {
    Write-Host "ERROR - Windows Defender blocked ngrok" -ForegroundColor Red
    Write-Host "Please disable Real-time protection temporarily and try again" -ForegroundColor Yellow
}

Remove-Item ngrok.zip -ErrorAction SilentlyContinue
