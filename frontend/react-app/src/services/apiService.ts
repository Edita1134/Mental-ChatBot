import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 60000, // Increase timeout to 60 seconds
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Change to false to avoid CORS issues
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isAudio?: boolean;
}

export interface ChatResponse {
  response: string;
  confidence?: number;
  language?: string;
  safety_score?: number;
}

export interface AudioTranscription {
  text: string;
  confidence: number;
  language: string;
  duration: number;
}

export interface SystemStatus {
  stt_ready: boolean;
  llm_ready: boolean;
  services_healthy: boolean;
  last_check: string;
}

class ApiService {
  async sendMessage(message: string, language: string = 'arabic'): Promise<ChatResponse> {
    try {
      const response = await apiClient.post('/api/chat/message', {
        message,
        language,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw new Error('Failed to send message');
    }
  }

  async transcribeAudio(audioFile: File, language: string = 'arabic'): Promise<AudioTranscription> {
    try {
      console.log('Starting audio transcription...', {
        name: audioFile.name,
        size: audioFile.size,
        type: audioFile.type
      });

      // Validate file before upload
      if (audioFile.size === 0) {
        throw new Error('Audio file is empty');
      }

      if (audioFile.size > 10 * 1024 * 1024) {
        throw new Error('Audio file too large. Maximum size is 10MB.');
      }

      // Ensure proper MIME type
      let mimeType = audioFile.type;
      if (!mimeType || !mimeType.startsWith('audio/')) {
        const extension = audioFile.name.split('.').pop()?.toLowerCase();
        const mimeTypes: Record<string, string> = {
          'mp3': 'audio/mpeg',
          'wav': 'audio/wav',
          'ogg': 'audio/ogg',
          'm4a': 'audio/mp4',
          'aac': 'audio/aac'
        };
        mimeType = mimeTypes[extension || ''] || 'audio/wav';
      }

      // Create sanitized file
      const blob = audioFile.slice(0, audioFile.size, mimeType);
      const sanitizedFile = new File([blob], audioFile.name, { 
        type: mimeType,
        lastModified: Date.now()
      });

      const formData = new FormData();
      formData.append('audio', sanitizedFile);
      formData.append('language', language);

      // Calculate timeout based on file size
      const fileSize = sanitizedFile.size / (1024 * 1024);
      const timeout = Math.max(15000, fileSize * 15000);

      console.log(`Uploading ${sanitizedFile.name} (${mimeType}, ${sanitizedFile.size} bytes)`);

      const response = await apiClient.post('/api/audio/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: timeout,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
          console.log(`Upload progress: ${percentCompleted}%`);
        },
      });

      console.log('Transcription successful:', response.data);
      return response.data;

    } catch (error: any) {
      console.error('Transcription error:', error);

      // Handle specific error types
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timed out. Please try with a shorter audio file.');
      }

      if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || 'Unknown error';

        switch (status) {
          case 400:
            throw new Error(`Invalid audio file: ${detail}`);
          case 413:
            throw new Error('Audio file too large. Maximum size is 10MB.');
          case 415:
            throw new Error('Unsupported audio format. Please use WAV, MP3, OGG, or M4A.');
          case 422:
            throw new Error(`Could not process audio: ${detail}`);
          case 500:
            throw new Error(`Server error: ${detail}`);
          default:
            throw new Error(`Upload failed (${status}): ${detail}`);
        }
      }

