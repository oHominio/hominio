"""
Configuration and environment setup for hominio-voice application
"""
import os
import sys
import multiprocessing
import torch
from typing import Dict, Any


def setup_environment():
    """Setup environment variables for headless operation and stability"""
    
    # Suppress ALSA warnings in headless environment
    os.environ['ALSA_PCM_CARD'] = '-1'
    os.environ['ALSA_PCM_DEVICE'] = '-1'
    os.environ['ALSA_CARD'] = 'none'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['PULSE_RUNTIME_PATH'] = '/tmp/pulse-runtime'
    
    # Additional ALSA suppression for headless operation
    os.environ['ALSA_MIXER_CARD'] = 'none'
    os.environ['ALSA_MIXER_DEVICE'] = '-1'
    os.environ['ALSA_SEQ_CARD'] = 'none'
    os.environ['ALSA_SEQ_DEVICE'] = '-1'
    
    # Redirect ALSA error output to null
    try:
        import ctypes
        import ctypes.util
        
        # Try to suppress ALSA errors at the C library level
        alsa_lib = ctypes.util.find_library('asound')
        if alsa_lib:
            libasound = ctypes.CDLL(alsa_lib)
            # Set ALSA error handler to null to suppress warnings
            libasound.snd_lib_error_set_handler(None)
            print("✅ ALSA error handler suppressed")
    except Exception as e:
        print(f"⚠️ Could not suppress ALSA errors: {e}")
    
    # Prevent multiprocessing resource leaks and SIGABRT crashes
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # CRITICAL: Fix multiprocessing semaphore leaks
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMBA_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    
    # Force single-threaded execution for stability
    os.environ['PYTORCH_NUM_THREADS'] = '1'
    os.environ['TF_NUM_INTRAOP_THREADS'] = '1'
    os.environ['TF_NUM_INTEROP_THREADS'] = '1'
    
    # FORCE CUDA usage - NO CPU FALLBACKS
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Force GPU 0
    os.environ['NVIDIA_VISIBLE_DEVICES'] = 'all'
    os.environ['NVIDIA_DRIVER_CAPABILITIES'] = 'compute,utility'
    os.environ['FORCE_CUDA'] = '1'
    
    # Multiprocessing stability - CRITICAL for preventing SIGABRT
    try:
        # Set multiprocessing start method BEFORE any other imports
        multiprocessing.set_start_method('spawn', force=True)
        print("✅ Set multiprocessing start method to 'spawn'")
    except RuntimeError as e:
        print(f"⚠️ Could not set multiprocessing start method: {e}")
    
    # Additional stability fixes
    os.environ['MALLOC_TRIM_THRESHOLD_'] = '0'  # Prevent memory fragmentation
    os.environ['MALLOC_MMAP_THRESHOLD_'] = '131072'  # Control memory mapping
    
    # CUDA validation - warn but don't exit immediately to allow container startup
    try:
        if not torch.cuda.is_available():
            print("⚠️ WARNING: CUDA is not available! This application requires GPU acceleration.")
            print("⚠️ Please ensure:")
            print("   1. NVIDIA GPU is properly configured")
            print("   2. NVIDIA drivers are installed")
            print("   3. CUDA runtime is available")
            print("   4. Container has GPU access")
            print("🔄 Continuing startup - CUDA validation will happen during engine initialization...")
        else:
            # Log CUDA information
            print(f"✅ CUDA is available! Device count: {torch.cuda.device_count()}")
            print(f"✅ Current CUDA device: {torch.cuda.current_device()}")
            print(f"✅ CUDA device name: {torch.cuda.get_device_name(0)}")
            print(f"✅ CUDA version: {torch.version.cuda}")
            
            # Force PyTorch to use CUDA
            torch.cuda.set_device(0)
            print("🚀 Forced PyTorch to use CUDA device 0")
    except ImportError:
        print("⚠️ PyTorch not yet available - CUDA validation will happen later")
    except Exception as e:
        print(f"⚠️ CUDA validation error: {e}")
        print("🔄 Continuing startup - will retry during engine initialization...")


