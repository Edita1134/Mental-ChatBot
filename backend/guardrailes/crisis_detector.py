import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CrisisType(Enum):
    """Types of mental health crises."""
    SUICIDE = "suicide"
    SELF_HARM = "self_harm"
    VIOLENCE = "violence"
    SEVERE_DEPRESSION = "severe_depression"
    PSYCHOSIS = "psychosis"
    SUBSTANCE_ABUSE = "substance_abuse"
    EATING_DISORDER = "eating_disorder"

class CrisisLevel(Enum):
    """Levels of crisis severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CrisisDetectionSystem:
    """
    Comprehensive crisis detection system for Arabic mental health conversations.
    Monitors for suicidal ideation, self-harm, and other mental health emergencies.
    """
    
    def __init__(self):
        """Initialize the crisis detection system."""
        # Crisis keywords in Arabic
        self.crisis_keywords = self._build_crisis_keywords()
        
        # Crisis patterns and severity weights
        self.crisis_patterns = self._build_crisis_patterns()
        
        # Omani dialect crisis expressions
        self.omani_crisis_expressions = self._build_omani_crisis_expressions()
        
        # Emergency resources in Oman
        self.emergency_resources = self._build_emergency_resources()
        
        # Session tracking for pattern analysis
        self.session_history = {}
        
        logger.info("Crisis detection system initialized")
    
    def _build_crisis_keywords(self) -> Dict[CrisisType, List[str]]:
        """
        Build comprehensive crisis keyword dictionary.
        
        Returns:
            Dictionary mapping crisis types to keyword lists
        """
        return {
            CrisisType.SUICIDE: [
                # Direct suicidal language
                "أريد أن أموت", "بدي أموت", "نفسي أموت", "أقتل نفسي",
                "سأقتل نفسي", "أنتحر", "انتحار", "أنهي حياتي",
                "لا أريد أن أعيش", "مللت من الحياة", "الموت أحسن",
                "أستحق الموت", "العالم أحسن بدوني", "أذهب للأبد",
                
                # Indirect suicidal ideation
                "لا فائدة من وجودي", "محد يحتاجني", "عبء على الجميع",
                "أرتاح لو مت", "أتمنى أنام ولا أصحى", "خلصت من الدنيا",
                "نهاية المطاف", "آخر خيار", "حل نهائي", "راحة أبدية",
                
                # Planning indicators
                "أخطط لـ", "قررت أن", "لن أكون هنا", "وداعاً للجميع",
                "آخر رسالة", "توديع", "وصية", "انتهى كل شيء"
            ],
            
            CrisisType.SELF_HARM: [
                # Self-injury language
                "أؤذي نفسي", "أجرح نفسي", "أقطع نفسي", "أضرب نفسي",
                "أحرق نفسي", "أعذب نفسي", "أكسر", "أخدش",
                "سكين", "شفرة", "حرق", "ضرب", "عض", "خدش",
                
                # Self-punishment
                "أستحق الألم", "أعاقب نفسي", "أستحق العذاب",
                "ألم جسدي", "أشعر بالألم", "دم", "جروح", "ندوب",
                
                # Emotional pain externalization
                "أريد أن أشعر بشيء", "ألم حقيقي", "ألم أستطيع رؤيته",
                "طريقة للتحكم", "الألم الوحيد", "أتحكم في ألمي"
            ],
            
            CrisisType.VIOLENCE: [
                # Violence toward others
                "سأقتل", "أريد أن أؤذي", "سأضرب", "سأدمر",
                "أنتقم", "سأؤذي من", "أقتله", "أكسر رأسه",
                "أفجر", "أحرق", "أدمر كل شيء", "أنهي الجميع",
                
                # Anger escalation
                "لا أستطيع التحكم", "سأفقد السيطرة", "غضب شديد",
                "أعمى من الغضب", "سأفعل شيئاً سيئاً", "أفقد عقلي"
            ],
            
            CrisisType.SEVERE_DEPRESSION: [
                # Hopelessness
                "لا أمل", "لا فائدة", "مستحيل", "ميؤوس منه",
                "الظلام فقط", "لا ضوء", "نفق مظلم", "لا مخرج",
                "مسدود الأفق", "لا حل", "انتهى كل شيء",
                
                # Worthlessness
                "لا قيمة لي", "فاشل", "عديم الفائدة", "لا أستحق",
                "أسوأ شخص", "لا أصلح لشيء", "عبء على الجميع",
                
                # Isolation
                "وحيد تماماً", "محد يفهمني", "محد يحبني", "منبوذ",
                "لا أحد يهتم", "معزول", "منفرد", "وحش"
            ],
            
            CrisisType.PSYCHOSIS: [
                # Delusions and hallucinations
                "أسمع أصوات", "أرى أشياء", "يراقبونني", "يتجسسون",
                "مؤامرة ضدي", "يطاردونني", "صوت يقول لي",
                "أشياء غريبة", "لست حقيقي", "العالم ليس حقيقي",
                
                # Disorganized thinking
                "أفكاري مختلطة", "لا أفهم نفسي", "كلام غير منطقي",
                "رسائل خفية", "معاني مخفية", "علامات"
            ],
            
            CrisisType.SUBSTANCE_ABUSE: [
                # Substance use crisis
                "أفرط في", "إدمان", "مخدرات", "كحول", "حبوب",
                "لا أستطيع التوقف", "أحتاج المزيد", "انسحاب",
                "جرعة زائدة", "تسمم", "أعراض", "اعتماد"
            ]
        }
    
    def _build_crisis_patterns(self) -> Dict[str, Tuple[CrisisType, float]]:
        """
        Build regex patterns for crisis detection with severity weights.
        
        Returns:
            Dictionary mapping patterns to crisis type and weight
        """
        return {
            # High-risk suicide patterns
            r"(أريد|بدي|نفسي).*(أموت|أقتل نفسي|أنتحر)": (CrisisType.SUICIDE, 0.9),
            r"(سأقتل|راح أقتل).*(نفسي|روحي)": (CrisisType.SUICIDE, 0.95),
            r"(لا أريد|ما بدي).*(أعيش|أكمل|أستمر)": (CrisisType.SUICIDE, 0.8),
            
            # Self-harm patterns
            r"(أؤذي|أجرح|أقطع).*(نفسي|روحي)": (CrisisType.SELF_HARM, 0.85),
            r"(شفرة|سكين|حرق).*(نفس|جسم)": (CrisisType.SELF_HARM, 0.8),
            
            # Violence patterns  
            r"(سأقتل|راح أقتل|أقتل).*(كل|جميع|الناس)": (CrisisType.VIOLENCE, 0.9),
            r"(أؤذي|أضرب|أكسر).*(أحد|شخص|واحد)": (CrisisType.VIOLENCE, 0.7),
            
            # Severe depression patterns
            r"(لا أمل|لا فائدة|مستحيل).*(نهائياً|أبداً|تماماً)": (CrisisType.SEVERE_DEPRESSION, 0.7),
            r"(عبء|فاشل|عديم).*(الجميع|الكل|الناس)": (CrisisType.SEVERE_DEPRESSION, 0.6)
        }
    
    def _build_omani_crisis_expressions(self) -> Dict[CrisisType, List[str]]:
        """
        Build Omani dialect specific crisis expressions.
        
        Returns:
            Dictionary of Omani crisis expressions
        """
        return {
            CrisisType.SUICIDE: [
                "خلاص تعبت من الدنيا", "ما عد أقدر أكمل",
                "أرتاح لو رحت", "مللت من كل شي", "ما لي فايدة",
                "الموت أحسن لي", "خلصت من هالحياة"
            ],
            
            CrisisType.SELF_HARM: [
                "أعذب روحي", "أوجع نفسي", "أضر بروحي",
                "أستاهل الألم", "ألم أحسه بجسمي"
            ],
            
            CrisisType.SEVERE_DEPRESSION: [
                "محطم نفسياً واجد", "ضايق صدري مرة", "قلبي مكسور",
                "حالتي زينة ما هي", "نفسيتي في الأرض", "دايخ من الهموم"
            ],
            
            CrisisType.VIOLENCE: [
                "راح أكسر كل شي", "أفجر فيهم", "أورجيهم",
                "أخليهم يندمون", "ما راح أسكت"
            ]
        }
    
    def _build_emergency_resources(self) -> Dict[str, Dict[str, str]]:
        """
        Build emergency resources directory for Oman.
        
        Returns:
            Dictionary of emergency contacts and resources
        """
        return {
            "emergency": {
                "general_emergency": "999",
                "police": "999", 
                "ambulance": "999",
                "fire": "999"
            },
            
            "hospitals": {
                "sultan_qaboos_hospital": "+968 24211411",
                "royal_hospital": "+968 24599000",
                "khoula_hospital": "+968 24560441",
                "nizwa_hospital": "+968 25431800"
            },
            
            "mental_health": {
                "mental_health_hotline": "مكتوب قريباً",
                "psychological_services": "وزارة الصحة - الخدمات النفسية",
                "crisis_intervention": "قسم الطوارئ النفسية",
                "social_services": "وزارة التنمية الاجتماعية"
            },
            
            "support": {
                "family_guidance": "مراكز الإرشاد الأسري",
                "youth_centers": "مراكز الشباب",
                "women_centers": "مراكز المرأة",
                "community_centers": "المراكز المجتمعية"
            }
        }
    
    def assess_crisis_level(self, text: str, session_id: str = None) -> Dict:
        """
        Assess crisis level in user input.
        
        Args:
            text: User's message
            session_id: Session identifier for pattern tracking
            
        Returns:
            Crisis assessment results
        """
        text_lower = text.lower()
        
        # Check direct keywords
        keyword_results = self._check_crisis_keywords(text_lower)
        
        # Check regex patterns
        pattern_results = self._check_crisis_patterns(text_lower)
        
        # Check Omani dialect expressions
        dialect_results = self._check_omani_expressions(text_lower)
        
        # Combine all results
        combined_score = self._calculate_combined_score(
            keyword_results, pattern_results, dialect_results
        )
        
        # Determine crisis level
        crisis_level = self._determine_crisis_level(combined_score)
        
        # Check session patterns if session_id provided
        session_pattern_risk = 0
        if session_id:
            session_pattern_risk = self._analyze_session_patterns(session_id, combined_score)
        
        # Final assessment
        assessment = {
            "crisis_level": crisis_level.value,
            "crisis_score": combined_score["total_score"],
            "detected_types": combined_score["types"],
            "requires_escalation": crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL],
            "requires_immediate_intervention": crisis_level == CrisisLevel.CRITICAL,
            "session_pattern_risk": session_pattern_risk,
            "emergency_resources": self._get_relevant_resources(combined_score["types"])
        }
        
        # Log crisis detection
        if assessment["requires_escalation"]:
            logger.warning(f"Crisis detected: {assessment}")
        
        return assessment
    
    def _check_crisis_keywords(self, text: str) -> Dict:
        """
        Check for crisis keywords in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Keyword analysis results
        """
        results = {"types": [], "scores": {}, "keywords_found": []}
        
        for crisis_type, keywords in self.crisis_keywords.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
                    found_keywords.append(keyword)
            
            if score > 0:
                results["types"].append(crisis_type.value)
                results["scores"][crisis_type.value] = score
                results["keywords_found"].extend(found_keywords)
        
        return results
    
    def _check_crisis_patterns(self, text: str) -> Dict:
        """
        Check for crisis patterns using regex.
        
        Args:
            text: Text to analyze
            
        Returns:
            Pattern analysis results
        """
        results = {"types": [], "scores": {}, "patterns_found": []}
        
        for pattern, (crisis_type, weight) in self.crisis_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                type_name = crisis_type.value
                if type_name not in results["scores"]:
                    results["scores"][type_name] = 0
                    results["types"].append(type_name)
                
                results["scores"][type_name] += len(matches) * weight
                results["patterns_found"].extend(matches)
        
        return results
    
    def _check_omani_expressions(self, text: str) -> Dict:
        """
        Check for Omani dialect crisis expressions.
        
        Args:
            text: Text to analyze
            
        Returns:
            Omani expression analysis results
        """
        results = {"types": [], "scores": {}, "expressions_found": []}
        
        for crisis_type, expressions in self.omani_crisis_expressions.items():
            score = 0
            found_expressions = []
            
            for expression in expressions:
                if expression.lower() in text:
                    score += 1.2  # Higher weight for dialect expressions
                    found_expressions.append(expression)
            
            if score > 0:
                type_name = crisis_type.value
                results["types"].append(type_name)
                results["scores"][type_name] = score
                results["expressions_found"].extend(found_expressions)
        
        return results
    
    def _calculate_combined_score(self, keyword_results: Dict, pattern_results: Dict, dialect_results: Dict) -> Dict:
        """
        Calculate combined crisis score from all analysis methods.
        
        Args:
            keyword_results: Keyword analysis results
            pattern_results: Pattern analysis results
            dialect_results: Dialect analysis results
            
        Returns:
            Combined score analysis
        """
        all_types = set()
        combined_scores = {}
        
        # Combine all detected types
        for results in [keyword_results, pattern_results, dialect_results]:
            all_types.update(results.get("types", []))
        
        # Calculate combined scores for each type
        for crisis_type in all_types:
            total_score = 0
            
            # Add keyword score
            total_score += keyword_results.get("scores", {}).get(crisis_type, 0) * 0.3
            
            # Add pattern score  
            total_score += pattern_results.get("scores", {}).get(crisis_type, 0) * 0.5
            
            # Add dialect score
            total_score += dialect_results.get("scores", {}).get(crisis_type, 0) * 0.4
            
            combined_scores[crisis_type] = total_score
        
        # Calculate total score
        total_score = sum(combined_scores.values())
        
        return {
            "types": list(all_types),
            "scores": combined_scores,
            "total_score": total_score,
            "keyword_details": keyword_results,
            "pattern_details": pattern_results,
            "dialect_details": dialect_results
        }
    
    def _determine_crisis_level(self, combined_score: Dict) -> CrisisLevel:
        """
        Determine crisis level based on combined score.
        
        Args:
            combined_score: Combined analysis results
            
        Returns:
            Crisis level
        """
        total_score = combined_score["total_score"]
        detected_types = combined_score["types"]
        
        # Critical level indicators
        if total_score >= 3.0:
            return CrisisLevel.CRITICAL
        
        if "suicide" in detected_types and total_score >= 2.0:
            return CrisisLevel.CRITICAL
        
        if "violence" in detected_types and total_score >= 2.5:
            return CrisisLevel.CRITICAL
        
        # High level indicators
        if total_score >= 2.0:
            return CrisisLevel.HIGH
        
        if ("suicide" in detected_types or "self_harm" in detected_types) and total_score >= 1.0:
            return CrisisLevel.HIGH
        
        # Medium level indicators
        if total_score >= 1.0:
            return CrisisLevel.MEDIUM
        
        if "severe_depression" in detected_types and total_score >= 0.5:
            return CrisisLevel.MEDIUM
        
        # Low level (default)
        return CrisisLevel.LOW
    
    def _analyze_session_patterns(self, session_id: str, current_score: Dict) -> float:
        """
        Analyze patterns across session history.
        
        Args:
            session_id: Session identifier
            current_score: Current crisis score
            
        Returns:
            Session pattern risk score
        """
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        # Add current score to history
        self.session_history[session_id].append({
            "timestamp": datetime.now(),
            "score": current_score["total_score"],
            "types": current_score["types"]
        })
        
        # Keep only last 10 interactions
        self.session_history[session_id] = self.session_history[session_id][-10:]
        
        history = self.session_history[session_id]
        
        # Check for escalating pattern
        if len(history) >= 3:
            recent_scores = [entry["score"] for entry in history[-3:]]
            if all(recent_scores[i] < recent_scores[i+1] for i in range(len(recent_scores)-1)):
                return 0.5  # Escalating pattern
        
        # Check for persistent crisis indicators
        crisis_count = sum(1 for entry in history if entry["score"] > 1.0)
        if crisis_count >= 2:
            return 0.3  # Persistent crisis indicators
        
        return 0.0
    
    def _get_relevant_resources(self, crisis_types: List[str]) -> Dict[str, str]:
        """
        Get relevant emergency resources based on crisis types.
        
        Args:
            crisis_types: List of detected crisis types
            
        Returns:
            Relevant emergency resources
        """
        resources = {}
        
        # Always include general emergency
        resources.update(self.emergency_resources["emergency"])
        
        # Add specific resources based on crisis type
        if any(t in crisis_types for t in ["suicide", "self_harm", "severe_depression"]):
            resources.update(self.emergency_resources["mental_health"])
            resources.update(self.emergency_resources["hospitals"])
        
        if "violence" in crisis_types:
            resources["police"] = self.emergency_resources["emergency"]["police"]
        
        # Add support resources
        resources.update(self.emergency_resources["support"])
        
        return resources
    
    def generate_crisis_response(self, assessment: Dict) -> str:
        """
        Generate appropriate crisis response message.
        
        Args:
            assessment: Crisis assessment results
            
        Returns:
            Crisis response message in Arabic
        """
        crisis_level = assessment["crisis_level"]
        detected_types = assessment["detected_types"]
        
        if crisis_level == "critical":
            return self._generate_critical_response(detected_types)
        elif crisis_level == "high":
            return self._generate_high_response(detected_types)
        elif crisis_level == "medium":
            return self._generate_medium_response(detected_types)
        else:
            return self._generate_low_response(detected_types)
    
    def _generate_critical_response(self, crisis_types: List[str]) -> str:
        """Generate critical crisis response."""
        if "suicide" in crisis_types:
            return """
