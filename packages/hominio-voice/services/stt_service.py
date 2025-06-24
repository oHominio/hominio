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
from .turndetect import TurnDetection
import time

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
        self.on_vad_interruption_callback = None  # NEW: For speech pipeline abort
        
        # TurnDetection for intelligent interruption timing
        self.turn_detection = None
        self.current_waiting_time = 0.0
        
        # Message router reference (set by message router during initialization)
        self.message_router = None
        
        # NEW: Startup grace period to prevent immediate interruptions
        self.startup_time = None
        self.startup_grace_period = 2.5  # 2.5 seconds grace period after initialization
        self.min_text_length_for_interruption = 3  # Minimum text length to consider for interruption
    
    def set_message_router(self, router):
        """Set message router reference for coordination"""
        self.message_router = router
        logger.info("✅ [STT] Message router reference set - routing through master coordinator")
    
    def set_callbacks(self, on_full_sentence=None, on_realtime_transcription=None, on_vad_interruption=None):
        """Set callback functions for STT events (called by message router)"""
        self.on_full_sentence_callback = on_full_sentence
        self.on_realtime_transcription_callback = on_realtime_transcription
        self.on_vad_interruption_callback = on_vad_interruption
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
        
        # Feed to TurnDetection for intelligent analysis
        if self.turn_detection and text and text.strip():
            # NEW: Additional safety check - don't feed very short text during startup
            if self.startup_time and (time.time() - self.startup_time) < self.startup_grace_period:
                if len(text.strip()) < self.min_text_length_for_interruption:
                    logger.debug(f"🎤🔍 [STT] STARTUP PERIOD - Skipping short text for TurnDetection: '{text}' (length: {len(text.strip())})")
                    # Still call the callback for UI updates, but don't feed to TurnDetection
                    if self.on_realtime_transcription_callback:
                        try:
                            self.on_realtime_transcription_callback(text)
                        except Exception as e:
                            logger.error(f"❌ [STT] Error in realtime transcription callback: {e}")
                    return
            
            try:
                self.turn_detection.calculate_waiting_time(text)
                logger.debug(f"🎤🧠 [STT] Fed text to TurnDetection: '{text}'")
            except Exception as e:
                logger.error(f"❌ [STT] Error feeding text to TurnDetection: {e}")
        
        # Call the callback if set (this routes through message router)
        if self.on_realtime_transcription_callback:
            try:
                self.on_realtime_transcription_callback(text)
            except Exception as e:
                logger.error(f"❌ [STT] Error in realtime transcription callback: {e}")
    
    def on_turn_detection_update(self, waiting_time: float, text: str = None):
        """
        Handle TurnDetection waiting time updates
        CRITICAL: This determines WHEN to actually interrupt based on sentence completion
        """
        try:
            self.current_waiting_time = waiting_time
            logger.info(f"🎤⏱️ [STT] TurnDetection suggests waiting {waiting_time:.2f}s for: '{text}'")
            
            # NEW: Check startup grace period to prevent immediate interruptions
            if self.startup_time and (time.time() - self.startup_time) < self.startup_grace_period:
                logger.info(f"🎤⏳ [STT] STARTUP GRACE PERIOD - Ignoring interruption for {self.startup_grace_period - (time.time() - self.startup_time):.1f}s more")
                return
            
            # NEW: Filter out very short/empty text that might cause false interruptions
            if not text or len(text.strip()) < self.min_text_length_for_interruption:
                logger.info(f"🎤🔍 [STT] TEXT TOO SHORT - Ignoring interruption for text: '{text}' (length: {len(text.strip()) if text else 0})")
                return
            
            # Smart interruption logic based on waiting time
            if waiting_time < 0.8:  # Very short wait = likely sentence complete
                logger.info("🎤🛑 [STT] SHORT WAIT - SENTENCE LIKELY COMPLETE - TRIGGERING IMMEDIATE INTERRUPT")
                self.trigger_intelligent_interruption("sentence_complete", waiting_time)
            elif waiting_time < 1.5:  # Medium wait = possible pause
                logger.info("🎤⏸️ [STT] MEDIUM WAIT - POSSIBLE PAUSE - TRIGGERING POLITE INTERRUPT")
                self.trigger_intelligent_interruption("pause_detected", waiting_time)
            else:  # Long wait = mid-sentence
                logger.info("🎤⏳ [STT] LONG WAIT - MID-SENTENCE - NO INTERRUPT (wait for completion)")
                # Don't interrupt - wait for sentence to complete
        except Exception as e:
            logger.error(f"❌ [STT] CRITICAL ERROR in turn detection update - preventing disconnection: {e}")
            # Don't re-raise the exception to prevent disconnection

    def trigger_intelligent_interruption(self, reason: str, confidence: float):
        """Trigger intelligent interruption with context"""
        try:
            logger.info(f"🎤🧠 [STT] INTELLIGENT INTERRUPT: {reason} (confidence: {confidence:.2f}s)")
            
            # Immediately trigger speech pipeline abort through message router
            if self.on_vad_interruption_callback:
                try:
                    self.on_vad_interruption_callback(f"intelligent_interruption_{reason}")
                except Exception as e:
                    logger.error(f"❌ [STT] Error in intelligent interruption callback: {e}")
            
            # Send detailed interrupt info through message router
            if self.message_router:
                import asyncio
                try:
                    async def send_intelligent_interrupt():
                        await self.message_router.send_websocket_message({
                            "type": "intelligent_interrupt",
                            "reason": reason,
                            "confidence": confidence,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(send_intelligent_interrupt(), loop)
                    except RuntimeError:
                        asyncio.run(send_intelligent_interrupt())
                except Exception as e:
                    logger.error(f"❌ [STT] Error sending intelligent interrupt: {e}")
        except Exception as e:
            logger.error(f"❌ [STT] CRITICAL ERROR in trigger_intelligent_interruption - preventing disconnection: {e}")
            # Don't re-raise the exception to prevent disconnection

    def on_vad_recording_start(self, *args):
        """Handle VAD detection start - Now with INTELLIGENT turn detection"""
        logger.info("🎤🔍 [STT] VAD detected user speech - analyzing with TurnDetection")
        
        # Send basic VAD start for UI feedback
        if self.message_router:
            import asyncio
            try:
                async def send_vad_start():
                    await self.message_router.send_websocket_message({
                        "type": "vad_detect_start",
                        "timestamp": datetime.now().isoformat()
                    })
                
                try:
                    loop = asyncio.get_event_loop()
                    asyncio.run_coroutine_threadsafe(send_vad_start(), loop)
                except RuntimeError:
                    asyncio.run(send_vad_start())
            except Exception as e:
                logger.error(f"❌ [STT] Error sending VAD start: {e}")
        
        # The actual interruption decision is now handled by TurnDetection
        # when it processes the current transcript and calculates waiting time
    
    def on_vad_recording_stop(self, *args):
        """Handle VAD detection stop"""
        logger.info("⏹️ [STT] VAD stopped detecting speech")
        
        # Send VAD stop through message router for frontend coordination
        if self.message_router:
            import asyncio
            try:
                async def send_vad_stop():
                    await self.message_router.send_websocket_message({
                        "type": "vad_detect_stop", 
                        "timestamp": datetime.now().isoformat()
                    })
                
                try:
                    loop = asyncio.get_event_loop()
                    asyncio.run_coroutine_threadsafe(send_vad_stop(), loop)
                except RuntimeError:
                    asyncio.run(send_vad_stop())
            except Exception as e:
                logger.error(f"❌ [STT] Error sending VAD stop message: {e}")
    
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
                'on_recording_start': self.on_vad_recording_start,  # NEW: Trigger interruption
                'on_recording_stop': self.on_vad_recording_stop,   # NEW: Handle VAD stop
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
            
            # Initialize TurnDetection for intelligent interruption
            self.status.update({
                "status": "loading",
                "progress": 90,
                "message": "Initializing turn detection...",
                "last_updated": datetime.now().isoformat()
            })
            
            # NEW: Set startup time BEFORE turn detection to activate grace period
            self.startup_time = time.time()
            logger.info(f"🎤⏰ [STT] Startup grace period activated for {self.startup_grace_period}s")
            
            # Initialize TurnDetection but mark it as inactive during startup
            self.turn_detection = TurnDetection(
                on_new_waiting_time=self.on_turn_detection_update,
                local=True,  # Use local model
                pipeline_latency=0.3,  # Adjust based on your system
                pipeline_latency_overhead=0.1
            )
            
            # Engine is ready
            self.status.update({
                "status": "ready",
                "progress": 100,
                "message": "STT engine with turn detection ready (grace period active)",
                "last_updated": datetime.now().isoformat(),
                "model_info": {
                    "model": Config.STT_MODEL,
                    "realtime_model": Config.STT_REALTIME_MODEL,
                    "language": Config.STT_LANGUAGE,
                    "device": Config.STT_DEVICE,
                    "turn_detection": "enabled_with_grace_period"
                }
            })
            
            logger.info("✅ [STT] RealtimeSTT with TurnDetection initialized successfully!")
            logger.info(f"🎤⏰ [STT] Turn detection will be fully active after {self.startup_grace_period}s grace period")
            
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