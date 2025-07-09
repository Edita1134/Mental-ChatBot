"""
Emotion Understanding Tests for Omani-Therapist-Voice

This module contains test cases to validate the system's ability to detect
emotional states from Arabic speech and text.
"""

import os
import sys
import time
import logging
import unittest
import json
import numpy as np
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
    from emotion.detector import EmotionDetector
    from speech_to_Text.whisper import create_omani_stt
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    raise


class EmotionUnderstandingTests(unittest.TestCase):
    """Test suite for Omani Arabic emotion understanding capabilities."""
    
    def setUp(self):
        """Set up the test environment."""
        # Initialize emotion detector
        self.emotion_detector = EmotionDetector()
        
        # Initialize STT engine
        self.stt = create_omani_stt()
        
        # Test audio file paths - replace with actual paths
        self.test_files = {
            "anxiety": "test_data/audio/anxiety.mp3",  # Anxiety expression
            "depression": "test_data/audio/depression.mp3",  # Depression indicators
            "mixed_emotions": "test_data/audio/mixed_emotions.mp3",  # Conflicting emotions
            "cultural_expression": "test_data/audio/cultural_expression.mp3",  # Cultural-specific
            "subtle_emotion": "test_data/audio/subtle_emotion.mp3",  # Subtle cues
        }
        
        # Expected primary emotions
        self.expected_emotions = {
            "anxiety": "anxiety",
            "depression": "sadness",
            "mixed_emotions": "confusion",
            "cultural_expression": "shame",
            "subtle_emotion": "worry",
        }
        
        # Create test data directory if it doesn't exist
        os.makedirs(Path(__file__).parent / "test_results", exist_ok=True)
    
    def test_anxiety_detection(self):
        """Test EU-01: Anxiety detection in Omani dialect."""
        audio_path = Path(__file__).parent / self.test_files["anxiety"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # First transcribe the audio
        text = self.stt.transcribe_audio(audio_path)
        
        # Then detect emotions
        emotion_results = self.emotion_detector.detect_emotions(text)
        
        # Get primary emotion and score
        primary_emotion, score = self._get_primary_emotion(emotion_results)
        
        # Log results
        logger.info(f"Anxiety Detection Test:")
        logger.info(f"Text: {text}")
        logger.info(f"Detected primary emotion: {primary_emotion} (score: {score:.2f})")
        logger.info(f"Expected emotion: {self.expected_emotions['anxiety']}")
        logger.info(f"All emotions: {emotion_results}")
        
        # Assert correct emotion with minimum confidence
        self.assertEqual(primary_emotion, self.expected_emotions["anxiety"], 
                       "Failed to identify anxiety as primary emotion")
        self.assertGreaterEqual(score, 0.7, "Anxiety detection confidence too low")
    
    def test_depression_detection(self):
        """Test EU-02: Depression indicators detection."""
        audio_path = Path(__file__).parent / self.test_files["depression"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # First transcribe the audio
        text = self.stt.transcribe_audio(audio_path)
        
        # Then detect emotions
        emotion_results = self.emotion_detector.detect_emotions(text)
        
        # Get primary emotion and score
        primary_emotion, score = self._get_primary_emotion(emotion_results)
        
        # Log results
        logger.info(f"Depression Detection Test:")
        logger.info(f"Text: {text}")
        logger.info(f"Detected primary emotion: {primary_emotion} (score: {score:.2f})")
        logger.info(f"Expected emotion: {self.expected_emotions['depression']}")
        logger.info(f"All emotions: {emotion_results}")
        
        # Assert correct emotion with minimum confidence
        self.assertEqual(primary_emotion, self.expected_emotions["depression"], 
                       "Failed to identify depression as primary emotion")
        self.assertGreaterEqual(score, 0.7, "Depression detection confidence too low")
    
    def test_mixed_emotions(self):
        """Test EU-03: Mixed emotions detection."""
        audio_path = Path(__file__).parent / self.test_files["mixed_emotions"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # First transcribe the audio
        text = self.stt.transcribe_audio(audio_path)
        
        # Then detect emotions
        emotion_results = self.emotion_detector.detect_emotions(text)
        
        # Get primary emotion and score
        primary_emotion, score = self._get_primary_emotion(emotion_results)
        
        # Check for secondary emotions
        secondary_emotions = self._get_secondary_emotions(emotion_results, primary_emotion)
        
        # Log results
        logger.info(f"Mixed Emotions Test:")
        logger.info(f"Text: {text}")
        logger.info(f"Detected primary emotion: {primary_emotion} (score: {score:.2f})")
        logger.info(f"Secondary emotions: {secondary_emotions}")
        logger.info(f"Expected primary emotion: {self.expected_emotions['mixed_emotions']}")
        
        # Assert correct primary emotion with minimum confidence
        self.assertEqual(primary_emotion, self.expected_emotions["mixed_emotions"], 
                       "Failed to identify primary emotion in mixed state")
        self.assertGreaterEqual(score, 0.6, "Mixed emotions primary detection confidence too low")
        
        # Assert detection of at least one secondary emotion
        self.assertGreaterEqual(len(secondary_emotions), 1, 
                              "Failed to detect secondary emotions in mixed state")
    
    def test_cultural_expression(self):
        """Test EU-04: Culturally specific emotional expressions."""
        audio_path = Path(__file__).parent / self.test_files["cultural_expression"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # First transcribe the audio
        text = self.stt.transcribe_audio(audio_path)
        
        # Then detect emotions
        emotion_results = self.emotion_detector.detect_emotions(text)
        
        # Get primary emotion and score
        primary_emotion, score = self._get_primary_emotion(emotion_results)
        
        # Log results
        logger.info(f"Cultural Expression Test:")
        logger.info(f"Text: {text}")
        logger.info(f"Detected primary emotion: {primary_emotion} (score: {score:.2f})")
        logger.info(f"Expected emotion: {self.expected_emotions['cultural_expression']}")
        
        # Check cultural context detection
        cultural_context = self.emotion_detector.detect_cultural_context(text)
        
        # Assert cultural context detection
        self.assertIsNotNone(cultural_context, "Failed to detect cultural context")
        self.assertIn("cultural_factors", cultural_context, "No cultural factors detected")
        
        # Assert correct emotion with minimum confidence
        self.assertEqual(primary_emotion, self.expected_emotions["cultural_expression"], 
                       "Failed to identify culturally specific emotion")
        self.assertGreaterEqual(score, 0.65, "Cultural emotion detection confidence too low")
    
    def test_subtle_emotional_cues(self):
        """Test EU-05: Detection of subtle emotional undertones."""
        audio_path = Path(__file__).parent / self.test_files["subtle_emotion"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # First transcribe the audio
        text = self.stt.transcribe_audio(audio_path)
        
        # Then detect emotions with deep analysis
        emotion_results = self.emotion_detector.detect_emotions(text, deep_analysis=True)
        
        # Get primary emotion and score
        primary_emotion, score = self._get_primary_emotion(emotion_results)
        
        # Get underlying emotions
        underlying_emotions = self.emotion_detector.detect_underlying_emotions(text)
        
        # Log results
        logger.info(f"Subtle Emotional Cues Test:")
        logger.info(f"Text: {text}")
        logger.info(f"Detected primary emotion: {primary_emotion} (score: {score:.2f})")
        logger.info(f"Underlying emotions: {underlying_emotions}")
        logger.info(f"Expected subtle emotion: {self.expected_emotions['subtle_emotion']}")
        
        # Assert detection of underlying emotion
        self.assertIn(self.expected_emotions["subtle_emotion"], 
                    [e for e, _ in underlying_emotions], 
                    "Failed to detect underlying subtle emotion")
        
        # Get score for expected subtle emotion
        subtle_score = next((s for e, s in underlying_emotions 
                          if e == self.expected_emotions["subtle_emotion"]), 0)
        
        # Assert minimum confidence in subtle emotion detection
        self.assertGreaterEqual(subtle_score, 0.5, 
                              "Subtle emotion detection confidence too low")
    
    def test_response_time(self):
        """Test PT-01: Emotion detection response time."""
        audio_path = Path(__file__).parent / self.test_files["anxiety"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
        
        # First transcribe the audio
        text = self.stt.transcribe_audio(audio_path)
        
        # Measure processing time for emotion detection
        start_time = time.time()
        _ = self.emotion_detector.detect_emotions(text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Log results
        logger.info(f"Emotion Detection Processing Time: {processing_time:.2f} seconds")
        
        # Assert maximum processing time (3 seconds for emotion component)
        self.assertLessEqual(processing_time, 3, "Emotion detection time exceeded limit")
    
    def _get_primary_emotion(self, emotion_results: Dict[str, float]) -> Tuple[str, float]:
        """
        Extract the primary emotion and its score.
        
        Args:
            emotion_results: Dictionary of emotion names to scores
            
        Returns:
            Tuple of (primary_emotion, score)
        """
        if not emotion_results:
            return ("neutral", 0.0)
        
        primary_emotion = max(emotion_results.items(), key=lambda x: x[1])
        return primary_emotion
    
    def _get_secondary_emotions(self, 
                              emotion_results: Dict[str, float], 
                              primary_emotion: str,
                              threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Extract secondary emotions above threshold.
        
        Args:
            emotion_results: Dictionary of emotion names to scores
            primary_emotion: Name of primary emotion to exclude
            threshold: Minimum score to consider
            
        Returns:
            List of (emotion, score) tuples for secondary emotions
        """
        if not emotion_results:
            return []
        
        secondary = [(e, s) for e, s in emotion_results.items() 
                   if e != primary_emotion and s >= threshold]
        return sorted(secondary, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    unittest.main()
