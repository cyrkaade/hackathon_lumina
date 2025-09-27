
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os

app = FastAPI(title="Call Center Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


speech_recognizer = SpeechRecognizer()
emotion_analyzer = EmotionAnalyzer()
resolution_detector = ResolutionDetector()
scoring_engine = ScoringEngine()


class AssessmentRequest(BaseModel):
    worker_id: int
    call_id: str
    language: str = "ru" 

class AssessmentResponse(BaseModel):
    call_id: str
    worker_id: int
    total_score: float
    emotion_score: float
    resolution_score: float
    communication_score: float
    professionalism_score: float
    recommendations: List[str]
    timestamp: datetime

class WorkerPerformance(BaseModel):
    worker_id: int
    average_score: float
    total_calls: int
    trend: str
    recent_assessments: List[AssessmentResponse]


@app.post("/api/upload-call")
async def upload_call(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    worker_id: int = None,
    language: str = "ru"
):

    

    if not file.filename.endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid audio format")

    call_id = str(uuid.uuid4())
    file_path = f"uploads/{call_id}_{file.filename}"
    
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    

    background_tasks.add_task(
        process_call_assessment,
        call_id=call_id,
        worker_id=worker_id,
        file_path=file_path,
        language=language
    )
    
    return {
        "call_id": call_id,
        "status": "processing",
        "message": "Call uploaded and queued for assessment"
    }

@app.post("/api/assess-call/{call_id}")
async def assess_call(call_id: str, language: str = "ru"):
    """Trigger assessment for a specific call"""

    call = get_call_from_db(call_id)
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    assessment = await process_call_assessment(
        call_id=call["id"],
        worker_id=call["worker_id"],
        file_path=call["audio_file_path"],
        language=language
    )
    
    return assessment

@app.get("/api/assessment/{call_id}")
async def get_assessment(call_id: str):
    """Get assessment results for a call"""
    
    assessment = get_assessment_from_db(call_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return AssessmentResponse(**assessment)

@app.get("/api/worker/{worker_id}/performance")
async def get_worker_performance(
    worker_id: int,
    days: int = 30
):

    
    performance = get_worker_performance_from_db(worker_id, days)
    
    if not performance:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return WorkerPerformance(**performance)

@app.get("/api/workers/rankings")
async def get_workers_rankings(
    department: Optional[str] = None,
    limit: int = 10
):

    
    rankings = get_rankings_from_db(department, limit)
    
    return {
        "rankings": rankings,
        "period": "last_30_days",
        "department": department or "all"
    }


async def process_call_assessment(
    call_id: str,
    worker_id: int,
    file_path: str,
    language: str
):

    
    try:

        transcription = speech_recognizer.transcribe_audio(file_path, language)
        

        worker_text, customer_text = speech_recognizer.separate_speakers(
            transcription["segments"]
        )
        

        emotions = emotion_analyzer.analyze_emotions(customer_text)
        emotion_progression = emotion_analyzer.track_emotion_progression(
            transcription["segments"]
        )
        

        resolution = resolution_detector.detect_issue_resolution(
            transcription["text"],
            customer_text
        )
        

        call_analysis = {
            "emotions": emotions,
            "emotion_progression": emotion_progression,
            "resolution": resolution,
            "worker_text": worker_text,
            "customer_text": customer_text,
            "response_times": calculate_response_times(transcription["segments"]),
            "interruptions": count_interruptions(transcription["segments"]),
            "greeting": check_greeting(worker_text),
            "closing": check_closing(worker_text)
        }
        
        scores = scoring_engine.calculate_total_score(call_analysis)
        

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

        print(f"Assessment failed for call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_response_times(segments: List) -> List[float]:
    """Calculate response times between speakers"""
    return []

def count_interruptions(segments: List) -> int:
    """Count speech interruptions"""

    return 0

def check_greeting(text: str) -> bool:

    greetings = ["здравствуйте", "добрый день", "добрый вечер", "доброе утро"]
    return any(g in text.lower()[:100] for g in greetings)

def check_closing(text: str) -> bool:

    closings = ["до свидания", "всего доброго", "хорошего дня", "спасибо за звонок"]
    return any(c in text.lower()[-200:] for c in closings)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)