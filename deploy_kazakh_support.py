import subprocess
import os

def deploy_kazakh_support():
    print("🚀 Deploying Kazakh Language Support")
    print("=" * 50)
    
    print("📋 New Features Added:")
    print("✅ Automatic language detection (Russian/Kazakh)")
    print("✅ Kazakh-specific keywords and phrases")
    print("✅ Bilingual emotion analysis")
    print("✅ Language-aware scoring system")
    print("✅ Kazakh greetings and closings detection")
    print("✅ Professional/unprofessional indicators in Kazakh")
    print("✅ Resolution keywords in Kazakh")
    
    print("\n🌍 Language Support:")
    print("• Russian (ru): Full support")
    print("• Kazakh (kk): Full support")
    print("• Auto-detection: Enabled")
    print("• Fallback: Russian (if detection fails)")
    
    print("\n📊 Kazakh Keywords Added:")
    print("Greetings: сәлеметсіз бе, қайырлы күн, қайырлы кеш, қайырлы таң")
    print("Resolutions: шешілді, көмектестім, түзетілді, дайын")
    print("Professional: рахмет, өтінемін, кешіріңіз, ризамын")
    print("Closings: сау болыңыз, барлығы жақсы, жақсы күн")
    
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Add Kazakh language support with auto-detection"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print("\n✅ Changes pushed to GitHub")
        print("🔄 Render will automatically redeploy...")
        print("⏳ Wait 3-5 minutes for deployment to complete")
        
        print("\n🧪 Test Your Deployment:")
        print("1. Run: python test_kazakh_support.py")
        print("2. Upload a Kazakh audio file")
        print("3. Check language detection in results")
        
        print("\n📱 API Usage:")
        print("POST /api/upload-call")
        print("• file: audio file (WAV, MP3, M4A)")
        print("• language: optional (auto-detected if not provided)")
        print("• Returns: assessment with detected language")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")
        print("Please check your git configuration and try again")

if __name__ == "__main__":
    deploy_kazakh_support()
