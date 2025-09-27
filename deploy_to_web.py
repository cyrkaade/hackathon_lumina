
import os
import subprocess
import sys
from pathlib import Path

def create_deployment_files():
    print("🚀 Creating deployment files...")
    
    with open("Procfile", "w") as f:
        f.write("web: uvicorn main:app --host 0.0.0.0 --port $PORT\n")
    
    with open("runtime.txt", "w") as f:
        f.write("python-3.9.18\n")
    
    render_config = """services:
  - type: web
    name: call-center-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
"""
    with open("render.yaml", "w") as f:
        f.write(render_config)
    
    gcp_config = """runtime: python39
service: call-center-api

handlers:
- url: /.*
  script: auto

env_variables:
  PORT: 8080
"""
    with open("app.yaml", "w") as f:
        f.write(gcp_config)
    
    dockerfile = """FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads data

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    print("✅ Deployment files created!")

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
        subprocess.run(["git", "commit", "-m", "Initial commit for deployment"], check=True)
        print("✅ Git repository initialized")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to initialize git")
        return False

def setup_github():
    """Help setup GitHub repository"""
    print("\n📝 Setting up GitHub repository...")
    print("1. Go to https://github.com/new")
    print("2. Create a new repository")
    print("3. Copy the repository URL")
    print("4. Run these commands:")
    print("   git remote add origin <your-repo-url>")
    print("   git branch -M main")
    print("   git push -u origin main")

def main():
    print("🌐 Call Center Assessment System - Web Deployment Setup")
    print("=" * 60)
    
    create_deployment_files()
    
    if not check_git_status():
        print("\n📝 Setting up Git repository...")
        if not init_git():
            print("❌ Please install Git and try again")
            return
    
    print("\n🎯 Choose your deployment platform:")
    print("1. Railway (Recommended - Easiest)")
    print("2. Render")
    print("3. Heroku")
    print("4. Google Cloud Platform")
    print("5. AWS")
    print("6. Setup GitHub repository")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        print("\n🚀 Railway Deployment:")
        print("1. Go to https://railway.app")
        print("2. Sign up with GitHub")
        print("3. Click 'New Project' → 'Deploy from GitHub repo'")
        print("4. Select your repository")
        print("5. Railway will auto-detect Python and deploy!")
        print("\n✅ Your app will be available at: https://your-app-name.railway.app")
        print("\n📋 Environment Variables to set in Railway:")
        print("- PYTHON_VERSION: 3.9")
        print("- CORS_ORIGINS: https://your-frontend-domain.com")
        
    elif choice == "2":
        print("\n🚀 Render Deployment:")
        print("1. Go to https://render.com")
        print("2. Sign up and connect GitHub")
        print("3. Click 'New' → 'Web Service'")
        print("4. Connect your repository")
        print("5. Use the render.yaml configuration")
        print("6. Deploy!")
        print("\n✅ Your app will be available at: https://your-app-name.onrender.com")
        
    elif choice == "3":
        print("\n🚀 Heroku Deployment:")
        print("1. Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli")
        print("2. Run: heroku login")
        print("3. Run: heroku create your-app-name")
        print("4. Run: git push heroku main")
        print("\n✅ Your app will be available at: https://your-app-name.herokuapp.com")
        
    elif choice == "4":
        print("\n🚀 Google Cloud Platform Deployment:")
        print("1. Install Google Cloud SDK")
        print("2. Run: gcloud auth login")
        print("3. Run: gcloud config set project YOUR_PROJECT_ID")
        print("4. Run: gcloud app deploy")
        print("\n✅ Your app will be available at: https://your-project-id.appspot.com")
        
    elif choice == "5":
        print("\n🚀 AWS Deployment:")
        print("1. Install AWS CLI")
        print("2. Configure AWS credentials")
        print("3. Use Elastic Beanstalk or Lambda")
        print("4. Deploy using EB CLI or Serverless Framework")
        print("\n✅ Your app will be available at your AWS domain")
        
    elif choice == "6":
        setup_github()
        
    else:
        print("❌ Invalid choice")
        return
    
    print("\n📋 Post-Deployment Checklist:")
    print("- [ ] Test your API endpoints")
    print("- [ ] Update CORS origins in main.py for your frontend")
    print("- [ ] Set environment variables if needed")
    print("- [ ] Monitor logs for any issues")
    print("- [ ] Update your frontend to use the new API URL")
    
    print("\n🔧 Frontend Integration:")
    print("Update your frontend to use the new API URL:")
    print("const api = new CallCenterAPI('https://your-app-name.railway.app');")
    print("// or")
    print("const api = new CallCenterAPI('https://your-app-name.onrender.com');")

if __name__ == "__main__":
    main()
