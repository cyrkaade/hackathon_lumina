@echo off
echo Installing FFmpeg for Windows...
echo.

REM Method 1: Try chocolatey
echo Trying Chocolatey...
choco install ffmpeg -y
if %errorlevel% equ 0 (
    echo FFmpeg installed successfully via Chocolatey!
    goto :success
)

REM Method 2: Try winget
echo Trying winget...
winget install ffmpeg
if %errorlevel% equ 0 (
    echo FFmpeg installed successfully via winget!
    goto :success
)

REM Method 3: Manual download instructions
echo.
echo Automatic installation failed. Please install FFmpeg manually:
echo.
echo 1. Go to https://ffmpeg.org/download.html
echo 2. Download Windows builds
echo 3. Extract to C:\ffmpeg
echo 4. Add C:\ffmpeg\bin to your PATH environment variable
echo.
echo Or run this PowerShell command as Administrator:
echo.
echo [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
echo Invoke-WebRequest -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile "ffmpeg.zip"
echo Expand-Archive -Path "ffmpeg.zip" -DestinationPath "C:\"
echo [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg-master-latest-win64-gpl\bin", [EnvironmentVariableTarget]::Machine)
echo.
goto :end

:success
echo.
echo FFmpeg is now installed! Please restart your command prompt/PowerShell.
echo Then restart your Python server: python main.py
echo.

:end
pause

