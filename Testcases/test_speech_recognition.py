"""
Speech Recognition Tests for Omani-Therapist-Voice

This module contains test cases to validate the system's ability to accurately
transcribe Omani Arabic speech in various conditions.
"""

import os
import sys
import time
import logging
import unittest
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import required modules
try:
    from speech_to_Text.whisper import create_omani_stt, OmaniSTT
except ImportError as e:
    logger.error(f"Failed to import STT module: {e}")
    raise


class SpeechRecognitionTests(unittest.TestCase):
    """Test suite for Omani Arabic speech recognition capabilities."""
    
    def setUp(self):
        """Set up the test environment."""
        # Initialize STT engine
        self.stt = create_omani_stt()
        
        # Test audio file paths - replace with actual paths
        self.test_files = {
            "basic_greeting": "test_data/audio/basic_greeting.mp3",  # "السلام عليكم، كيف حالك؟"
            "medical_terms": "test_data/audio/medical_terms.mp3",    # Mental health terms in Arabic
            "code_switching": "test_data/audio/code_switching.mp3",  # Mixed Arabic-English
            "background_noise": "test_data/audio/background_noise.mp3", # With ambient noise
            "female_speaker": "test_data/audio/female_speaker.mp3",  # Female voice
            "male_speaker": "test_data/audio/male_speaker.mp3",      # Male voice
            "child_speaker": "test_data/audio/child_speaker.mp3",    # Child voice
        }
        
        # Expected transcriptions
        self.expected_texts = {
            "basic_greeting": "السلام عليكم، كيف حالك؟",
            "medical_terms": "أشعر بالقلق والاكتئاب منذ فترة طويلة",
            "code_switching": "أنا feeling depressed لأنني failed الامتحان",
            "background_noise": "لدي صعوبة في التركيز على عملي",
            "female_speaker": "أحتاج إلى مساعدة للتعامل مع ضغوط الحياة",
            "male_speaker": "أشعر بالتوتر عندما أتحدث أمام الآخرين",
            "child_speaker": "أخاف من الذهاب إلى المدرسة كل يوم",
        }
        
        # Create test data directory if it doesn't exist
        os.makedirs(Path(__file__).parent / "test_results", exist_ok=True)
    
    def test_basic_greeting(self):
        """Test SR-01: Basic Omani greeting recognition."""
        audio_path = Path(__file__).parent / self.test_files["basic_greeting"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # Process audio
        result = self.stt.transcribe_audio(audio_path)
        
        # Check accuracy
        expected = self.expected_texts["basic_greeting"]
        accuracy = self._calculate_accuracy(result, expected)
        
        # Log results
        logger.info(f"Basic Greeting Test: {accuracy:.2f}% accuracy")
        logger.info(f"Expected: {expected}")
        logger.info(f"Received: {result}")
        
        # Assert minimum accuracy
        self.assertGreaterEqual(accuracy, 95, "Basic greeting recognition failed")
    
    def test_medical_terminology(self):
        """Test SR-02: Medical terminology recognition."""
        audio_path = Path(__file__).parent / self.test_files["medical_terms"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # Process audio
        result = self.stt.transcribe_audio(audio_path)
        
        # Check accuracy
        expected = self.expected_texts["medical_terms"]
        accuracy = self._calculate_accuracy(result, expected)
        
        # Log results
        logger.info(f"Medical Terminology Test: {accuracy:.2f}% accuracy")
        logger.info(f"Expected: {expected}")
        logger.info(f"Received: {result}")
        
        # Assert minimum accuracy
        self.assertGreaterEqual(accuracy, 90, "Medical terminology recognition failed")
    
    def test_code_switching(self):
        """Test SR-03: Code-switching between Arabic and English."""
        audio_path = Path(__file__).parent / self.test_files["code_switching"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # Process audio
        result = self.stt.transcribe_audio(audio_path)
        
        # Check accuracy
        expected = self.expected_texts["code_switching"]
        accuracy = self._calculate_accuracy(result, expected)
        
        # Log results
        logger.info(f"Code-Switching Test: {accuracy:.2f}% accuracy")
        logger.info(f"Expected: {expected}")
        logger.info(f"Received: {result}")
        
        # Assert minimum accuracy
        self.assertGreaterEqual(accuracy, 90, "Code-switching recognition failed")
    
    def test_background_noise(self):
        """Test SR-04: Speech recognition with background noise."""
        audio_path = Path(__file__).parent / self.test_files["background_noise"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
            
        # Process audio
        result = self.stt.transcribe_audio(audio_path)
        
        # Check accuracy
        expected = self.expected_texts["background_noise"]
        accuracy = self._calculate_accuracy(result, expected)
        
        # Log results
        logger.info(f"Background Noise Test: {accuracy:.2f}% accuracy")
        logger.info(f"Expected: {expected}")
        logger.info(f"Received: {result}")
        
        # Assert minimum accuracy
        self.assertGreaterEqual(accuracy, 85, "Background noise test failed")
    
    def test_varied_speakers(self):
        """Test SR-05: Recognition across different speaker types."""
        speaker_types = ["female_speaker", "male_speaker", "child_speaker"]
        accuracies = []
        
        for speaker_type in speaker_types:
            audio_path = Path(__file__).parent / self.test_files[speaker_type]
            if not audio_path.exists():
                logger.warning(f"Test audio file not found: {audio_path}")
                continue
                
            # Process audio
            result = self.stt.transcribe_audio(audio_path)
            
            # Check accuracy
            expected = self.expected_texts[speaker_type]
            accuracy = self._calculate_accuracy(result, expected)
            accuracies.append(accuracy)
            
            # Log results
            logger.info(f"{speaker_type.replace('_', ' ').title()} Test: {accuracy:.2f}% accuracy")
            logger.info(f"Expected: {expected}")
            logger.info(f"Received: {result}")
        
        # Assert minimum average accuracy
        avg_accuracy = np.mean(accuracies) if accuracies else 0
        self.assertGreaterEqual(avg_accuracy, 90, "Varied speaker recognition failed")
    
    def test_response_time(self):
        """Test PT-01: Speech recognition response time."""
        audio_path = Path(__file__).parent / self.test_files["basic_greeting"]
        if not audio_path.exists():
            self.skipTest(f"Test audio file not found: {audio_path}")
        
        # Measure processing time
        start_time = time.time()
        _ = self.stt.transcribe_audio(audio_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Log results
        logger.info(f"STT Processing Time: {processing_time:.2f} seconds")
        
        # Assert maximum processing time (7 seconds for STT component)
        self.assertLessEqual(processing_time, 7, "STT processing time exceeded limit")
    
    def _calculate_accuracy(self, result: str, expected: str) -> float:
        """
        Calculate the accuracy of the transcription.
        
        Args:
            result: The actual transcription
            expected: The expected transcription
            
        Returns:
            Accuracy percentage (0-100)
        """
        # Simple character-based accuracy
        if not expected:
            return 0
        
        # Normalize Arabic text (remove diacritics, normalize alif forms, etc.)
        result = self._normalize_arabic(result)
        expected = self._normalize_arabic(expected)
        
        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(result, expected)
        max_length = max(len(result), len(expected))
        
        if max_length == 0:
            return 100
        
        return max(0, 100 * (1 - distance / max_length))
    
    def _normalize_arabic(self, text: str) -> str:
        """
        Normalize Arabic text for comparison.
        
        Args:
            text: Arabic text to normalize
            
        Returns:
            Normalized text
        """
        # Remove whitespace and lowercase
        text = text.strip().lower()
        
        # Add more normalization if needed
        
        return text
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Edit distance
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]


if __name__ == "__main__":
    unittest.main()
