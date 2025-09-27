
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
            model_size = os.environ.get("WHISPER_MODEL_SIZE", "base")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.model = whisper.load_model(model_size, device=self.device)
        except Exception as e:
            print(f"Failed to load {model_size} model, trying smaller model: {e}")
            self.model = whisper.load_model("tiny", device=self.device)
        
    def transcribe_audio(self, audio_path: str, language: str = "ru") -> Dict:
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            print(f"Transcribing audio file: {audio_path}")
            
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
                "language": result["language"],
                "duration": result.get("duration", 0)
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def separate_speakers(self, segments: list) -> Tuple[str, str]:


        worker_text = ""
        customer_text = ""

        
        return worker_text, customer_text