# Mental Health Support Application

A full-stack mental health support system featuring a professional React frontend and a robust Python backend. Leverages Microsoft Azure Cognitive Services, Groq API, and the Claude Opus code for efficient, high-quality speech interactions.

## 🚀 Overview

- **Frontend**: React 18 + TypeScript with Material-UI and Emotion for a polished, responsive UI.
- **Backend**: FastAPI (Python 3.8+) providing REST endpoints for chat, audio processing, and system health.
- **AI Integrations**:
  - **Azure Speech Services**: Real-time speech-to-text and text-to-speech.
  - **Groq API**: Hardware-accelerated inference for natural language understanding.
    

## 🌟 Key Features

### 1. Professional React UI
- Modern design with Material-UI components
- Responsive layout (desktop, tablet, mobile)
- RTL support for Arabic and English (dynamic switching)
- Smooth animations and theme customization

### 2. Voice Interaction
- Browser-based recording and file upload (MP3, WAV, OGG, M4A)
- Real-time transcription via Azure Speech-to-Text
- Compressed playback using Azure TTS + Clause Opus encoder
- Visual recording indicators and audio timelines

### 3. AI-Powered Chat
- Persistent conversation history
- Intent detection and recommendations via Groq API
- Crisis detection with real-time alerts
- Cultural context engine tailored to Omani and Islamic values

### 4. System Monitoring & Emergency Support
- Health dashboard showing service status and performance metrics
- Quick access to local emergency contacts and resources
- Configurable alerts for service disruptions



### 2. Manual Setup

**Backend**
```powershell
cd backend
pip install -r requirements.txt
pip install -r api_requirements.txt
python api/main.py
```

**Frontend**
```powershell
cd frontend/react-app
npm install
npm start
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in **backend** and **frontend/react-app**:

**Backend `.env`**
```env
GROQ_API_KEY=your_groq_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
```

**Frontend `.env`**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GROQ_API_KEY=your_groq_key
REACT_APP_GROQ_ENDPOINT=https://api.groq.dev/v1
``` 

## 🛠️ Technology Stack

**Frontend**
- React 18 + TypeScript
- Material-UI (MUI) v5 & Emotion
- Axios for HTTP requests
- Web Audio API & Clause Opus codec

**Backend**
- FastAPI + Uvicorn
- Python 3.8+ with asyncio
- Whisper & Azure Speech SDK
- Groq API client

