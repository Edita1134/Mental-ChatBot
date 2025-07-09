import os
import tempfile
import logging
from typing import Optional, Tuple
import mimetypes

logger = logging.getLogger(__name__)

class AudioHelper:
    """Helper class for audio file processing and validation"""
    
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.ogg', '.m4a', '.aac', '.flac']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_audio_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate audio file format and size
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, "Audio file does not exist"
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "Audio file is empty"
            
            if file_size > AudioHelper.MAX_FILE_SIZE:
                return False, f"Audio file too large. Maximum size is {AudioHelper.MAX_FILE_SIZE // (1024*1024)}MB"
            
            # Check file extension
            _, ext = os.path.splitext(file_path.lower())
            if ext not in AudioHelper.SUPPORTED_FORMATS:
                return False, f"Unsupported audio format. Supported formats: {', '.join(AudioHelper.SUPPORTED_FORMATS)}"
            
            return True, "Valid audio file"
            
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return False, f"Error validating audio file: {str(e)}"
    
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """Get MIME type for audio file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type and mime_type.startswith('audio/'):
            return mime_type
        
        # Fallback based on extension
        ext = os.path.splitext(file_path.lower())[1]
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/aac',
            '.flac': 'audio/flac'
        }
        
        return mime_types.get(ext, 'audio/wav')
    
    @staticmethod
    def create_temp_audio_file(audio_data: bytes, extension: str = '.wav') -> str:
        """
        Create temporary audio file from bytes
        
        Returns:
            Path to temporary file
        """
        try:
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=extension,
                prefix='audio_'
            )
            temp_file.write(audio_data)
            temp_file.close()
            
            logger.info(f"Created temporary audio file: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating temporary audio file: {e}")
            raise
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """Clean up temporary audio file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not clean up temporary file {file_path}: {e}")
    
    @staticmethod
    def convert_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert audio file to WAV format (requires ffmpeg or similar)
        
        Returns:
            Path to converted WAV file
        """
        try:
            import subprocess
            
            if output_path is None:
                output_path = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix='.wav',
                    prefix='converted_'
                ).name
            
            # Use ffmpeg to convert (if available)
            cmd = [
                'ffmpeg', '-i', input_path, 
                '-acodec', 'pcm_s16le', 
                '-ar', '16000', 
                '-ac', '1',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully converted {input_path} to {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return input_path  # Return original if conversion fails
                
        except Exception as e:
            logger.warning(f"Could not convert audio file: {e}")
            return input_path  # Return original if conversion fails