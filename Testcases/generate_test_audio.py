#!/usr/bin/env python3
"""
Test Audio Generator for Omani-Therapist-Voice

This script generates test audio files from predefined Arabic text
using the system's TTS engine.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import TTS module
try:
    from Text_to_Speech.arabic_tts import OmaniTTS
except ImportError as e:
    logger.error(f"Failed to import TTS module: {e}")
    raise


def generate_test_audio():
    """Generate test audio files from predefined text."""
    # Initialize TTS engine
    tts = OmaniTTS()
    
    # Create output directory
    output_dir = Path(__file__).parent / "test_data" / "audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define test texts
    test_texts = {
        # Speech recognition test texts
        "basic_greeting": "السلام عليكم، كيف حالك؟",
        "medical_terms": "أشعر بالقلق والاكتئاب منذ فترة طويلة",
        "code_switching": "أنا feeling depressed لأنني failed الامتحان",
        "background_noise": "لدي صعوبة في التركيز على عملي",
        "female_speaker": "أحتاج إلى مساعدة للتعامل مع ضغوط الحياة",
        "male_speaker": "أشعر بالتوتر عندما أتحدث أمام الآخرين",
        "child_speaker": "أخاف من الذهاب إلى المدرسة كل يوم",
        
        # Emotion test texts
        "anxiety": "أشعر بالتوتر الشديد. قلبي يدق بسرعة وأجد صعوبة في التنفس. أخاف من المستقبل ولا أعرف ماذا سيحدث.",
        "depression": "لا أشعر برغبة في فعل أي شيء. أنام كثيراً ولا أستطيع الاستمتاع بالأشياء التي كنت أحبها. الحياة تبدو بلا معنى.",
        "mixed_emotions": "أنا سعيد بنجاحي في العمل لكنني قلق جداً من مشاكل عائلتي. لا أعرف إن كنت أشعر بالفرح أم بالحزن.",
        "cultural_expression": "أشعر بالعيب من مشاركة مشاعري. عائلتي تقول إن الرجل يجب أن يكون قوياً ولا يُظهر ضعفه.",
        "subtle_emotion": "الأمور تسير بشكل جيد. لدي عمل مستقر وعائلة جيدة. نعم، كل شيء على ما يرام.",
        
        # Crisis test texts
        "suicidal": "لا أستطيع الاستمرار في الحياة. أفكر في الانتحار كل يوم. لقد كتبت وصيتي بالفعل.",
        "self_harm": "عندما أشعر بألم نفسي، أقطع نفسي لأشعر بشيء حقيقي. ذراعي مليء بالجروح.",
        "severe_anxiety": "قلبي يدق بسرعة جنونية. لا أستطيع التنفس. أشعر أنني سأموت الآن. هذا هلع حقيقي.",
        "substance_abuse": "أشرب الكحول كل يوم لأنسى مشاكلي. لا أستطيع التوقف حتى لو حاولت.",
        "immediate_danger": "لقد قررت إنهاء حياتي الليلة. لدي خطة واضحة وسأنفذها حالما ننتهي من المحادثة.",
        
        # Performance test texts
        "short_input": "مرحباً، كيف يمكنني مساعدتك اليوم؟",
        "medium_input": "أشعر بالقلق حول عملي. مديري يضغط علي كثيراً وأنا لا أعرف كيف أتعامل مع هذا الضغط.",
        "long_input": """أنا أعاني من مشاكل في علاقتي مع زوجتي. نحن متزوجان منذ خمس سنوات ولدينا طفلان. 
        المشكلة أننا لا نتواصل بشكل جيد. هي تقول إنني لا أصغي إليها وأنا أشعر أنها لا تقدر جهودي في العمل والمنزل. 
        نتشاجر كثيراً خاصة حول تربية الأطفال وإدارة أمورنا المالية. أخاف أن تنهار علاقتنا ولا أعرف ماذا أفعل.""",
    }
    
    # Generate audio files
    for name, text in test_texts.items():
        try:
            output_file = output_dir / f"{name}.mp3"
            
            logger.info(f"Generating audio for '{name}'")
            
            # Generate speech
            tts.synthesize_speech(text, output_file=str(output_file))
            
            logger.info(f"Generated: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate audio for '{name}': {e}")
    
    logger.info(f"Audio generation complete. Files saved to: {output_dir}")


# Special handling for female and male speakers
def generate_gender_specific_audio():
    """Generate gender-specific test audio using voice parameters."""
    # Initialize TTS engine
    tts = OmaniTTS()
    
    # Create output directory
    output_dir = Path(__file__).parent / "test_data" / "audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # Female voice sample
    female_text = "أحتاج إلى مساعدة للتعامل مع ضغوط الحياة"
    female_file = output_dir / "female_speaker.mp3"
    
    # Try to set female voice parameters
    tts.voice_settings["voice_id"] = "ar-female"  # Voice ID depends on TTS engine
    tts.voice_settings["pitch"] = 1.2  # Higher pitch for female voice
    
    # Generate female voice
    logger.info("Generating female voice sample")
    tts.synthesize_speech(female_text, output_file=str(female_file))
    
    # Male voice sample
    male_text = "أشعر بالتوتر عندما أتحدث أمام الآخرين"
    male_file = output_dir / "male_speaker.mp3"
    
    # Set male voice parameters
    tts.voice_settings["voice_id"] = "ar-male"  # Voice ID depends on TTS engine
    tts.voice_settings["pitch"] = 0.9  # Lower pitch for male voice
    
    # Generate male voice
    logger.info("Generating male voice sample")
    tts.synthesize_speech(male_text, output_file=str(male_file))
    
    # Child voice (simulated)
    child_text = "أخاف من الذهاب إلى المدرسة كل يوم"
    child_file = output_dir / "child_speaker.mp3"
    
    # Set child voice parameters
    tts.voice_settings["voice_id"] = "ar-female"  # Base on female voice
    tts.voice_settings["pitch"] = 1.5  # Much higher pitch for child voice
    tts.voice_settings["rate"] = 1.1  # Slightly faster rate
    
    # Generate child voice
    logger.info("Generating child voice sample")
    tts.synthesize_speech(child_text, output_file=str(child_file))
    
    logger.info("Gender-specific audio generation complete")


if __name__ == "__main__":
    generate_test_audio()
    try:
        generate_gender_specific_audio()
    except Exception as e:
        logger.warning(f"Could not generate gender-specific audio: {e}")
        logger.warning("Continuing with generic voice samples only")
    
    logger.info("Test audio generation complete")
