
from transformers import pipeline
import re
from typing import Dict
import torch

class ResolutionDetector:
    def __init__(self):
        try:
            self.qa_pipeline = pipeline(
                "question-answering",
                model="DeepPavlov/rubert-base-cased-squad",
                device=0 if torch.cuda.is_available() else -1
            )
            print("✅ Loaded Russian QA model successfully")
        except Exception as e:
            print(f"⚠️ Russian QA model failed, using English fallback: {e}")
            self.qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                device=0 if torch.cuda.is_available() else -1
            )

        self.resolution_keywords = {
            "resolved": ["решено", "решил", "помог", "исправлено", "готово"],
            "unresolved": ["не решено", "не помогло", "проблема осталась", "не работает"],
            "partial": ["частично", "попробую", "посмотрим", "возможно"]
        }
        
    def detect_issue_resolution(self, conversation: str, customer_text: str) -> Dict:


        resolution_status = self._check_keywords(customer_text)

        customer_sentences = customer_text.split('.')
        final_sentiment = self._analyze_final_sentiment(customer_sentences[-3:])

        resolution_score = self._calculate_resolution_score(
            resolution_status,
            final_sentiment
        )
        
        return {
            "resolved": resolution_score > 70,
            "resolution_score": resolution_score,
            "status": resolution_status,
            "final_sentiment": final_sentiment
        }
    
    def _check_keywords(self, text: str) -> str:
        text_lower = text.lower()
        
        for status, keywords in self.resolution_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return status
        
        return "unclear"
    
    def _analyze_final_sentiment(self, sentences: list) -> str:
        return "neutral"
    
    def _calculate_resolution_score(self, status: str, sentiment: str) -> float:
        base_scores = {
            "resolved": 90,
            "partial": 60,
            "unresolved": 20,
            "unclear": 50
        }
        
        sentiment_modifiers = {
            "positive": 10,
            "neutral": 0,
            "negative": -10
        }
        
        score = base_scores.get(status, 50) + sentiment_modifiers.get(sentiment, 0)
        return max(0, min(100, score))