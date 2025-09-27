import os
import subprocess
import sys

def check_git_status():
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository is ready")
            return True
        else:
            print("❌ Git repository not found")
            return False
    except FileNotFoundError:
        print("❌ Git not installed")
        return False

def init_git():
    try:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Deploy to Render - Fixed Whisper model loading"], check=True)
        print("✅ Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git initialization failed: {e}")
        return False

def main():
    print("🚀 Render Deployment Setup")
    print("=" * 40)
    
    if not check_git_status():
        print("\n📝 Setting up Git repository...")
        if not init_git():
            print("❌ Please install Git and try again")
            return
    
    print("\n🎯 Render Deployment Instructions:")
    print("1. Go to https://render.com")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New +' → 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Select your repository")
    print("6. Configure:")
    print("   - Name: call-center-api")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT")
    print("7. Add Environment Variables:")
    print("   - WHISPER_MODEL_SIZE: base")
    print("   - PORT: 10000")
    print("8. Click 'Create Web Service'")
    
    print("\n✅ Your deployment should now work!")
    print("The Whisper model will be downloaded on first use, not during build.")

if __name__ == "__main__":
    main()
