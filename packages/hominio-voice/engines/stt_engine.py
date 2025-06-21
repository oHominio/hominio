"""
STT Engine Management
Handles RealtimeSTT initialization and management with enhanced VAD
"""
import logging
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from RealtimeSTT import AudioToTextRecorder

from core.config import Config

logger = logging.getLogger(__name__)


class STTEngineManager:
    """Manages STT engine initialization and transcription operations with VAD"""
    
    def __init__(self):
        self.engine: Optional[AudioToTextRecorder] = None
        self.status = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting STT engine...",
            "last_updated": datetime.now().isoformat()
        }
        self._is_ready = False
        self.message_queue: Optional[asyncio.Queue] = None
        self.transcription_thread: Optional[threading.Thread] = None
        
        # VAD state tracking
        self.vad_active = False
        self.is_listening = False
        
        # Callbacks for state changes
        self.on_vad_start: Optional[Callable] = None
        self.on_vad_stop: Optional[Callable] = None
        self.on_vad_detect_start: Optional[Callable] = None
        self.on_vad_detect_stop: Optional[Callable] = None
        self.on_realtime_transcription: Optional[Callable] = None
        self.on_final_transcription: Optional[Callable] = None
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set callback functions for various STT events"""
        self.on_vad_start = callbacks.get('on_vad_start')
        self.on_vad_stop = callbacks.get('on_vad_stop')
        self.on_vad_detect_start = callbacks.get('on_vad_detect_start')
        self.on_vad_detect_stop = callbacks.get('on_vad_detect_stop')
        self.on_realtime_transcription = callbacks.get('on_realtime_transcription')
        self.on_final_transcription = callbacks.get('on_final_transcription')
    
    async def initialize(self) -> bool:
        """Initialize the STT engine with enhanced VAD"""
        try:
            logger.info("🎤 Initializing STT engine...")
            
            self.status.update({
                "status": "loading",
                "progress": 20,
                "message": "Loading Whisper STT model...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Create message queue for WebSocket communication
            self.message_queue = asyncio.Queue()
            
            # Get current event loop for callbacks
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            
            # Define VAD callback functions
            def on_vad_detect_start():
                """Called when voice activity is first detected"""
                logger.info("🎤 VAD: Voice activity detected")
                self.vad_active = True
                if self.on_vad_detect_start:
                    self.on_vad_detect_start()
                
                # Send VAD detection message
                if loop and not loop.is_closed():
                    message = {'type': 'vad_detect_start'}
                    asyncio.run_coroutine_threadsafe(
                        self.message_queue.put(message), loop
                    )
            
            def on_vad_detect_stop():
                """Called when voice activity stops"""
                logger.info("🎤 VAD: Voice activity stopped")
                self.vad_active = False
                if self.on_vad_detect_stop:
                    self.on_vad_detect_stop()
                
                # Send VAD stop message
                if loop and not loop.is_closed():
                    message = {'type': 'vad_detect_stop'}
                    asyncio.run_coroutine_threadsafe(
                        self.message_queue.put(message), loop
                    )
            
            def on_realtime_transcription_update(text: str):
                """Handle real-time transcription updates"""
                if loop and not loop.is_closed():
                    # Clean up text
                    text = text.lstrip()
                    if text.startswith("..."):
                        text = text[3:]
                    if text.endswith("...'."):
                        text = text[:-1]
                    if text.endswith("...'"):
                        text = text[:-1]
                    text = text.lstrip()
                    if text:
                        text = text[0].upper() + text[1:]
                    
                    if self.on_realtime_transcription:
                        self.on_realtime_transcription(text)
                    
                    message = {'type': 'realtime', 'text': text}
                    try:
                        asyncio.run_coroutine_threadsafe(
                            self.message_queue.put(message), loop
                        )
                    except Exception as e:
                        logger.error(f"Error sending realtime transcription: {e}")
            
            def process_full_sentence(full_sentence: str):
                """Callback for when a full sentence is transcribed"""
                logger.info(f"✅ STT Full sentence: {full_sentence}")
                
                # Send final transcription message
                if loop and not loop.is_closed():
                    message = {'type': 'fullSentence', 'text': full_sentence}
                    asyncio.run_coroutine_threadsafe(
                        self.message_queue.put(message), loop
                    )
                
                # Trigger conversation processing with the transcribed text
                if full_sentence.strip():
                    # Import here to avoid circular imports
                    from services.conversation_manager import conversation_manager
                    
                    # Schedule the async task in the main event loop (like the old code)
                    if loop and not loop.is_closed():
                        asyncio.run_coroutine_threadsafe(
                            conversation_manager.process_user_input(full_sentence.strip()), 
                            loop
                        )
                    else:
                        logger.error("Event loop not available to schedule LLM call.")
            
            self.status.update({
                "status": "loading",
                "progress": 60,
                "message": "Configuring VAD callbacks...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Create VAD callbacks dictionary
            vad_callbacks = {
                'on_vad_detect_start': on_vad_detect_start,
                'on_vad_detect_stop': on_vad_detect_stop,
                'on_realtime_transcription_update': on_realtime_transcription_update,
            }
            
            # Get STT configuration with VAD callbacks
            stt_config = Config.get_stt_config(vad_callbacks)
            
            self.status.update({
                "status": "loading",
                "progress": 80,
                "message": "Creating STT recorder...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Create STT engine
            self.engine = AudioToTextRecorder(**stt_config)
            
            # Note: Do NOT call engine.listen() here - the text() method handles listening
            logger.info("🔄 STT engine created, ready for transcription loop")
            
            self.status.update({
                "status": "ready",
                "progress": 100,
                "message": "STT engine ready with enhanced VAD",
                "last_updated": datetime.now().isoformat(),
                "model_info": {
                    "engine": "RealtimeSTT",
                    "model": Config.STT_MODEL,
                    "language": Config.STT_LANGUAGE,
                    "vad_enabled": True,
                    "silero_sensitivity": Config.STT_SILERO_SENSITIVITY,
                    "webrtc_sensitivity": Config.STT_WEBRTC_SENSITIVITY
                }
            })
            
            self._is_ready = True
            
            logger.info("✅ STT engine initialized successfully with enhanced VAD")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize STT engine: {e}")
            self.status.update({
                "status": "error",
                "progress": 0,
                "message": f"Failed to initialize STT engine: {str(e)}",
                "last_updated": datetime.now().isoformat(),
                "error": str(e)
            })
            return False
    
    def is_ready(self) -> bool:
        """Check if the engine is ready"""
        return self._is_ready and self.engine is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return self.status.copy()
    
    def get_message_queue(self) -> Optional[asyncio.Queue]:
        """Get the message queue for WebSocket communication"""
        return self.message_queue
    
    def feed_audio(self, audio_data: bytes):
        """Feed audio data to the STT engine"""
        if not self.is_ready():
            logger.warning("STT engine not ready for audio data")
            return
        
        try:
            self.engine.feed_audio(audio_data)
        except Exception as e:
            logger.error(f"Error feeding audio to STT engine: {e}")
    
    def start_listening(self):
        """Start listening for audio input"""
        if not self.is_listening:
            self.is_listening = True
            logger.info("👂 STT engine started listening")
            # Start the continuous transcription loop when we start listening
            if not self.transcription_thread or not self.transcription_thread.is_alive():
                self.start_transcription_loop()
        else:
            logger.debug("👂 STT engine already listening")
    
    def stop_listening(self):
        """Stop listening for audio input"""
        self.is_listening = False
        logger.info("👂 STT engine stopped listening")
    
    def get_vad_state(self) -> Dict[str, bool]:
        """Get current VAD state"""
        return {
            "vad_active": self.vad_active,
            "is_listening": self.is_listening
        }
    
    def shutdown(self):
        """Shutdown the STT engine"""
        logger.info("🎤 Shutting down STT engine")
        
        try:
            self._is_ready = False
            
            # Wait for transcription thread to finish
            if self.transcription_thread and self.transcription_thread.is_alive():
                self.transcription_thread.join(timeout=2.0)
            
            # Shutdown the engine
            if self.engine:
                self.engine.shutdown()
                self.engine = None
                
            logger.info("🎤 STT engine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error shutting down STT engine: {e}")
        finally:
            self._is_ready = False

    def start_transcription_loop(self):
        """Start the continuous transcription loop following reference implementation pattern"""
        if not self._is_ready or not self.engine:
            logger.error("Cannot start transcription loop: STT engine not ready")
            return
            
        def transcription_loop():
            """Continuous transcription loop - follows reference implementation pattern"""
            logger.info("🔄 Starting continuous transcription loop...")
            
            def on_final_transcription(text: str):
                """Callback for when a full sentence is transcribed"""
                logger.info(f"✅ STT Full sentence: {text}")
                
                # Send final transcription message
                if self.message_queue:
                    try:
                        # Get the current event loop
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = asyncio.get_event_loop()
                            
                        message = {'type': 'fullSentence', 'text': text}
                        asyncio.run_coroutine_threadsafe(
                            self.message_queue.put(message), loop
                        )
                    except Exception as e:
                        logger.error(f"Error sending final transcription: {e}")
                
                # Trigger conversation processing
                if text.strip() and self.on_final_transcription:
                    try:
                        # Get the current event loop
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = asyncio.get_event_loop()
                            
                        # Schedule the async task in the main event loop
                        asyncio.run_coroutine_threadsafe(
                            self.on_final_transcription(text.strip()), 
                            loop
                        )
                    except Exception as e:
                        logger.error(f"Error scheduling conversation processing: {e}")
            
            # Continuous transcription loop - this is the key pattern from reference
            while self._is_ready and self.is_listening:
                try:
                    logger.debug("🔄 Calling STT engine text() method...")
                    # This blocks until a complete transcription is available
                    # When it returns, we immediately call it again for continuous processing
                    self.engine.text(on_final_transcription)
                    logger.debug("🔄 STT engine text() method returned, calling again...")
                except Exception as e:
                    logger.error(f"STT transcription error: {e}")
                    time.sleep(0.1)  # Brief pause on error before retrying
                    
            logger.info("🔄 Transcription loop ended")
        
        # Start the transcription loop in a daemon thread
        self.transcription_thread = threading.Thread(target=transcription_loop, daemon=True)
        self.transcription_thread.start()
        logger.info("🔄 Transcription loop thread started")


# Global STT engine manager instance
stt_manager = STTEngineManager() 