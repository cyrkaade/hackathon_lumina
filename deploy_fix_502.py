import subprocess
import os

def deploy_fix_502():
    print("Fixing 502 Error on Render Deployment")
    print("=" * 50)
    
    print("Common causes of 502 errors:")
    print("- Application crashes on startup")
    print("- Memory issues during model loading")
    print("- Missing dependencies")
    print("- Port binding issues")
    print("- Import errors")
    
    print("\nApplying fixes...")
    
    try:
        # Step 1: Use minimal requirements for testing
        print("\nStep 1: Using minimal requirements for testing...")
        subprocess.run(["cp", "requirements_minimal.txt", "requirements.txt"], check=True)
        
        # Step 2: Update render.yaml
        print("Step 2: Updating render.yaml...")
        subprocess.run(["cp", "render_fixed.yaml", "render.yaml"], check=True)
        
        # Step 3: Commit and push
        print("Step 3: Committing and pushing changes...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Fix 502 error: use minimal requirements and fixed render config"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print("\n✅ Fixes applied and deployed!")
        print("\nNext steps:")
        print("1. Check Render logs for any remaining errors")
        print("2. Test the /health endpoint")
        print("3. If working, gradually add back full requirements")
        print("4. Monitor deployment status")
        
        print("\nTest URLs:")
        print("- Health check: https://your-app.onrender.com/health")
        print("- Root: https://your-app.onrender.com/")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Please check your git configuration and try again")

if __name__ == "__main__":
    deploy_fix_502()
