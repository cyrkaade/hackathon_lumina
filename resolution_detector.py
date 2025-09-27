
from transformers import pipeline
import re
from typing import Dict
import torch

class ResolutionDetector:
    def __init__(self):
        self.qa_pipeline = None
        self.resolution_keywords = {
            "ru": {
                "resolved": ["решено", "решил", "помог", "исправлено", "готово", "все в порядке", "проблема решена"],
                "unresolved": ["не решено", "не помогло", "проблема осталась", "не работает", "не получилось"],
                "partial": ["частично", "попробую", "посмотрим", "возможно", "попробуем"]
            },
            "kk": {
                "resolved": ["шешілді", "шештім", "көмектестім", "түзетілді", "дайын", "барлығы дұрыс", "мәселе шешілді"],
                "unresolved": ["шешілмеді", "көмектеспеді", "мәселе қалды", "жұмыс істемейді", "болмады"],
                "partial": ["жартылай", "көрейін", "қараймыз", "мүмкін", "көрейік"]
            }
        }
        
    def _load_qa_model(self):
        if self.qa_pipeline is None:
            try:
                # Use a smaller, more efficient model
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model="distilbert-base-cased-distilled-squad",
                    device=0 if torch.cuda.is_available() else -1
                )
                print("✅ Loaded efficient QA model successfully")
            except Exception as e:
                print(f"⚠️ QA model failed: {e}")
                # Fallback to even smaller model or disable QA
                self.qa_pipeline = None
        
    def detect_issue_resolution(self, conversation: str, customer_text: str, language: str = "ru") -> Dict:
        resolution_status = self._check_keywords(customer_text, language)

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
            "final_sentiment": final_sentiment,
            "language": language
        }
    
    def _check_keywords(self, text: str, language: str = "ru") -> str:
        text_lower = text.lower()
        
        # Get keywords for the specific language
        lang_keywords = self.resolution_keywords.get(language, self.resolution_keywords["ru"])
        
        for status, keywords in lang_keywords.items():
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