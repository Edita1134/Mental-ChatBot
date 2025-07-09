import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Divider,
} from '@mui/material';
import {
  RecordVoiceOver,
  Psychology,
  Language,
  Security,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { translations, TranslationKeys } from '../utils/translations';

interface SystemStatusProps {
  sttReady: boolean;
  llmReady: boolean;
  language: 'arabic' | 'english';
}

const SystemStatus: React.FC<SystemStatusProps> = ({
  sttReady,
  llmReady,
  language,
}) => {
  const t: TranslationKeys = translations[language];

  const statusItems = [
    {
      icon: <RecordVoiceOver />,
      primary: language === 'arabic' ? 'التعرف على الكلام' : 'Speech Recognition',
      secondary: 'Groq Whisper v3',
      status: sttReady,
    },
    {
      icon: <Psychology />,
      primary: language === 'arabic' ? 'الذكاء الاصطناعي' : 'AI Analysis',
      secondary: 'Azure OpenAI GPT-4',
      status: llmReady,
    },
    {
      icon: <Language />,
      primary: language === 'arabic' ? 'اللغة' : 'Language',
      secondary: language === 'arabic' ? 'العربية العمانية' : 'Omani Arabic + English',
      status: true,
    },
    {
      icon: <Security />,
      primary: language === 'arabic' ? 'الأمان والخصوصية' : 'Security & Privacy',
      secondary: language === 'arabic' ? 'معايير وزارة الصحة' : 'Ministry of Health Standards',
      status: true,
    },
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1B4332', mb: 2 }}>
        {language === 'arabic' ? 'حالة النظام' : 'System Status'}
      </Typography>
      
      <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
        {statusItems.map((item, index) => (
          <React.Fragment key={index}>
            <ListItem sx={{ px: 2, py: 1.5 }}>
              <ListItemIcon sx={{ minWidth: 40, color: '#1B4332' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="body2" sx={{ fontWeight: 500, color: '#2D3748' }}>
                      {item.primary}
                    </Typography>
                    <Chip
                      icon={item.status ? <CheckCircle /> : <Error />}
                      label={item.status ? 
                        (language === 'arabic' ? 'متصل' : 'Online') : 
                        (language === 'arabic' ? 'خطأ' : 'Error')
                      }
                      size="small"
                      color={item.status ? 'success' : 'error'}
                      sx={{ 
                        height: 24,
                        fontWeight: 500,
                        fontSize: '0.75rem'
                      }}
                    />
                  </Box>
                }
                secondary={
                  <Typography variant="caption" sx={{ color: '#6C757D', fontSize: '0.75rem' }}>
                    {item.secondary}
                  </Typography>
                }
              />
            </ListItem>
            {index < statusItems.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
};

export default SystemStatus;
