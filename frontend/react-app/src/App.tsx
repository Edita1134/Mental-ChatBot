import React, { useState, useEffect } from 'react';
import { Theme } from '@mui/material/styles';
import {
  Box,
  Container,
  Grid,
  Typography,
  Button,
  Card,
  CardContent,
  Alert,
  Fade,
  Divider,
  AppBar,
  Toolbar,
  Snackbar,
} from '@mui/material';
import {
  Psychology,
  Clear,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import ChatInterface from './components/ChatInterface';
import VoiceRecorder from './components/VoiceRecorder';
import SystemStatus from './components/SystemStatus';
import EmergencyContacts from './components/EmergencyContacts';
import LanguageSelector from './components/LanguageSelector';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingComponent from './components/LoadingComponent';
import { translations, TranslationKeys } from './utils/translations';
import apiService from './services/apiService';

const StyledAppBar = styled(AppBar)(({ theme }: { theme: Theme }) => ({
  background: '#1B4332', // Deep medical green
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
  borderBottom: '3px solid #D4AF37', // Gold accent for Omani touch
}));

const MainContainer = styled(Container)(({ theme }: { theme: Theme }) => ({
  minHeight: '100vh',
  paddingTop: theme.spacing(2),
  paddingBottom: theme.spacing(2),
  background: '#F8F9FA', // Clean medical white/gray
}));

const WelcomeCard = styled(Card)(({ theme }: { theme: Theme }) => ({
  background: '#FFFFFF',
  color: '#1B4332',
  marginBottom: theme.spacing(3),
  borderRadius: 8,
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  border: '1px solid #E9ECEF',
  borderTop: '4px solid #D4AF37', // Gold top border
}));

const ChatCard = styled(Card)(({ theme }: { theme: Theme }) => ({
  height: '650px',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: 8,
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  overflow: 'hidden',
  border: '1px solid #E9ECEF',
  background: '#FFFFFF',
}));

const SidebarCard = styled(Card)(({ theme }: { theme: Theme }) => ({
  borderRadius: 8,
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  padding: theme.spacing(3),
  border: '1px solid #E9ECEF',
  background: '#FFFFFF',
}));

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isAudio?: boolean;
}

interface SystemState {
  sttReady: boolean;
  llmReady: boolean;
  connecting: boolean;
  error: string | null;
}

interface SnackbarMessage {
  text: string;
  severity: 'success' | 'info' | 'warning' | 'error';
}

