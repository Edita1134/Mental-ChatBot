"""
Emotion detection module for Arabic text analysis.
Supports cultural context and Arabic language nuances.
"""

import logging
import re
from typing import Dict, List, Optional
import numpy as np

# Try to import transformers for advanced emotion detection
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Emotion detection system for Arabic text with cultural awareness.
    Uses both rule-based and ML-based approaches.
    """
    
    def __init__(self, use_ml: bool = True):
        """
        Initialize the emotion detector.
        
        Args:
            use_ml: Whether to use ML models (requires transformers)
        """
        self.use_ml = use_ml and HAS_TRANSFORMERS
        
        # Initialize ML model if available
        if self.use_ml:
            try:
                self.emotion_pipeline = self._initialize_ml_model()
                logger.info("ML emotion model initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize ML model: {e}")
                self.use_ml = False
        
        # Arabic emotion lexicon
        self.emotion_lexicon = self._build_arabic_emotion_lexicon()
        
        # Omani dialect emotion patterns
        self.omani_patterns = self._build_omani_emotion_patterns()
        
        logger.info("Emotion detector initialized")
    
    def _initialize_ml_model(self):
        """
        Initialize the ML emotion detection model.
        
        Returns:
            Emotion detection pipeline
        """
        try:
            # Use a multilingual emotion model
            model_name = "j-hartmann/emotion-english-distilroberta-base"
            return pipeline(
                "text-classification",
                model=model_name,
                tokenizer=model_name,
                device=-1  # Use CPU
            )
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            return None
    
    def _build_arabic_emotion_lexicon(self) -> Dict[str, List[str]]:
        """
        Build Arabic emotion lexicon with keywords.
        
        Returns:
            Dictionary mapping emotions to Arabic keywords
        """
        return {
            "joy": [
                "سعيد", "مبسوط", "فرحان", "مرتاح", "منشرح", 
                "سرور", "بهجة", "حبور", "غبطة", "ابتهاج",
                "الحمد لله", "فرحة", "سعادة"
            ],
            "sadness": [
                "حزين", "مكتئب", "منكسر", "متألم", "مهموم",
                "كئيب", "محبط", "يائس", "متضايق", "مصدوم",
                "حزن", "أسى", "غم", "هم", "كآبة"
            ],
            "anger": [
                "غاضب", "زعلان", "متضايق", "مستاء", "محنق",
                "ثائر", "منفعل", "متوتر", "عصبي", "مجنون",
                "غضب", "زعل", "انفعال", "استياء"
            ],
            "fear": [
                "خايف", "قلق", "متوتر", "مرعوب", "فزعان",
                "خوف", "قلق", "رعب", "فزع", "هلع",
                "رهبة", "وجل", "ترقب"
            ],
            "anxiety": [
                "قلقان", "متوتر", "مضطرب", "مشتت", "متردد",
                "قلق", "توتر", "اضطراب", "ارتباك", "حيرة",
                "شك", "ريبة", "تردد"
            ],
            "hope": [
                "متفائل", "واثق", "طموح", "أمل", "تفاؤل",
                "إن شاء الله", "بإذن الله", "ثقة", "يقين",
                "رجاء", "تطلع", "انتظار"
            ],
            "gratitude": [
                "شاكر", "ممتن", "معترف", "مقدر",
                "شكر", "امتنان", "تقدير", "اعتراف",
                "الحمد لله", "جزاك الله خير", "بارك الله فيك"
            ],
            "love": [
                "محب", "معجب", "مولع", "مفتون",
                "حب", "عشق", "إعجاب", "ولع", "هيام",
                "مودة", "رحمة", "حنان"
            ]
        }
    
    def _build_omani_emotion_patterns(self) -> Dict[str, List[str]]:
        """
        Build Omani dialect specific emotion patterns.
        
        Returns:
            Dictionary of Omani emotional expressions
        """
        return {
            "joy": [
                "مبسوط واجد", "فرحان زين", "مرتاح بالي",
                "الحمد لله خلاص", "زين جداً", "والله حلو"
            ],
            "sadness": [
                "محطم نفسياً", "دايخ من الهم", "مكسور خاطري",
                "قلبي ضايق", "ما أدري شبي", "تعبان نفسياً"
            ],
            "anger": [
                "زعلان مرة", "متضايق واجد", "عصبي زين",
                "ما عد أقدر", "خلاص تعبت", "مستفز"
            ],
            "worry": [
                "قلقان على روحي", "خايف من البكرة", "مهموم زين",
                "ما عندي راحة", "دايماً أفكر", "متوتر واجد"
            ],
            "confusion": [
                "ما أدري شبي", "محتار في أموري", "مشتت بالي",
                "ما أعرف وين أروح", "كله ملخبط", "دايخ"
            ]
        }
    
    def detect_emotions(self, text: str) -> Dict[str, float]:
        """
        Detect emotions in Arabic text.
        
        Args:
            text: Arabic text to analyze
            
        Returns:
            Dictionary mapping emotions to confidence scores
        """
        if not text.strip():
            return {}
        
        # Combine rule-based and ML-based detection
        rule_based_emotions = self._detect_emotions_rule_based(text)
        
        if self.use_ml and self.emotion_pipeline:
            ml_emotions = self._detect_emotions_ml(text)
            # Combine results with weighted average
            combined_emotions = self._combine_emotion_results(rule_based_emotions, ml_emotions)
        else:
            combined_emotions = rule_based_emotions
        
        # Add cultural context adjustments
        adjusted_emotions = self._adjust_for_cultural_context(text, combined_emotions)
        
        return adjusted_emotions
    
    def _detect_emotions_rule_based(self, text: str) -> Dict[str, float]:
        """
        Rule-based emotion detection using Arabic lexicon.
        
        Args:
            text: Text to analyze
            
        Returns:
            Emotion scores dictionary
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        # Check standard Arabic emotions
        for emotion, keywords in self.emotion_lexicon.items():
            score = 0
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                score += count * 0.3  # Base weight for each occurrence
            
            if score > 0:
                emotion_scores[emotion] = min(score, 1.0)  # Cap at 1.0
        
        # Check Omani dialect patterns
        for emotion, patterns in self.omani_patterns.items():
            if emotion not in emotion_scores:
                emotion_scores[emotion] = 0
            
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    emotion_scores[emotion] += 0.5  # Higher weight for dialect matches
        
        # Normalize scores
        if emotion_scores:
            max_score = max(emotion_scores.values())
            if max_score > 0:
                for emotion in emotion_scores:
                    emotion_scores[emotion] = emotion_scores[emotion] / max_score
        
        return emotion_scores
    
    def _detect_emotions_ml(self, text: str) -> Dict[str, float]:
        """
        ML-based emotion detection (fallback to English translation if needed).
        
        Args:
            text: Text to analyze
            
        Returns:
            Emotion scores dictionary
        """
        try:
            if not self.emotion_pipeline:
                return {}
            
            # For Arabic text, we might need to translate or use Arabic-specific models
            # For now, using the multilingual model directly
            results = self.emotion_pipeline(text)
            
            ml_emotions = {}
            for result in results:
                emotion = result['label'].lower()
                score = result['score']
                
                # Map model labels to our emotion categories
                emotion_mapping = {
                    'joy': 'joy',
                    'sadness': 'sadness',
                    'anger': 'anger',
                    'fear': 'fear',
                    'surprise': 'surprise',
                    'disgust': 'anger',  # Map disgust to anger
                    'love': 'love'
                }
                
                mapped_emotion = emotion_mapping.get(emotion, emotion)
                ml_emotions[mapped_emotion] = score
            
            return ml_emotions
            
        except Exception as e:
            logger.error(f"ML emotion detection failed: {e}")
            return {}
    
    def _combine_emotion_results(
        self, 
        rule_based: Dict[str, float], 
        ml_based: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Combine rule-based and ML-based emotion results.
        
        Args:
            rule_based: Rule-based emotion scores
            ml_based: ML-based emotion scores
            
        Returns:
            Combined emotion scores
        """
        combined = {}
        all_emotions = set(rule_based.keys()) | set(ml_based.keys())
        
        for emotion in all_emotions:
            rule_score = rule_based.get(emotion, 0)
            ml_score = ml_based.get(emotion, 0)
            
            # Weighted combination (favor rule-based for Arabic)
            combined_score = 0.7 * rule_score + 0.3 * ml_score
            if combined_score > 0:
                combined[emotion] = combined_score
        
        return combined
    
    def _adjust_for_cultural_context(
        self, 
        text: str, 
        emotions: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Adjust emotion scores based on cultural context.
        
        Args:
            text: Original text
            emotions: Current emotion scores
            
        Returns:
            Culturally adjusted emotion scores
        """
        adjusted = emotions.copy()
        text_lower = text.lower()
        
        # Islamic expressions often indicate acceptance/patience
        islamic_expressions = [
            "الحمد لله", "إن شاء الله", "بإذن الله", "ما شاء الله",
            "سبحان الله", "اللهم", "توكلت على الله"
        ]
        
        has_islamic_expression = any(expr in text_lower for expr in islamic_expressions)
        
        if has_islamic_expression:
            # Reduce intensity of negative emotions
            for emotion in ["sadness", "anger", "fear", "anxiety"]:
                if emotion in adjusted:
                    adjusted[emotion] *= 0.8  # Reduce by 20%
            
            # Increase hope and gratitude
            if "hope" in adjusted:
                adjusted["hope"] = min(1.0, adjusted["hope"] + 0.2)
            else:
                adjusted["hope"] = 0.3
            
            if "gratitude" in adjusted:
                adjusted["gratitude"] = min(1.0, adjusted["gratitude"] + 0.2)
            else:
                adjusted["gratitude"] = 0.3
        
        # Family context adjustments
        family_words = ["أهل", "عائلة", "والدي", "والدتي", "أخوي", "أختي", "زوجي", "زوجتي"]
        has_family_context = any(word in text_lower for word in family_words)
        
        if has_family_context:
            # Family issues often carry more weight in Arab culture
            for emotion in ["sadness", "anxiety", "worry"]:
                if emotion in adjusted:
                    adjusted[emotion] = min(1.0, adjusted[emotion] * 1.2)
        
        return adjusted
    
    def get_dominant_emotion(self, emotions: Dict[str, float]) -> Optional[str]:
        """
        Get the dominant emotion from emotion scores.
        
        Args:
            emotions: Emotion scores dictionary
            
        Returns:
            Name of dominant emotion or None
        """
        if not emotions:
            return None
        
        return max(emotions.items(), key=lambda x: x[1])[0]
    
    def get_emotion_summary(self, emotions: Dict[str, float]) -> str:
        """
        Get a human-readable summary of detected emotions.
        
        Args:
            emotions: Emotion scores dictionary
            
        Returns:
            Arabic summary of emotions
        """
        if not emotions:
            return "لم يتم اكتشاف مشاعر واضحة"
        
        # Sort emotions by score
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        # Emotion names in Arabic
        emotion_names = {
            "joy": "سعادة",
            "sadness": "حزن", 
            "anger": "غضب",
            "fear": "خوف",
            "anxiety": "قلق",
            "hope": "أمل",
            "gratitude": "امتنان",
            "love": "محبة",
            "worry": "قلق",
            "confusion": "حيرة"
        }
        
        dominant = sorted_emotions[0]
        summary = f"المشاعر السائدة: {emotion_names.get(dominant[0], dominant[0])}"
        
        if len(sorted_emotions) > 1:
            secondary = sorted_emotions[1]
            if secondary[1] > 0.3:  # Only include if significant
                summary += f" مع {emotion_names.get(secondary[0], secondary[0])}"
        
        return summary
