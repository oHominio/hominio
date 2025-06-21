"""
Audio utility functions
"""
import wave
import io
import logging
from typing import Tuple, Optional

try:
    import numpy as np
    from scipy.signal import resample
    HAS_AUDIO_PROCESSING = True
except ImportError:
    HAS_AUDIO_PROCESSING = False

logger = logging.getLogger(__name__)


def create_wave_header(channels: int, sample_rate: int, sample_width: int = 2) -> bytes:
    """Create WAV header for audio stream"""
    wav_header = io.BytesIO()
    with wave.open(wav_header, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)

    wav_header.seek(0)
    wave_header_bytes = wav_header.read()
    wav_header.close()

    return wave_header_bytes


def create_wave_header_for_engine(engine) -> bytes:
    """Create WAV header for the given TTS engine"""
    try:
        _, channels, sample_rate = engine.get_stream_info()
        return create_wave_header(channels, sample_rate)
    except Exception as e:
        logger.error(f"Error getting engine stream info: {e}")
        # Fallback to default values
        return create_wave_header(1, 24000)


def decode_and_resample(audio_data: bytes, original_sample_rate: int, target_sample_rate: int = 16000) -> bytes:
    """Decode and resample audio data"""
    if not HAS_AUDIO_PROCESSING:
        logger.warning("Audio processing libraries not available, returning original data")
        return audio_data
    
    try:
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate resampling ratio
        ratio = target_sample_rate / original_sample_rate
        
        # Resample if needed
        if ratio != 1.0:
            # Convert to float for resampling
            audio_float = audio_array.astype(np.float32)
            
            # Resample
            resampled_length = int(len(audio_float) * ratio)
            resampled_audio = resample(audio_float, resampled_length)
            
            # Convert back to int16
            resampled_audio = np.clip(resampled_audio, -32768, 32767).astype(np.int16)
            
            return resampled_audio.tobytes()
        else:
            return audio_data
            
    except Exception as e:
        logger.error(f"Error resampling audio: {e}")
        return audio_data


def calculate_audio_duration(audio_data: bytes, sample_rate: int, sample_width: int = 2, channels: int = 1) -> float:
    """Calculate duration of audio data in seconds"""
    try:
        # Calculate number of samples
        bytes_per_sample = sample_width * channels
        num_samples = len(audio_data) // bytes_per_sample
        
        # Calculate duration
        duration = num_samples / sample_rate
        return duration
    except Exception as e:
        logger.error(f"Error calculating audio duration: {e}")
        return 0.0


def is_audio_silent(audio_data: bytes, threshold: float = 0.01) -> bool:
    """Check if audio data is silent (below threshold)"""
    if not HAS_AUDIO_PROCESSING:
        return False
    
    try:
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
        
        # Normalize to 0-1 range
        normalized_rms = rms / 32768.0
        
        return normalized_rms < threshold
    except Exception as e:
        logger.error(f"Error checking audio silence: {e}")
        return False 