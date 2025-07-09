import React, { useState, useRef } from 'react';
import { Theme } from '@mui/material/styles';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Paper,
  LinearProgress,
  Alert,
  Chip,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Mic,
  Stop,
  CloudUpload,
  VolumeUp,
  Delete,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { translations, TranslationKeys } from '../utils/translations';
import apiService from '../services/apiService';

const VoiceContainer = styled(Box)(({ theme }: { theme: Theme }) => ({
  padding: theme.spacing(3),
}));

const RecordButton = styled(IconButton, {
  shouldForwardProp: (prop) => prop !== 'isRecording',
})<{ isRecording?: boolean }>(({ theme, isRecording }: { theme: Theme; isRecording?: boolean }) => ({
  width: 80,
  height: 80,
  background: isRecording ? '#DC3545' : '#1B4332',
  color: '#ffffff',
  margin: theme.spacing(2),
  borderRadius: '12px',
  '&:hover': {
    background: isRecording ? '#C82333' : '#2D5016',
    transform: 'scale(1.05)',
  },
  animation: isRecording ? 'pulse 2s infinite' : 'none',
  '@keyframes pulse': {
    '0%': {
      transform: 'scale(1)',
      boxShadow: '0 0 0 0 rgba(220, 53, 69, 0.7)',
    },
    '70%': {
      transform: 'scale(1.05)',
      boxShadow: '0 0 0 10px rgba(220, 53, 69, 0)',
    },
    '100%': {
      transform: 'scale(1)',
      boxShadow: '0 0 0 0 rgba(220, 53, 69, 0)',
    },
  },
}));

const UploadArea = styled(Paper)(({ theme }: { theme: Theme }) => ({
  border: '2px dashed #C1C8CD',
  borderRadius: theme.spacing(1),
  padding: theme.spacing(3),
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  backgroundColor: '#F8F9FA',
  '&:hover': {
    borderColor: '#1B4332',
    backgroundColor: '#F1F3F4',
  },
  '&.dragover': {
    borderColor: '#1B4332',
    backgroundColor: '#E8F5E8',
  },
}));

const ProcessingOverlay = styled(Box)(({ theme }: { theme: Theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(255, 255, 255, 0.8)',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 10,
  borderRadius: 8,
  padding: theme.spacing(2),
}));

const RecordingIndicator = styled(Box)(({ theme }: { theme: Theme }) => ({
  width: 16,
  height: 16,
  borderRadius: '50%',
  backgroundColor: '#DC3545',
  marginRight: theme.spacing(1),
  animation: 'pulse 1.5s infinite',
  '@keyframes pulse': {
    '0%': {
      transform: 'scale(0.95)',
      boxShadow: '0 0 0 0 rgba(220, 53, 69, 0.7)',
    },
    '70%': {
      transform: 'scale(1)',
      boxShadow: '0 0 0 10px rgba(220, 53, 69, 0)',
    },
    '100%': {
      transform: 'scale(0.95)',
      boxShadow: '0 0 0 0 rgba(220, 53, 69, 0)',
    },
  },
}));

