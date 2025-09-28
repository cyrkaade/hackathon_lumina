from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import os
import json
from pathlib import Path

# Try to import custom modules with error handling
try:
    from speech_recognition import SpeechRecognizer
    SPEECH_AVAILABLE = True
except ImportError:
    print("⚠️ SpeechRecognizer not available - using mock")
    SPEECH_AVAILABLE = False
    class SpeechRecognizer:
        def transcribe_audio(self, *args, **kwargs):
            return {"text": "Mock transcription for testing", "segments": [], "language": "ru"}
        def separate_speakers(self, *args, **kwargs):
            return "Mock worker text", "Mock customer text"

try:
    from emotion_analyzer import EmotionAnalyzer
    EMOTION_AVAILABLE = True
except ImportError:
    print("⚠️ EmotionAnalyzer not available - using mock")
    EMOTION_AVAILABLE = False
    class EmotionAnalyzer:
        def analyze_emotions(self, *args, **kwargs):
            return {"sentiment": "neutral", "sentiment_confidence": 0.5}
        def track_emotion_progression(self, *args, **kwargs):
            return []

try:
    from resolution_detector import ResolutionDetector
    RESOLUTION_AVAILABLE = True
except ImportError:
    print("⚠️ ResolutionDetector not available - using mock")
    RESOLUTION_AVAILABLE = False
    class ResolutionDetector:
        def detect_issue_resolution(self, *args, **kwargs):
            return {"resolved": True, "resolution_score": 75}

try:
    from scoring_engine import ScoringEngine
    SCORING_AVAILABLE = True
except ImportError:
    print("⚠️ ScoringEngine not available - using mock")
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

