import React, { useState, useRef, useEffect } from 'react';
import { Theme } from '@mui/material/styles';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Chip,
  CircularProgress,
  Fade,
} from '@mui/material';
import { Send, Person, SmartToy, VolumeUp } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { translations, TranslationKeys } from '../utils/translations';

const ChatContainer = styled(Box)(({ theme }: { theme: Theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const MessagesContainer = styled(Box)(({ theme }: { theme: Theme }) => ({
  flex: 1,
  overflowY: 'auto',
  padding: theme.spacing(3),
  background: '#F8F9FA',
  '&::-webkit-scrollbar': {
    width: '6px',
  },
  '&::-webkit-scrollbar-track': {
    background: '#F1F3F4',
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#C1C8CD',
    borderRadius: '3px',
    '&:hover': {
      background: '#A8B2BA',
    },
  },
}));

const MessageBubble = styled(Paper, {
  shouldForwardProp: (prop: string) => prop !== 'isUser',
})<{ isUser?: boolean }>(({ theme, isUser }: { theme: Theme; isUser?: boolean }) => ({
  padding: theme.spacing(2.5),
  marginBottom: theme.spacing(2),
  borderRadius: '12px',
  maxWidth: '75%',
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  background: isUser ? '#1B4332' : '#FFFFFF',
  color: isUser ? '#FFFFFF' : '#2D3748',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  border: isUser ? 'none' : '1px solid #E9ECEF',
  position: 'relative',
  '&::before': isUser ? {
    content: '""',
    position: 'absolute',
    bottom: '0',
    right: '-8px',
    width: '0',
    height: '0',
    borderLeft: '8px solid #1B4332',
    borderTop: '8px solid transparent',
    borderBottom: '8px solid transparent',
  } : {
    content: '""',
    position: 'absolute',
    bottom: '0',
    left: '-8px',
    width: '0',
    height: '0',
    borderRight: '8px solid #FFFFFF',
    borderTop: '8px solid transparent',
    borderBottom: '8px solid transparent',
  },
}));

const InputContainer = styled(Box)(({ theme }: { theme: Theme }) => ({
  padding: theme.spacing(2.5),
  background: '#FFFFFF',
  borderTop: '1px solid #E9ECEF',
  display: 'flex',
  gap: theme.spacing(2),
  alignItems: 'flex-end',
}));

const StyledTextField = styled(TextField)(({ theme }: { theme: Theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: '8px',
    background: '#F8F9FA',
    fontSize: '1rem',
    '& fieldset': {
      borderColor: '#E9ECEF',
    },
    '&:hover fieldset': {
      borderColor: '#1B4332',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#1B4332',
      borderWidth: '2px',
    },
  },
}));

const SendButton = styled(IconButton)(({ theme }: { theme: Theme }) => ({
  background: '#1B4332',
  color: '#FFFFFF',
  width: 48,
  height: 48,
  borderRadius: '8px',
  '&:hover': {
    background: '#2D5016',
  },
  '&:disabled': {
    background: '#E9ECEF',
    color: '#6C757D',
  },
}));

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isAudio?: boolean;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string, isAudio?: boolean) => void;
  isLoading: boolean;
  language: 'arabic' | 'english';
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading,
  language,
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const t: TranslationKeys = translations[language];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString(language === 'arabic' ? 'ar-OM' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <ChatContainer>
      <Box sx={{ 
        p: 2.5, 
        background: '#1B4332', 
        color: 'white', 
        borderBottom: '1px solid #E9ECEF',
        direction: language === 'arabic' ? 'rtl' : 'ltr' 
      }}>
        <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
          <SmartToy sx={{ 
            [language === 'arabic' ? 'ml' : 'mr']: 1, 
            color: '#D4AF37' 
          }} />
          {language === 'arabic' ? 'المحادثة الطبية' : 'Medical Consultation'}
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
          {language === 'arabic' ? 'استشارة نفسية متخصصة' : 'Professional Mental Health Consultation'}
        </Typography>
      </Box>

      <MessagesContainer sx={{ direction: language === 'arabic' ? 'rtl' : 'ltr' }}>
        {messages.length === 0 ? (
          <Box textAlign="center" sx={{ mt: 6, direction: language === 'arabic' ? 'rtl' : 'ltr' }}>
            <SmartToy sx={{ fontSize: 72, color: '#C1C8CD', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#6C757D', fontWeight: 600, mb: 1 }}>
              {language === 'arabic' ? 'مرحباً بك في النظام الصحي النفسي العماني' : 'Welcome to Omani Mental Health System'}
            </Typography>
            <Typography variant="body2" sx={{ color: '#6C757D', maxWidth: '400px', mx: 'auto' }}>
              {language === 'arabic' 
                ? 'أهلاً وسهلاً بك. يمكنك بدء المحادثة بكتابة رسالة أو استخدام الإدخال الصوتي' 
                : 'Welcome to our professional mental health consultation system. You can start by typing a message or using voice input'}
            </Typography>
          </Box>
        ) : (
          <>
            {messages.map((message: Message, index: number) => (
              <Fade key={message.id} in timeout={300}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: message.role === 'user' ? 
                      (language === 'arabic' ? 'flex-start' : 'flex-end') : 
                      (language === 'arabic' ? 'flex-end' : 'flex-start'),
                    mb: 2,
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 1.5,
                      maxWidth: '80%',
                      flexDirection: message.role === 'user' ? 
                        (language === 'arabic' ? 'row' : 'row-reverse') : 
                        (language === 'arabic' ? 'row-reverse' : 'row'),
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: message.role === 'user' ? '#1B4332' : '#28A745',
                        width: 40,
                        height: 40,
                        mt: 1,
                      }}
                    >
                      {message.role === 'user' ? <Person /> : <SmartToy />}
                    </Avatar>
                    <Box>
                      <MessageBubble 
                        isUser={message.role === 'user'}
                        sx={{
                          direction: language === 'arabic' ? 'rtl' : 'ltr',
                          textAlign: language === 'arabic' ? 'right' : 'left',
                        }}
                      >
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                          {message.content}
                        </Typography>
                        {message.isAudio && (
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            mt: 1,
                            p: 1,
                            bgcolor: message.role === 'user' ? 
                              'rgba(255,255,255,0.2)' : 
                              'rgba(27,67,50,0.1)',
                            borderRadius: 1
                          }}>
                            <VolumeUp sx={{ 
                              mr: 1, 
                              fontSize: '1rem',
                              color: message.role === 'user' ? '#FFFFFF' : '#1B4332'
                            }} />
                            <Typography variant="caption" sx={{ 
                              fontWeight: 500,
                              color: message.role === 'user' ? '#FFFFFF' : '#1B4332'
                            }}>
                              {language === 'arabic' ? 'رسالة صوتية' : 'Voice Message'}
                            </Typography>
                          </Box>
                        )}
                      </MessageBubble>
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#6C757D',
                          ml: message.role === 'user' ? 0 : (language === 'arabic' ? 0 : 1),
                          mr: message.role === 'user' ? (language === 'arabic' ? 0 : 1) : 0,
                          textAlign: message.role === 'user' ? 
                            (language === 'arabic' ? 'left' : 'right') : 
                            (language === 'arabic' ? 'right' : 'left'),
                        }}
                      >
                        {formatTimestamp(message.timestamp)}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Fade>
            ))}
            {isLoading && (
              <Box sx={{ 
                display: 'flex', 
                justifyContent: language === 'arabic' ? 'flex-end' : 'flex-start', 
                mb: 2 
              }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1.5,
                  flexDirection: language === 'arabic' ? 'row-reverse' : 'row'
                }}>
                  <Avatar sx={{ bgcolor: '#28A745', width: 40, height: 40 }}>
                    <SmartToy />
                  </Avatar>
                  <MessageBubble sx={{ direction: language === 'arabic' ? 'rtl' : 'ltr' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} sx={{ color: '#1B4332' }} />
                      <Typography variant="body2" sx={{ color: '#6C757D' }}>
                        {language === 'arabic' ? 'جاري التحليل...' : 'Analyzing...'}
                      </Typography>
                    </Box>
                  </MessageBubble>
                </Box>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </MessagesContainer>

      <InputContainer sx={{ direction: language === 'arabic' ? 'rtl' : 'ltr' }}>
        <StyledTextField
          fullWidth
          multiline
          maxRows={4}
          value={inputMessage}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={language === 'arabic' ? 'اكتب رسالتك هنا...' : 'Type your message here...'}
          disabled={isLoading}
          sx={{
            '& .MuiInputBase-root': {
              fontSize: '1rem',
              direction: language === 'arabic' ? 'rtl' : 'ltr',
              textAlign: language === 'arabic' ? 'right' : 'left',
            },
            '& .MuiInputBase-input::placeholder': {
              textAlign: language === 'arabic' ? 'right' : 'left',
            },
          }}
        />
        <SendButton
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isLoading}
          sx={{
            order: language === 'arabic' ? -1 : 0,
          }}
        >
          <Send sx={{ transform: language === 'arabic' ? 'scaleX(-1)' : 'none' }} />
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatInterface;