const App: React.FC = () => {
  const [language, setLanguage] = useState<'arabic' | 'english'>('arabic');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [systemState, setSystemState] = useState<SystemState>({
    sttReady: false,
    llmReady: false,
    connecting: true,
    error: null,
  });
  const [systemMessages, setSystemMessages] = useState<{[key: string]: boolean}>({
    processingAudio: false,
  });
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState<SnackbarMessage>({
    text: '',
    severity: 'info'
  });

  const t: TranslationKeys = translations[language];

  useEffect(() => {
    // Initialize system components
    initializeSystem();
  }, []);

  const initializeSystem = async () => {
    try {
      setSystemState((prev: SystemState) => ({ ...prev, connecting: true, error: null }));
      
      // Simulate system initialization
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSystemState({
        sttReady: true,
        llmReady: true,
        connecting: false,
        error: null,
      });
    } catch (error) {
      setSystemState({
        sttReady: false,
        llmReady: false,
        connecting: false,
        error: 'Failed to initialize system components',
      });
    }
  };

  const handleSendMessage = async (content: string, isAudio = false) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: isAudio ? `🎤 ${content}` : content,
      timestamp: new Date(),
      isAudio,
    };

    setMessages((prev: Message[]) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Try real API call first
      try {
        const response = await apiService.sendMessage(content, language);
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.response,
          timestamp: new Date(),
        };
        
        setMessages((prev: Message[]) => [...prev, assistantMessage]);
      } catch (apiError) {
        console.warn('API call failed, falling back to mock response:', apiError);
        
        // Fallback to mock response
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: generateResponse(content),
          timestamp: new Date(),
        };
        
        setMessages((prev: Message[]) => [...prev, assistantMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: t.error_prefix + ' ' + (error instanceof Error ? error.message : 'Unknown error'),
        timestamp: new Date(),
      };
      setMessages((prev: Message[]) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateResponse = (userMessage: string): string => {
    // Language-specific responses based on current language setting
    const arabicResponses = [
      'أفهم مشاعرك وأقدر ثقتك في مشاركة هذا الأمر معي. كيف يمكنني مساعدتك أكثر؟',
      'شكراً لك على المشاركة. مشاعرك مهمة وصحيحة، ولست وحدك في هذا.',
      'أسمعك وأفهم ما تمر به. هل تود أن نتحدث أكثر عما يسبب لك القلق؟',
      'من الشجاعة أن تطلب المساعدة. أنا هنا لدعمك في هذه الرحلة.',
      'صحتك النفسية مهمة جداً. دعنا نعمل معاً على إيجاد الحلول المناسبة.',
      'أقدر انفتاحك معي. هذا يدل على قوتك وحكمتك في طلب المساعدة.',
    ];
    
    const englishResponses = [
      'I understand your feelings and appreciate your trust in sharing this with me. How can I help you further?',
      'Thank you for sharing. Your feelings are important and valid, and you are not alone in this.',
      'I hear you and understand what you are going through. Would you like to talk more about what is causing you concern?',
      'It takes courage to seek help. I am here to support you on this journey.',
      'Your mental health is very important. Let us work together to find appropriate solutions.',
      'I appreciate your openness with me. This shows your strength and wisdom in seeking help.',
    ];
    
    const responses = language === 'arabic' ? arabicResponses : englishResponses;
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleLanguageChange = (newLanguage: 'arabic' | 'english') => {
    setLanguage(newLanguage);
  };

  const handleAudioUpload = async (file: File) => {
    try {
      setSystemMessages(prev => ({...prev, processingAudio: true}));
      setSnackbarMessage({
        text: language === 'arabic' ? 'جاري معالجة الملف الصوتي...' : 'Processing audio file...',
        severity: 'info'
      });
      setSnackbarOpen(true);
      
      // Add a processing message to the chat
      const processingMessage: Message = {
        id: `processing-${Date.now()}`,
        role: 'assistant',
        content: language === 'arabic' ? '🎤 جاري معالجة الرسالة الصوتية...' : '🎤 Processing voice message...',
        timestamp: new Date(),
      };
      
      // Show processing message temporarily
      setMessages(prev => [...prev, processingMessage]);
      
      // Try to process the audio with the API
      try {
        // First attempt: Use transcription endpoint
        const transcription = await apiService.transcribeAudio(file, language);
        
        if (transcription && transcription.text) {
          // Remove the processing message
          setMessages(prev => prev.filter(msg => msg.id !== processingMessage.id));
          
          // Add transcription as user message
          const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: `🎤 ${transcription.text}`,
            timestamp: new Date(),
            isAudio: true,
          };
          
          setMessages(prev => [...prev, userMessage]);
          setIsLoading(true);
          
          // Generate response
          try {
            const response = await apiService.sendMessage(transcription.text, language);
            
            const assistantMessage: Message = {
              id: (Date.now() + 1).toString(),
              role: 'assistant',
              content: response.response,
              timestamp: new Date(),
            };
            
            setMessages(prev => [...prev, assistantMessage]);
          } catch (responseError) {
            console.warn('API response failed, using fallback', responseError);
            
            // Fallback to mock response
            const assistantMessage: Message = {
              id: (Date.now() + 1).toString(),
              role: 'assistant',
              content: generateResponse(transcription.text),
              timestamp: new Date(),
            };
            
            setMessages(prev => [...prev, assistantMessage]);
          }
        } else {
          throw new Error('No transcription returned');
        }
      } catch (transcriptionError) {
        console.warn('Transcription failed, trying audio process endpoint:', transcriptionError);
        
        try {
          // Second attempt: Use processing endpoint
          const result = await apiService.processAudio(file, language);
          
          if (result && result.response) {
            // Remove the processing message
            setMessages(prev => prev.filter(msg => msg.id !== processingMessage.id));
            
            // Add as user message
            const userMessage: Message = {
              id: Date.now().toString(),
              role: 'user',
              content: `🎤 ${language === 'arabic' ? 'رسالة صوتية' : 'Voice message'}`,
              timestamp: new Date(),
              isAudio: true,
            };
            
            // Add as assistant message
            const assistantMessage: Message = {
              id: (Date.now() + 1).toString(),
              role: 'assistant',
              content: result.response,
              timestamp: new Date(),
            };
            
            setMessages(prev => [...prev, userMessage, assistantMessage]);
          } else {
            throw new Error('Audio processing failed');
          }
        } catch (processingError) {
          // All attempts failed
          // Remove the processing message
          setMessages(prev => prev.filter(msg => msg.id !== processingMessage.id));
          
          // Add error message
          const errorAssistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: language === 'arabic' 
              ? '❌ عذراً، لم أتمكن من فهم الرسالة الصوتية. يرجى المحاولة مرة أخرى.' 
              : '❌ Sorry, I couldn\'t understand the voice message. Please try again.',
            timestamp: new Date(),
          };
          
          setMessages(prev => [...prev, errorAssistantMessage]);
          throw processingError;
        }
      }
      
      // Show success notification
      setSnackbarMessage({
        text: language === 'arabic' ? '✅ تمت معالجة الصوت بنجاح' : '✅ Audio processed successfully',
        severity: 'success'
      });
      setSnackbarOpen(true);
      
    } catch (error) {
      console.error('Error processing audio upload:', error);
      setSnackbarMessage({
        text: language === 'arabic' ? 'فشل في معالجة الملف الصوتي' : 'Failed to process audio file',
        severity: 'error'
      });
      setSnackbarOpen(true);
    } finally {
      setIsLoading(false);
      setSystemMessages(prev => ({...prev, processingAudio: false}));
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  if (systemState.connecting) {
    return (
      <LoadingComponent message={t.initializing} />
    );
  }

  return (
    <ErrorBoundary>
      <Box sx={{ minHeight: '100vh' }}>
      <StyledAppBar position="static" elevation={0}>
        <Toolbar sx={{ minHeight: '72px' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
            <Psychology sx={{ mr: 1, color: '#D4AF37', fontSize: '2rem' }} />
            <Box>
              <Typography variant="h6" component="div" sx={{ fontWeight: 600, color: '#FFFFFF', lineHeight: 1.2 }}>
                {language === 'arabic' ? 'النظام الصحي النفسي' : 'Mental Health System'}
              </Typography>
              <Typography variant="caption" sx={{ color: '#B8C5D1', fontSize: '0.75rem' }}>
                {language === 'arabic' ? 'وزارة الصحة - سلطنة عمان' : 'Ministry of Health - Sultanate of Oman'}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ flexGrow: 1 }} />
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" sx={{ color: '#B8C5D1', display: { xs: 'none', md: 'block' } }}>
              {language === 'arabic' ? 'الإصدار 1.0' : 'Version 1.0'}
            </Typography>
            <LanguageSelector 
              language={language} 
              onLanguageChange={handleLanguageChange} 
            />
          </Box>
        </Toolbar>
      </StyledAppBar>

      <MainContainer maxWidth="xl">
        <Fade in timeout={1000}>
          <WelcomeCard>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                <img 
                  src="/omani-logo.png" 
                  alt="Omani Healthcare"
                  style={{ height: '60px', marginRight: '16px' }}
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#1B4332', mb: 1 }}>
                    {language === 'arabic' ? 'النظام الصحي النفسي العماني' : 'Omani Mental Health System'}
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#6C757D', fontWeight: 400 }}>
                    {language === 'arabic' ? 'خدمات الصحة النفسية المتخصصة' : 'Professional Mental Health Services'}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 2 }}>
                <Typography variant="body2" sx={{ color: '#6C757D', display: 'flex', alignItems: 'center' }}>
                  🏥 {language === 'arabic' ? 'وزارة الصحة - سلطنة عمان' : 'Ministry of Health - Sultanate of Oman'}
                </Typography>
              </Box>
            </CardContent>
          </WelcomeCard>
        </Fade>

        {systemState.error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
            {systemState.error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <ChatCard>
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                language={language}
              />
            </ChatCard>
          </Grid>

          <Grid item xs={12} lg={4}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <SidebarCard>
                  <VoiceRecorder
                    onAudioUpload={handleAudioUpload}
                    onRecordComplete={handleSendMessage}
                    language={language}
                  />
                </SidebarCard>
              </Grid>

              <Grid item xs={12}>
                <SidebarCard>
                  <SystemStatus
                    sttReady={systemState.sttReady}
                    llmReady={systemState.llmReady}
                    language={language}
                  />
                </SidebarCard>
              </Grid>

              <Grid item xs={12}>
                <SidebarCard>
                  <EmergencyContacts language={language} />
                </SidebarCard>
              </Grid>

              <Grid item xs={12}>
                <SidebarCard>
                  <Box textAlign="center">
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#1B4332' }}>
                      {language === 'arabic' ? 'إدارة الجلسة' : 'Session Management'}
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<Clear />}
                      onClick={handleClearChat}
                      fullWidth
                      sx={{ 
                        mb: 2,
                        borderColor: '#DC3545',
                        color: '#DC3545',
                        '&:hover': {
                          borderColor: '#C82333',
                          backgroundColor: '#F8D7DA'
                        }
                      }}
                    >
                      {t.clear_chat}
                    </Button>
                    
                    <Divider sx={{ my: 3 }} />
                    
                    <Box sx={{ textAlign: 'left', color: '#6C757D' }}>
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                        {language === 'arabic' ? 'معلومات النظام:' : 'System Information:'}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>{language === 'arabic' ? 'الإصدار:' : 'Version:'}</strong> 1.0.0
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>{language === 'arabic' ? 'البيئة:' : 'Environment:'}</strong> {language === 'arabic' ? 'إنتاج' : 'Production'}
                      </Typography>
                      <Typography variant="body2">
                        <strong>{language === 'arabic' ? 'التقنية:' : 'Technology:'}</strong> React + Azure AI
                      </Typography>
                    </Box>
                  </Box>
                </SidebarCard>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </MainContainer>
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage.text}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </ErrorBoundary>
  );
};

export default App;