🚨 أفهم أنك تمر بوقت صعب جداً، لكن حياتك مهمة وقيمة.

يرجى التواصل فوراً مع:
📞 الطوارئ: 999
🏥 مستشفى السلطان قابوس: 24211411
🆘 أو توجه لأقرب قسم طوارئ

لست وحدك. هناك أشخاص يريدون مساعدتك.
            """
        elif "violence" in crisis_types:
            return """
⚠️ أرى أنك تشعر بغضب شديد. دعنا نجد طرق آمنة للتعامل مع هذه المشاعر.

يرجى:
📞 الاتصال بـ 999 إذا كنت في خطر
🚶‍♂️ أخذ مساحة آمنة من الموقف
🧘‍♂️ التنفس بعمق وهدوء

أتفهم غضبك، لكن سلامتك وسلامة الآخرين أهم.
            """
        else:
            return """
🆘 أشعر بقلق شديد عليك. يرجى طلب المساعدة المهنية فوراً.

📞 اتصل بـ 999 أو توجه لأقرب مستشفى
👨‍⚕️ تحدث مع طبيب أو أخصائي نفسي
👨‍👩‍👧‍👦 أخبر شخص تثق به من عائلتك

وضعك يمكن تحسينه بالمساعدة المناسبة.
            """
    
    def _generate_high_response(self, crisis_types: List[str]) -> str:
        """Generate high-level crisis response."""
        return """
