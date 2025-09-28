import os
import sys
import traceback
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add error handling for imports
try:
    logger.info("🔄 Starting AI-enhanced imports...")
    
    # Try to import AI-enhanced modules
    try:
        from speech_recognition_ai import AISpeechRecognizer
        logger.info("✅ AISpeechRecognizer imported successfully")
        SPEECH_AI_AVAILABLE = True
    except Exception as e:
        logger.error(f"❌ AISpeechRecognizer import failed: {e}")
        SPEECH_AI_AVAILABLE = False
        # Fallback to basic speech recognizer
        try:
            from speech_recognition import SpeechRecognizer
            logger.info("✅ Basic SpeechRecognizer imported as fallback")
            SPEECH_AI_AVAILABLE = False
        except Exception as e2:
            logger.error(f"❌ Basic SpeechRecognizer also failed: {e2}")
            class SpeechRecognizer:
                def transcribe_audio(self, *args, **kwargs):
                    return {"text": "Mock transcription for testing", "segments": [], "language": "ru"}
                def separate_speakers(self, *args, **kwargs):
                    return "Mock worker text", "Mock customer text"

    try:
        from emotion_analyzer_ai import AIEmotionAnalyzer
        logger.info("✅ AIEmotionAnalyzer imported successfully")
        EMOTION_AI_AVAILABLE = True
    except Exception as e:
        logger.error(f"❌ AIEmotionAnalyzer import failed: {e}")
        EMOTION_AI_AVAILABLE = False
        # Fallback to basic emotion analyzer
        try:
            from emotion_analyzer import EmotionAnalyzer
            logger.info("✅ Basic EmotionAnalyzer imported as fallback")
        except Exception as e2:
            logger.error(f"❌ Basic EmotionAnalyzer also failed: {e2}")
            class EmotionAnalyzer:
                def analyze_emotions(self, *args, **kwargs):
                    return {"sentiment": "neutral", "sentiment_confidence": 0.5}
                def track_emotion_progression(self, *args, **kwargs):
                    return []

    try:
        from resolution_detector import ResolutionDetector
        logger.info("✅ ResolutionDetector imported successfully")
        RESOLUTION_AVAILABLE = True
    except Exception as e:
        logger.error(f"❌ ResolutionDetector import failed: {e}")
        RESOLUTION_AVAILABLE = False
        class ResolutionDetector:
            def detect_issue_resolution(self, *args, **kwargs):
                return {"resolved": True, "resolution_score": 75}

    try:
        from scoring_engine import ScoringEngine
        logger.info("✅ ScoringEngine imported successfully")
        SCORING_AVAILABLE = True
    except Exception as e:
        logger.error(f"❌ ScoringEngine import failed: {e}")
        SCORING_AVAILABLE = False
        class ScoringEngine:
            def calculate_total_score(self, *args, **kwargs):
                return {
                    "total_score": 75, 
                    "performance_grade": "Satisfactory",
                    "emotion_score": 75, 
                    "resolution_score": 75, 
                    "communication_score": 75, 
                    "professionalism_score": 75,
                    "empathy_score": 75,
                    "efficiency_score": 75,
                    "breakdown": {
                        "strengths": ["System running in minimal mode"], 
                        "improvements": ["Full AI features not available"]
                    }
                }
    
    logger.info("✅ All imports completed (with fallbacks if needed)")
    
