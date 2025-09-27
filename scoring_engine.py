
from typing import Dict, List
import numpy as np

class ScoringEngine:
    def __init__(self):
        self.weights = {
            "emotion": 0.25,
            "resolution": 0.35,
            "communication": 0.20,
            "professionalism": 0.20
        }
        
    def calculate_total_score(self, call_analysis: Dict) -> Dict:


        emotion_score = self._calculate_emotion_score(
            call_analysis["emotions"],
            call_analysis["emotion_progression"]
        )

        resolution_score = call_analysis["resolution"]["resolution_score"]

        communication_score = self._calculate_communication_score(
            call_analysis["worker_text"],
            call_analysis["response_times"],
            call_analysis["interruptions"]
        )

        professionalism_score = self._calculate_professionalism_score(
            call_analysis["worker_text"],
            call_analysis["greeting"],
            call_analysis["closing"]
        )
        
 
        total_score = (
            emotion_score * self.weights["emotion"] +
            resolution_score * self.weights["resolution"] +
            communication_score * self.weights["communication"] +
            professionalism_score * self.weights["professionalism"]
        )
        
        return {
            "total_score": round(total_score, 2),
            "emotion_score": round(emotion_score, 2),
            "resolution_score": round(resolution_score, 2),
            "communication_score": round(communication_score, 2),
            "professionalism_score": round(professionalism_score, 2),
            "breakdown": {
                "strengths": self._identify_strengths(locals()),
                "improvements": self._identify_improvements(locals())
            }
        }
    
    def _calculate_emotion_score(self, emotions: Dict, progression: List) -> float:


        positive_weight = 0.7
        negative_weight = -0.5
        
        score = 50
        

        if progression:
            start_emotion = progression[0]["emotions"]["sentiment"]
            end_emotion = progression[-1]["emotions"]["sentiment"]
            
            if end_emotion == "positive":
                score += 30
            elif end_emotion == "neutral" and start_emotion == "negative":
                score += 20
            elif end_emotion == "negative":
                score -= 20
        
        return max(0, min(100, score))
    
    def _calculate_communication_score(self, text: str, response_times: List, interruptions: int) -> float:

        score = 80

        score -= interruptions * 5

        avg_response_time = np.mean(response_times) if response_times else 0
        if avg_response_time > 5:
            score -= 10

        clarity_phrases = ["понимаю", "ясно", "конечно", "помогу"]
        for phrase in clarity_phrases:
            if phrase in text.lower():
                score += 2
        
        return max(0, min(100, score))
    
    def _calculate_professionalism_score(self, text: str, greeting: bool, closing: bool) -> float:

        score = 60
        
        if greeting:
            score += 15
        if closing:
            score += 15

        professional_indicators = ["здравствуйте", "спасибо", "пожалуйста", "извините"]
        unprofessional_indicators = ["блин", "черт", "дурак"]
        
        for indicator in professional_indicators:
            if indicator in text.lower():
                score += 2.5
        
        for indicator in unprofessional_indicators:
            if indicator in text.lower():
                score -= 10
        
        return max(0, min(100, score))
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        strengths = []
        if scores.get("emotion_score", 0) > 80:
            strengths.append("Excellent emotional management")
        if scores.get("resolution_score", 0) > 85:
            strengths.append("Strong problem-solving skills")
        return strengths
    
    def _identify_improvements(self, scores: Dict) -> List[str]:
        improvements = []
        if scores.get("emotion_score", 0) < 60:
            improvements.append("Work on empathy and emotional connection")
        if scores.get("communication_score", 0) < 60:
            improvements.append("Improve response time and clarity")
        return improvements