app = FastAPI(title="Call Center Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
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

class WorkerPerformance(BaseModel):
    worker_id: int
    average_score: float
    total_calls: int
    performance_trend: str
    period: str

@app.get("/")
async def root():
    return {
        "message": "Call Center Assessment API",
        "status": "running",
        "mode": "minimal" if not all([SPEECH_AVAILABLE, EMOTION_AVAILABLE, RESOLUTION_AVAILABLE, SCORING_AVAILABLE]) else "full",
        "features": {
            "speech_recognition": SPEECH_AVAILABLE,
            "emotion_analysis": EMOTION_AVAILABLE,
            "resolution_detection": RESOLUTION_AVAILABLE,
            "scoring_engine": SCORING_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is working",
        "mode": "minimal" if not all([SPEECH_AVAILABLE, EMOTION_AVAILABLE, RESOLUTION_AVAILABLE, SCORING_AVAILABLE]) else "full",
        "features_available": {
            "speech_recognition": SPEECH_AVAILABLE,
            "emotion_analysis": EMOTION_AVAILABLE,
            "resolution_detection": RESOLUTION_AVAILABLE,
            "scoring_engine": SCORING_AVAILABLE
        }
    }

@app.post("/api/upload-call")
async def upload_call(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = None
):
    """Upload audio file for call assessment"""
    
    if not file.filename.endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid audio format")

    call_id = str(uuid.uuid4())
    file_path = f"uploads/{call_id}_{file.filename}"
    
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        assessment = await process_call_assessment(
            call_id=call_id,
            worker_id=1,
            file_path=file_path,
            language=language
        )
        
        return {
            "status": "success",
            "message": "Call processed successfully",
            "assessment": assessment
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Assessment failed: {str(e)}",
            "assessment": None
        }

async def process_call_assessment(
    call_id: str,
    worker_id: int,
    file_path: str,
    language: str = None
):
    """Process call assessment with fallback for missing features"""
    
    try:
        print(f"🎯 Starting assessment for call {call_id}")
        print(f"📁 Audio file: {file_path}")
        print(f"🌍 Language hint: {language}")

        # Step 1: Transcribe audio (with fallback)
        print("🎤 Transcribing audio...")
        if SPEECH_AVAILABLE:
            transcription = speech_recognizer.transcribe_audio(file_path, language)
        else:
            # Mock transcription for testing
            transcription = {
                "text": "Здравствуйте! У меня проблема с картой. Понимаю, помогу решить. Спасибо!",
                "segments": [
                    {"text": "Здравствуйте! У меня проблема с картой.", "start": 0, "end": 3},
                    {"text": "Понимаю, помогу решить.", "start": 3, "end": 6},
                    {"text": "Спасибо!", "start": 6, "end": 8}
                ],
                "language": "ru",
                "detected_language": "ru"
            }
            print("🔄 Using mock transcription (AI features not available)")
        
        print(f"📝 Transcription result: {transcription}")
        
        # Get the detected language from transcription
        detected_language = transcription.get("language", transcription.get("detected_language", "ru"))
        print(f"🌍 Processing call in language: {detected_language}")
        print(f"📄 Full transcription text: '{transcription.get('text', '')}'")

        # Step 2: Separate speakers (with fallback)
        print("👥 Separating speakers...")
        segments = transcription.get("segments", [])
        print(f"📊 Found {len(segments)} segments")
        
        if SPEECH_AVAILABLE:
            worker_text, customer_text = speech_recognizer.separate_speakers(segments)
        else:
            # Mock speaker separation
            full_text = transcription.get("text", "")
            mid_point = len(full_text) // 2
            worker_text = full_text[:mid_point]
            customer_text = full_text[mid_point:]
            print("🔄 Using mock speaker separation")
        
        print(f"👨‍💼 Worker text: '{worker_text}'")
        print(f"👤 Customer text: '{customer_text}'")
        
        # Step 3: Analyze emotions (with fallback)
        print("😊 Analyzing emotions...")
        if EMOTION_AVAILABLE:
            emotions = emotion_analyzer.analyze_emotions(customer_text, detected_language)
            emotion_progression = emotion_analyzer.track_emotion_progression(segments, detected_language)
        else:
            # Mock emotion analysis
            emotions = {"sentiment": "positive", "sentiment_confidence": 0.8}
            emotion_progression = []
            print("🔄 Using mock emotion analysis")
        
        print(f"😊 Emotion analysis result: {emotions}")
        print(f"📈 Emotion progression: {len(emotion_progression)} segments analyzed")
        
        # Step 4: Detect resolution (with fallback)
        print("✅ Detecting issue resolution...")
        if RESOLUTION_AVAILABLE:
            resolution = resolution_detector.detect_issue_resolution(
                transcription["text"],
                customer_text,
                detected_language
            )
        else:
            # Mock resolution detection
            resolution = {"resolved": True, "resolution_score": 85}
            print("🔄 Using mock resolution detection")
        
        print(f"✅ Resolution detection result: {resolution}")
        
        # Step 5: Calculate additional metrics
        print("📊 Calculating additional metrics...")
        response_times = calculate_response_times(segments)
        interruptions = count_interruptions(segments)
        greeting = check_greeting(worker_text, detected_language)
        closing = check_closing(worker_text, detected_language)
        
        print(f"⏱️ Response times: {response_times}")
        print(f"🔇 Interruptions: {interruptions}")
        print(f"👋 Greeting detected: {greeting}")
        print(f"👋 Closing detected: {closing}")

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
            "transcription": transcription
        }
        
        # Step 6: Calculate scores (with fallback)
        print("🎯 Calculating final scores...")
        if SCORING_AVAILABLE:
            scores = scoring_engine.calculate_total_score(call_analysis)
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
                    "improvements": ["Full AI features not available - upgrade requirements.txt"],
                    "detailed_analysis": {
                        "call_duration": 245,
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
            print("🔄 Using mock scoring")
        
        print(f"🎯 Final scores: {scores}")
        
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
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        print(f"❌ Assessment failed for call {call_id}: {str(e)}")
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
