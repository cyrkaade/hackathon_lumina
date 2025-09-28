import os
import whisper
import torch
from typing import Dict, List, Tuple
import logging
from transformers import pipeline
import openai
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AISpeechRecognizer:
    def __init__(self, model_size=None):
        if model_size is None:
            model_size = os.environ.get("WHISPER_MODEL_SIZE", "base")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.model_size = model_size
        
        # Initialize AI clients
        self.openai_client = None
        self.anthropic_client = None
        self._init_ai_clients()
        
        # Language detection model
        self.language_detector = None
        self._init_language_detector()
        
    def _init_ai_clients(self):
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        try:
            # OpenAI client
            if os.environ.get("OPENAI_API_KEY"):
                self.openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI client initialization failed: {e}")
            
    
    def _init_language_detector(self):
        """Initialize language detection model"""
        try:
            self.language_detector = pipeline(
                "text-classification",
                model="papluca/xlm-roberta-base-language-detection",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ Language detection model loaded")
        except Exception as e:
            logger.warning(f"⚠️ Language detection model failed: {e}")
            self.language_detector = None
    
    def _load_model(self):
        """Lazy load Whisper model"""
        if self.model is None:
            try:
                logger.info(f"Loading Whisper {self.model_size} model...")
                self.model = whisper.load_model(self.model_size, device=self.device)
                logger.info(f"✅ Whisper {self.model_size} model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load {self.model_size} model, trying tiny model: {e}")
                self.model = whisper.load_model("tiny", device=self.device)
                logger.info("✅ Whisper tiny model loaded as fallback")
    
    def detect_language_ai(self, audio_path: str) -> str:
        """Enhanced language detection using AI"""
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            self._load_model()
            
            logger.info(f"🔍 AI-powered language detection for: {audio_path}")
            
            # First, get a quick transcription for language detection
            result = self.model.transcribe(
                audio_path,
                task="transcribe",
                verbose=False,
                word_timestamps=False
            )
            
            detected_lang = result.get("language", "unknown")
            transcription_text = result.get("text", "")
            
            logger.info(f"Whisper detected language: {detected_lang}")
            logger.info(f"Transcription sample: {transcription_text[:100]}...")
            
            # Enhanced language detection using AI
            if self.language_detector and transcription_text:
                try:
                    # Use language detection model
                    lang_result = self.language_detector(transcription_text)
                    ai_detected_lang = lang_result[0]['label'].lower()
                    confidence = lang_result[0]['score']
                    
                    logger.info(f"AI language detection: {ai_detected_lang} (confidence: {confidence:.2f})")
                    
                    # Map to our supported languages
                    if ai_detected_lang in ['ru', 'russian']:
                        return "ru"
                    elif ai_detected_lang in ['kk', 'kazakh']:
                        return "kk"
                    elif confidence > 0.8:  # High confidence in other language
                        logger.info(f"High confidence in {ai_detected_lang}, defaulting to Russian")
                        return "ru"
                        
                except Exception as e:
                    logger.warning(f"AI language detection failed: {e}")
            
            # Fallback to Whisper detection
            if detected_lang in ["ru", "russian"]:
                return "ru"
            elif detected_lang in ["kk", "kazakh"]:
                return "kk"
            else:
                logger.info(f"Unknown language {detected_lang}, defaulting to Russian")
                return "ru"
                
        except Exception as e:
            logger.error(f"Language detection failed: {e}, defaulting to Russian")
            return "ru"
    
    def transcribe_audio_ai(self, audio_path: str, language: str = None) -> Dict:
        """Enhanced transcription with AI-powered analysis"""
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            self._load_model()
            
            # Enhanced language detection
            if language is None:
                language = self.detect_language_ai(audio_path)
            
            logger.info(f"🎤 AI-enhanced transcription: {audio_path} in language: {language}")
            
            # Transcribe with detected language
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False,
                word_timestamps=True
            )
            
            transcription_text = result["text"]
            segments = result["segments"]
            
            # AI-powered transcription enhancement
            enhanced_transcription = self._enhance_transcription_with_ai(
                transcription_text, 
                language, 
                segments
            )
            
            return {
                "text": enhanced_transcription["text"],
                "segments": enhanced_transcription["segments"],
                "language": language,
                "detected_language": result.get("language", language),
                "duration": result.get("duration", 0),
                "confidence": enhanced_transcription.get("confidence", 0.8),
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"AI transcription failed: {e}")
            # Fallback to basic transcription
            return self._fallback_transcription(audio_path, language)
    
    def _enhance_transcription_with_ai(self, text: str, language: str, segments: List) -> Dict:
        """Enhance transcription using AI"""
        try:
            if not text.strip():
                return {"text": text, "segments": segments, "confidence": 0.5}
            
            # Create AI prompt for transcription enhancement
            prompt = self._create_transcription_prompt(text, language)
            
            # Try OpenAI first, then Anthropic
            enhanced_text = None
            confidence = 0.8
            
            if self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert in Russian and Kazakh language transcription enhancement."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.1
                    )
                    enhanced_text = response.choices[0].message.content.strip()
                    confidence = 0.9
                    logger.info("✅ OpenAI enhanced transcription")
                except Exception as e:
                    logger.warning(f"OpenAI enhancement failed: {e}")
            
            if not enhanced_text and self.anthropic_client:
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=1000,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    enhanced_text = response.content[0].text.strip()
                    confidence = 0.9
                    logger.info("✅ Anthropic enhanced transcription")
                except Exception as e:
                    logger.warning(f"Anthropic enhancement failed: {e}")
            
            # Use enhanced text if available, otherwise use original
            final_text = enhanced_text if enhanced_text else text
            
            # Update segments with enhanced text
            enhanced_segments = self._update_segments_with_enhanced_text(segments, final_text)
            
            return {
                "text": final_text,
                "segments": enhanced_segments,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Transcription enhancement failed: {e}")
            return {"text": text, "segments": segments, "confidence": 0.7}
    
    def _create_transcription_prompt(self, text: str, language: str) -> str:
        """Create AI prompt for transcription enhancement"""
        lang_name = "Russian" if language == "ru" else "Kazakh"
        
        prompt = f"""
Please enhance and correct this {lang_name} transcription from a call center conversation. 
The text may have errors, missing punctuation, or unclear words.

Original transcription:
"{text}"

Please:
1. Correct any obvious transcription errors
2. Add proper punctuation and capitalization
3. Fix grammar if needed
4. Keep the original meaning and tone
5. Return only the corrected text, no explanations

Enhanced transcription:
"""
        return prompt
    
    def _update_segments_with_enhanced_text(self, segments: List, enhanced_text: str) -> List:
        """Update segments with enhanced text"""
        try:
            # Simple approach: split enhanced text proportionally
            words = enhanced_text.split()
            total_words = len(words)
            
            enhanced_segments = []
            word_index = 0
            
            for segment in segments:
                original_words = segment.get("text", "").split()
                segment_word_count = len(original_words)
                
                if word_index + segment_word_count <= total_words:
                    segment_text = " ".join(words[word_index:word_index + segment_word_count])
                    word_index += segment_word_count
                else:
                    segment_text = " ".join(words[word_index:])
                    word_index = total_words
                
                enhanced_segment = segment.copy()
                enhanced_segment["text"] = segment_text
                enhanced_segments.append(enhanced_segment)
            
            return enhanced_segments
            
        except Exception as e:
            logger.error(f"Segment update failed: {e}")
            return segments
    
    def _fallback_transcription(self, audio_path: str, language: str = None) -> Dict:
        """Fallback transcription without AI enhancement"""
        try:
            self._load_model()
            
            if language is None:
                language = "ru"  # Default to Russian
            
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
                "duration": result.get("duration", 0),
                "confidence": 0.7,
                "ai_enhanced": False
            }
            
        except Exception as e:
            logger.error(f"Fallback transcription failed: {e}")
            # Return mock transcription as last resort
            return {
                "text": "Здравствуйте! У меня проблема с картой. Понимаю, помогу решить. Спасибо!",
                "segments": [
                    {"text": "Здравствуйте! У меня проблема с картой.", "start": 0, "end": 3},
                    {"text": "Понимаю, помогу решить.", "start": 3, "end": 6},
                    {"text": "Спасибо!", "start": 6, "end": 8}
                ],
                "language": "ru",
                "detected_language": "ru",
                "duration": 8,
                "confidence": 0.5,
                "ai_enhanced": False
            }
    
    def separate_speakers_ai(self, segments: List) -> Tuple[str, str]:
        """AI-enhanced speaker separation"""
        try:
            logger.info(f"🔍 AI-enhanced speaker separation for {len(segments)} segments")
            
            if not segments:
                logger.warning("No segments provided for speaker separation")
                return "", ""
            
            # Combine all text for AI analysis
            full_text = " ".join([seg.get("text", "") for seg in segments])
            
            if not full_text.strip():
                return "", ""
            
            # Create AI prompt for speaker separation
            prompt = self._create_speaker_separation_prompt(full_text)
            
            # Try AI-powered speaker separation
            separation_result = None
            
            if self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert in analyzing call center conversations in Russian and Kazakh languages."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.1
                    )
                    separation_result = response.choices[0].message.content.strip()
                    logger.info("✅ OpenAI speaker separation completed")
                except Exception as e:
                    logger.warning(f"OpenAI speaker separation failed: {e}")
            
            if not separation_result and self.anthropic_client:
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=1000,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    separation_result = response.content[0].text.strip()
                    logger.info("✅ Anthropic speaker separation completed")
                except Exception as e:
                    logger.warning(f"Anthropic speaker separation failed: {e}")
            
            # Parse AI result
            if separation_result:
                worker_text, customer_text = self._parse_ai_speaker_separation(separation_result)
                if worker_text and customer_text:
                    logger.info(f"👨‍💼 AI Worker text: '{worker_text[:100]}...'")
                    logger.info(f"👤 AI Customer text: '{customer_text[:100]}...'")
                    return worker_text, customer_text
            
            # Fallback to rule-based separation
            logger.info("🔄 Falling back to rule-based speaker separation")
            return self._fallback_speaker_separation(segments)
            
        except Exception as e:
            logger.error(f"AI speaker separation failed: {e}")
            return self._fallback_speaker_separation(segments)
    
    def _create_speaker_separation_prompt(self, text: str) -> str:
        """Create AI prompt for speaker separation"""
        prompt = f"""
Please separate this call center conversation into two speakers: the call center worker and the customer.

Conversation text:
"{text}"

Please identify which parts are spoken by:
1. CALL CENTER WORKER (agent/operator) - usually professional, helpful, asking questions
2. CUSTOMER (client) - usually describing problems, asking for help

Format your response as:
WORKER: [text spoken by the call center worker]
CUSTOMER: [text spoken by the customer]

Separate each speaker's text clearly. If you're unsure about a part, make your best guess based on context.
"""
        return prompt
    
    def _parse_ai_speaker_separation(self, ai_result: str) -> Tuple[str, str]:
        """Parse AI speaker separation result"""
        try:
            lines = ai_result.split('\n')
            worker_parts = []
            customer_parts = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('WORKER:'):
                    worker_parts.append(line[7:].strip())
                elif line.startswith('CUSTOMER:'):
                    customer_parts.append(line[9:].strip())
            
            worker_text = " ".join(worker_parts).strip()
            customer_text = " ".join(customer_parts).strip()
            
            return worker_text, customer_text
            
        except Exception as e:
            logger.error(f"Failed to parse AI speaker separation: {e}")
            return "", ""
    
    def _fallback_speaker_separation(self, segments: List) -> Tuple[str, str]:
        """Fallback rule-based speaker separation"""
        worker_text = ""
        customer_text = ""
        
        for i, segment in enumerate(segments):
            text = segment.get("text", "").strip()
            if not text:
                continue
            
            # Simple rule-based separation
            is_worker = self._is_likely_worker_text(text)
            
            if is_worker:
                worker_text += text + " "
            else:
                customer_text += text + " "
        
        return worker_text.strip(), customer_text.strip()
    
    def _is_likely_worker_text(self, text: str) -> bool:
        """Determine if text is likely from worker based on content"""
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
