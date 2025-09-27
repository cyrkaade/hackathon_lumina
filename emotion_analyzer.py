
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
        self._load_models(language)
        
        # Fallback emotion analysis if models fail to load
        if self.emotion_classifier is None:
            return {
                "emotions": [{"label": "neutral", "score": 0.5}],
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "language": language
            }
        
        emotions = self.emotion_classifier(text)

        # Fallback sentiment analysis if tokenizer/model fails
        if self.sentiment_model is None or self.sentiment_tokenizer is None:
            return {
                "emotions": emotions,
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "language": language
            }

        inputs = self.sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.sentiment_model(**inputs)
        sentiment_scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        sentiment_labels = ['negative', 'neutral', 'positive']
        sentiment = sentiment_labels[torch.argmax(sentiment_scores)]
        
        return {
            "emotions": emotions,
            "sentiment": sentiment,
            "sentiment_confidence": float(torch.max(sentiment_scores)),
            "language": language
        }
    
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