import base64
import httpx
import asyncio
import librosa
import numpy as np
import logging
from typing import Optional, Union
import os
import tempfile
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class OmaniSTT:
   
    def __init__(self, provider: str = "gemini", api_key: str = None, model_name: str = None):
        """
        Initialize the STT engine with API provider.
        
        Args:
            provider: API provider ('gemini' or 'groq')
            api_key: API key for the chosen provider
            model_name: Model name (optional, uses defaults)
        """
        try:
            self.provider = provider.lower()
            self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
            
            if not self.api_key:
                raise ValueError(f"API key required for {provider}. Set {provider.upper()}_API_KEY environment variable.")
            
            # Set up provider-specific configurations
            if self.provider == "gemini":
                self.model_name = model_name or "gemini-1.5-pro"
                self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                self.headers = {"Content-Type": "application/json"}
            elif self.provider == "groq":
                self.model_name = model_name or "whisper-large-v3"
                self.api_url = "https://api.groq.com/openai/v1/audio/transcriptions"
                self.headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "multipart/form-data"
                }
            else:
                raise ValueError(f"Unsupported provider: {provider}. Use 'gemini' or 'groq'")
            
            # Omani dialect specific prompts and context
            self.omani_context = {
                "initial_prompt": "هذا محادثة باللهجة العمانية والعربية الخليجية. يرجى النسخ بدقة مع مراعاة اللهجة المحلية العمانية.",
                "language": "ar",
                "task": "transcribe",
                "cultural_context": "Omani dialect Arabic transcription"
            }
            
            # Common Omani words and phrases for better recognition
            self.omani_vocabulary = [
                "شلونك", "كيفك", "وش أخبارك", "حمدالله", "إن شاء الله",
                "والله", "يالله", "طيب", "زين", "صج", "لا والله",
                "ما شاء الله", "سبحان الله", "الحمد لله", "بسم الله",
                "عساك بخير", "الله يعطيك العافية", "مشكور"
            ]
            
            logger.info(f"{provider.capitalize()} STT initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize {provider} STT: {e}")
            raise
    
    async def transcribe_audio(self, audio_input) -> Optional[str]:
        """
        Transcribe audio to text using the configured API provider.
        
        Args:
            audio_input: Audio file path or numpy array
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Handle different input types
            if isinstance(audio_input, str):
                audio_path = audio_input
            else:
                # Convert numpy array to temporary WAV file
                audio_path = self._save_temp_audio(audio_input)
            
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return None
            
            # Transcribe based on provider
            if self.provider == "gemini":
                return await self._transcribe_with_gemini(audio_path)
            elif self.provider == "groq":
                return await self._transcribe_with_groq(audio_path)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    async def _transcribe_with_gemini(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Google Gemini API.
        """
        try:
            # Convert audio to base64
            audio_data = self._audio_to_base64(audio_path)
            
            url = self.api_url.format(model=self.model_name) + f"?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": f"Please transcribe this Arabic audio with focus on Omani dialect. {self.omani_context['initial_prompt']}"
                        },
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": audio_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1000
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    return self._postprocess_omani_text(text.strip())
                
                return None
                
        except Exception as e:
            logger.error(f"Gemini transcription failed: {e}")
            return None
    
    async def _transcribe_with_groq(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Groq API.
        """
        try:
            # Prepare multipart form data
            files = {
                "file": (os.path.basename(audio_path), open(audio_path, "rb"), "audio/wav"),
                "model": (None, self.model_name),
                "language": (None, "ar"),
                "prompt": (None, self.omani_context["initial_prompt"]),
                "temperature": (None, "0.1")
            }
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, files=files, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                if "text" in result:
                    return self._postprocess_omani_text(result["text"].strip())
                
                return None
                
        except Exception as e:
            logger.error(f"Groq transcription failed: {e}")
            return None
        finally:
            # Close file if opened
            try:
                files["file"][1].close()
            except:
                pass
    
    def _audio_to_base64(self, audio_path: str) -> str:
        """
        Convert audio file to base64 string.
        """
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            return base64.b64encode(audio_bytes).decode('utf-8')
    
    def _save_temp_audio(self, audio_data) -> str:
        """
        Save audio data to temporary WAV file.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Path to temporary audio file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Convert and save audio
            if isinstance(audio_data, np.ndarray):
                # Normalize audio
                audio_data = audio_data.astype(np.float32)
                if audio_data.max() > 1.0:
                    audio_data = audio_data / np.abs(audio_data).max()
                
                # Save as WAV using wave module
                import wave
                with wave.open(temp_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(16000)  # 16kHz
                    
                    # Convert to 16-bit PCM
                    audio_16bit = (audio_data * 32767).astype(np.int16)
                    wav_file.writeframes(audio_16bit.tobytes())
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to save temporary audio: {e}")
            raise
    
    def transcribe_audio_sync(self, audio_input) -> Optional[str]:
        """
        Synchronous wrapper for transcribe_audio.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.transcribe_audio(audio_input))
        finally:
            loop.close()
    
    def _postprocess_omani_text(self, text: str) -> str:
        """
        Post-process transcribed text for Omani dialect normalization.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Processed text with Omani dialect corrections
        """
        # Common transcription corrections for Omani dialect
        corrections = {
            # Common API mistakes with Arabic
            "شلون": "شلونك",
            "كيف": "كيفك", 
            "وش": "وش أخبارك",
            "ان شاء الله": "إن شاء الله",
            "ما شاء الله": "ما شاء الله",
            "الحمد لله": "الحمد لله",
            "سبحان الله": "سبحان الله",
            "بسم الله": "بسم الله",
            "عساك بخير": "عساك بخير",
            "الله يعطيك العافية": "الله يعطيك العافية"
        }
        
        processed_text = text
        
        # Apply corrections
        for mistake, correction in corrections.items():
            processed_text = processed_text.replace(mistake, correction)
        
        # Clean up extra spaces and normalize
        processed_text = " ".join(processed_text.split())
        
        # Remove any unwanted characters that might come from API responses
        processed_text = processed_text.replace("**", "").replace("*", "")
        
        return processed_text
    
    def is_speech_detected(self, audio_path: str, threshold: float = 0.1) -> bool:
        """
        Check if the audio contains speech above the threshold.
        
        Args:
            audio_path: Path to audio file
            threshold: Minimum energy threshold for speech detection
            
        Returns:
            True if speech is detected, False otherwise
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Calculate RMS energy
            rms_energy = librosa.feature.rms(y=audio)[0]
            avg_energy = np.mean(rms_energy)
            
            return avg_energy > threshold
            
        except Exception as e:
            logger.error(f"Speech detection failed: {e}")
            return False
    
    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds or None if failed
        """
        try:
            audio, sr = librosa.load(audio_path, sr=None)
            duration = len(audio) / sr
            return duration
            
        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            return None

# Factory function for easy instantiation
def create_omani_stt(provider: str = "gemini", **kwargs) -> OmaniSTT:
    """
    Factory function to create OmaniSTT instance with proper configuration.
    
    Args:
        provider: Either 'gemini' or 'groq'
        **kwargs: Additional arguments passed to OmaniSTT constructor
        
    Returns:
        Configured OmaniSTT instance
        
    Example:
        # Using Gemini
        stt = create_omani_stt("gemini", api_key="your_key")
        
        # Using Groq
        stt = create_omani_stt("groq", api_key="your_key")
    """
    return OmaniSTT(provider=provider, **kwargs)

def setup_environment_variables():
    """
    Setup instructions for environment variables.
    """
    instructions = {
        "gemini": {
            "env_var": "GEMINI_API_KEY",
            "description": "Get API key from Google AI Studio: https://makersuite.google.com/app/apikey",
            "setup": "export GEMINI_API_KEY=your_api_key_here"
        },
        "groq": {
            "env_var": "GROQ_API_KEY", 
            "description": "Get API key from Groq Console: https://console.groq.com/keys",
            "setup": "export GROQ_API_KEY=your_api_key_here"
        }
    }
    return instructions