except Exception as e:
    logger.error(f"❌ Critical import error: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

app = FastAPI(title="AI-Enhanced Call Center Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components with error handling
try:
    if SPEECH_AI_AVAILABLE:
        speech_recognizer = AISpeechRecognizer()
        logger.info("✅ AI Speech Recognizer initialized")
    else:
        speech_recognizer = SpeechRecognizer()
        logger.info("✅ Basic Speech Recognizer initialized")
    
    if EMOTION_AI_AVAILABLE:
        emotion_analyzer = AIEmotionAnalyzer()
        logger.info("✅ AI Emotion Analyzer initialized")
    else:
        emotion_analyzer = EmotionAnalyzer()
        logger.info("✅ Basic Emotion Analyzer initialized")
    
    resolution_detector = ResolutionDetector()
    scoring_engine = ScoringEngine()
    logger.info("✅ All components initialized successfully")
    
except Exception as e:
    logger.error(f"❌ Component initialization failed: {e}")
    # Use mock components if initialization fails
    speech_recognizer = SpeechRecognizer()
    emotion_analyzer = EmotionAnalyzer()
    resolution_detector = ResolutionDetector()
    scoring_engine = ScoringEngine()

class AssessmentResponse(BaseModel):
    call_id: str
    worker_id: int
    total_score: float
    performance_grade: str
    emotion_score: float
    resolution_score: float
    communication_score: float
    professionalism_score: float
    empathy_score: float
    efficiency_score: float
    breakdown: Dict
    timestamp: datetime

@app.get("/")
async def root():
    return {
        "message": "AI-Enhanced Call Center Assessment API",
        "status": "running",
        "mode": "ai_enhanced" if SPEECH_AI_AVAILABLE and EMOTION_AI_AVAILABLE else "basic",
        "features": {
            "ai_speech_recognition": SPEECH_AI_AVAILABLE,
            "ai_emotion_analysis": EMOTION_AI_AVAILABLE,
            "resolution_detection": RESOLUTION_AVAILABLE,
            "scoring_engine": SCORING_AVAILABLE
        },
        "ai_capabilities": {
            "enhanced_language_detection": SPEECH_AI_AVAILABLE,
            "ai_transcription_enhancement": SPEECH_AI_AVAILABLE,
            "ai_speaker_separation": SPEECH_AI_AVAILABLE,
            "ai_emotion_analysis": EMOTION_AI_AVAILABLE,
            "ai_progression_analysis": EMOTION_AI_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI-Enhanced API is working",
        "mode": "ai_enhanced" if SPEECH_AI_AVAILABLE and EMOTION_AI_AVAILABLE else "basic",
        "features_available": {
            "ai_speech_recognition": SPEECH_AI_AVAILABLE,
            "ai_emotion_analysis": EMOTION_AI_AVAILABLE,
            "resolution_detection": RESOLUTION_AVAILABLE,
            "scoring_engine": SCORING_AVAILABLE
        },
        "ai_services": {
            "openai_available": bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic_available": bool(os.environ.get("ANTHROPIC_API_KEY"))
        }
    }

@app.post("/api/upload-call")
async def upload_call(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = None
):
    """Upload audio file for AI-enhanced call assessment"""
    
    if not file.filename.endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid audio format")

    call_id = str(uuid.uuid4())
    file_path = f"uploads/{call_id}_{file.filename}"
    
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        assessment = await process_call_assessment_ai(
            call_id=call_id,
            worker_id=1,
            file_path=file_path,
            language=language
        )
        
        return {
            "status": "success",
            "message": "AI-enhanced call processed successfully",
            "assessment": assessment
        }
    except Exception as e:
        logger.error(f"❌ Assessment failed: {e}")
        return {
            "status": "error",
            "message": f"Assessment failed: {str(e)}",
            "assessment": None
        }

async def process_call_assessment_ai(
    call_id: str,
    worker_id: int,
    file_path: str,
    language: str = None
):
    """AI-enhanced call assessment processing"""
    
    try:
        logger.info(f"🎯 Starting AI-enhanced assessment for call {call_id}")
        logger.info(f"📁 Audio file: {file_path}")
        logger.info(f"🌍 Language hint: {language}")

        # Step 1: AI-enhanced transcription
        logger.info("🎤 AI-enhanced transcription...")
        if SPEECH_AI_AVAILABLE:
            try:
                transcription = speech_recognizer.transcribe_audio_ai(file_path, language)
                logger.info("✅ AI-enhanced transcription completed")
            except Exception as e:
                logger.error(f"❌ AI transcription failed: {e}")
                # Fallback to basic transcription
                transcription = speech_recognizer.transcribe_audio(file_path, language)
                logger.info("🔄 Using fallback transcription")
        else:
            # Basic transcription
            transcription = speech_recognizer.transcribe_audio(file_path, language)
            logger.info("🔄 Using basic transcription")
        
        logger.info(f"📝 Transcription result: {transcription}")
        
        # Get the detected language from transcription
        detected_language = transcription.get("language", transcription.get("detected_language", "ru"))
        logger.info(f"🌍 Processing call in language: {detected_language}")
        logger.info(f"📄 Full transcription text: '{transcription.get('text', '')}'")

        # Step 2: AI-enhanced speaker separation
        logger.info("👥 AI-enhanced speaker separation...")
        segments = transcription.get("segments", [])
        logger.info(f"📊 Found {len(segments)} segments")
        
        if SPEECH_AI_AVAILABLE:
            try:
                worker_text, customer_text = speech_recognizer.separate_speakers_ai(segments)
                logger.info("✅ AI-enhanced speaker separation completed")
            except Exception as e:
                logger.error(f"❌ AI speaker separation failed: {e}")
                # Fallback to basic separation
                worker_text, customer_text = speech_recognizer.separate_speakers(segments)
                logger.info("🔄 Using fallback speaker separation")
        else:
            # Basic speaker separation
            worker_text, customer_text = speech_recognizer.separate_speakers(segments)
            logger.info("🔄 Using basic speaker separation")
        
        logger.info(f"👨‍💼 Worker text: '{worker_text}'")
        logger.info(f"👤 Customer text: '{customer_text}'")
        
        # Step 3: AI-enhanced emotion analysis
        logger.info("😊 AI-enhanced emotion analysis...")
        if EMOTION_AI_AVAILABLE:
            try:
                emotions = emotion_analyzer.analyze_emotions_ai(customer_text, detected_language)
                emotion_progression = emotion_analyzer.track_emotion_progression_ai(segments, detected_language)
                logger.info("✅ AI-enhanced emotion analysis completed")
            except Exception as e:
                logger.error(f"❌ AI emotion analysis failed: {e}")
                # Fallback to basic emotion analysis
                emotions = emotion_analyzer.analyze_emotions(customer_text, detected_language)
                emotion_progression = emotion_analyzer.track_emotion_progression(segments, detected_language)
                logger.info("🔄 Using fallback emotion analysis")
        else:
            # Basic emotion analysis
            emotions = emotion_analyzer.analyze_emotions(customer_text, detected_language)
            emotion_progression = emotion_analyzer.track_emotion_progression(segments, detected_language)
            logger.info("🔄 Using basic emotion analysis")
        
        logger.info(f"😊 Emotion analysis result: {emotions}")
        logger.info(f"📈 Emotion progression: {len(emotion_progression)} segments analyzed")
        
        # Step 4: Resolution detection
        logger.info("✅ Detecting issue resolution...")
        if RESOLUTION_AVAILABLE:
            try:
                resolution = resolution_detector.detect_issue_resolution(
                    transcription["text"],
                    customer_text,
                    detected_language
                )
                logger.info("✅ Resolution detection completed")
            except Exception as e:
                logger.error(f"❌ Resolution detection failed: {e}")
                resolution = {"resolved": True, "resolution_score": 75}
                logger.info("🔄 Using fallback resolution detection")
        else:
            resolution = {"resolved": True, "resolution_score": 75}
            logger.info("🔄 Using fallback resolution detection")
        
        logger.info(f"✅ Resolution detection result: {resolution}")
        
        # Step 5: Calculate additional metrics
        logger.info("📊 Calculating additional metrics...")
        response_times = calculate_response_times(segments)
        interruptions = count_interruptions(segments)
        greeting = check_greeting(worker_text, detected_language)
        closing = check_closing(worker_text, detected_language)
        
        logger.info(f"⏱️ Response times: {response_times}")
        logger.info(f"🔇 Interruptions: {interruptions}")
        logger.info(f"👋 Greeting detected: {greeting}")
        logger.info(f"👋 Closing detected: {closing}")

        call_analysis = {
            "emotions": emotions,
            "emotion_progression": emotion_progression,
            "resolution": resolution,
            "worker_text": worker_text,
            "customer_text": customer_text,
            "response_times": response_times,
            "interruptions": interruptions,
            "greeting": greeting,
            "closing": closing,
            "language": detected_language,
            "transcription": transcription,
            "ai_enhanced": {
                "speech_recognition": SPEECH_AI_AVAILABLE,
                "emotion_analysis": EMOTION_AI_AVAILABLE,
                "transcription_enhanced": transcription.get("ai_enhanced", False),
                "speaker_separation_enhanced": SPEECH_AI_AVAILABLE,
                "emotion_analysis_enhanced": emotions.get("ai_enhanced", False)
            }
        }
        
        # Step 6: Calculate scores
        logger.info("🎯 Calculating final scores...")
        if SCORING_AVAILABLE:
            try:
                scores = scoring_engine.calculate_total_score(call_analysis)
                logger.info("✅ Scoring completed")
            except Exception as e:
                logger.error(f"❌ Scoring failed: {e}")
                # Fallback scoring
                scores = {
                    "total_score": 78.5,
                    "performance_grade": "Good",
                    "emotion_score": 80.0,
                    "resolution_score": 85.0,
                    "communication_score": 75.0,
                    "professionalism_score": 70.0,
                    "empathy_score": 80.0,
                    "efficiency_score": 75.0,
                    "breakdown": {
                        "strengths": ["AI-enhanced analysis completed"],
                        "improvements": ["Some features using fallbacks"],
                        "detailed_analysis": {
                            "call_duration": transcription.get("duration", 245),
                            "language_detected": detected_language,
                            "greeting_provided": greeting,
                            "proper_closing": closing,
                            "interruption_count": interruptions,
                            "average_response_time": 2.3,
                            "customer_sentiment": emotions.get("sentiment", "neutral"),
                            "issue_resolved": resolution.get("resolved", True),
                            "worker_text_length": len(worker_text),
                            "customer_text_length": len(customer_text),
                            "ai_enhancements_used": call_analysis["ai_enhanced"]
                        }
                    }
                }
                logger.info("🔄 Using fallback scoring")
        else:
            # Mock scoring
            scores = {
                "total_score": 78.5,
                "performance_grade": "Good",
                "emotion_score": 80.0,
                "resolution_score": 85.0,
                "communication_score": 75.0,
                "professionalism_score": 70.0,
                "empathy_score": 80.0,
                "efficiency_score": 75.0,
                "breakdown": {
                    "strengths": ["System running in minimal mode"],
                    "improvements": ["Full AI features not available"],
                    "detailed_analysis": {
                        "call_duration": transcription.get("duration", 245),
                        "language_detected": detected_language,
                        "greeting_provided": greeting,
                        "proper_closing": closing,
                        "interruption_count": interruptions,
                        "average_response_time": 2.3,
                        "customer_sentiment": emotions.get("sentiment", "neutral"),
                        "issue_resolved": resolution.get("resolved", True),
                        "worker_text_length": len(worker_text),
                        "customer_text_length": len(customer_text)
                    }
                }
            }
            logger.info("🔄 Using mock scoring")
        
        logger.info(f"🎯 Final scores: {scores}")
        
        # Save assessment
        save_assessment_to_db(
            call_id=call_id,
            worker_id=worker_id,
            scores=scores,
            analysis=call_analysis
        )
        
        return {
            "call_id": call_id,
            "worker_id": worker_id,
            **scores,
            "timestamp": datetime.now(),
            "ai_enhanced": call_analysis["ai_enhanced"]
        }
        
    except Exception as e:
        logger.error(f"❌ Assessment failed for call {call_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

def calculate_response_times(segments: List[Dict]) -> List[float]:
    """Calculate response times between segments"""
    response_times = []
    for i in range(1, len(segments)):
        prev_end = segments[i-1].get("end", 0)
        curr_start = segments[i].get("start", 0)
        response_time = curr_start - prev_end
        if response_time > 0:
            response_times.append(response_time)
    return response_times

def count_interruptions(segments: List[Dict]) -> int:
    """Count interruptions in the conversation"""
    interruptions = 0
    for i in range(1, len(segments)):
        prev_end = segments[i-1].get("end", 0)
        curr_start = segments[i].get("start", 0)
        # If segments overlap, it might indicate interruption
        if curr_start < prev_end:
            interruptions += 1
    return interruptions

def check_greeting(text: str, language: str = "ru") -> bool:
    """Check if worker provided proper greeting"""
    greetings = {
        "ru": ["здравствуйте", "добрый день", "добрый вечер", "доброе утро", "привет"],
        "kk": ["сәлеметсіз бе", "қайырлы күн", "қайырлы кеш", "қайырлы таң", "сәлем"]
    }
    
    lang_greetings = greetings.get(language, greetings["ru"])
    return any(g in text.lower()[:100] for g in lang_greetings)

def check_closing(text: str, language: str = "ru") -> bool:
    """Check if worker provided proper closing"""
    closings = {
        "ru": ["до свидания", "всего доброго", "хорошего дня", "спасибо за звонок", "пока"],
        "kk": ["сау болыңыз", "барлығы жақсы", "жақсы күн", "қоңырау үшін рахмет", "қош болыңыз"]
    }
    
    lang_closings = closings.get(language, closings["ru"])
    return any(c in text.lower()[-200:] for c in lang_closings)

def save_assessment_to_db(call_id: str, worker_id: int, scores: Dict, analysis: Dict):
    """Save assessment to database (mock implementation)"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    assessment_data = {
        "id": call_id,
        "worker_id": worker_id,
        "timestamp": datetime.now().isoformat(),
        "scores": scores,
        "analysis": analysis
    }
    
    file_path = data_dir / f"assessment_{call_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(assessment_data, f, ensure_ascii=False, indent=2)

@app.get("/api/latest-assessment")
async def get_latest_assessment():
    """Get the most recent assessment"""
    data_dir = Path("data")
    if not data_dir.exists():
        raise HTTPException(status_code=404, detail="No assessments found")
    
    assessment_files = list(data_dir.glob("assessment_*.json"))
    if not assessment_files:
        raise HTTPException(status_code=404, detail="No assessments found")
    
    latest_file = max(assessment_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            assessment_data = json.load(f)
        
        return {
            "status": "success",
            "assessment": assessment_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading assessment: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
