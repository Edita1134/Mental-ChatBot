

import streamlit as st
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv
import tempfile
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import audio-recorder, but provide fallback
try:
    from streamlit_audiorec import st_audiorec
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

# Import components
from src.stt.whisper_stt import create_omani_stt
from src.llm.azure_openai_client import create_azure_omani_llm

# Set page configuration
st.set_page_config(
    page_title="OMANI Therapist",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stt_engine" not in st.session_state:
    st.session_state.stt_engine = None
if "llm_engine" not in st.session_state:
    st.session_state.llm_engine = None
if "components_ready" not in st.session_state:
    st.session_state.components_ready = False
if "language" not in st.session_state:
    st.session_state.language = "arabic"
if "processing_audio" not in st.session_state:
    st.session_state.processing_audio = False

# Language dictionaries
TRANSLATIONS = {
    "arabic": {
        "title": "🧠 المستشار النفسي العماني",
        "subtitle": "OMANI Therapist Voice Solution",
        "chat_placeholder": "اكتب رسالتك هنا... أو ارفع ملف صوتي",
        "audio_message": "أو سجل رسالة صوتية:",
        "upload_label": "📤 تحميل ملف صوتي (MP3, WAV, OGG)",
        "record_label": "🎤 اضغط للتسجيل:",
        "recording_unavailable": "التسجيل المباشر غير متاح. يرجى تحميل ملف صوتي.",
        "processing_audio": "جاري تحليل الصوت...",
        "thinking": "جاري التفكير...",
        "audio_processing": "🎤 جاري معالجة الرسالة الصوتية...",
        "audio_error": "عذراً، لم أتمكن من فهم الرسالة الصوتية. يرجى المحاولة مرة أخرى.",
        "system_status": "📊 حالة النظام",
        "stt_system": "نظام التعرف على الكلام",
        "llm_system": "نظام الذكاء الاصطناعي",
        "language_label": "اللغة",
        "safety_label": "الأمان",
        "safety_value": "مراعاة القيم الإسلامية والثقافة العمانية",
        "clear_chat": "مسح المحادثة",
        "about_section": "حول التطبيق",
        "about_text": "**المستشار النفسي العماني** هو نظام ذكاء اصطناعي مصمم خصيصاً للثقافة العمانية واللهجة العربية، يقدم دعماً نفسياً مع مراعاة القيم الإسلامية والعادات المحلية.",
        "initializing": "جاري تهيئة المكونات...",
        "language_selector": "🌍 اختر اللغة:",
        "error_prefix": "❌ خطأ:",
        "audio_error_prefix": "❌ خطأ في معالجة الصوت:",
        "upload_success": "✅ تم تحميل الملف الصوتي بنجاح",
        "process_button": "🚀 معالجة الرسالة الصوتية",
        "emergency_contacts": "📞 جهات الاتصال الطارئة",
        "emergency_info": """
        **🆘 في حالة الطوارئ:**
        - الطوارئ العامة: 999
        - مستشفى السلطان قابوس: 24211411
        - الصحة النفسية: متاح 24/7
        """
    },
    "english": {
        "title": "🧠 OMANI Therapist",
        "subtitle": "Omani Psychological Support Assistant",
        "chat_placeholder": "Type your message here... or upload an audio file",
        "audio_message": "Or record a voice message:",
        "upload_label": "📤 Upload Audio File (MP3, WAV, OGG)",
        "record_label": "🎤 Press to Record:",
        "recording_unavailable": "Direct recording unavailable. Please upload an audio file.",
        "processing_audio": "Processing audio...",
        "thinking": "Thinking...",
        "audio_processing": "🎤 Processing voice message...",
        "audio_error": "Sorry, I couldn't understand the voice message. Please try again.",
        "system_status": "📊 System Status",
        "stt_system": "Speech Recognition System",
        "llm_system": "AI System",
        "language_label": "Language",
        "safety_label": "Safety",
        "safety_value": "Respectful of Islamic values and Omani culture",
        "clear_chat": "Clear Chat",
        "about_section": "About",
        "about_text": "**OMANI Therapist** is an AI system designed for Omani culture and Arabic dialect, providing psychological support while respecting Islamic values and local customs.",
        "initializing": "Initializing components...",
        "language_selector": "🌍 Select Language:",
        "error_prefix": "❌ Error:",
        "audio_error_prefix": "❌ Error processing audio:",
        "upload_success": "✅ Audio file uploaded successfully",
        "process_button": "🚀 Process Voice Message",
        "emergency_contacts": "📞 Emergency Contacts",
        "emergency_info": """
        **🆘 In case of emergency:**
        - General Emergency: 999
        - Sultan Qaboos Hospital: 24211411
        - Mental Health Hotline: Available 24/7
        """
    }
}

def get_text(key):
    """Get text in the current language."""
    return TRANSLATIONS[st.session_state.language].get(key, key)

@st.cache_resource
def initialize_components():
    """Initialize the AI components with caching."""
    try:
        logger.info("Initializing STT engine...")
        stt_engine = create_omani_stt("groq")
        
        logger.info("Initializing LLM engine...")
        llm_engine = create_azure_omani_llm()
        
        logger.info("All components initialized successfully")
        return stt_engine, llm_engine, True
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        st.error(f"❌ {get_text('error_prefix')} {str(e)}")
        return None, None, False

def process_text_sync(message: str):
    """Process text message synchronously."""
    if not message.strip():
        return
    
    try:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": message})
        
        # Generate response
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response_data = loop.run_until_complete(
                st.session_state.llm_engine.generate_therapeutic_response(
                    message, 
                )
            )
            response = response_data.get("response", f"{get_text('error_prefix')} An error occurred.")
        finally:
            loop.close()
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        st.error(f"{get_text('error_prefix')} {str(e)}")

def process_audio_sync(audio_file):
    """Process audio file synchronously."""
    if not audio_file:
        return
    
    try:
        # Show processing message
        with st.chat_message("assistant"):
            st.markdown(get_text('audio_processing'))
        
        # Save audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_file.read())
            audio_path = tmp_file.name
        
        # Process audio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Transcribe audio
            logger.info(f"Transcribing audio file: {audio_path}")
            transcription = loop.run_until_complete(
                st.session_state.stt_engine.transcribe_audio(audio_path)
            )
            
            if transcription and transcription.strip():
                # Add transcription as user message
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"🎤 {transcription}"
                })
                
                # Generate therapeutic response
                logger.info("Generating therapeutic response...")
                response_data = loop.run_until_complete(
                    st.session_state.llm_engine.generate_therapeutic_response(
                        transcription,
                    )
                )
                response = response_data.get("response", f"{get_text('error_prefix')} An error occurred.")
                
                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })
                
                logger.info("Audio processing completed successfully")
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": get_text('audio_error')
                })
                logger.warning("No transcription received")
                
        finally:
            loop.close()
            # Clean up temporary file
            try:
                os.unlink(audio_path)
            except Exception as cleanup_error:
                logger.warning(f"Could not clean up temp file: {cleanup_error}")
                
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        st.error(f"{get_text('audio_error_prefix')} {str(e)}")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"{get_text('audio_error_prefix')} {str(e)}"
        })

