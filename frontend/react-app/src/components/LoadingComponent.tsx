import React from 'react';
import { Box, CircularProgress, Typography, Fade } from '@mui/material';
import { Psychology } from '@mui/icons-material';

interface LoadingComponentProps {
  message?: string;
  size?: number;
}

const LoadingComponent: React.FC<LoadingComponentProps> = ({ 
  message = "Loading...", 
  size = 60 
}) => {
  return (
    <Fade in timeout={300}>
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        flexDirection="column"
        gap={2}
        sx={{
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        }}
      >
        <Box position="relative">
          <CircularProgress 
            size={size} 
            sx={{ 
              color: '#667eea',
              animationDuration: '550ms',
            }} 
          />
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <Psychology 
              sx={{ 
                color: '#667eea',
                fontSize: size * 0.4,
              }} 
            />
          </Box>
        </Box>
        <Typography 
          variant="h6" 
          color="textSecondary"
          sx={{
            fontWeight: 500,
            letterSpacing: 0.5,
          }}
        >
          {message}
        </Typography>
      </Box>
    </Fade>
  );
};

export default LoadingComponent;
