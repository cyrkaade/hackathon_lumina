
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
        """Separate worker and customer speech from segments"""
        worker_text = ""
        customer_text = ""
        
        print(f"🔍 Processing {len(segments)} segments for speaker separation")
        
        if not segments:
            print("⚠️ No segments provided for speaker separation")
            return "", ""
        
        for i, segment in enumerate(segments):
            text = segment.get("text", "").strip()
            if not text:
                print(f"⚠️ Segment {i} has no text, skipping")
                continue
            
            print(f"📝 Segment {i}: '{text[:50]}...'")
                
            # Try to identify speaker from segment
            speaker = self._identify_speaker(segment)
            print(f"👤 Segment {i} identified as: {speaker}")
            
            if speaker == "worker":
                worker_text += text + " "
            elif speaker == "customer":
                customer_text += text + " "
            else:
                # If speaker is unknown, try to guess based on content
                is_worker = self._is_likely_worker_text(text)
                print(f"🤔 Segment {i} content analysis: {'worker' if is_worker else 'customer'}")
                
                if is_worker:
                    worker_text += text + " "
                else:
                    customer_text += text + " "
        
        print(f"👨‍💼 Final worker text: '{worker_text.strip()}'")
        print(f"👤 Final customer text: '{customer_text.strip()}'")
        
        return worker_text.strip(), customer_text.strip()
    
    def _identify_speaker(self, segment: dict) -> str:
        """Identify speaker from segment metadata"""
        # Check for speaker labels in segment
        speaker = segment.get("speaker")
        if speaker is not None:
            if isinstance(speaker, str):
                speaker = speaker.lower()
                if "agent" in speaker or "operator" in speaker or "worker" in speaker:
                    return "worker"
                elif "client" in speaker or "customer" in speaker or "caller" in speaker:
                    return "customer"
            elif isinstance(speaker, (int, float)):
                return "customer" if int(speaker) == 0 else "worker"
        
        # Check for speaker in segment text (if Whisper detected it)
        text = segment.get("text", "").lower()
        if any(word in text for word in ["agent:", "operator:", "worker:"]):
            return "worker"
        elif any(word in text for word in ["customer:", "client:", "caller:"]):
            return "customer"
        
        return "unknown"
    
    def _is_likely_worker_text(self, text: str) -> bool:
        """Guess if text is from worker based on content"""
        text_lower = text.lower()
        
        # Worker indicators
        worker_phrases = [
            "здравствуйте", "добрый день", "как дела", "чем могу помочь",
            "понимаю", "ясно", "конечно", "помогу", "решим",
            "сәлеметсіз бе", "қайырлы күн", "қалай көмектесе аламын",
            "түсіндім", "анық", "әрине", "көмектесемін", "шешеміз"
        ]
        
        # Customer indicators
        customer_phrases = [
            "у меня проблема", "не работает", "помогите", "что делать",
            "менің мәселем бар", "жұмыс істемейді", "көмектесіңіз", "не істеу керек"
        ]
        
        worker_score = sum(1 for phrase in worker_phrases if phrase in text_lower)
        customer_score = sum(1 for phrase in customer_phrases if phrase in text_lower)
        
        return worker_score > customer_score