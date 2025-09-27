import subprocess
import os

def redeploy():
    print("🚀 Redeploying to Render with fixed requirements...")
    
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Fix: Use openai-whisper instead of whisper package"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Changes pushed to GitHub")
        print("🔄 Render will automatically redeploy...")
        print("⏳ Wait 2-3 minutes for deployment to complete")
        print("🌐 Check your Render dashboard for deployment status")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")
        print("Please check your git configuration and try again")

if __name__ == "__main__":
    redeploy()
