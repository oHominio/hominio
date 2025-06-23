"""
Speech-to-Text Service
Handles RealtimeSTT engine initialization and speech recognition
Routes all communication through message router as single source of truth
"""
import logging
import json
from datetime import datetime
from RealtimeSTT import AudioToTextRecorder
from core.config import Config

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self):
        self.stt_engine = None
        self.status = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting STT engine...",
            "last_updated": datetime.now().isoformat()
        }
        # Shared state - these will be updated by callbacks
        self.current_transcript = ""
        self.current_full_sentence = ""
        self.current_realtime_text = ""
        
        # Callback functions - will be set by message router for coordination
        self.on_full_sentence_callback = None
        self.on_realtime_transcription_callback = None
        
        # Message router reference (set by message router during initialization)
        self.message_router = None
    
    def set_message_router(self, router):
        """Set message router reference for coordination"""
        self.message_router = router
        logger.info("✅ [STT] Message router reference set - routing through master coordinator")
    
    def set_callbacks(self, on_full_sentence=None, on_realtime_transcription=None):
        """Set callback functions for STT events (called by message router)"""
        self.on_full_sentence_callback = on_full_sentence
        self.on_realtime_transcription_callback = on_realtime_transcription
        logger.info("✅ [STT] Callbacks set by message router")
    
    async def process_full_sentence(self, text: str):
        """Process a complete sentence from STT - routes through message router"""
        self.current_full_sentence = text
        logger.info(f"📝 [STT] Full sentence: '{text}'")
        
        # Call the callback if set (this routes through message router)
        if self.on_full_sentence_callback:
            await self.on_full_sentence_callback(text)
    
    def on_realtime_transcription(self, text: str):
        """Handle realtime transcription updates - routes through message router"""
        self.current_realtime_text = text
        logger.debug(f"🔄 [STT] Realtime transcription: '{text}'")
        
        # Call the callback if set (this routes through message router)
        if self.on_realtime_transcription_callback:
            try:
                self.on_realtime_transcription_callback(text)
            except Exception as e:
                logger.error(f"❌ [STT] Error in realtime transcription callback: {e}")
    
    async def initialize_stt_engine(self):
        """Initialize RealtimeSTT engine"""
        try:
            self.status.update({
                "status": "loading",
                "progress": 20,
                "message": "Loading Whisper model...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Create VAD callbacks for different states
            vad_callbacks = {
                'on_realtime_transcription_update': self.on_realtime_transcription,
                'on_recording_start': lambda *args: logger.info("🎤 [STT] Recording started"),
                'on_recording_stop': lambda *args: logger.info("⏹️ [STT] Recording stopped"),
                'on_transcription_start': lambda *args: logger.info("🔄 [STT] Transcription started"),
            }
            
            # Get STT configuration from config
            stt_config = Config.get_stt_config(vad_callbacks)
            
            self.status.update({
                "status": "loading",
                "progress": 50,
                "message": "Initializing audio recorder...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Initialize AudioToTextRecorder with config
            self.stt_engine = AudioToTextRecorder(**stt_config)
            
            self.status.update({
                "status": "loading",
                "progress": 80,
                "message": "Testing engine...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Set logging level (if method exists)
            try:
                if hasattr(self.stt_engine, 'set_log_level'):
                    self.stt_engine.set_log_level(logging.WARNING)
                else:
                    logger.info("[STT] Engine doesn't support set_log_level method")
            except Exception as e:
                logger.warning(f"[STT] Could not set log level: {e}")
            
            # Engine is ready
            self.status.update({
                "status": "ready",
                "progress": 100,
                "message": "STT engine ready for audio processing",
                "last_updated": datetime.now().isoformat(),
                "model_info": {
                    "model": Config.STT_MODEL,
                    "realtime_model": Config.STT_REALTIME_MODEL,
                    "language": Config.STT_LANGUAGE,
                    "device": Config.STT_DEVICE
                }
            })
            
            logger.info("✅ [STT] RealtimeSTT initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ [STT] Failed to initialize RealtimeSTT: {e}")
            self.status.update({
                "status": "error",
                "progress": 0,
                "message": f"Failed to initialize STT engine: {str(e)}",
                "last_updated": datetime.now().isoformat(),
                "error": str(e)
            })
            raise
    
    async def feed_audio_data(self, audio_data: bytes):
        """Feed audio data to STT engine"""
        if not self.stt_engine:
            raise RuntimeError("STT engine not initialized")
        
        # Feed audio data to the engine
        self.stt_engine.feed_audio(audio_data)
    
    async def clear_transcript(self):
        """Clear all transcript data"""
        self.current_transcript = ""
        self.current_full_sentence = ""
        self.current_realtime_text = ""
        logger.info("🧹 [STT] Transcript cleared")
    
    async def process_audio_async(self, message_router_callback=None):
        """
        Process audio in an async loop - routes through message router
        
        Args:
            message_router_callback: Callback to send messages through message router
        """
        if not self.stt_engine:
            raise RuntimeError("STT engine not initialized")
        
        try:
            # Listen for audio continuously
            while True:
                # Get transcription (this will block until speech is detected)
                transcription = self.stt_engine.text()
                
                if transcription.strip():
                    self.current_transcript = transcription
                    logger.info(f"🎙️ [STT] Transcription: '{transcription}'")
                    
                    # Send transcription through message router (single source of truth)
                    if message_router_callback:
                        await message_router_callback({
                            "type": "transcription",
                            "text": transcription,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Process as full sentence (routes through message router)
                    await self.process_full_sentence(transcription)
                    
        except Exception as e:
            logger.error(f"❌ [STT] Error in audio processing: {e}")
            if message_router_callback:
                await message_router_callback({
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def get_status(self):
        """Get current STT status"""
        status = self.status.copy()
        status["message_router_connected"] = self.message_router is not None
        status["callbacks_set"] = bool(self.on_full_sentence_callback and self.on_realtime_transcription_callback)
        return status
    
    def get_current_transcript(self):
        """Get current transcript data"""
        return {
            "full_sentence": self.current_full_sentence,
            "realtime_text": self.current_realtime_text,
            "transcript": self.current_transcript
        }
    
    def is_ready(self):
        """Check if STT engine is ready"""
        return self.status["status"] == "ready" and self.stt_engine is not None 