interface VoiceRecorderProps {
  onAudioUpload: (file: File) => void;
  onRecordComplete: (transcript: string, isAudio: boolean) => void;
  language: 'arabic' | 'english';
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onAudioUpload,
  onRecordComplete,
  language,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [processingError, setProcessingError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const t: TranslationKeys = translations[language];

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Use specific audio MIME type based on browser support
      // Default to audio/webm which is widely supported
      const mimeType = MediaRecorder.isTypeSupported('audio/webm') 
        ? 'audio/webm' 
        : (MediaRecorder.isTypeSupported('audio/mp4') 
            ? 'audio/mp4' 
            : 'audio/ogg');
      
      console.log(`Using MIME type: ${mimeType} for recording`);
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType,
        audioBitsPerSecond: 128000
      });
      
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
          console.log(`Recorded chunk: ${event.data.size} bytes, type: ${event.data.type}`);
        }
      };

      mediaRecorder.onstop = () => {
        if (chunks.length === 0) {
          console.error('No audio data recorded');
          setProcessingError('No audio data was recorded. Please try again.');
          return;
        }
        
        const blob = new Blob(chunks, { type: mimeType });
        console.log(`Recording completed: ${blob.size} bytes, type: ${blob.type}`);
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      // Request data every second to handle potential issues
      mediaRecorder.start(1000);
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setRecordingTime(0);
      setProcessingError(null);

      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert(t.microphone_error || 'Error accessing microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }
  };

  const processAudio = async () => {
    if (!audioBlob) return;

    setIsProcessing(true);
    setProcessingError(null);
    
    try {
      // Debug: Log blob details before creating File
      console.log('Processing audio blob:', {
        size: audioBlob.size,
        type: audioBlob.type,
        lastModified: new Date().toString()
      });
      
      // Create a File object from the blob with explicit MIME type
      const filename = `recording-${Date.now()}.wav`;
      const audioFile = new File([audioBlob], filename, { 
        type: audioBlob.type || 'audio/wav',
        lastModified: Date.now()
      });
      
      console.log('Created audio file:', {
        name: audioFile.name,
        size: audioFile.size,
        type: audioFile.type,
        lastModified: new Date(audioFile.lastModified).toString()
      });
      
      // First try with the original transcription endpoint
      try {
        // Use the actual API service to transcribe
        const transcriptionResult = await apiService.transcribeAudio(audioFile, language);
        
        if (transcriptionResult && transcriptionResult.text) {
          // Show success message
          const successMessage = language === 'arabic' ? 
            `تم التعرف على الصوت: ${transcriptionResult.text.substring(0, 30)}...` : 
            `Speech recognized: ${transcriptionResult.text.substring(0, 30)}...`;
            
          console.log(successMessage);
          
          // Pass the real transcription to the parent component
          onRecordComplete(transcriptionResult.text, true);
          
          setAudioBlob(null);
          setRecordingTime(0);
          return;
        } else {
          throw new Error("No transcription text returned");
        }
      } catch (firstError) {
        console.warn("First transcription attempt failed, trying audio processing endpoint...", firstError);
        
        // Create a fresh copy of the file before trying the fallback
        const freshBlob = audioBlob.slice(0, audioBlob.size, audioBlob.type || 'audio/wav');
        const fallbackFile = new File([freshBlob], filename, { 
          type: 'audio/wav',
          lastModified: Date.now()
        });
        
        console.log('Trying fallback with fresh file:', {
          name: fallbackFile.name,
          size: fallbackFile.size,
          type: fallbackFile.type
        });
        
        // Try with the audio processing endpoint as fallback
        const processResult = await apiService.processAudio(fallbackFile, language);
        
        if (processResult && processResult.response) {
          const successMessage = language === 'arabic' ? 
            'تمت معالجة الصوت بنجاح' : 
            'Audio processed successfully';
            
          console.log(successMessage);
          
          onRecordComplete(processResult.response, true);
          
          setAudioBlob(null);
          setRecordingTime(0);
          return;
        } else {
          throw new Error("Audio processing failed");
        }
      }
    } catch (error) {
      console.error('Error processing audio:', error);
      const errorMessage = language === 'arabic' 
        ? 'خطأ في معالجة الصوت. يرجى المحاولة مرة أخرى.' 
        : 'Error processing audio. Please try again.';
      setProcessingError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (file: File) => {
    // Check if file is valid
    if (!file || file.size === 0) {
      alert(t.empty_file || 'The audio file appears to be empty');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert(t.file_too_large || 'File too large. Maximum size is 10MB.');
      return;
    }

    // Accept any file that claims to be audio type or has an audio extension
    const validAudioExtensions = ['.wav', '.mp3', '.ogg', '.m4a', '.aac', '.wma', '.flac', '.opus'];
    const hasValidExtension = validAudioExtensions.some(ext => 
      file.name.toLowerCase().endsWith(ext)
    );
    
    if (file.type.startsWith('audio/') || hasValidExtension) {
      console.log('Processing valid audio file:', file.name, file.type, file.size);
      
      // Determine the MIME type to use
      let mimeType = file.type;
      
      // If no MIME type, try to infer it from extension
      if (!mimeType || mimeType === '') {
        const extension = file.name.split('.').pop()?.toLowerCase();
        switch (extension) {
          case 'mp3': mimeType = 'audio/mpeg'; break;
          case 'wav': mimeType = 'audio/wav'; break;
          case 'ogg': mimeType = 'audio/ogg'; break;
          case 'm4a': mimeType = 'audio/mp4'; break;
          case 'aac': mimeType = 'audio/aac'; break;
          case 'flac': mimeType = 'audio/flac'; break;
          case 'opus': mimeType = 'audio/opus'; break;
          default: mimeType = 'audio/wav';
        }
      }
      
      setUploadedFile(file);
      
      // Create a clean copy of the file with proper MIME type
      const blob = file.slice(0, file.size, file.type);
      const cleanFile = new File([blob], file.name, { 
        type: mimeType,
        lastModified: Date.now()
      });
      
      console.log('Created clean file with type:', cleanFile.type);
      
      onAudioUpload(cleanFile);
    } else {
      alert(t.invalid_file_type || 'Please upload an audio file');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <VoiceContainer sx={{ position: 'relative' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1B4332', mb: 3 }}>
        {language === 'arabic' ? 'التسجيل الصوتي' : 'Voice Recording'}
      </Typography>

      {isProcessing && (
        <ProcessingOverlay>
          <CircularProgress size={48} sx={{ color: '#1B4332', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#1B4332', mb: 1 }}>
            {language === 'arabic' ? 'جاري معالجة الصوت...' : 'Processing Audio...'}
          </Typography>
          <Typography variant="body2" sx={{ color: '#6C757D', textAlign: 'center' }}>
            {language === 'arabic' 
              ? 'يرجى الانتظار بينما يتم تحليل التسجيل الصوتي وإنشاء استجابة مناسبة.' 
              : 'Please wait while we analyze your audio recording and generate an appropriate response.'}
          </Typography>
        </ProcessingOverlay>
      )}

      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <RecordButton
          isRecording={isRecording}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
        >
          {isRecording ? <Stop /> : <Mic />}
        </RecordButton>
        
        <Typography variant="body2" sx={{ color: '#6C757D', mt: 1 }}>
          {isRecording ? 
            (language === 'arabic' ? 'اضغط لإيقاف التسجيل' : 'Click to stop recording') :
            (language === 'arabic' ? 'اضغط لبدء التسجيل' : 'Click to start recording')
          }
        </Typography>
        
        {isRecording && (
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <RecordingIndicator />
            <Chip
              label={`${language === 'arabic' ? 'جاري التسجيل' : 'Recording'} ${formatTime(recordingTime)}`}
              color="error"
              sx={{ 
                fontWeight: 500,
                fontSize: '0.875rem'
              }}
            />
          </Box>
        )}
      </Box>

      {processingError && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 3,
            backgroundColor: '#FFF5F5',
            border: '1px solid #F8D7DA',
            borderRadius: 1
          }}
          onClose={() => setProcessingError(null)}
        >
          {processingError}
        </Alert>
      )}

      {audioBlob && (
        <Box sx={{ mb: 3 }}>
          <Alert 
            severity="success" 
            sx={{ 
              mb: 2,
              backgroundColor: '#E8F5E8',
              border: '1px solid #C3E6C3',
              borderRadius: 1
            }}
          >
            {language === 'arabic' ? 'تم التسجيل بنجاح!' : 'Recording completed successfully!'}
          </Alert>
          <audio 
            controls 
            src={URL.createObjectURL(audioBlob)} 
            style={{ 
              width: '100%', 
              height: '40px',
              borderRadius: '8px'
            }} 
          />
          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              onClick={processAudio}
              disabled={isProcessing}
              fullWidth
              sx={{
                backgroundColor: '#1B4332',
                '&:hover': {
                  backgroundColor: '#2D5016',
                },
                borderRadius: '8px',
                textTransform: 'none',
                fontWeight: 500
              }}
            >
              {isProcessing ? 
                (language === 'arabic' ? 'جاري المعالجة...' : 'Processing...') : 
                (language === 'arabic' ? 'معالجة التسجيل' : 'Process Recording')
              }
            </Button>
            <IconButton 
              onClick={() => setAudioBlob(null)} 
              sx={{ 
                color: '#DC3545',
                border: '1px solid #DC3545',
                borderRadius: '8px',
                '&:hover': {
                  backgroundColor: '#FFF5F5'
                }
              }}
            >
              <Delete />
            </IconButton>
          </Box>
        </Box>
      )}

      {isProcessing && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress 
            sx={{ 
              borderRadius: 2, 
              height: 8,
              backgroundColor: '#E9ECEF',
              '& .MuiLinearProgress-bar': {
                backgroundColor: '#1B4332'
              }
            }} 
          />
          <Typography variant="body2" textAlign="center" sx={{ mt: 1, color: '#6C757D' }}>
            {language === 'arabic' ? 'جاري تحليل التسجيل الصوتي...' : 'Processing audio recording...'}
          </Typography>
        </Box>
      )}

      <Divider sx={{ my: 3 }} />

      <UploadArea
        className={dragOver ? 'dragover' : ''}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <CloudUpload sx={{ fontSize: 48, color: '#C1C8CD', mb: 2 }} />
        <Typography variant="body1" gutterBottom sx={{ fontWeight: 500, color: '#2D3748' }}>
          {language === 'arabic' ? 'تحميل ملف صوتي' : 'Upload Audio File'}
        </Typography>
        <Typography variant="body2" sx={{ color: '#6C757D', mb: 1 }}>
          {language === 'arabic' ? 
            'اسحب وأسقط ملف صوتي هنا، أو انقر للاختيار' : 
            'Drag and drop an audio file here, or click to select'
          }
        </Typography>
        <Typography variant="caption" sx={{ color: '#6C757D' }}>
          {language === 'arabic' ? 
            'الصيغ المدعومة: MP3, WAV, OGG, M4A' : 
            'Supported formats: MP3, WAV, OGG, M4A'
          }
        </Typography>
      </UploadArea>

      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        style={{ display: 'none' }}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFileUpload(file);
        }}
      />

      {uploadedFile && (
        <Box sx={{ mt: 2 }}>
          <Alert 
            severity="info"
            sx={{
              backgroundColor: '#E3F2FD',
              border: '1px solid #90CAF9',
              borderRadius: 1
            }}
          >
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              {language === 'arabic' ? 'الملف المرفوع:' : 'Uploaded file:'} {uploadedFile.name}
            </Typography>
          </Alert>
        </Box>
      )}
    </VoiceContainer>
  );
};

export default VoiceRecorder;
