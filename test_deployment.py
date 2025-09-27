import requests
import json
import time

def test_deployment(base_url):
    print(f"🧪 Testing deployment at: {base_url}")
    
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API is accessible")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_upload(base_url):
    print("\n🧪 Testing audio upload...")
    
    dummy_data = b"dummy audio data"
    files = {"file": ("test.wav", dummy_data, "audio/wav")}
    
    try:
        response = requests.post(
            f"{base_url}/api/upload-call",
            files=files,
            params={"language": "ru"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Upload endpoint working")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload test failed: {e}")
        return False

def main():
    print("🚀 Deployment Test")
    print("=" * 30)
    
    base_url = input("Enter your Render app URL (e.g., https://your-app.onrender.com): ").strip()
    
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    
    if test_deployment(base_url):
        test_upload(base_url)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
