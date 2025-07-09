# OMANI Therapist React UI

A professional React-based user interface for the OMANI Therapist mental health support system.

## Features

- **Modern React UI**: Built with React 18, TypeScript, and Material-UI
- **Bilingual Support**: Arabic and English language support
- **Voice Integration**: Audio recording and file upload capabilities
- **Real-time Chat**: Interactive chat interface with typing indicators
- **System Status**: Real-time system health monitoring
- **Emergency Contacts**: Quick access to emergency services
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Cultural Sensitivity**: Designed with Islamic values and Omani culture in mind

## Technology Stack

- **Frontend**: React 18 with TypeScript
- **UI Framework**: Material-UI (MUI) v5
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Audio Processing**: Web Audio API
- **Styling**: Emotion (styled-components)

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Modern web browser with audio support

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys and configuration.

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Project Structure

```
src/
├── components/           # React components
│   ├── ChatInterface.tsx # Main chat interface
│   ├── VoiceRecorder.tsx # Audio recording component
│   ├── SystemStatus.tsx  # System health display
│   ├── EmergencyContacts.tsx # Emergency contact info
│   └── LanguageSelector.tsx # Language switcher
├── services/            # API services
│   └── apiService.ts    # Main API client
├── utils/               # Utility functions
│   └── translations.ts  # Translation strings
├── App.tsx              # Main app component
└── index.tsx            # Entry point
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GROQ_API_KEY=your_groq_api_key
REACT_APP_AZURE_OPENAI_API_KEY=your_azure_key
REACT_APP_AZURE_OPENAI_ENDPOINT=your_azure_endpoint
```

### API Integration

The app connects to the Python backend via REST API:

- `POST /api/chat/message` - Send text message
- `POST /api/audio/process` - Process audio file
- `GET /api/system/status` - Get system health
- `POST /api/chat/clear` - Clear conversation

