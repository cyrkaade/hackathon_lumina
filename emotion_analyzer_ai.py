import os
import torch
from typing import Dict, List
import logging
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import openai
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AIEmotionAnalyzer:
    def __init__(self):
        self.emotion_classifier = None
        self.sentiment_model = None
        self.sentiment_tokenizer = None
        
        # Initialize AI clients
        self.openai_client = None
        self.anthropic_client = None
        self._init_ai_clients()
        
    def _init_ai_clients(self):
        """Initialize AI clients for enhanced analysis"""
        try:
            if os.environ.get("OPENAI_API_KEY"):
                self.openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                logger.info("✅ OpenAI client initialized for emotion analysis")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI client initialization failed: {e}")
            
        try:
            if os.environ.get("ANTHROPIC_API_KEY"):
                self.anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                logger.info("✅ Anthropic client initialized for emotion analysis")
        except Exception as e:
            logger.warning(f"⚠️ Anthropic client initialization failed: {e}")
        
    def _load_models(self, language: str = "ru"):
        """Load emotion analysis models"""
        if self.emotion_classifier is None:
            try:
                # Use a smaller, more efficient model for all languages
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="cardiffnlp/twitter-roberta-base-emotion",
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info(f"✅ Loaded efficient sentiment model for {language} language")
            except Exception as e:
                logger.warning(f"⚠️ Sentiment model failed: {e}")
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
                logger.info(f"✅ Loaded efficient sentiment tokenizer for {language} language")
            except Exception as e:
                logger.warning(f"⚠️ Sentiment tokenizer failed: {e}")
                self.sentiment_model = None
                self.sentiment_tokenizer = None
    
    def analyze_emotions_ai(self, text: str, language: str = "ru") -> Dict:
        """AI-enhanced emotion analysis"""
        logger.info(f"😊 AI-enhanced emotion analysis for text: '{text[:100]}...' in language: {language}")
        
        if not text or not text.strip():
            logger.warning("Empty text provided for emotion analysis")
            return {
                "emotions": [{"label": "neutral", "score": 0.5}],
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "language": language,
                "ai_enhanced": False
            }
        
        # Try AI-powered emotion analysis first
        ai_analysis = self._analyze_emotions_with_ai(text, language)
        if ai_analysis:
            return ai_analysis
        
        # Fallback to traditional analysis
        logger.info("🔄 Falling back to traditional emotion analysis")
        return self._analyze_emotions_traditional(text, language)
    
    def _analyze_emotions_with_ai(self, text: str, language: str) -> Dict:
        """Analyze emotions using AI"""
        try:
            # Create AI prompt for emotion analysis
            prompt = self._create_emotion_analysis_prompt(text, language)
            
            ai_result = None
            
            # Try OpenAI first
            if self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert in analyzing emotions in Russian and Kazakh call center conversations."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.1
                    )
                    ai_result = response.choices[0].message.content.strip()
                    logger.info("✅ OpenAI emotion analysis completed")
                except Exception as e:
                    logger.warning(f"OpenAI emotion analysis failed: {e}")
            
            # Try Anthropic if OpenAI failed
            if not ai_result and self.anthropic_client:
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=500,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    ai_result = response.content[0].text.strip()
                    logger.info("✅ Anthropic emotion analysis completed")
                except Exception as e:
                    logger.warning(f"Anthropic emotion analysis failed: {e}")
            
            # Parse AI result
            if ai_result:
                parsed_result = self._parse_ai_emotion_result(ai_result)
                if parsed_result:
                    logger.info(f"🎯 AI emotion analysis result: {parsed_result}")
                    return parsed_result
            
            return None
            
        except Exception as e:
            logger.error(f"AI emotion analysis failed: {e}")
            return None
    
    def _create_emotion_analysis_prompt(self, text: str, language: str) -> str:
        """Create AI prompt for emotion analysis"""
        lang_name = "Russian" if language == "ru" else "Kazakh"
        
        prompt = f"""
Analyze the emotional state of the customer in this {lang_name} call center conversation.

Customer text: "{text}"

Please provide:
1. Overall sentiment: positive, negative, or neutral
2. Confidence level (0.0 to 1.0)
3. Primary emotions detected
4. Emotional intensity (low, medium, high)

Format your response as:
SENTIMENT: [positive/negative/neutral]
CONFIDENCE: [0.0-1.0]
EMOTIONS: [list of emotions]
INTENSITY: [low/medium/high]
"""
        return prompt
    
    def _parse_ai_emotion_result(self, ai_result: str) -> Dict:
        """Parse AI emotion analysis result"""
        try:
            lines = ai_result.split('\n')
            sentiment = "neutral"
            confidence = 0.5
            emotions = []
            intensity = "medium"
            
            for line in lines:
                line = line.strip()
                if line.startswith('SENTIMENT:'):
                    sentiment = line[10:].strip().lower()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line[11:].strip())
                    except:
                        confidence = 0.5
                elif line.startswith('EMOTIONS:'):
                    emotions_text = line[9:].strip()
                    emotions = [e.strip() for e in emotions_text.split(',')]
                elif line.startswith('INTENSITY:'):
                    intensity = line[10:].strip().lower()
            
            return {
                "emotions": [{"label": sentiment, "score": confidence}],
                "sentiment": sentiment,
                "sentiment_confidence": confidence,
                "ai_emotions": emotions,
                "intensity": intensity,
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI emotion result: {e}")
            return None
    
    def _analyze_emotions_traditional(self, text: str, language: str) -> Dict:
        """Traditional emotion analysis using ML models"""
        # First try keyword-based analysis (more reliable for Russian/Kazakh)
        logger.info("🔍 Running keyword-based sentiment analysis...")
        keyword_sentiment = self._analyze_sentiment_keywords(text, language)
        logger.info(f"🔍 Keyword analysis result: {keyword_sentiment}")
        
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
                    "analysis_method": "ml_keyword_combined",
                    "ai_enhanced": False
                }
            except Exception as e:
                logger.warning(f"ML emotion analysis failed: {e}")
        
        # Fallback to keyword-based analysis
        return {
            "emotions": [{"label": keyword_sentiment["sentiment"], "score": keyword_sentiment["confidence"]}],
            "sentiment": keyword_sentiment["sentiment"],
            "sentiment_confidence": keyword_sentiment["confidence"],
            "language": language,
            "analysis_method": "keyword_based",
            "ai_enhanced": False
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
    
    def _extract_sentiment_from_emotions(self, emotions: List) -> Dict:
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
    
    def track_emotion_progression_ai(self, segments: List, language: str = "ru") -> List:
        """AI-enhanced emotion progression tracking"""
        emotion_timeline = []
        
        for i, segment in enumerate(segments):
            segment_text = segment.get("text", "")
            if not segment_text.strip():
                continue
            
            # Analyze emotions for this segment
            emotions = self.analyze_emotions_ai(segment_text, language)
            
            emotion_timeline.append({
                "timestamp": segment.get("start", i),
                "emotions": emotions,
                "text_snippet": segment_text[:100],
                "ai_enhanced": emotions.get("ai_enhanced", False)
            })
        
        # AI-powered progression analysis
        if len(emotion_timeline) > 1:
            progression_analysis = self._analyze_emotion_progression_with_ai(emotion_timeline)
            if progression_analysis:
                # Add progression insights to timeline
                for item in emotion_timeline:
                    item["progression_insights"] = progression_analysis
        
        return emotion_timeline
    
    def _analyze_emotion_progression_with_ai(self, emotion_timeline: List) -> Dict:
        """Analyze emotion progression using AI"""
        try:
            if not self.openai_client and not self.anthropic_client:
                return None
            
            # Create summary of emotion progression
            progression_summary = []
            for item in emotion_timeline:
                progression_summary.append(f"Time {item['timestamp']}s: {item['emotions']['sentiment']} ({item['emotions']['sentiment_confidence']:.2f})")
            
            prompt = f"""
Analyze the emotional progression of a customer during a call center conversation.

Emotion timeline:
{chr(10).join(progression_summary)}

Please provide:
1. Overall emotional trend (improving, deteriorating, stable)
2. Key emotional turning points
3. Customer satisfaction level at the end
4. Recommendations for the call center worker

Format as:
TREND: [improving/deteriorating/stable]
TURNING_POINTS: [list key moments]
FINAL_SATISFACTION: [high/medium/low]
RECOMMENDATIONS: [brief recommendations]
"""
            
            ai_result = None
            
            if self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert in analyzing customer emotional progression in call center interactions."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.1
                    )
                    ai_result = response.choices[0].message.content.strip()
                except Exception as e:
                    logger.warning(f"OpenAI progression analysis failed: {e}")
            
            if not ai_result and self.anthropic_client:
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=500,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    ai_result = response.content[0].text.strip()
                except Exception as e:
                    logger.warning(f"Anthropic progression analysis failed: {e}")
            
            if ai_result:
                return self._parse_progression_analysis(ai_result)
            
            return None
            
        except Exception as e:
            logger.error(f"AI progression analysis failed: {e}")
            return None
    
    def _parse_progression_analysis(self, ai_result: str) -> Dict:
        """Parse AI progression analysis result"""
        try:
            lines = ai_result.split('\n')
            trend = "stable"
            turning_points = []
            final_satisfaction = "medium"
            recommendations = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('TREND:'):
                    trend = line[6:].strip().lower()
                elif line.startswith('TURNING_POINTS:'):
                    turning_points_text = line[15:].strip()
                    turning_points = [tp.strip() for tp in turning_points_text.split(',')]
                elif line.startswith('FINAL_SATISFACTION:'):
                    final_satisfaction = line[19:].strip().lower()
                elif line.startswith('RECOMMENDATIONS:'):
                    recommendations_text = line[16:].strip()
                    recommendations = [rec.strip() for rec in recommendations_text.split(',')]
            
            return {
                "trend": trend,
                "turning_points": turning_points,
                "final_satisfaction": final_satisfaction,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to parse progression analysis: {e}")
            return None
