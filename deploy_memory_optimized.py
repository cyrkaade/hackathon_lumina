import subprocess
import os

def deploy_memory_optimized():
    print("🚀 Deploying Memory-Optimized Version to Render")
    print("=" * 50)
    
    print("📋 Memory Optimizations Applied:")
    print("✅ Using 'tiny' Whisper model (39MB vs 139MB)")
    print("✅ Lazy loading of AI models")
    print("✅ Environment variable configuration")
    print("✅ Optimized Docker configuration")
    
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Memory optimization: Use tiny Whisper model and lazy loading"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print("\n✅ Changes pushed to GitHub")
        print("🔄 Render will automatically redeploy...")
        print("⏳ Wait 3-5 minutes for deployment to complete")
        print("💾 Memory usage should now be under 512MB")
        
        print("\n📊 Model Size Comparison:")
        print("• tiny: 39MB (current)")
        print("• base: 139MB (previous - caused OOM)")
        print("• small: 244MB")
        print("• medium: 769MB")
        print("• large: 1550MB")
        
        print("\n🎯 Expected Results:")
        print("• Faster startup time")
        print("• Lower memory usage")
        print("• Successful deployment")
        print("• Still good transcription quality")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")
        print("Please check your git configuration and try again")

if __name__ == "__main__":
    deploy_memory_optimized()
