
import os
import subprocess
import sys
import zipfile
import urllib.request
from pathlib import Path

def download_ffmpeg():
    print("📥 Downloading FFmpeg...")
    
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        urllib.request.urlretrieve(url, "ffmpeg.zip")
        print("✅ FFmpeg downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to download FFmpeg: {e}")
        return False

def extract_ffmpeg():
    print("📦 Extracting FFmpeg...")
    
    try:
        with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_extracted")
        print("✅ FFmpeg extracted successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to extract FFmpeg: {e}")
        return False

def setup_ffmpeg():
    print("🔧 Setting up FFmpeg...")
    
    try:
        extracted_path = Path("ffmpeg_extracted")
        if not extracted_path.exists():
            print("❌ Extracted folder not found")
            return False
        
        ffmpeg_folders = list(extracted_path.glob("ffmpeg-*"))
        if not ffmpeg_folders:
            print("❌ FFmpeg folder not found in extraction")
            return False
        
        ffmpeg_folder = ffmpeg_folders[0]
        ffmpeg_bin = ffmpeg_folder / "bin"
        
        if not ffmpeg_bin.exists():
            print("❌ FFmpeg bin folder not found")
            return False
        
        target_path = Path("ffmpeg")
        if target_path.exists():
            import shutil
            shutil.rmtree(target_path)
        
        import shutil
        shutil.copytree(ffmpeg_folder, target_path)
        
        print(f"✅ FFmpeg set up at: {target_path.absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to set up FFmpeg: {e}")
        return False

def test_ffmpeg():
    print("🧪 Testing FFmpeg...")
    
    try:
        ffmpeg_path = Path("ffmpeg/bin/ffmpeg.exe")
        if not ffmpeg_path.exists():
            print("❌ FFmpeg executable not found")
            return False
        
        result = subprocess.run([str(ffmpeg_path), "-version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ FFmpeg is working!")
            return True
        else:
            print("❌ FFmpeg test failed")
            return False
            
    except Exception as e:
        print(f"❌ FFmpeg test error: {e}")
        return False

def main():
    print("🚀 FFmpeg Setup for Call Center Assessment System")
    print("=" * 50)
    
    if not download_ffmpeg():
        return False
    
    if not extract_ffmpeg():
        return False
    
    if not setup_ffmpeg():
        return False
    
    if not test_ffmpeg():
        return False
    
    print("\n🎉 FFmpeg setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart your Python server: python main.py")
    print("2. Test audio processing: python test_audio.py")
    print("3. Test your API: python test_backend.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ FFmpeg setup failed. Please install manually:")
        print("1. Go to https://ffmpeg.org/download.html")
        print("2. Download Windows build")
        print("3. Extract to C:\\ffmpeg")
        print("4. Add C:\\ffmpeg\\bin to PATH")
    
    input("\nPress Enter to exit...")
