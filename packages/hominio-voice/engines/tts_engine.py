"""
TTS Engine Management
Handles KokoroEngine initialization and management
"""
import logging
import asyncio
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from RealtimeTTS import TextToAudioStream, KokoroEngine

from core.config import Config
from utils.audio_utils import create_wave_header_for_engine

logger = logging.getLogger(__name__)


class TTSEngineManager:
    """Manages TTS engine initialization and synthesis operations"""
    
    def __init__(self):
        self.engine: Optional[KokoroEngine] = None
        self.status = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting TTS engine...",
            "last_updated": datetime.now().isoformat()
        }
        self._is_ready = False
    
    async def initialize(self) -> bool:
        """Initialize the TTS engine"""
        try:
            logger.info("🔊 Initializing TTS engine...")
            
            self.status.update({
                "status": "loading",
                "progress": 20,
                "message": "Loading Kokoro TTS model...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Initialize KokoroEngine with configured voice
            self.engine = KokoroEngine(voice=Config.TTS_VOICE)
            
            self.status.update({
                "status": "loading",
                "progress": 80,
                "message": "Testing engine in headless mode...",
                "last_updated": datetime.now().isoformat()
            })
            
            # Test the engine by generating a small sample
            if await self._test_engine():
                self.status.update({
                    "status": "ready",
                    "progress": 100,
                    "message": "Kokoro TTS engine ready for headless synthesis",
                    "last_updated": datetime.now().isoformat(),
                    "model_info": {
                        "engine": "KokoroEngine",
                        "voice": Config.TTS_VOICE,
                        "language": "English (American)",
                        "mode": "headless"
                    }
                })
                
                self._is_ready = True
                logger.info("✅ TTS engine initialized successfully")
                return True
            else:
                raise Exception("Engine test failed")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize TTS engine: {e}")
            self.status.update({
                "status": "error",
                "progress": 0,
                "message": f"Failed to initialize TTS engine: {str(e)}",
                "last_updated": datetime.now().isoformat(),
                "error": str(e)
            })
            return False
    
    async def _test_engine(self) -> bool:
        """Test the TTS engine with a small sample"""
        try:
            test_stream = TextToAudioStream(self.engine, muted=True)
            test_audio_chunks = []
            
            def collect_chunk(chunk):
                test_audio_chunks.append(chunk)
            
            # Run test synthesis in a thread
            def test_synthesis():
                test_stream.feed("Test")
                test_stream.play(muted=True, on_audio_chunk=collect_chunk)
            
            # Run in thread to avoid blocking
            thread = threading.Thread(target=test_synthesis, daemon=True)
            thread.start()
            thread.join(timeout=10)  # 10 second timeout
            
            if test_audio_chunks:
                logger.info(f"✅ TTS engine test successful - generated {len(test_audio_chunks)} audio chunks")
                return True
            else:
                logger.error("❌ TTS engine test failed - no audio generated")
                return False
                
        except Exception as e:
            logger.error(f"❌ TTS engine test error: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if the engine is ready"""
        return self._is_ready and self.engine is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return self.status.copy()
    
    def get_wave_header(self) -> bytes:
        """Get WAV header for the engine"""
        if not self.is_ready():
            raise RuntimeError("TTS engine not ready")
        return create_wave_header_for_engine(self.engine)
    
    async def synthesize_text(self, text: str, on_audio_chunk: Optional[Callable] = None) -> List[bytes]:
        """
        Synthesize text to audio chunks
        
        Args:
            text: Text to synthesize
            on_audio_chunk: Optional callback for each audio chunk
            
        Returns:
            List of audio chunks
        """
        if not self.is_ready():
            raise RuntimeError("TTS engine not ready")
        
        logger.info(f"🔊 Synthesizing text: '{text[:50]}...'")
        
        # Create audio stream
        tts_stream = TextToAudioStream(self.engine, muted=True)
        audio_chunks = []
        
        def collect_and_callback(chunk):
            audio_chunks.append(chunk)
            if on_audio_chunk:
                on_audio_chunk(chunk)
        
        # Run synthesis in thread
        def synthesize():
            tts_stream.feed(text)
            tts_stream.play(muted=True, on_audio_chunk=collect_and_callback)
        
        # Execute synthesis
        thread = threading.Thread(target=synthesize, daemon=True)
        thread.start()
        thread.join()
        
        logger.info(f"✅ Synthesis completed: {len(audio_chunks)} chunks generated")
        return audio_chunks
    
    def shutdown(self):
        """Shutdown the TTS engine"""
        try:
            if self.engine:
                # KokoroEngine doesn't have explicit shutdown, just clear reference
                self.engine = None
                logger.info("🔊 TTS engine shutdown")
        except Exception as e:
            logger.error(f"Error shutting down TTS engine: {e}")
        finally:
            self._is_ready = False


# Global TTS engine manager instance
tts_manager = TTSEngineManager() 