
from typing import Dict, List
import numpy as np

class ScoringEngine:
    def __init__(self):
        # Enhanced weights for comprehensive call center assessment
        self.weights = {
            "emotion": 0.25,        # Customer emotional satisfaction
            "resolution": 0.25,     # Issue resolution effectiveness  
            "communication": 0.20,  # Communication clarity and helpfulness
            "professionalism": 0.15, # Professional behavior and courtesy
            "empathy": 0.10,        # Empathy and understanding
            "efficiency": 0.05      # Call efficiency and time management
        }
        
    def calculate_total_score(self, call_analysis: Dict) -> Dict:
        """Calculate comprehensive 100-point call center worker assessment"""

        # Core assessment components
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
        
        # Additional call center specific metrics
        empathy_score = self._calculate_empathy_score(
            call_analysis["worker_text"],
            call_analysis["emotions"],
            call_analysis.get("language", "ru")
        )
        
        efficiency_score = self._calculate_efficiency_score(
            call_analysis["response_times"],
            call_analysis["interruptions"],
            call_analysis.get("transcription", {})
        )
        
        # Weighted total score (100-point scale)
        total_score = (
            emotion_score * self.weights["emotion"] +
            resolution_score * self.weights["resolution"] +
            communication_score * self.weights["communication"] +
            professionalism_score * self.weights["professionalism"] +
            empathy_score * self.weights["empathy"] +
            efficiency_score * self.weights["efficiency"]
        )
        
        # Performance grade
        performance_grade = self._get_performance_grade(total_score)
        
        return {
            "total_score": round(total_score, 1),
            "performance_grade": performance_grade,
            "emotion_score": round(emotion_score, 1),
            "resolution_score": round(resolution_score, 1),
            "communication_score": round(communication_score, 1),
            "professionalism_score": round(professionalism_score, 1),
            "empathy_score": round(empathy_score, 1),
            "efficiency_score": round(efficiency_score, 1),
            "breakdown": {
                "strengths": self._identify_strengths(locals()),
                "improvements": self._identify_improvements(locals()),
                "detailed_analysis": self._get_detailed_analysis(call_analysis, locals())
            }
        }
    
    def _calculate_emotion_score(self, emotions: Dict, progression: List) -> float:
        """Calculate emotion score based on customer satisfaction"""
        score = 50  # Base score
        
        # Get current emotion sentiment
        current_sentiment = emotions.get("sentiment", "neutral")
        sentiment_confidence = emotions.get("sentiment_confidence", 0.5)
        
        # Score based on current sentiment
        if current_sentiment == "positive":
            score += 30 * sentiment_confidence
        elif current_sentiment == "negative":
            score -= 25 * sentiment_confidence
        else:  # neutral
            score += 5 * sentiment_confidence
        
        # Analyze emotion progression if available
        if progression and len(progression) > 1:
            start_emotion = progression[0]["emotions"]["sentiment"]
            end_emotion = progression[-1]["emotions"]["sentiment"]
            
            # Bonus for improving emotions
            if start_emotion == "negative" and end_emotion == "positive":
                score += 25  # Great improvement
            elif start_emotion == "negative" and end_emotion == "neutral":
                score += 15  # Good improvement
            elif start_emotion == "neutral" and end_emotion == "positive":
                score += 10  # Some improvement
            elif start_emotion == "positive" and end_emotion == "negative":
                score -= 20  # Deterioration
            elif start_emotion == "neutral" and end_emotion == "negative":
                score -= 15  # Deterioration
        
        return max(0, min(100, score))
    
    def _calculate_communication_score(self, text: str, response_times: List, interruptions: int) -> float:
        """Calculate communication quality score"""
        score = 70  # Base score
        
        # Penalty for interruptions
        score -= interruptions * 8
        
        # Response time analysis
        if response_times:
            avg_response_time = np.mean(response_times)
            if avg_response_time > 10:  # Very slow responses
                score -= 20
            elif avg_response_time > 5:  # Slow responses
                score -= 10
            elif avg_response_time < 2:  # Very fast responses (good)
                score += 10
        else:
            # No response time data, assume moderate performance
            score -= 5

        # Check for clarity and helpful phrases
        clarity_phrases = {
            "ru": ["понимаю", "ясно", "конечно", "помогу", "разберёмся", "объясню", "покажу"],
            "kk": ["түсіндім", "анық", "әрине", "көмектесемін", "шешеміз", "түсіндіремін", "көрсетемін"]
        }
        
        clarity_bonus = 0
        for lang, phrases in clarity_phrases.items():
            for phrase in phrases:
                if phrase in text.lower():
                    clarity_bonus += 3
        
        score += min(15, clarity_bonus)  # Cap clarity bonus
        
        # Check for unclear or unhelpful phrases
        unclear_phrases = {
            "ru": ["не знаю", "не понимаю", "не могу", "не получается", "сложно"],
            "kk": ["білмеймін", "түсінбеймін", "аламын", "болмады", "қиын"]
        }
        
        unclear_penalty = 0
        for lang, phrases in unclear_phrases.items():
            for phrase in phrases:
                if phrase in text.lower():
                    unclear_penalty += 5
        
        score -= min(20, unclear_penalty)  # Cap unclear penalty
        
        return max(0, min(100, score))
    
    def _calculate_professionalism_score(self, text: str, greeting: bool, closing: bool) -> float:
        """Calculate professionalism score based on language and behavior"""
        score = 50  # Base score
        
        # Greeting and closing bonuses
        if greeting:
            score += 20
        if closing:
            score += 20
        
        # Professional language indicators
        professional_indicators = {
            "ru": ["здравствуйте", "спасибо", "пожалуйста", "извините", "благодарю", "разрешите", "позвольте"],
            "kk": ["сәлеметсіз бе", "рахмет", "өтінемін", "кешіріңіз", "ризамын", "рұқсат етіңіз", "жалдаңыз"]
        }
        
        professional_bonus = 0
        for lang, indicators in professional_indicators.items():
            for indicator in indicators:
                if indicator in text.lower():
                    professional_bonus += 3
        
        score += min(20, professional_bonus)  # Cap professional bonus
        
        # Unprofessional language penalties
        unprofessional_indicators = {
            "ru": ["блин", "черт", "дурак", "идиот", "тупой", "глупый", "бред"],
            "kk": ["құдай", "шайтан", "ақымақ", "идиот", "ақымақ", "ақылсыз", "мағынасыз"]
        }
        
        unprofessional_penalty = 0
        for lang, indicators in unprofessional_indicators.items():
            for indicator in indicators:
                if indicator in text.lower():
                    unprofessional_penalty += 15  # Heavy penalty for unprofessional language
        
        score -= min(40, unprofessional_penalty)  # Cap unprofessional penalty
        
        # Check for appropriate tone and politeness
        polite_phrases = {
            "ru": ["будьте добры", "не могли бы", "если можно", "прошу вас"],
            "kk": ["жақсы болыңыз", "ала алмайсыз ба", "мүмкін болса", "өтінемін"]
        }
        
        for lang, phrases in polite_phrases.items():
            for phrase in phrases:
                if phrase in text.lower():
                    score += 5
        
        return max(0, min(100, score))
    
    def _calculate_empathy_score(self, worker_text: str, emotions: Dict, language: str = "ru") -> float:
        """Calculate empathy score based on worker's understanding and compassion"""
        score = 60  # Base score
        
        # Empathy indicators
        empathy_phrases = {
            "ru": [
                "понимаю ваши чувства", "сочувствую", "понимаю вашу ситуацию",
                "представляю как это сложно", "понимаю ваше беспокойство",
                "извините за неудобства", "понимаю вашу проблему"
            ],
            "kk": [
                "сезімдеріңізді түсінемін", "ынталаймын", "жағдайыңызды түсінемін",
                "қаншалықты қиын екенін елестетемін", "мазасыздығыңызды түсінемін",
                "ыңғайсыздық үшін кешіріңіз", "мәселеңізді түсінемін"
            ]
        }
        
        # Check for empathy phrases
        text_lower = worker_text.lower()
        lang_phrases = empathy_phrases.get(language, empathy_phrases["ru"])
        
        empathy_bonus = 0
        for phrase in lang_phrases:
            if phrase in text_lower:
                empathy_bonus += 8
        
        score += min(25, empathy_bonus)  # Cap empathy bonus
        
        # Bonus for acknowledging customer emotions
        customer_sentiment = emotions.get("sentiment", "neutral")
        if customer_sentiment == "negative":
            # Extra points for showing empathy to upset customers
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_efficiency_score(self, response_times: List, interruptions: int, transcription: Dict) -> float:
        """Calculate efficiency score based on call management"""
        score = 70  # Base score
        
        # Response time efficiency
        if response_times:
            avg_response_time = np.mean(response_times)
            if avg_response_time < 2:  # Very fast responses
                score += 15
            elif avg_response_time < 4:  # Good response time
                score += 10
            elif avg_response_time > 8:  # Slow responses
                score -= 15
            elif avg_response_time > 5:  # Moderately slow
                score -= 10
        
        # Interruption penalty
        score -= interruptions * 5
        
        # Call length efficiency (optimal 3-8 minutes)
        call_duration = transcription.get("duration", 0)
        if 180 <= call_duration <= 480:  # 3-8 minutes
            score += 10
        elif call_duration > 600:  # Over 10 minutes
            score -= 10
        elif call_duration < 60:  # Under 1 minute (too short)
            score -= 5
        
        return max(0, min(100, score))
    
    def _get_performance_grade(self, total_score: float) -> str:
        """Get performance grade based on total score"""
        if total_score >= 90:
            return "Excellent"
        elif total_score >= 80:
            return "Good"
        elif total_score >= 70:
            return "Satisfactory"
        elif total_score >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _get_detailed_analysis(self, call_analysis: Dict, scores: Dict) -> Dict:
        """Get detailed analysis for call center management"""
        return {
            "call_duration": call_analysis.get("transcription", {}).get("duration", 0),
            "language_detected": call_analysis.get("language", "unknown"),
            "greeting_provided": call_analysis.get("greeting", False),
            "proper_closing": call_analysis.get("closing", False),
            "interruption_count": call_analysis.get("interruptions", 0),
            "average_response_time": np.mean(call_analysis.get("response_times", [0])) if call_analysis.get("response_times") else 0,
            "customer_sentiment": call_analysis.get("emotions", {}).get("sentiment", "neutral"),
            "issue_resolved": call_analysis.get("resolution", {}).get("resolved", False),
            "worker_text_length": len(call_analysis.get("worker_text", "")),
            "customer_text_length": len(call_analysis.get("customer_text", ""))
        }
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        """Identify worker strengths based on scores"""
        strengths = []
        
        if scores.get("emotion_score", 0) > 85:
            strengths.append("Excellent customer emotional management")
        elif scores.get("emotion_score", 0) > 75:
            strengths.append("Good emotional awareness")
            
        if scores.get("resolution_score", 0) > 85:
            strengths.append("Outstanding problem-solving skills")
        elif scores.get("resolution_score", 0) > 75:
            strengths.append("Effective issue resolution")
            
        if scores.get("communication_score", 0) > 85:
            strengths.append("Exceptional communication clarity")
        elif scores.get("communication_score", 0) > 75:
            strengths.append("Clear and helpful communication")
            
        if scores.get("professionalism_score", 0) > 85:
            strengths.append("Exemplary professional conduct")
        elif scores.get("professionalism_score", 0) > 75:
            strengths.append("Professional and courteous service")
            
        if scores.get("empathy_score", 0) > 85:
            strengths.append("High level of empathy and understanding")
        elif scores.get("empathy_score", 0) > 75:
            strengths.append("Good customer empathy")
            
        if scores.get("efficiency_score", 0) > 85:
            strengths.append("Excellent call efficiency")
        elif scores.get("efficiency_score", 0) > 75:
            strengths.append("Good time management")
        
        return strengths
    
    def _identify_improvements(self, scores: Dict) -> List[str]:
        """Identify areas for improvement based on scores"""
        improvements = []
        
        if scores.get("emotion_score", 0) < 60:
            improvements.append("Improve emotional connection with customers")
        elif scores.get("emotion_score", 0) < 70:
            improvements.append("Enhance customer emotional support")
            
        if scores.get("resolution_score", 0) < 60:
            improvements.append("Strengthen problem resolution techniques")
        elif scores.get("resolution_score", 0) < 70:
            improvements.append("Improve issue resolution effectiveness")
            
        if scores.get("communication_score", 0) < 60:
            improvements.append("Enhance communication clarity and helpfulness")
        elif scores.get("communication_score", 0) < 70:
            improvements.append("Improve communication effectiveness")
            
        if scores.get("professionalism_score", 0) < 60:
            improvements.append("Maintain higher professional standards")
        elif scores.get("professionalism_score", 0) < 70:
            improvements.append("Enhance professional conduct")
            
        if scores.get("empathy_score", 0) < 60:
            improvements.append("Develop better empathy and understanding")
        elif scores.get("empathy_score", 0) < 70:
            improvements.append("Show more empathy toward customers")
            
        if scores.get("efficiency_score", 0) < 60:
            improvements.append("Improve call efficiency and time management")
        elif scores.get("efficiency_score", 0) < 70:
            improvements.append("Enhance call handling efficiency")
        
        return improvements