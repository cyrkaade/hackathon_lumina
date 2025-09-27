
import whisper
import torch
from typing import Tuple, Dict
import numpy as np
from scipy.io import wavfile
import os
import subprocess
import tempfile

class SpeechRecognizer:
    def __init__(self, model_size=None):
        if model_size is None:
            model_size = os.environ.get("WHISPER_MODEL_SIZE", "tiny")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.model_size = model_size
        
    def _load_model(self):
        if self.model is None:
            try:
                print(f"Loading Whisper {self.model_size} model...")
                self.model = whisper.load_model(self.model_size, device=self.device)
                print(f"✅ Whisper {self.model_size} model loaded successfully")
            except Exception as e:
                print(f"Failed to load {self.model_size} model, trying tiny model: {e}")
                self.model = whisper.load_model("tiny", device=self.device)
                print("✅ Whisper tiny model loaded as fallback")
        
    def detect_language(self, audio_path: str) -> str:
        """Detect the language of the audio file"""
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            self._load_model()
            
            print(f"Detecting language for: {audio_path}")
            
            # First, transcribe without specifying language to detect it
            result = self.model.transcribe(
                audio_path,
                task="transcribe",
                verbose=False,
                word_timestamps=False
            )
            
            detected_lang = result.get("language", "unknown")
            print(f"Detected language: {detected_lang}")
            
            # Map detected language codes to our supported languages
            if detected_lang in ["ru", "russian"]:
                return "ru"
            elif detected_lang in ["kk", "kazakh"]:
                return "kk"
            else:
                # Default to Russian if language is not clearly detected
                print(f"Unknown language {detected_lang}, defaulting to Russian")
                return "ru"
                
        except Exception as e:
            print(f"Language detection failed: {e}, defaulting to Russian")
            return "ru"
    
    def transcribe_audio(self, audio_path: str, language: str = None) -> Dict:
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            self._load_model()
            
            # Auto-detect language if not specified
            if language is None:
                language = self.detect_language(audio_path)
            
            print(f"Transcribing audio file: {audio_path} in language: {language}")
            
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False,
                word_timestamps=True
            )
            
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": language,
                "detected_language": result.get("language", language),
                "duration": result.get("duration", 0)
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def separate_speakers(self, segments: list) -> Tuple[str, str]:


        worker_text = ""
        customer_text = ""

        
        return worker_text, customer_text