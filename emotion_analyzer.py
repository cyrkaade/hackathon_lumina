
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict

class EmotionAnalyzer:
    def __init__(self):
        self.emotion_classifier = None
        self.sentiment_model = None
        self.sentiment_tokenizer = None
        
    def _load_models(self, language: str = "ru"):
        if self.emotion_classifier is None:
            try:
                # Use a smaller, more efficient model for all languages
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="cardiffnlp/twitter-roberta-base-emotion",
                    device=0 if torch.cuda.is_available() else -1
                )
                print(f"✅ Loaded efficient sentiment model for {language} language")
            except Exception as e:
                print(f"⚠️ Sentiment model failed: {e}")
                self.emotion_classifier = None

        if self.sentiment_model is None:
            try:
                # Use a smaller, more efficient model for all languages
                self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                    "cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                    "cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                print(f"✅ Loaded efficient sentiment tokenizer for {language} language")
            except Exception as e:
                print(f"⚠️ Sentiment tokenizer failed: {e}")
                self.sentiment_model = None
                self.sentiment_tokenizer = None
        
    def analyze_emotions(self, text: str, language: str = "ru") -> Dict:
        print(f"😊 Analyzing emotions for text: '{text[:100]}...' in language: {language}")
        
        if not text or not text.strip():
            print("⚠️ Empty text provided for emotion analysis")
            return {
                "emotions": [{"label": "neutral", "score": 0.5}],
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "language": language
            }
        
        # First try keyword-based analysis (more reliable for Russian/Kazakh)
        print("🔍 Running keyword-based sentiment analysis...")
        keyword_sentiment = self._analyze_sentiment_keywords(text, language)
        print(f"🔍 Keyword analysis result: {keyword_sentiment}")
        
        self._load_models(language)
        
        # Try ML model analysis if available
        if self.emotion_classifier is not None:
            try:
                emotions = self.emotion_classifier(text)
                ml_sentiment = self._extract_sentiment_from_emotions(emotions)
                
                # Combine keyword and ML analysis
                final_sentiment = self._combine_sentiment_analysis(keyword_sentiment, ml_sentiment)
                
                return {
                    "emotions": emotions,
                    "sentiment": final_sentiment["sentiment"],
                    "sentiment_confidence": final_sentiment["confidence"],
                    "language": language,
                    "analysis_method": "ml_keyword_combined"
                }
            except Exception as e:
                print(f"ML emotion analysis failed: {e}")
        
        # Fallback to keyword-based analysis
        return {
            "emotions": [{"label": keyword_sentiment["sentiment"], "score": keyword_sentiment["confidence"]}],
            "sentiment": keyword_sentiment["sentiment"],
            "sentiment_confidence": keyword_sentiment["confidence"],
            "language": language,
            "analysis_method": "keyword_based"
        }
    
    def _analyze_sentiment_keywords(self, text: str, language: str = "ru") -> Dict:
        """Analyze sentiment using keyword matching"""
        text_lower = text.lower()
        
        positive_keywords = {
            "ru": ["спасибо", "хорошо", "отлично", "понятно", "помогли", "решено", "благодарю", "доволен"],
            "kk": ["рахмет", "жақсы", "керемет", "түсіндім", "көмектесті", "шешілді", "ризамын", "қуанышты"]
        }
        
        negative_keywords = {
            "ru": ["плохо", "ужасно", "не работает", "проблема", "злой", "недоволен", "разочарован", "бесполезно"],
            "kk": ["жаман", "қорқынышты", "жұмыс істемейді", "мәселе", "ашулы", "ризасыз", "көңілі толмаған", "пайдасыз"]
        }
        
        lang_keywords = positive_keywords.get(language, positive_keywords["ru"])
        lang_negative = negative_keywords.get(language, negative_keywords["ru"])
        
        positive_count = sum(1 for word in lang_keywords if word in text_lower)
        negative_count = sum(1 for word in lang_negative if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count * 0.1))
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {"sentiment": sentiment, "confidence": confidence}
    
    def _extract_sentiment_from_emotions(self, emotions: list) -> Dict:
        """Extract sentiment from ML emotion results"""
        if not emotions:
            return {"sentiment": "neutral", "confidence": 0.5}
        
        # Get the highest scoring emotion
        top_emotion = max(emotions, key=lambda x: x.get("score", 0))
        emotion_label = top_emotion.get("label", "").lower()
        confidence = top_emotion.get("score", 0.5)
        
        # Map emotion labels to sentiment
        if any(word in emotion_label for word in ["positive", "joy", "happy", "satisfied"]):
            sentiment = "positive"
        elif any(word in emotion_label for word in ["negative", "anger", "sad", "frustrated", "disappointed"]):
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {"sentiment": sentiment, "confidence": confidence}
    
    def _combine_sentiment_analysis(self, keyword_result: Dict, ml_result: Dict) -> Dict:
        """Combine keyword and ML sentiment analysis"""
        # Weight keyword analysis more heavily for Russian/Kazakh
        keyword_weight = 0.7
        ml_weight = 0.3
        
        if keyword_result["sentiment"] == ml_result["sentiment"]:
            # Both agree
            confidence = (keyword_result["confidence"] * keyword_weight + 
                         ml_result["confidence"] * ml_weight)
            return {"sentiment": keyword_result["sentiment"], "confidence": confidence}
        else:
            # They disagree, prefer keyword analysis
            return keyword_result
    
    def track_emotion_progression(self, segments: list, language: str = "ru") -> list:
        emotion_timeline = []
        
        for segment in segments:
            emotions = self.analyze_emotions(segment["text"], language)
            emotion_timeline.append({
                "timestamp": segment["start"],
                "emotions": emotions,
                "text_snippet": segment["text"][:100]
            })
        
        return emotion_timeline