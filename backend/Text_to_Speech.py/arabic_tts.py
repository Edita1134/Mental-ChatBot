"""
Text-to-Speech module for Arabic language synthesis.
Optimized for Omani dialect and therapeutic conversations.
"""

import logging
import tempfile
import os
import subprocess
from typing import Optional
import asyncio
from pathlib import Path

# Try different TTS engines
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

logger = logging.getLogger(__name__)

class OmaniTTS:
    """
    Arabic Text-to-Speech synthesizer for therapeutic conversations.
    Supports multiple TTS engines with fallback options.
    """
    
    def __init__(self, engine: str = "auto"):
        """
        Initialize the TTS engine.
        
        Args:
            engine: TTS engine to use ('espeak', 'gtts', 'pyttsx3', 'auto')
        """
        self.engine = engine
        self.temp_dir = tempfile.mkdtemp()
        
        # Arabic voice settings
        self.voice_settings = {
            "language": "ar",
            "rate": 150,  # Speaking rate
            "volume": 0.9,  # Volume level
            "voice_id": "ar"  # Arabic voice identifier
        }
        
        # Initialize the best available engine
        self.active_engine = self._initialize_engine()
        
        logger.info(f"TTS initialized with engine: {self.active_engine}")
    
    def _initialize_engine(self) -> str:
        """
        Initialize the best available TTS engine.
        
        Returns:
            Name of the initialized engine
        """
        if self.engine == "auto":
            # Try engines in order of preference
            if self._test_espeak():
                return "espeak"
            elif HAS_GTTS:
                return "gtts"
            elif HAS_PYTTSX3:
                return "pyttsx3"
            else:
                logger.warning("No TTS engine available, using text fallback")
                return "text"
        else:
            return self.engine
    
    def _test_espeak(self) -> bool:
        """
        Test if eSpeak-NG is available.
        
        Returns:
            True if eSpeak is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["espeak", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def synthesize_speech(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text: Arabic text to synthesize
            output_file: Output audio file path (auto-generated if None)
            
        Returns:
            Path to generated audio file or None if failed
        """
        if not text.strip():
            logger.warning("Empty text provided for TTS")
            return None
        
        if not output_file:
            output_file = os.path.join(
                self.temp_dir, 
                f"tts_output_{hash(text) % 10000}.wav"
            )
        
        try:
            if self.active_engine == "espeak":
                return self._synthesize_espeak(text, output_file)
            elif self.active_engine == "gtts":
                return self._synthesize_gtts(text, output_file)
            elif self.active_engine == "pyttsx3":
                return self._synthesize_pyttsx3(text, output_file)
            else:
                logger.error("No working TTS engine available")
                return None
                
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return None
    
    def _synthesize_espeak(self, text: str, output_file: str) -> Optional[str]:
        """
        Synthesize speech using eSpeak-NG.
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            Output file path or None if failed
        """
        try:
            # Prepare eSpeak command
            command = [
                "espeak",
                "-v", "ar",  # Arabic voice
                "-s", str(self.voice_settings["rate"]),  # Speed
                "-a", str(int(self.voice_settings["volume"] * 200)),  # Amplitude
                "-w", output_file,  # Write to file
                text
            ]
            
            # Execute eSpeak
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                logger.info("eSpeak TTS synthesis completed")
                return output_file
            else:
                logger.error(f"eSpeak failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("eSpeak synthesis timed out")
            return None
        except Exception as e:
            logger.error(f"eSpeak synthesis error: {e}")
            return None
    
    def _synthesize_gtts(self, text: str, output_file: str) -> Optional[str]:
        """
        Synthesize speech using Google Text-to-Speech.
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            Output file path or None if failed
        """
        try:
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang="ar",  # Arabic
                slow=False,
                tld="com"
            )
            
            # Save to file
            tts.save(output_file)
            
            if os.path.exists(output_file):
                logger.info("gTTS synthesis completed")
                return output_file
            else:
                logger.error("gTTS file not created")
                return None
                
        except Exception as e:
            logger.error(f"gTTS synthesis error: {e}")
            return None
    
    def _synthesize_pyttsx3(self, text: str, output_file: str) -> Optional[str]:
        """
        Synthesize speech using pyttsx3.
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            Output file path or None if failed
        """
        try:
            engine = pyttsx3.init()
            
            # Set properties
            engine.setProperty('rate', self.voice_settings["rate"])
            engine.setProperty('volume', self.voice_settings["volume"])
            
            # Try to set Arabic voice
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'ar' in voice.id.lower() or 'arabic' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            # Save to file
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            
            if os.path.exists(output_file):
                logger.info("pyttsx3 synthesis completed")
                return output_file
            else:
                logger.error("pyttsx3 file not created")
                return None
                
        except Exception as e:
            logger.error(f"pyttsx3 synthesis error: {e}")
            return None
    
    def preprocess_arabic_text(self, text: str) -> str:
        """
        Preprocess Arabic text for better TTS pronunciation.
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Add pauses for better speech flow
        text = text.replace(".", ". ")
        text = text.replace("،", "، ")
        text = text.replace("؟", "؟ ")
        text = text.replace("!", "! ")
        
        # Normalize common Arabic characters
        text = text.replace("أ", "ا")  # Normalize alif
        text = text.replace("إ", "ا")  # Normalize alif
        text = text.replace("آ", "ا")  # Normalize alif
        
        # Handle Omani dialect specific pronunciations
        omani_pronunciations = {
            "شلونك": "شلون حالك",
            "كيفك": "كيف حالك",
            "وش أخبارك": "وش اخبارك",
            "صج": "صحيح",
            "زين": "زين جداً"
        }
        
        for omani, standard in omani_pronunciations.items():
            text = text.replace(omani, standard)
        
        return text
    
    def get_voice_info(self) -> dict:
        """
        Get information about the current voice settings.
        
        Returns:
            Dictionary with voice information
        """
        return {
            "engine": self.active_engine,
            "language": self.voice_settings["language"],
            "rate": self.voice_settings["rate"],
            "volume": self.voice_settings["volume"],
            "available_engines": self._get_available_engines()
        }
    
    def _get_available_engines(self) -> list:
        """
        Get list of available TTS engines.
        
        Returns:
            List of available engine names
        """
        available = []
        
        if self._test_espeak():
            available.append("espeak")
        if HAS_GTTS:
            available.append("gtts")
        if HAS_PYTTSX3:
            available.append("pyttsx3")
        
        return available
    
    def set_voice_settings(self, **kwargs):
        """
        Update voice settings.
        
        Args:
            **kwargs: Voice settings to update
        """
        for key, value in kwargs.items():
            if key in self.voice_settings:
                self.voice_settings[key] = value
                logger.info(f"Updated {key} to {value}")
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info("TTS temporary files cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup TTS files: {e}")
    
    def __del__(self):
        """Destructor to cleanup resources."""
        self.cleanup()
