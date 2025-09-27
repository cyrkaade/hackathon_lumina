
import whisper
import torch
from typing import Tuple, Dict
import numpy as np
from scipy.io import wavfile

class SpeechRecognizer:
    def __init__(self, model_size="large"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size, device=self.device)
        
    def transcribe_audio(self, audio_path: str, language: str = "ru") -> Dict:

        try:

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