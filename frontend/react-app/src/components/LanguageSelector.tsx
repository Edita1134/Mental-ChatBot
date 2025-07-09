import React from 'react';
import {
  Box,
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent,
  Chip,
  Typography,
} from '@mui/material';

interface LanguageSelectorProps {
  language: 'arabic' | 'english';
  onLanguageChange: (language: 'arabic' | 'english') => void;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  language,
  onLanguageChange,
}) => {
  const handleChange = (event: SelectChangeEvent<string>) => {
    onLanguageChange(event.target.value as 'arabic' | 'english');
  };

  const languages = [
    { value: 'arabic', label: 'العربية', nativeLabel: 'العربية العمانية', flag: '🇴🇲' },
    { value: 'english', label: 'English', nativeLabel: 'English', flag: '🇬🇧' },
  ];

  return (
    <Box sx={{ minWidth: 180 }}>
      <FormControl size="small" fullWidth>
        <Select
          value={language}
          onChange={handleChange}
          sx={{
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(255, 255, 255, 0.3)',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(255, 255, 255, 0.5)',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#D4AF37',
              borderWidth: '2px',
            },
            '& .MuiSvgIcon-root': {
              color: 'white',
            },
          }}
          displayEmpty
          renderValue={(selected: unknown) => {
            const selectedLang = languages.find(lang => lang.value === selected);
            return selectedLang ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography component="span" sx={{ fontSize: '1rem' }}>
                  {selectedLang.flag}
                </Typography>
                <Typography component="span" sx={{ fontSize: '0.875rem', fontWeight: 500 }}>
                  {selectedLang.label}
                </Typography>
              </Box>
            ) : '';
          }}
        >
          {languages.map((lang) => (
            <MenuItem key={lang.value} value={lang.value} sx={{ py: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
                <Typography component="span" sx={{ fontSize: '1.2rem' }}>
                  {lang.flag}
                </Typography>
                <Box sx={{ flex: 1 }}>
                  <Typography component="span" sx={{ fontWeight: 500 }}>
                    {lang.label}
                  </Typography>
                  <Typography 
                    component="div" 
                    sx={{ 
                      fontSize: '0.75rem', 
                      color: 'text.secondary',
                      lineHeight: 1.2
                    }}
                  >
                    {lang.nativeLabel}
                  </Typography>
                </Box>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default LanguageSelector;
