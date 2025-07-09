#!/usr/bin/env python3
"""
FastAPI backend for OMANI Therapist React UI
"""
import os
import sys
import random
import tempfile
import uvicorn
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
env_path = backend_dir / ".env"
load_dotenv(env_path)  # Add this line

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Print environment loading status
logger.info(f"Loading environment variables from: {env_path}")
logger.info(f"Environment file exists: {env_path.exists()}")
logger.info(f"GROQ_API_KEY loaded: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
logger.info(f"AZURE_OPENAI_API_KEY loaded: {'Yes' if os.getenv('AZURE_OPENAI_API_KEY') else 'No'}")

# Import backend modules
try:
    from speech_to_Text.whisper import create_omani_stt
    from llm.openai_client import create_azure_omani_llm
    BACKEND_AVAILABLE = True
    logger.info("Backend modules loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import backend modules: {e}")
    BACKEND_AVAILABLE = False

# Temporarily comment out:
# from frontend.audio_helper import AudioHelper

# Add this simple helper class instead:
class SimpleAudioHelper:
    @staticmethod
    def validate_audio_file(file_path: str):
        """Simple validation"""
        if not os.path.exists(file_path):
            return False, "File not found"
        if os.path.getsize(file_path) == 0:
            return False, "Empty file"
        return True, "Valid"
    
    @staticmethod
    def create_temp_audio_file(audio_data: bytes, extension: str = '.wav') -> str:
        """Create temp file"""
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
        temp_file.write(audio_data)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """Clean up temp file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass

# FastAPI app
app = FastAPI(
    title="OMANI Therapist API",
    description="API for OMANI Therapist React UI",
    version="1.0.0"
)

# CORS middleware - Fixed configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Add backup port
        "http://127.0.0.1:3001"
    ],
    allow_credentials=False,  # Changed to False to match frontend
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=86400,  # 24 hours
)

# Global variables for AI engines
stt_engine = None
llm_engine = None
conversation_history = []

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    language: str = "arabic"
    timestamp: str = None

class ChatResponse(BaseModel):
    response: str
    confidence: float = 0.0
    language: str = "arabic"
    safety_score: float = 0.0

class SystemStatus(BaseModel):
    stt_ready: bool
    llm_ready: bool
    services_healthy: bool
    last_check: str

class AudioTranscription(BaseModel):
    text: str
    confidence: float
    language: str
    duration: float

@app.on_event("startup")
async def startup_event():
    """Initialize AI engines on startup"""
    global stt_engine, llm_engine
    
    try:
        if BACKEND_AVAILABLE:
            logger.info("Initializing AI engines...")
            stt_engine = create_omani_stt("groq")
            llm_engine = create_azure_omani_llm()
            logger.info("AI engines initialized successfully")
        else:
            logger.warning("Backend modules not available, running in demo mode")
    except Exception as e:
        logger.error(f"Failed to initialize AI engines: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "OMANI Therapist API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/system/status")
async def get_system_status():
    """Get system status"""
    return SystemStatus(
        stt_ready=stt_engine is not None,
        llm_ready=llm_engine is not None,
        services_healthy=True,
        last_check=datetime.now().isoformat()
    )

@app.post("/api/chat/message")
async def send_message(message: ChatMessage):
    """Send a text message to the AI"""
    global conversation_history
    
    try:
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.now().isoformat()
        })
        
        if llm_engine:
            # Generate response using LLM
            response_data = await llm_engine.generate_therapeutic_response(
                message.message
            )
            response_text = response_data.get("response", "I understand. Let me help you.")
        else:
            # Demo response
            response_text = generate_demo_response(message.message, message.language)
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        return ChatResponse(
            response=response_text,
            confidence=0.85,
            language=message.language,
            safety_score=0.95
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), language: str = "arabic"):
    """Transcribe audio file with enhanced error handling"""
    audio_path = None
    try:
        # Validate upload
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        logger.info(f"Processing audio upload: {audio.filename}, type: {audio.content_type}")
        
        # Read and validate content
        content = await audio.read()
        if not content or len(content) == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")
        
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="Audio file too large (max 10MB)")
        
        # Create temporary file
        audio_path = SimpleAudioHelper.create_temp_audio_file(content, '.wav')
        
        # Validate the created file
        is_valid, error_msg = SimpleAudioHelper.validate_audio_file(audio_path)
        if not is_valid:
            raise HTTPException(status_code=422, detail=f"Invalid audio file: {error_msg}")
        
        logger.info(f"Audio file validated successfully: {audio_path}")
        
        # Process with STT engine
        if stt_engine:
            try:
                transcription = await stt_engine.transcribe_audio(audio_path)
                if not transcription or not transcription.strip():
                    raise HTTPException(status_code=422, detail="Could not transcribe audio - no speech detected")
                
                logger.info(f"Transcription successful: {transcription[:50]}...")
                
                return AudioTranscription(
                    text=transcription,
                    confidence=0.9,
                    language=language,
                    duration=10.0
                )
                
            except Exception as stt_error:
                logger.error(f"STT engine error: {stt_error}")
                raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(stt_error)}")
        else:
            # Fallback to demo transcription
            demo_text = generate_demo_transcription(language)
            logger.info(f"Using demo transcription: {demo_text}")
            
            return AudioTranscription(
                text=demo_text,
                confidence=0.8,
                language=language,
                duration=5.0
            )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error in audio transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    finally:
        # Clean up temporary file
        if audio_path:
            SimpleAudioHelper.cleanup_temp_file(audio_path)

@app.post("/api/audio/process")
async def process_audio(audio: UploadFile = File(...), language: str = "arabic"):
    """Process audio file and generate response with enhanced error handling"""
    try:
        logger.info(f"Processing audio for response: {audio.filename}")
        
        # First transcribe the audio
        transcription_result = await transcribe_audio(audio, language)
        
        if not transcription_result or not transcription_result.text:
            raise HTTPException(status_code=422, detail="No transcription obtained from audio")
        
        logger.info(f"Audio transcribed successfully, generating response...")
        
        # Generate therapeutic response
        message = ChatMessage(
            message=transcription_result.text,
            language=language
        )
        
        response = await send_message(message)
        
        # Add transcription info to response
        if hasattr(response, 'transcription'):
            response.transcription = transcription_result.text
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing audio for response: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/chat/clear")
async def clear_conversation():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    
    if llm_engine:
        llm_engine.clear_conversation_history()
    
    return {"message": "Conversation cleared"}

@app.get("/api/chat/history")
async def get_conversation_history():
    """Get conversation history"""
    return {"messages": conversation_history}

@app.post("/api/emergency/report")
async def report_emergency(details: dict):
    """Report an emergency (log for now)"""
    logger.warning(f"Emergency reported: {details}")
    return {"message": "Emergency reported successfully"}

def generate_demo_response(message: str, language: str) -> str:
    """Generate a demo response when LLM is not available"""
    responses = {
        "arabic": [
            "أفهم مشاعرك وأقدر ثقتك في التحدث معي.",
            "شكراً لك على مشاركة هذا معي. مشاعرك مهمة ومعتبرة.",
            "أسمعك وأفهم ما تمر به. هل تريد التحدث أكثر عن ما يضايقك؟",
            "يتطلب الأمر شجاعة للتواصل. أنا هنا لدعمك.",
            "صحتك النفسية مهمة. دعنا نعمل على هذا معاً.",
        ],
        "english": [
            "I understand your feelings and appreciate your trust in talking to me.",
            "Thank you for sharing this with me. Your feelings are important and valid.",
            "I hear you and understand what you're going through. Would you like to talk more about what's bothering you?",
            "It takes courage to reach out. I'm here to support you.",
            "Your mental health matters. Let's work through this together.",
        ]
    }
    
    import random
    return random.choice(responses.get(language, responses["english"]))

def generate_demo_transcription(language: str) -> str:
    """Generate demo transcription when STT is not available"""
    transcriptions = {
        "arabic": "مرحبا، أشعر بالحزن اليوم وأحتاج إلى التحدث مع شخص ما",
        "english": "Hello, I am feeling sad today and need to talk to someone"
    }
    return transcriptions.get(language, transcriptions["english"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
