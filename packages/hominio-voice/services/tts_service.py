"""
Text-to-Speech Service
Handles Kokoro TTS engine initialization and audio generation
"""
import logging
import io
import wave
import threading
from datetime import datetime
from RealtimeTTS import TextToAudioStream, KokoroEngine
from core.config import Config

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.kokoro_engine = None
        self.status = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting TTS engine...",
            "last_updated": datetime.now().isoformat()
        }
    
    def create_wave_header_for_engine(self, engine):
        """Create WAV header for the given engine"""
        _, channels, sample_rate = engine.get_stream_info()
        
        num_channels = channels
        sample_width = 2  # 16-bit audio
        frame_rate = sample_rate

        wav_header = io.BytesIO()
        with wave.open(wav_header, "wb") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(frame_rate)

        wav_header.seek(0)
        wave_header_bytes = wav_header.read()
        wav_header.close()

        return wave_header_bytes

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
                    "mode": "headless"
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

    async def synthesize_text(self, text: str, websocket):
        """Synthesize text to audio and send via WebSocket"""
        if not self.kokoro_engine:
            raise RuntimeError("TTS engine not initialized")
            
        # Create a new stream for this synthesis (headless mode)
        tts_stream = TextToAudioStream(self.kokoro_engine, muted=Config.TTS_MUTED)

        # Store audio chunks to send them after synthesis
        audio_chunks = []
        
        def on_audio_chunk(chunk):
            """Collect audio chunks during synthesis"""
            audio_chunks.append(chunk)

        # Send WAV header first for proper audio playback on client
        if websocket:
            wav_header = self.create_wave_header_for_engine(self.kokoro_engine)
            await websocket.send_bytes(wav_header)

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
        
        # Send all collected audio chunks
        if websocket:
            for chunk in audio_chunks:
                await websocket.send_bytes(chunk)
        
        # Send end marker to signal completion
        if websocket:
            await websocket.send_text("END")
            logger.info("🔊 TTS synthesis completed, audio sent to client")

    def get_status(self):
        """Get current TTS status"""
        return self.status
    
    def is_ready(self):
        """Check if TTS engine is ready"""
        return self.status["status"] == "ready" and self.kokoro_engine is not None 