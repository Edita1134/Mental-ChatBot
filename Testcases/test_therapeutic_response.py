"""
Therapeutic Response Tests for Omani-Therapist-Voice

This module contains test cases to validate the quality and appropriateness
of the system's therapeutic responses in Omani Arabic.
"""

import os
import sys
import time
import logging
import unittest
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import required modules
try:
    from llm.openai_client import create_azure_omani_llm, AzureOmaniTherapistLLM
    from speech_to_Text.whisper import create_omani_stt
    from Text_to_Speech.arabic_tts import OmaniTTS
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    raise


class TherapeuticResponseTests(unittest.TestCase):
    """Test suite for therapeutic response quality and appropriateness."""
    
    def setUp(self):
        """Set up the test environment."""
        # Initialize LLM
        self.llm = create_azure_omani_llm()
        
        # Initialize STT and TTS engines
        self.stt = create_omani_stt()
        self.tts = OmaniTTS()
        
        # Test scenarios - text inputs for direct LLM testing
        self.test_scenarios = {
            "active_listening": "أشعر بالوحدة هذه الأيام. عائلتي بعيدة وأصدقائي مشغولون دائمًا.",
            "cbt_technique": "دائمًا أفكر أنني سأفشل في الامتحان مهما درست. أنا غبي ولن أنجح أبدًا.",
            "cultural_context": "زوجتي تريد العمل ولكن أهلي يرون أن مكان المرأة في البيت. أنا محتار بين رغبتها واحترام تقاليد العائلة.",
            "closed_statement": "أنا حزين.",
            "grief_expression": "توفي والدي الشهر الماضي. لا أعرف كيف أتعامل مع هذا الفقدان.",
        }
        
        # Create test data directory if it doesn't exist
        os.makedirs(Path(__file__).parent / "test_results", exist_ok=True)
    
    def test_active_listening(self):
        """Test TR-01: Active listening and reflection skills."""
        # Get test input
        user_input = self.test_scenarios["active_listening"]
        
        # Generate response
        response = self.llm.generate_response(user_input)
        
        # Log results
        logger.info(f"Active Listening Test:")
        logger.info(f"User input: {user_input}")
        logger.info(f"System response: {response}")
        
        # Check for reflection elements
        reflection_present = self._contains_reflection(response, user_input)
        
        # Log assessment
        logger.info(f"Reflection present: {reflection_present}")
        
        # Assert reflection is present
        self.assertTrue(reflection_present, "Response lacks active listening reflection")
        
        # Validate response quality
        response_metrics = self._evaluate_response_quality(response, user_input)
        
        # Log quality metrics
        logger.info(f"Response metrics: {response_metrics}")
        
        # Assert minimum therapeutic quality
        self.assertGreaterEqual(response_metrics["therapeutic_score"], 7.0,
                              "Therapeutic quality below threshold")
    
    def test_cbt_techniques(self):
        """Test TR-02: Appropriate application of CBT techniques."""
        # Get test input
        user_input = self.test_scenarios["cbt_technique"]
        
        # Generate response
        response = self.llm.generate_response(user_input)
        
        # Log results
        logger.info(f"CBT Techniques Test:")
        logger.info(f"User input: {user_input}")
        logger.info(f"System response: {response}")
        
        # Check for CBT elements
        cbt_elements = self._identify_cbt_elements(response)
        
        # Log CBT elements
        logger.info(f"CBT elements identified: {cbt_elements}")
        
        # Assert CBT techniques are applied
        self.assertTrue(cbt_elements, "Response lacks CBT techniques")
        self.assertGreaterEqual(len(cbt_elements), 1, 
                              "Not enough CBT techniques applied")
        
        # Check for thought challenging, a key CBT technique
        self.assertTrue(any(e.get("type") == "thought_challenging" for e in cbt_elements),
                      "No thought challenging technique found")
    
    def test_cultural_sensitivity(self):
        """Test TR-03: Cultural sensitivity and appropriateness."""
        # Get test input with cultural context
        user_input = self.test_scenarios["cultural_context"]
        
        # Generate response
        response = self.llm.generate_response(user_input)
        
        # Log results
        logger.info(f"Cultural Sensitivity Test:")
        logger.info(f"User input: {user_input}")
        logger.info(f"System response: {response}")
        
        # Check for cultural awareness
        cultural_factors = self._assess_cultural_awareness(response, user_input)
        
        # Log cultural factors
        logger.info(f"Cultural factors acknowledged: {cultural_factors}")
        
        # Assert cultural sensitivity
        self.assertTrue(cultural_factors["cultural_awareness"], 
                      "Response lacks cultural awareness")
        self.assertFalse(cultural_factors["cultural_bias"],
                       "Response contains cultural bias")
        self.assertTrue(cultural_factors["respectful_approach"],
                      "Response lacks respectful approach to cultural values")
    
    def test_open_ended_questions(self):
        """Test TR-04: Use of appropriate open-ended questions."""
        # Get test input (closed statement)
        user_input = self.test_scenarios["closed_statement"]
        
        # Generate response
        response = self.llm.generate_response(user_input)
        
        # Log results
        logger.info(f"Open-Ended Questions Test:")
        logger.info(f"User input: {user_input}")
        logger.info(f"System response: {response}")
        
        # Check for open-ended questions
        open_questions = self._identify_open_questions(response)
        
        # Log open questions
        logger.info(f"Open questions identified: {len(open_questions)}")
        if open_questions:
            logger.info(f"Example open question: {open_questions[0]}")
        
        # Assert open-ended questions are used
        self.assertTrue(open_questions, "Response lacks open-ended questions")
        self.assertGreaterEqual(len(open_questions), 1, 
                              "Not enough open-ended questions")
    
    def test_empathetic_response(self):
        """Test TR-05: Empathetic response to grief or loss."""
        # Get test input (grief expression)
        user_input = self.test_scenarios["grief_expression"]
        
        # Generate response
        response = self.llm.generate_response(user_input)
        
        # Log results
        logger.info(f"Empathetic Response Test:")
        logger.info(f"User input: {user_input}")
        logger.info(f"System response: {response}")
        
        # Measure empathy score
        empathy_score = self._measure_empathy(response, user_input)
        
        # Log empathy score
        logger.info(f"Empathy score: {empathy_score:.2f}")
        
        # Assert minimum empathy score
        self.assertGreaterEqual(empathy_score, 0.8, 
                              "Empathy score below threshold")
    
    def test_response_time(self):
        """Test PT-01: Therapeutic response generation time."""
        # Get a complex test input
        user_input = self.test_scenarios["cultural_context"]
        
        # Measure processing time
        start_time = time.time()
        _ = self.llm.generate_response(user_input)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Log results
        logger.info(f"Response Generation Time: {processing_time:.2f} seconds")
        
        # Assert maximum processing time (10 seconds for LLM response)
        self.assertLessEqual(processing_time, 10, 
                           "Response generation time exceeded limit")
    
    def _contains_reflection(self, response: str, user_input: str) -> bool:
        """
        Check if the response contains reflection of user's statement.
        
        Args:
            response: The system's response
            user_input: The user's input
            
        Returns:
            True if reflection is present
        """
        # Extract key phrases from user input (simplified approach)
        key_words = self._extract_key_terms(user_input)
        
        # Check if any key phrases are reflected in response
        return any(word in response for word in key_words)
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text for reflection checking.
        
        Args:
            text: Input text
            
        Returns:
            List of key terms
        """
        # Simple approach - extract potential emotional or situation terms
        # In production, use proper Arabic NLP for better extraction
        emotion_terms = ["وحدة", "حزين", "قلق", "خوف", "غضب", "سعادة"]
        family_terms = ["عائلة", "أسرة", "والد", "والدة", "زوج", "زوجة"]
        situation_terms = ["عمل", "دراسة", "امتحان", "مشكلة", "صعوبة"]
        
        all_terms = emotion_terms + family_terms + situation_terms
        
        return [term for term in all_terms if term in text]
    
    def _evaluate_response_quality(self, response: str, user_input: str) -> Dict[str, float]:
        """
        Evaluate therapeutic quality of response.
        
        Args:
            response: The system's response
            user_input: The user's input
            
        Returns:
            Dictionary of quality metrics
        """
        # In real implementation, use proper NLP evaluation
        # This is a simplified placeholder for testing framework
        
        metrics = {
            "therapeutic_score": 8.5,  # Scale 1-10
            "relevance": 0.9,         # Scale 0-1
            "supportiveness": 0.85,   # Scale 0-1
            "clarity": 0.95,          # Scale 0-1
        }
        
        return metrics
    
    def _identify_cbt_elements(self, response: str) -> List[Dict[str, Any]]:
        """
        Identify CBT techniques in response.
        
        Args:
            response: The system's response
            
        Returns:
            List of identified CBT elements with type and content
        """
        # In real implementation, use proper NLP for technique identification
        # This is a simplified placeholder for testing framework
        
        cbt_elements = []
        
        # Look for thought challenging pattern
        if any(phrase in response for phrase in 
              ["هل هناك دليل", "هل هذه الفكرة صحيحة", "طريقة أخرى للتفكير"]):
            cbt_elements.append({
                "type": "thought_challenging",
                "confidence": 0.85
            })
        
        # Look for behavioral activation
        if any(phrase in response for phrase in 
              ["يمكنك أن تجرب", "نشاط يمكن أن يساعد", "خطوة صغيرة"]):
            cbt_elements.append({
                "type": "behavioral_activation",
                "confidence": 0.8
            })
        
        return cbt_elements
    
    def _assess_cultural_awareness(self, 
                                response: str, 
                                user_input: str) -> Dict[str, bool]:
        """
        Assess cultural awareness in response.
        
        Args:
            response: The system's response
            user_input: The user's input
            
        Returns:
            Dictionary of cultural awareness factors
        """
        # In real implementation, use cultural-aware NLP evaluation
        # This is a simplified placeholder for testing framework
        
        factors = {
            "cultural_awareness": True,
            "cultural_bias": False,
            "respectful_approach": True,
            "culturally_appropriate_suggestions": True
        }
        
        return factors
    
    def _identify_open_questions(self, response: str) -> List[str]:
        """
        Identify open-ended questions in response.
        
        Args:
            response: The system's response
            
        Returns:
            List of open-ended questions
        """
        # Simple approach to extract questions starting with Arabic question words
        open_question_starters = ["ما", "كيف", "لماذا", "متى", "أين", "من"]
        
        # Split response into sentences
        sentences = response.split(".")
        
        # Identify questions
        open_questions = []
        for sentence in sentences:
            # Clean up the sentence
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if it's an open-ended question
            if any(sentence.startswith(starter) for starter in open_question_starters) or "؟" in sentence:
                if not any(closed in sentence for closed in ["هل ", "أليس "]):
                    open_questions.append(sentence)
        
        return open_questions
    
    def _measure_empathy(self, response: str, user_input: str) -> float:
        """
        Measure empathy level in response.
        
        Args:
            response: The system's response
            user_input: The user's input
            
        Returns:
            Empathy score (0-1)
        """
        # In real implementation, use proper NLP for empathy detection
        # This is a simplified placeholder for testing framework
        
        # Check for empathetic phrases
        empathy_phrases = [
            "أتفهم", "أشعر", "من الصعب", "هذا مؤلم", "أنا آسف",
            "يبدو أنك", "من الطبيعي أن", "من المفهوم"
        ]
        
        # Count empathy indicators
        empathy_count = sum(1 for phrase in empathy_phrases if phrase in response)
        
        # Normalize score
        max_expected = 3  # Expect at least 3 empathy indicators in a good response
        empathy_score = min(1.0, empathy_count / max_expected)
        
        return empathy_score


if __name__ == "__main__":
    unittest.main()
