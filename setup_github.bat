@echo off
echo Setting up GitHub repository for Call Center Assessment System
echo.

echo Step 1: Initialize Git repository
git init
git add .
git commit -m "Initial commit: Call Center Assessment System"

echo.
echo Step 2: Create GitHub repository
echo Please go to https://github.com/new
echo Create a new repository named "call-center-assessment"
echo Copy the repository URL
echo.

set /p repo_url="Enter your GitHub repository URL: "

echo.
echo Step 3: Connect to GitHub
git remote add origin %repo_url%
git branch -M main
git push -u origin main

echo.
echo ✅ GitHub repository setup complete!
echo.
echo Next steps:
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub
echo 3. Click "New Project" → "Deploy from GitHub repo"
echo 4. Select your repository
echo 5. Deploy!
echo.
pause