      throw new Error('Network error. Please check your connection and try again.');
    }
  }
  
  async processAudio(audioFile: File, language: string = 'arabic'): Promise<ChatResponse> {
    try {
      // First check if server is accessible
      await this.healthCheck();
      
      console.log('Original audio file:', audioFile.name, audioFile.type, audioFile.size);
      
      // Make sure we have a valid MIME type
      let mimeType = audioFile.type;
      if (!mimeType || !mimeType.startsWith('audio/')) {
        const extension = audioFile.name.split('.').pop()?.toLowerCase();
        switch (extension) {
          case 'mp3': mimeType = 'audio/mpeg'; break;
          case 'wav': mimeType = 'audio/wav'; break;
          case 'ogg': mimeType = 'audio/ogg'; break;
          case 'm4a': mimeType = 'audio/mp4'; break;
          default: mimeType = 'audio/wav'; // Default to WAV
        }
        console.log(`Inferred MIME type '${mimeType}' from extension`);
      }
      
      const blob = audioFile.slice(0, audioFile.size, mimeType);
      const validatedFile = new File([blob], audioFile.name, { 
        type: mimeType,
        lastModified: Date.now()
      });
      
      const formData = new FormData();
      formData.append('audio', validatedFile);
      formData.append('language', language);

      console.log('Sending audio processing request:', validatedFile.name, validatedFile.type, validatedFile.size);

      // Validate audio file
      if (validatedFile.size === 0) {
        throw new Error('Audio file is empty');
      }

      if (validatedFile.size > 10 * 1024 * 1024) {
        throw new Error('Audio file is too large (max 10MB)');
      }
      
      // Calculate dynamic timeout based on file size
      const fileSize = validatedFile.size / (1024 * 1024); // in MB
      const timeout = Math.max(60000, fileSize * 30000); // min 60s, then 30s per MB
      
      console.log(`Using timeout of ${timeout}ms for audio processing`);
      
      const response = await apiClient.post('/api/audio/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json',
        },
        timeout: timeout,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
          console.log(`Upload progress: ${percentCompleted}%`);
        },
      });
      
      console.log('Audio processing response:', response.data);
      return response.data;
      
    } catch (error: any) {
      console.error('Error processing audio:', error);
      
      // Check if it's a connection error
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        throw new Error('Cannot connect to server. Please make sure the backend is running on port 8000.');
      }
      
      if (error.code === 'ECONNABORTED') {
        throw new Error('Audio processing timed out. Please try a shorter recording or check your internet connection.');
      }
      
      if (error.response) {
        console.error('Error response:', error.response.status, error.response.statusText, error.response.data);
        
        switch (error.response.status) {
          case 413:
            throw new Error('Audio file too large. Please try a shorter recording (max 10MB).');
          case 415:
            throw new Error('Unsupported audio format. Please try recording in WAV or MP3 format.');
          case 422:
            throw new Error(`Audio processing error: ${error.response.data?.detail || 'Unknown error'}`);
          case 500:
            const errorDetail = error.response.data?.detail || '';
            throw new Error(`Server error: ${errorDetail || 'Unknown error'}`);
          default:
            throw new Error(`Audio processing failed: ${error.response.status} ${error.response.statusText}`);
        }
      }
      
      throw new Error('Cannot connect to server. Please make sure the backend is running.');
    }
  }
  
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response = await apiClient.get('/api/system/status');
      return response.data;
    } catch (error) {
      console.error('Error getting system status:', error);
      throw new Error('Failed to get system status');
    }
  }

  async clearConversation(): Promise<void> {
    try {
      await apiClient.post('/api/chat/clear');
    } catch (error) {
      console.error('Error clearing conversation:', error);
      throw new Error('Failed to clear conversation');
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await apiClient.get('/api/health', { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error('Backend server is not running. Please start the server on port 8000.');
    }
  }

  async uploadAudio(file: File): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('audio', file);

      // Add timeout configuration
      const response = await apiClient.post('/api/audio/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
        onUploadProgress: (progressEvent) => {
          // Optional: Track upload progress
          console.log('Upload progress:', Math.round((progressEvent.loaded * 100) / progressEvent.total!));
        }
      });
      
      return response.data.file_id;
    } catch (error: any) {
      console.error('Error uploading audio:', error);
      
      // More specific error messages based on error type
      if (error.code === 'ECONNABORTED') {
        throw new Error('Audio upload timed out. Please try again with a shorter recording.');
      } else if (error.response?.status === 413) {
        throw new Error('Audio file too large. Please try a shorter recording.');
      } else if (error.response?.status === 415) {
        throw new Error('Unsupported audio format. Try recording again.');
      }
      
      throw new Error('Failed to upload audio. Please try again.');
    }
  }

  async synthesizeSpeech(text: string, language: string = 'arabic'): Promise<Blob> {
    try {
      const response = await apiClient.post('/api/tts/synthesize', {
        text,
        language,
      }, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Error synthesizing speech:', error);
      throw new Error('Failed to synthesize speech');
    }
  }

  async getConversationHistory(): Promise<ChatMessage[]> {
    try {
      const response = await apiClient.get('/api/chat/history');
      return response.data.messages || [];
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return [];
    }
  }

  async reportEmergency(details: string): Promise<void> {
    try {
      await apiClient.post('/api/emergency/report', {
        details,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Error reporting emergency:', error);
      throw new Error('Failed to report emergency');
    }
  }
}

export const apiService = new ApiService();
export default apiService;
