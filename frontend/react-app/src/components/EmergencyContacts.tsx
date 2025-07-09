import React from 'react';
import {
  Box,
  Typography,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  ReportProblem,
  LocalHospital,
  Phone,
  AccessTime,
} from '@mui/icons-material';
import { translations, TranslationKeys } from '../utils/translations';

interface EmergencyContactsProps {
  language: 'arabic' | 'english';
}

const EmergencyContacts: React.FC<EmergencyContactsProps> = ({ language }) => {
  const t: TranslationKeys = translations[language];

  const contacts = [
    {
      icon: <ReportProblem />,
      primary: language === 'arabic' ? 'الطوارئ العامة' : 'General Emergency',
      secondary: '999',
      description: language === 'arabic' ? 'للمساعدة الطارئة الفورية' : 'For immediate emergency assistance',
      color: '#DC3545',
    },
    {
      icon: <LocalHospital />,
      primary: language === 'arabic' ? 'مستشفى السلطان قابوس الجامعي' : 'Sultan Qaboos University Hospital',
      secondary: '24141414',
      description: language === 'arabic' ? 'المستشفى الجامعي الرئيسي' : 'Main University Hospital',
      color: '#007BFF',
    },
    {
      icon: <Phone />,
      primary: language === 'arabic' ? 'خط المساعدة النفسية' : 'Mental Health Hotline',
      secondary: language === 'arabic' ? 'متاح 24/7' : 'Available 24/7',
      description: language === 'arabic' ? 'دعم الصحة النفسية المتخصص' : 'Specialized mental health support',
      color: '#28A745',
    },
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1B4332', mb: 2 }}>
        {language === 'arabic' ? 'جهات الاتصال الطارئة' : 'Emergency Contacts'}
      </Typography>
      
      <Alert 
        severity="error" 
        sx={{ 
          mb: 2, 
          borderRadius: 1,
          backgroundColor: '#FFF5F5',
          border: '1px solid #FEB2B2',
          '& .MuiAlert-icon': {
            color: '#E53E3E'
          }
        }}
      >
        <Typography variant="body2" sx={{ fontWeight: 500, color: '#C53030' }}>
          {language === 'arabic' ? 
            'في حالة الطوارئ النفسية، اتصل فوراً بالأرقام أدناه' : 
            'In case of mental health emergency, contact the numbers below immediately'
          }
        </Typography>
      </Alert>

      <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
        {contacts.map((contact, index) => (
          <React.Fragment key={index}>
            <ListItem sx={{ px: 2, py: 2 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: '50%',
                    backgroundColor: `${contact.color}20`,
                    color: contact.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {contact.icon}
                </Box>
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography variant="body2" sx={{ fontWeight: 500, color: '#2D3748', mb: 0.5 }}>
                    {contact.primary}
                  </Typography>
                }
                secondary={
                  <Box>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        fontWeight: 700, 
                        color: contact.color,
                        fontSize: '1.1rem',
                        letterSpacing: '0.5px',
                        mb: 0.5
                      }}
                    >
                      {contact.secondary}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6C757D' }}>
                      {contact.description}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
            {index < contacts.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>

      <Box sx={{ mt: 3, p: 2, bgcolor: '#F8F9FA', borderRadius: 1, border: '1px solid #E9ECEF' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AccessTime sx={{ mr: 1, fontSize: 18, color: '#6C757D' }} />
          <Typography variant="body2" sx={{ fontWeight: 500, color: '#2D3748' }}>
            {language === 'arabic' ? 'تذكير هام' : 'Important Reminder'}
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#6C757D', lineHeight: 1.6 }}>
          {language === 'arabic' ? 
            'إذا كنت تواجه أزمة نفسية، يرجى التواصل فوراً مع الأرقام المذكورة. المساعدة متاحة على مدار الساعة.' : 
            'If you are experiencing a mental health crisis, please contact the numbers above immediately. Professional help is available 24/7.'
          }
        </Typography>
      </Box>
    </Box>
  );
};

export default EmergencyContacts;
