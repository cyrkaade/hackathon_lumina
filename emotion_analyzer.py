
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

class EmotionAnalyzer:
    def __init__(self):

        self.emotion_classifier = pipeline(
            "text-classification",
            model="seara/rubert-base-cased-russian-emotion",
            device=0 if torch.cuda.is_available() else -1
        )
        

        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
            "blanchefort/rubert-base-cased-sentiment"
        )
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
            "blanchefort/rubert-base-cased-sentiment"
        )
        
    def analyze_emotions(self, text: str) -> Dict:
        """Analyze emotional state from text"""
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
        """Track how emotions change throughout the call"""
        emotion_timeline = []
        
        for segment in segments:
            emotions = self.analyze_emotions(segment["text"])
            emotion_timeline.append({
                "timestamp": segment["start"],
                "emotions": emotions,
                "text_snippet": segment["text"][:100]
            })
        
        return emotion_timeline