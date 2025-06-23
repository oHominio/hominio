"""
Text-to-Speech Service (Reference-style implementation)
Handles Kokoro TTS engine with PCM processing and base64 encoding like RealtimeVoiceChat
Routes all communication through message router as single source of truth
"""
import logging
import base64
import numpy as np
import threading
import asyncio
from datetime import datetime
from typing import AsyncGenerator, Optional, Callable
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
    def __init__(self):
        self.kokoro_engine = None
        self.status = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting TTS engine...",
            "last_updated": datetime.now().isoformat()
        }
        # Streaming state
        self.current_synthesis_task = None
        self.is_synthesizing = False
        # Upsampling processor (reference implementation)
        self.upsampler = UpsampleOverlap()
        
        # Message router reference (set by message router during initialization)
        self.message_router = None
        self.websocket_send_callback = None
    
    def set_message_router(self, router, websocket_send_callback: Callable = None):
        """Set message router reference and WebSocket send callback"""
        self.message_router = router
        self.websocket_send_callback = websocket_send_callback
        logger.info("✅ [TTS] Message router reference set - routing through master coordinator")
    
    def process_audio_chunk(self, audio_data: bytes) -> str:
        """
        Process audio chunk with upsampling (reference-style)
        
        Args:
            audio_data: Raw PCM audio bytes from TTS engine (24kHz)
            
        Returns:
            Base64 encoded upsampled PCM data (48kHz) for frontend AudioWorklet
        """
        try:
            # Use reference implementation upsampling (24kHz → 48kHz)
            base64_chunk = self.upsampler.get_base64_chunk(audio_data)
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
            # No audio device initialization needed for headless operation
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
        Synthesize text to audio and stream as base64 PCM chunks (reference-style)
        Routes all communication through message router
        
        Args:
            text: Text to synthesize
            websocket: WebSocket connection (for backward compatibility, but routed through message router)
        """
        if not self.kokoro_engine:
            raise RuntimeError("TTS engine not initialized")
            
        logger.info(f"🔊 [TTS] Starting reference-style synthesis: '{text[:50]}...'")
        
        # Reset upsampler state for new synthesis (prevent artifacts)
        self.upsampler = UpsampleOverlap()
        
        # Create a new stream for this synthesis (headless mode)
        tts_stream = TextToAudioStream(self.kokoro_engine, muted=Config.TTS_MUTED)

        # Store audio chunks to process them
        audio_chunks = []
        
        def on_audio_chunk(chunk):
            """Collect audio chunks during synthesis"""
            audio_chunks.append(chunk)

        # Feed the text to TTS and synthesize in a thread
        def synthesize_sync():
            tts_stream.feed(text)
            tts_stream.play(
                muted=Config.TTS_MUTED,
                on_audio_chunk=on_audio_chunk
            )
        
        # Run synthesis in a separate thread
        synthesis_thread = threading.Thread(target=synthesize_sync, daemon=True)
        synthesis_thread.start()
        synthesis_thread.join()
        
        # Process and send all audio chunks as base64 PCM through message router
        if self.websocket_send_callback:
            valid_chunks = 0
            for chunk in audio_chunks:
                base64_chunk = self.process_audio_chunk(chunk)
                if base64_chunk and len(base64_chunk) > 0:  # Only send non-empty chunks
                    # Validate base64 encoding before sending
                    try:
                        # Test decode to ensure it's valid base64
                        base64.b64decode(base64_chunk)
                        valid_chunks += 1
                        
                        # Route through message router (single source of truth)
                        await self.websocket_send_callback({
                            "type": "tts_chunk",
                            "content": base64_chunk
                        })
                    except Exception as e:
                        logger.error(f"❌ [TTS] Invalid base64 chunk detected, skipping: {e}")
                        
            # Send final upsampled chunk (reference-style flush)
            final_chunk = self.upsampler.flush_base64_chunk()
            if final_chunk and len(final_chunk) > 0:
                try:
                    # Test decode to ensure it's valid base64
                    base64.b64decode(final_chunk)
                    valid_chunks += 1
                    
                    # Route through message router (single source of truth)
                    await self.websocket_send_callback({
                        "type": "tts_chunk", 
                        "content": final_chunk
                    })
                    logger.info("🔊 [TTS] Sent final upsampled chunk through message router")
                except Exception as e:
                    logger.error(f"❌ [TTS] Invalid final base64 chunk detected, skipping: {e}")
                    
            logger.info(f"🔊 [TTS] Reference-style synthesis completed, sent {valid_chunks} valid PCM chunks")
        else:
            # No WebSocket callback available - log warning
            logger.warning(f"🔊 [TTS] No WebSocket callback available - {len(audio_chunks)} audio chunks not sent")

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
        return status
    
    def is_ready(self):
        """Check if TTS engine is ready"""
        return self.status["status"] == "ready" and self.kokoro_engine is not None 