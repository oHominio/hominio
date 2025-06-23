"""
Speech-to-Text Service
Handles RealtimeSTT engine initialization and speech recognition
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
        # Shared state - these will be updated by main.py callbacks
        self.current_transcript = ""
        self.current_full_sentence = ""
        self.current_realtime_text = ""
        
        # Callback functions - will be set by main.py to handle inter-service communication
        self.on_full_sentence_callback = None
        self.on_realtime_transcription_callback = None
    
    def set_callbacks(self, on_full_sentence=None, on_realtime_transcription=None):
        """Set callback functions for STT events"""
        self.on_full_sentence_callback = on_full_sentence
        self.on_realtime_transcription_callback = on_realtime_transcription
    
    async def process_full_sentence(self, text: str):
        """Process a complete sentence from STT"""
        self.current_full_sentence = text
        logger.info(f"📝 Full sentence: '{text}'")
        
        # Call the callback if set (this will trigger LLM processing)
        if self.on_full_sentence_callback:
            await self.on_full_sentence_callback(text)
    
    def on_realtime_transcription(self, text: str):
        """Handle realtime transcription updates"""
        self.current_realtime_text = text
        logger.debug(f"🔄 Realtime transcription: '{text}'")
        
        # Call the callback if set
        if self.on_realtime_transcription_callback:
            try:
                self.on_realtime_transcription_callback(text)
            except Exception as e:
                logger.error(f"Error in realtime transcription callback: {e}")
    
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
                'on_recording_start': lambda *args: logger.info("🎤 Recording started"),
                'on_recording_stop': lambda *args: logger.info("⏹️ Recording stopped"),
                'on_transcription_start': lambda *args: logger.info("🔄 Transcription started"),
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
                    logger.info("STT engine doesn't support set_log_level method")
            except Exception as e:
                logger.warning(f"Could not set STT log level: {e}")
            
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
            
            logger.info("✅ RealtimeSTT initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize RealtimeSTT: {e}")
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
        logger.info("🧹 Transcript cleared")
    
    async def process_audio_async(self, websocket):
        """Process audio in an async loop"""
        if not self.stt_engine:
            raise RuntimeError("STT engine not initialized")
        
        try:
            # Listen for audio continuously
            while True:
                # Get transcription (this will block until speech is detected)
                transcription = self.stt_engine.text()
                
                if transcription.strip():
                    self.current_transcript = transcription
                    logger.info(f"🎙️ Transcription: '{transcription}'")
                    
                    # Send transcription to client via WebSocket
                    if websocket:
                        await websocket.send_text(json.dumps({
                            "type": "transcription",
                            "text": transcription,
                            "timestamp": datetime.now().isoformat()
                        }))
                    
                    # Process as full sentence (trigger LLM)
                    await self.process_full_sentence(transcription)
                    
        except Exception as e:
            logger.error(f"Error in STT processing: {e}")
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }))
    
    def get_status(self):
        """Get current STT status"""
        return self.status
    
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