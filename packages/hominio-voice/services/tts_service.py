"""
Text-to-Speech Service (Simplified Reference Implementation)
Handles ONLY Kokoro TTS engine with PCM processing and base64 encoding
Routes all communication through message router as single source of truth
NO pipeline logic - only audio synthesis and streaming
"""
import logging
import base64
import numpy as np
import threading
import asyncio
from datetime import datetime
from typing import Optional, Callable
from scipy.signal import resample_poly
from RealtimeTTS import TextToAudioStream, KokoroEngine
from core.config import Config

logger = logging.getLogger(__name__)

class UpsampleOverlap:
    """Reference implementation of upsampling with overlap (from RealtimeVoiceChat)"""
    def __init__(self):
        self.previous_chunk = None
        self.resampled_previous_chunk = None

    def get_base64_chunk(self, chunk: bytes) -> str:
        """Upsample 24kHz PCM to 48kHz and return as base64"""
        audio_int16 = np.frombuffer(chunk, dtype=np.int16)
        if audio_int16.size == 0:
            return ""

        audio_float = audio_int16.astype(np.float32) / 32768.0
        upsampled_current_chunk = resample_poly(audio_float, 48000, 24000)

        if self.previous_chunk is None:
            # First chunk: Output the first half of its upsampled version
            half = len(upsampled_current_chunk) // 2
            part = upsampled_current_chunk[:half]
        else:
            # Subsequent chunks: Combine previous float chunk with current float chunk
            combined = np.concatenate((self.previous_chunk, audio_float))
            up = resample_poly(combined, 48000, 24000)

            # Calculate lengths and indices for extracting the middle part
            assert self.resampled_previous_chunk is not None
            prev_len = len(self.resampled_previous_chunk)
            h_prev = prev_len // 2
            h_cur = (len(up) - prev_len) // 2 + prev_len
            part = up[h_prev:h_cur]

        # Update state for the next iteration
        self.previous_chunk = audio_float
        self.resampled_previous_chunk = upsampled_current_chunk

        # Convert back to PCM16 bytes and encode
        pcm = (part * 32767).astype(np.int16).tobytes()
        return base64.b64encode(pcm).decode('utf-8')

    def flush_base64_chunk(self) -> Optional[str]:
        """Return the final remaining segment after all chunks processed"""
        if self.resampled_previous_chunk is not None:
            pcm = (self.resampled_previous_chunk * 32767).astype(np.int16).tobytes()
            self.previous_chunk = None
            self.resampled_previous_chunk = None
            return base64.b64encode(pcm).decode('utf-8')
        return None

