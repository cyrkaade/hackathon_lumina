
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict

class EmotionAnalyzer:
    def __init__(self):
        try:
            self.emotion_classifier = pipeline(
                "text-classification",
                model="blanchefort/rubert-base-cased-sentiment",
                device=0 if torch.cuda.is_available() else -1
            )
            print("✅ Loaded Russian sentiment model successfully")
        except Exception as e:
            print(f"⚠️ Russian model failed, using English fallback: {e}")
            self.emotion_classifier = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-emotion",
                device=0 if torch.cuda.is_available() else -1
            )

        try:
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                "blanchefort/rubert-base-cased-sentiment"
            )
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                "blanchefort/rubert-base-cased-sentiment"
            )
            print("✅ Loaded Russian sentiment tokenizer successfully")
        except Exception as e:
            print(f"⚠️ Russian tokenizer failed, using English fallback: {e}")
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                "cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                "cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        
    def analyze_emotions(self, text: str) -> Dict:
        emotions = self.emotion_classifier(text)

        inputs = self.sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.sentiment_model(**inputs)
        sentiment_scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        sentiment_labels = ['negative', 'neutral', 'positive']
        sentiment = sentiment_labels[torch.argmax(sentiment_scores)]
        
        return {
            "emotions": emotions,
            "sentiment": sentiment,
            "sentiment_confidence": float(torch.max(sentiment_scores))
        }
    
    def track_emotion_progression(self, segments: list) -> list:
        emotion_timeline = []
        
        for segment in segments:
            emotions = self.analyze_emotions(segment["text"])
            emotion_timeline.append({
                "timestamp": segment["start"],
                "emotions": emotions,
                "text_snippet": segment["text"][:100]
            })
        
        return emotion_timeline