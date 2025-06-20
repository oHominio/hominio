"""
Configuration and environment setup for hominio-voice application
"""
import os
import multiprocessing
from typing import Dict, Any


def setup_environment():
    """Setup environment variables for headless operation and stability"""
    
    # Suppress ALSA warnings in headless environment
    os.environ['ALSA_PCM_CARD'] = '-1'
    os.environ['ALSA_PCM_DEVICE'] = '-1'
    os.environ['ALSA_CARD'] = 'none'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['PULSE_RUNTIME_PATH'] = '/tmp/pulse-runtime'
    
    # Prevent multiprocessing resource leaks
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Disable tokenizers parallelism to prevent resource conflicts
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    # Additional environment variables for stability
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    
    # CUDA and GPU settings for headless operation
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    
    # Set multiprocessing start method
    if __name__ == "__main__":
        multiprocessing.set_start_method('spawn', force=True)


class Config:
    """Application configuration"""
    
    # TTS Configuration
    TTS_ENGINE = "kokoro"
    TTS_VOICE = "af_heart"
    TTS_MUTED = True  # Always muted for headless operation
    
    # STT Configuration
    STT_MODEL = "tiny"
    STT_LANGUAGE = "en"
    STT_REALTIME_ENABLED = True
    STT_REALTIME_MODEL = "tiny"
    STT_REALTIME_PAUSE = 0.02
    STT_SILERO_SENSITIVITY = 0.05
    STT_WEBRTC_SENSITIVITY = 3
    STT_POST_SPEECH_SILENCE = 0.7
    STT_MIN_RECORDING_LENGTH = 1.1
    STT_MIN_GAP_BETWEEN_RECORDINGS = 0
    STT_EARLY_TRANSCRIPTION_SILENCE = 0.2
    STT_BEAM_SIZE = 1
    STT_BEAM_SIZE_REALTIME = 1
    STT_DEVICE = 'cpu'
    STT_COMPUTE_TYPE = 'int8'
    
    # LLM Configuration
    LLM_MODEL = "phala/qwen-2.5-7b-instruct"
    LLM_BASE_URL = "https://api.redpill.ai/v1"
    LLM_API_KEY = os.getenv("REDPILL_API_KEY")
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHUNK_SIZE = 256
    AUDIO_CHANNELS = 1
    AUDIO_SAMPLE_WIDTH = 2  # 16-bit
    
    # WebSocket Configuration
    WS_PING_INTERVAL = 30
    WS_PING_TIMEOUT = 10
    
    @classmethod
    def get_stt_config(cls) -> Dict[str, Any]:
        """Get STT engine configuration"""
        return {
            'model': cls.STT_MODEL,
            'language': cls.STT_LANGUAGE,
            'use_microphone': False,
            'spinner': False,
            'enable_realtime_transcription': cls.STT_REALTIME_ENABLED,
            'realtime_model_type': cls.STT_REALTIME_MODEL,
            'realtime_processing_pause': cls.STT_REALTIME_PAUSE,
            'silero_sensitivity': cls.STT_SILERO_SENSITIVITY,
            'webrtc_sensitivity': cls.STT_WEBRTC_SENSITIVITY,
            'post_speech_silence_duration': cls.STT_POST_SPEECH_SILENCE,
            'min_length_of_recording': cls.STT_MIN_RECORDING_LENGTH,
            'min_gap_between_recordings': cls.STT_MIN_GAP_BETWEEN_RECORDINGS,
            'silero_deactivity_detection': True,
            'early_transcription_on_silence': cls.STT_EARLY_TRANSCRIPTION_SILENCE,
            'beam_size': cls.STT_BEAM_SIZE,
            'beam_size_realtime': cls.STT_BEAM_SIZE_REALTIME,
            'no_log_file': True,
            'device': cls.STT_DEVICE,
            'compute_type': cls.STT_COMPUTE_TYPE,
            'initial_prompt': "Add periods only for complete sentences. Use ellipsis (...) for unfinished thoughts."
        }
    
    @classmethod
    def get_audio_config(cls) -> Dict[str, Any]:
        """Get audio processing configuration"""
        return {
            'sample_rate': cls.AUDIO_SAMPLE_RATE,
            'chunk_size': cls.AUDIO_CHUNK_SIZE,
            'channels': cls.AUDIO_CHANNELS,
            'sample_width': cls.AUDIO_SAMPLE_WIDTH
        } 