class TTSService:
    """
    Simplified TTS Service - ONLY handles audio synthesis and streaming
    NO pipeline logic, NO complex generators, NO coordination logic
    """
    def __init__(self):
        self.kokoro_engine = None
        self.status = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting TTS engine...",
            "last_updated": datetime.now().isoformat()
        }
        # Simple synthesis state
        self.is_synthesizing = False
        
        # Audio cache management
        self.active_streams = []  # Track active TTS streams for interruption
        
        # Message router reference (set by message router during initialization)
        self.message_router = None
        self.websocket_send_callback = None
    
    def set_message_router(self, router, websocket_send_callback: Callable = None):
        """Set message router reference and WebSocket send callback"""
        self.message_router = router
        self.websocket_send_callback = websocket_send_callback
        logger.info("✅ [TTS] Message router reference set - routing through master coordinator")
    
    def clear_audio_caches(self):
        """
        Clear any internal TTS engine buffers and stop ongoing synthesis
        CRITICAL: Called during VAD interruption to stop audio immediately
        """
        logger.info("🔊🛑 [TTS] CLEARING ALL AUDIO CACHES - interruption triggered")
        
        try:
            # 1. Stop any active synthesis
            self.is_synthesizing = False
            
            # 2. Clear active streams (if any are tracked) - CRITICAL FIX
            if self.active_streams:
                logger.info(f"🔊🧹 [TTS] Clearing {len(self.active_streams)} active streams")
                streams_to_clear = self.active_streams.copy()  # Create copy to avoid modification during iteration
                self.active_streams.clear()  # Clear immediately to prevent new registrations
                
                for stream in streams_to_clear:
                    try:
                        # Try to stop the stream if it has a stop method
                        if hasattr(stream, 'stop'):
                            logger.info(f"🔊🛑 [TTS] Calling stop() on active stream: {type(stream)}")
                            stream.stop()
                        elif hasattr(stream, 'close'):
                            logger.info(f"🔊🛑 [TTS] Calling close() on active stream: {type(stream)}")
                            stream.close()
                    except Exception as e:
                        logger.warning(f"🔊⚠️ [TTS] Error stopping stream {type(stream)}: {e}")
            
            # 3. Clear any Kokoro engine internal buffers (if available)
            if self.kokoro_engine:
                # Note: Kokoro engine may not have explicit clear methods
                # But creating new streams will naturally clear old state
                logger.info("🔊🔄 [TTS] Kokoro engine still active (will clear on next synthesis)")
            
            logger.info("✅ [TTS] Audio cache clearing completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ [TTS] Error clearing audio caches: {e}")
            return False

    def process_audio_chunk(self, audio_data: bytes) -> str:
        """
        Process audio chunk with upsampling (reference-style)
        
        Args:
            audio_data: Raw PCM audio bytes from TTS engine (24kHz)
            
        Returns:
            Base64 encoded upsampled PCM data (48kHz) for frontend AudioWorklet
        """
        try:
            # Create new upsampler for each synthesis to prevent artifacts
            upsampler = UpsampleOverlap()
            base64_chunk = upsampler.get_base64_chunk(audio_data)
            return base64_chunk
            
        except Exception as e:
            logger.error(f"❌ [TTS] Error processing audio chunk: {e}")
            return ""

    async def initialize_kokoro_engine(self):
        """Initialize KokoroEngine for headless operation"""
        try:
            self.status.update({
                "status": "loading",
                "progress": 20,
                "message": "Loading Kokoro TTS model...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Initialize KokoroEngine with voice from config
            self.kokoro_engine = KokoroEngine(voice=Config.TTS_VOICE)
            
            self.status.update({
                "status": "loading",
                "progress": 80,
                "message": "Testing engine in headless mode...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Test the engine by generating a small sample (no playback)
            test_stream = TextToAudioStream(self.kokoro_engine, muted=True)
            test_audio_chunks = []
            
            def collect_chunk(chunk):
                test_audio_chunks.append(chunk)
            
            test_stream.feed("Test")
            test_stream.play(muted=True, on_audio_chunk=collect_chunk)
            
            if test_audio_chunks:
                logger.info(f"✅ Kokoro engine test successful - generated {len(test_audio_chunks)} audio chunks")
            
            self.status.update({
                "status": "ready",
                "progress": 100,
                "message": "Kokoro TTS engine ready for headless synthesis",
                "last_updated": datetime.now().isoformat(),
                "model_info": {
                    "engine": "KokoroEngine",
                    "voice": "af_heart",
                    "language": "English (American)",
                    "mode": "headless",
                    "streaming_supported": True
                }
            })
            
            logger.info("✅ KokoroEngine initialized successfully in headless mode!")
            
        except Exception as e:
            logger.error(f"Failed to initialize KokoroEngine: {e}")
            self.status.update({
                "status": "error",
                "progress": 0,
                "message": f"Failed to initialize Kokoro engine: {str(e)}",
                "last_updated": datetime.now().isoformat(),
                "error": str(e)
            })

    async def synthesize_text_streaming(self, text: str, websocket=None):
        """
        SIMPLE text to audio synthesis with immediate streaming (reference-style)
        NO complex pipeline logic - just synthesize and stream
        
        Args:
            text: Text to synthesize
            websocket: WebSocket connection (for backward compatibility)
        """
        if not self.kokoro_engine:
            raise RuntimeError("TTS engine not initialized")
            
        logger.info(f"🔊 [TTS] Starting simple synthesis: '{text[:50]}...'")
        
        # Create upsampler for this synthesis
        upsampler = UpsampleOverlap()
        
        # Create a new stream for this synthesis (headless mode)
        tts_stream = TextToAudioStream(self.kokoro_engine, muted=Config.TTS_MUTED)
        
        # Track this stream for interruption handling
        self.active_streams.append(tts_stream)

        # Streaming chunk counter
        chunk_count = 0
        
        async def on_audio_chunk(chunk):
            """Stream audio chunks immediately as they're generated (reference pattern)"""
            nonlocal chunk_count
            
            if not self.websocket_send_callback:
                logger.warning(f"🔊 [TTS] No WebSocket callback available - chunk {chunk_count} not sent")
                return
                
            # Process chunk immediately (reference-style)
            base64_chunk = upsampler.get_base64_chunk(chunk)
            if base64_chunk and len(base64_chunk) > 0:
                try:
                    # Validate base64 encoding before sending
                    base64.b64decode(base64_chunk)
                    chunk_count += 1
                    
                    # Stream immediately through message router (reference pattern)
                    await self.websocket_send_callback({
                        "type": "tts_chunk",
                        "content": base64_chunk
                    })
                    
                    logger.debug(f"🔊 [TTS] Streamed chunk {chunk_count} immediately")
                    
                except Exception as e:
                    logger.error(f"❌ [TTS] Invalid base64 chunk {chunk_count} detected, skipping: {e}")

        # Create async-compatible synthesis function
        def synthesize_sync():
            """Synchronous synthesis that calls async chunk handler"""
            def sync_chunk_handler(chunk):
                """Synchronous wrapper for async chunk handler"""
                # Create new event loop for this thread if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run the async handler
                loop.run_until_complete(on_audio_chunk(chunk))
            
            tts_stream.feed(text)
            tts_stream.play(
                muted=Config.TTS_MUTED,
                on_audio_chunk=sync_chunk_handler  # Stream chunks immediately
            )
        
        # Run synthesis in a separate thread (reference pattern)
        synthesis_thread = threading.Thread(target=synthesize_sync, daemon=True)
        synthesis_thread.start()
        logger.debug(f"🔊 [TTS] Synthesis thread started for: '{text[:30]}...'")
        synthesis_thread.join()  # Wait for synthesis to complete
        logger.debug(f"🔊 [TTS] Synthesis thread finished for: '{text[:30]}...'")
        
        # Remove this stream from tracking (synthesis completed)
        if tts_stream in self.active_streams:
            self.active_streams.remove(tts_stream)
        
        # Send final upsampled chunk (reference-style flush)
        if self.websocket_send_callback:
            final_chunk = upsampler.flush_base64_chunk()
            if final_chunk and len(final_chunk) > 0:
                try:
                    # Test decode to ensure it's valid base64
                    base64.b64decode(final_chunk)
                    chunk_count += 1
                    
                    # Route through message router (single source of truth)
                    await self.websocket_send_callback({
                        "type": "tts_chunk", 
                        "content": final_chunk
                    })
                    logger.info("🔊 [TTS] Sent final upsampled chunk through message router")
                except Exception as e:
                    logger.error(f"❌ [TTS] Invalid final base64 chunk detected, skipping: {e}")
                    
            logger.info(f"🔊 [TTS] Simple synthesis completed, sent {chunk_count} chunks immediately")
        else:
            logger.warning(f"🔊 [TTS] No WebSocket callback available - synthesis completed but chunks not sent")

    async def synthesize_text(self, text: str, websocket=None, end_marker: str = "END"):
        """
        Legacy method for backward compatibility - now routes through message router
        
        Args:
            text: Text to synthesize
            websocket: WebSocket connection (for backward compatibility)
            end_marker: End marker to send after synthesis
        """
        await self.synthesize_text_streaming(text, websocket)
        
        # Send end marker through message router (single source of truth)
        if self.websocket_send_callback:
            await self.websocket_send_callback(end_marker)
        else:
            logger.warning(f"🔊 [TTS] No WebSocket callback available - end marker '{end_marker}' not sent")

    def get_status(self):
        """Get current TTS status"""
        status = self.status.copy()
        status["is_synthesizing"] = self.is_synthesizing
        status["message_router_connected"] = self.message_router is not None
        status["routing_method"] = "message_router" if self.websocket_send_callback else "direct_websocket"
        status["responsibility"] = "audio_synthesis_only"
        return status
    
    def is_ready(self):
        """Check if TTS engine is ready"""
        return self.status["status"] == "ready" and self.kokoro_engine is not None 