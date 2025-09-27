# FFmpeg Installation Script for Windows
Write-Host "Installing FFmpeg for Windows..." -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "This script needs to run as Administrator. Please run PowerShell as Administrator and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    # Method 1: Try chocolatey
    Write-Host "Trying Chocolatey..." -ForegroundColor Yellow
    choco install ffmpeg -y
    if ($LASTEXITCODE -eq 0) {
        Write-Host "FFmpeg installed successfully via Chocolatey!" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "Chocolatey not available or failed" -ForegroundColor Yellow
}

try {
    # Method 2: Try winget
    Write-Host "Trying winget..." -ForegroundColor Yellow
    winget install ffmpeg
    if ($LASTEXITCODE -eq 0) {
        Write-Host "FFmpeg installed successfully via winget!" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "winget not available or failed" -ForegroundColor Yellow
}

# Method 3: Manual download
Write-Host "Automatic installation failed. Downloading FFmpeg manually..." -ForegroundColor Yellow

# Set security protocol
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Download FFmpeg
$downloadUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$outputPath = "$env:TEMP\ffmpeg.zip"
$extractPath = "C:\ffmpeg"

Write-Host "Downloading FFmpeg from GitHub..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath

Write-Host "Extracting FFmpeg..." -ForegroundColor Yellow
Expand-Archive -Path $outputPath -DestinationPath "C:\" -Force

# Find the extracted folder
$extractedFolder = Get-ChildItem "C:\" -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1

if ($extractedFolder) {
    # Rename to ffmpeg
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    Rename-Item $extractedFolder.FullName $extractPath
    
    # Add to PATH
    $ffmpegBinPath = "$extractPath\bin"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
    
    if ($currentPath -notlike "*$ffmpegBinPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$ffmpegBinPath", [EnvironmentVariableTarget]::Machine)
        Write-Host "Added FFmpeg to system PATH" -ForegroundColor Green
    }
    
    # Clean up
    Remove-Item $outputPath -Force
    
    Write-Host "FFmpeg installed successfully!" -ForegroundColor Green
    Write-Host "Please restart your command prompt/PowerShell for PATH changes to take effect." -ForegroundColor Yellow
    Write-Host "Then restart your Python server: python main.py" -ForegroundColor Yellow
} else {
    Write-Host "Failed to extract FFmpeg. Please install manually from https://ffmpeg.org/download.html" -ForegroundColor Red
}

Read-Host "Press Enter to exit"