def main():
    """Main function to create Streamlit UI."""
    # Custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@400;500;600&display=swap');
    
    .rtl {
        direction: rtl;
        text-align: right;
        font-family: 'Amiri', serif;
    }
    
    .ltr {
        direction: ltr;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .emergency-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #155724;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Language selector at the top
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        language_option = st.selectbox(
            get_text('language_selector'),
            options=["arabic", "english"],
            index=0 if st.session_state.language == "arabic" else 1,
            format_func=lambda x: "🇴🇲 العربية" if x == "arabic" else "🇬🇧 English",
            key="language_selector"
        )
        
        if language_option != st.session_state.language:
            st.session_state.language = language_option
            st.rerun()
    
    # Header
    st.markdown(f"<h1 class='main-title'>{get_text('title')}</h1>", unsafe_allow_html=True)
    subtitle_class = 'rtl' if st.session_state.language == 'arabic' else 'ltr'
    st.markdown(f"<h3 class='main-title {subtitle_class}'>{get_text('subtitle')}</h3>", unsafe_allow_html=True)
    
    # Check environment variables
    required_vars = ["GROQ_API_KEY", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        st.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        st.info("Please check your .env file and restart the application.")
        return
    
    # Initialize components
    if not st.session_state.components_ready:
        with st.spinner(get_text('initializing')):
            stt_engine, llm_engine, ready = initialize_components()
            if ready:
                st.session_state.stt_engine = stt_engine
                st.session_state.llm_engine = llm_engine
                st.session_state.components_ready = True
                st.success("✅ Components initialized successfully!")
            else:
                st.error("❌ Failed to initialize components")
                return
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.markdown("### 💬 Chat Interface")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Text input
        user_input = st.chat_input(get_text('chat_placeholder'))
        if user_input:
            process_text_sync(user_input)
            st.rerun()
        
        # Audio upload section
        st.markdown("---")
        st.markdown("### 🎤 Voice Message")
        
        audio_file = st.file_uploader(
            get_text('upload_label'),
            type=["wav", "mp3", "ogg", "m4a"],
            help="Upload an audio file to process with voice recognition"
        )
        
        if audio_file:
            st.markdown(f"<div class='success-box'>{get_text('upload_success')}</div>", unsafe_allow_html=True)
            
            # Audio player
            st.audio(audio_file, format='audio/wav')
            
            # Process button
            if st.button(get_text('process_button')):
                with st.spinner(get_text('processing_audio')):
                    process_audio_sync(audio_file)
                st.rerun()
    
    with col2:
        # Sidebar content
        st.markdown(f"### {get_text('system_status')}")
        
        status_items = [
            f"**{get_text('stt_system')}**: Groq Whisper",
            f"**{get_text('llm_system')}**: Azure OpenAI GPT-4o",
            f"**{get_text('language_label')}**: {'العربية العمانية' if st.session_state.language == 'arabic' else 'Omani Arabic + English'}",
            f"**{get_text('safety_label')}**: {get_text('safety_value')}"
        ]
        
        for item in status_items:
            st.markdown(f"- {item}")
        
        # Clear chat button
        if st.button(get_text('clear_chat')):
            st.session_state.messages = []
            if st.session_state.llm_engine:
                st.session_state.llm_engine.clear_conversation_history()
            st.rerun()
        
        # Emergency contacts
        st.markdown("---")
        st.markdown(f"### {get_text('emergency_contacts')}")
        st.markdown(f"<div class='emergency-box'>{get_text('emergency_info')}</div>", unsafe_allow_html=True)
        
        # About section
        st.markdown("---")
        st.markdown(f"### {get_text('about_section')}")
        st.markdown(get_text('about_text'))
        
        # Version info
        st.markdown("---")
        st.markdown("**Version**: 1.0.0")
        st.markdown("**Build**: Streamlit + Azure OpenAI + Groq")

if __name__ == "__main__":
    main()