💛 أقدر ثقتك في مشاركة مشاعرك. ما تمر به صعب، لكن هناك حلول ومساعدة.

🔗 موارد المساعدة:
📞 خط المساعدة النفسية (قريباً)
🏥 مراكز الصحة النفسية
👨‍👩‍👧‍👦 التحدث مع شخص تثق به

🤲 تذكر أن الله معك في كل لحظة، والفرج قادم بإذن الله.
        """
    
    def _generate_medium_response(self, crisis_types: List[str]) -> str:
        """Generate medium-level crisis response."""
        return """
💙 أفهم أنك تواجه تحديات. هذا طبيعي في الحياة، والمهم كيف نتعامل معها.

💡 اقتراحات مفيدة:
🗣️ التحدث مع شخص تثق به
🤲 الدعاء والذكر للراحة النفسية
📚 قراءة القرآن للسكينة
🚶‍♂️ المشي والرياضة الخفيفة

أنا هنا لدعمك في هذه الرحلة.
        """
    
    def _generate_low_response(self, crisis_types: List[str]) -> str:
        """Generate low-level response."""
        return """
💚 أسعدني أنك تشاركني أفكارك. التعبير عن المشاعر خطوة إيجابية.

دعنا نتحدث أكثر عما تشعر به وكيف يمكنني مساعدتك.
        """