class Config:
    """Application configuration"""
    
    # TTS Configuration
    TTS_ENGINE = "kokoro"
    TTS_VOICE = "af_heart"
    TTS_MUTED = True  # Always muted for headless operation
    
    # STT Configuration - MATCHED TO REFERENCE IMPLEMENTATION (RealtimeVoiceChat)
    STT_MODEL = "base.en"  # Changed from "tiny" to match reference implementation
    STT_LANGUAGE = "en"
    STT_REALTIME_ENABLED = True
    STT_REALTIME_MODEL = "base.en"  # Changed from "tiny" to match reference implementation
    STT_REALTIME_PAUSE = 0.2  # RealtimeSTT README default (was 0.02)
    
    # VAD Configuration - MATCHED TO REFERENCE IMPLEMENTATION BEST PRACTICES
    STT_SILERO_SENSITIVITY = 0.6  # RealtimeSTT README default (was 0.05)
    STT_WEBRTC_SENSITIVITY = 3     # Matches main.py hardcoded value
    STT_POST_SPEECH_SILENCE = 0.2  # RealtimeSTT README default (was 0.7)
    STT_MIN_RECORDING_LENGTH = 1.0  # RealtimeSTT README default (was 1.1)
    STT_MIN_GAP_BETWEEN_RECORDINGS = 1.0  # RealtimeSTT README default (was 0)
    STT_EARLY_TRANSCRIPTION_SILENCE = 0  # RealtimeSTT README default (was 0.2)
    
    # Dynamic VAD settings for different conversation phases
    STT_MID_SENTENCE_PAUSE = 0.3      # Shorter pause for mid-sentence detection
    STT_END_SENTENCE_PAUSE = 0.7      # Standard pause for sentence endings
    STT_UNKNOWN_SENTENCE_PAUSE = 1.0  # Longer pause for unclear speech patterns
    
    STT_BEAM_SIZE = 5  # RealtimeSTT README default (was 1)
    STT_BEAM_SIZE_REALTIME = 3  # RealtimeSTT README default (was 1)
    STT_DEVICE = 'cuda'  # Force GPU usage - NO CPU FALLBACK
    STT_COMPUTE_TYPE = 'int8'
    
    # Additional STT Configuration from main.py
    STT_USE_MICROPHONE = False
    STT_SPINNER = False
    STT_SILERO_USE_ONNX = True
    STT_SILERO_DEACTIVITY_DETECTION = True
    STT_NO_LOG_FILE = True
    STT_DEBUG_MODE = False  # main.py doesn't set this
    STT_INITIAL_PROMPT = "Add periods only for complete sentences. Use ellipsis (...) for unfinished thoughts."
    STT_USE_MAIN_MODEL_FOR_REALTIME = False
    STT_FASTER_WHISPER_VAD_FILTER = False
    STT_ALLOWED_LATENCY_LIMIT = 500
    
    # LLM Configuration
    LLM_MODEL = "phala/llama-3.3-70b-instruct"
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
    def get_stt_config(cls, vad_callbacks: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get STT engine configuration matching main.py hardcoded values exactly"""
        config = {
            'model': cls.STT_MODEL,
            'language': cls.STT_LANGUAGE,
            'use_microphone': cls.STT_USE_MICROPHONE,
            'spinner': cls.STT_SPINNER,
            'enable_realtime_transcription': cls.STT_REALTIME_ENABLED,
            'realtime_model_type': cls.STT_REALTIME_MODEL,
            'realtime_processing_pause': cls.STT_REALTIME_PAUSE,
            'silero_sensitivity': cls.STT_SILERO_SENSITIVITY,
            'webrtc_sensitivity': cls.STT_WEBRTC_SENSITIVITY,
            'post_speech_silence_duration': cls.STT_POST_SPEECH_SILENCE,
            'min_length_of_recording': cls.STT_MIN_RECORDING_LENGTH,
            'min_gap_between_recordings': cls.STT_MIN_GAP_BETWEEN_RECORDINGS,
            'silero_deactivity_detection': cls.STT_SILERO_DEACTIVITY_DETECTION,
            'early_transcription_on_silence': cls.STT_EARLY_TRANSCRIPTION_SILENCE,
            'beam_size': cls.STT_BEAM_SIZE,
            'beam_size_realtime': cls.STT_BEAM_SIZE_REALTIME,
            'no_log_file': cls.STT_NO_LOG_FILE,
            'device': cls.STT_DEVICE,
            'compute_type': cls.STT_COMPUTE_TYPE,
            'initial_prompt': cls.STT_INITIAL_PROMPT,
            # Note: level and on_realtime_transcription_update will be added when used
        }
        
        # Add VAD callbacks if provided
        if vad_callbacks:
            config.update(vad_callbacks)
        
        return config
    
    @classmethod
    def get_audio_config(cls) -> Dict[str, Any]:
        """Get audio processing configuration"""
        return {
            'sample_rate': cls.AUDIO_SAMPLE_RATE,
            'chunk_size': cls.AUDIO_CHUNK_SIZE,
            'channels': cls.AUDIO_CHANNELS,
            'sample_width': cls.AUDIO_SAMPLE_WIDTH
        } 