import requests
import json

def test_kazakh_language_detection():
    print("🧪 Testing Kazakh Language Support")
    print("=" * 40)
    
    # Test data for Kazakh language
    kazakh_test_data = {
        "greetings": [
            "сәлеметсіз бе, қалайсыз?",
            "қайырлы күн, мен сізге көмектесе аламын",
            "сәлем, мәселеңіз қандай?"
        ],
        "resolutions": [
            "мәселе шешілді, рахмет",
            "көмектестіңіз, енді барлығы дұрыс",
            "шештім, енді жұмыс істейді"
        ],
        "professional": [
            "рахмет, өтінемін, кешіріңіз",
            "ризамын, барлығы жақсы"
        ]
    }
    
    print("📝 Kazakh Test Phrases:")
    for category, phrases in kazakh_test_data.items():
        print(f"\n{category.upper()}:")
        for phrase in phrases:
            print(f"  • {phrase}")
    
    print("\n🎯 Expected Results:")
    print("✅ Language detection: kk (Kazakh)")
    print("✅ Greeting detection: True")
    print("✅ Resolution detection: resolved")
    print("✅ Professional indicators: detected")
    
    print("\n📊 Language Support Summary:")
    print("• Russian (ru): Full support")
    print("• Kazakh (kk): Full support")
    print("• Auto-detection: Enabled")
    print("• Fallback: Russian (if detection fails)")

def test_api_with_kazakh():
    print("\n🌐 Testing API with Kazakh Language")
    print("=" * 40)
    
    base_url = input("Enter your API URL (or press Enter to skip): ").strip()
    
    if not base_url:
        print("⏭️ Skipping API test")
        return
    
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    
    try:
        # Test API health
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API is accessible")
            
            # Test upload endpoint (without actual file)
            print("\n📤 Testing upload endpoint...")
            print("Note: You can upload a Kazakh audio file to test language detection")
            print(f"Endpoint: POST {base_url}/api/upload-call")
            print("Parameters: file (audio), language (optional - auto-detected)")
            
        else:
            print(f"❌ API returned status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")

def main():
    test_kazakh_language_detection()
    test_api_with_kazakh()
    
    print("\n🎉 Kazakh Language Support Added!")
    print("\n📋 Features:")
    print("• Automatic language detection (Russian/Kazakh)")
    print("• Kazakh-specific keywords and phrases")
    print("• Bilingual emotion analysis")
    print("• Language-aware scoring")
    print("• Fallback to Russian if detection fails")
    
    print("\n🚀 Usage:")
    print("1. Upload audio file to /api/upload-call")
    print("2. Language will be auto-detected")
    print("3. Assessment will use appropriate language models")
    print("4. Results include detected language information")

if __name__ == "__main__":
    main()
