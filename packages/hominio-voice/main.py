from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from RealtimeTTS import TextToAudioStream, KokoroEngine
from RealtimeSTT import AudioToTextRecorder
import logging
import asyncio
import os
import signal
import sys
import time
import wave
import io
import tempfile
import threading
from datetime import datetime
from typing import Dict, Any
import json
import multiprocessing

# Additional imports for audio processing (following server examples)
try:
    import numpy as np
    from scipy.signal import resample
    HAS_AUDIO_PROCESSING = True
except ImportError:
    HAS_AUDIO_PROCESSING = False
    logging.warning("NumPy/SciPy not available - audio resampling disabled")

# Suppress ALSA warnings in headless environment
os.environ['ALSA_PCM_CARD'] = '-1'
os.environ['ALSA_PCM_DEVICE'] = '-1'
os.environ['ALSA_CARD'] = 'none'

# Prevent multiprocessing resource leaks
os.environ['PYTHONUNBUFFERED'] = '1'

# Prevent multiprocessing issues that cause semaphore leaks and SIGABRT crashes
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

# Disable tokenizers parallelism to prevent resource conflicts
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Additional environment variables for stability
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    # Cleanup global variables
    global kokoro_engine, stream, stt_engine, stt_message_queue
    try:
        if stt_engine:
            stt_engine.shutdown()
    except:
        pass
    try:
        if kokoro_engine:
            kokoro_engine = None
    except:
        pass
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
try:
    signal.signal(signal.SIGABRT, signal_handler)
except:
    pass  # SIGABRT may not be available on all systems

# Initialize engines as None
kokoro_engine = None
stt_engine = None
stt_message_queue = None

# Initialize status dictionaries
kokoro_status = {
    "status": "initializing",
    "progress": 0,
    "message": "Starting TTS engine...",
    "last_updated": datetime.now().isoformat()
}

stt_status = "initializing"
stt_ready_event = asyncio.Event()

def create_wave_header_for_engine(engine):
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

async def initialize_kokoro_engine():
    """Initialize KokoroEngine in background"""
    global kokoro_status, kokoro_engine, stream
    
    try:
        kokoro_status.update({
            "status": "loading",
            "progress": 20,
            "message": "Loading Kokoro TTS model...",
            "last_updated": datetime.now().isoformat()
        })
        
        # Initialize KokoroEngine with American English voice
        kokoro_engine = KokoroEngine(voice="af_heart")  # American female voice
        
        kokoro_status.update({
            "status": "loading",
            "progress": 60,
            "message": "Setting up audio stream...",
            "last_updated": datetime.now().isoformat()
        })
        
        # Create TextToAudioStream
        stream = TextToAudioStream(kokoro_engine, muted=True)
        
        kokoro_status.update({
            "status": "loading",
            "progress": 80,
            "message": "Prewarming engine...",
            "last_updated": datetime.now().isoformat()
        })
        
        # Prewarm the engine with a short text
        stream.feed("Warm up").play(muted=True)
        
        kokoro_status.update({
            "status": "ready",
            "progress": 100,
            "message": "Kokoro TTS engine ready for synthesis",
            "last_updated": datetime.now().isoformat(),
            "model_info": {
                "engine": "KokoroEngine",
                "voice": "af_heart",
                "language": "English (American)"
            }
        })
        
        logger.info("✅ KokoroEngine initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize KokoroEngine: {e}")
        kokoro_status.update({
            "status": "error",
            "progress": 0,
            "message": f"Failed to initialize Kokoro engine: {str(e)}",
            "last_updated": datetime.now().isoformat(),
            "error": str(e)
        })

async def initialize_stt_engine():
    """Initialize the STT engine using RealtimeSTT"""
    global stt_engine, stt_status, stt_ready_event
    
    try:
        print("🎤 Initializing STT engine...")
        
        # Import required modules
        import multiprocessing
        multiprocessing.set_start_method('spawn', force=True)
        
        # Set environment variable to avoid tokenizer warnings
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        
        def create_recorder():
            from RealtimeSTT import AudioToTextRecorder
            import asyncio
            
            # Get the current event loop for callbacks
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            
            def preprocess_text(text):
                """Clean up transcribed text"""
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
                return text
            
            def on_realtime_transcription(text):
                """Handle real-time transcription updates"""
                if loop and not loop.is_closed():
                    text = preprocess_text(text)
                    message = {
                        'type': 'realtime',
                        'text': text
                    }
                    # Put message in queue for WebSocket broadcast
                    try:
                        asyncio.run_coroutine_threadsafe(
                            stt_message_queue.put(json.dumps(message)), 
                            loop
                        )
                    except Exception as e:
                        print(f"❌ Error sending realtime transcription: {e}")
            
            # STT configuration matching RealtimeSTT server examples
            stt_config = {
                'model': 'tiny',  # Fastest model for real-time processing
                'language': 'en',
                'use_microphone': False,  # We feed audio manually
                'spinner': False,
                'enable_realtime_transcription': True,
                'realtime_model_type': 'tiny',
                'realtime_processing_pause': 0.02,
                'on_realtime_transcription_update': on_realtime_transcription,
                'silero_sensitivity': 0.05,
                'webrtc_sensitivity': 3,
                'post_speech_silence_duration': 0.7,
                'min_length_of_recording': 1.1,
                'min_gap_between_recordings': 0,
                'silero_deactivity_detection': True,
                'early_transcription_on_silence': 0.2,
                'beam_size': 1,  # Minimal beam size for speed
                'beam_size_realtime': 1,
                'no_log_file': True,
                'device': 'cpu',  # Use CPU to avoid CUDA issues
                'compute_type': 'int8',  # Optimize for CPU
                'level': logging.WARNING,
                'initial_prompt': "Add periods only for complete sentences. Use ellipsis (...) for unfinished thoughts."
            }
            
            return AudioToTextRecorder(**stt_config)
        
        # Create recorder
        stt_engine = create_recorder()
        
        # Create message queue for STT WebSocket communication
        global stt_message_queue
        stt_message_queue = asyncio.Queue()
        
        # Start transcription thread (THIS IS THE MISSING PIECE!)
        def transcription_worker():
            """Worker thread that continuously processes transcriptions"""
            print("🔄 Starting STT transcription worker thread...")
            
            def process_full_sentence(full_sentence):
                """Process complete transcribed sentences"""
                try:
                    # Clean up the text
                    full_sentence = full_sentence.lstrip()
                    if full_sentence.startswith("..."):
                        full_sentence = full_sentence[3:]
                    if full_sentence.endswith("...'."):
                        full_sentence = full_sentence[:-1]
                    if full_sentence.endswith("...'"):
                        full_sentence = full_sentence[:-1]
                    full_sentence = full_sentence.lstrip()
                    if full_sentence:
                        full_sentence = full_sentence[0].upper() + full_sentence[1:]
                    
                    # Create message for WebSocket broadcast
                    message = {
                        'type': 'fullSentence',
                        'text': full_sentence
                    }
                    
                    # Send to WebSocket clients
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(stt_message_queue.put(json.dumps(message)))
                        loop.close()
                    except Exception as e:
                        print(f"❌ Error sending full sentence: {e}")
                    
                    print(f"✅ STT Full sentence: {full_sentence}")
                    
                except Exception as e:
                    print(f"❌ Error processing full sentence: {e}")
            
            # Main transcription loop - this is what was missing!
            while True:
                try:
                    # This call blocks until audio is processed and returns transcribed text
                    stt_engine.text(process_full_sentence)
                except Exception as e:
                    print(f"❌ STT transcription error: {e}")
                    time.sleep(0.1)  # Brief pause before retrying
        
        # Start the transcription worker thread
        import threading
        transcription_thread = threading.Thread(target=transcription_worker, daemon=True)
        transcription_thread.start()
        
        stt_status = "ready"
        stt_ready_event.set()
        print("✅ STT engine initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize STT engine: {e}")
        stt_status = f"error: {str(e)}"
        stt_ready_event.set()
        raise

# Initialize engines as None
stream = None

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Hominio Voice application...")
    
    # Initialize engines sequentially to avoid resource conflicts
    try:
        logger.info("Initializing TTS engine...")
        await initialize_kokoro_engine()
        logger.info("TTS engine initialization completed")
    except Exception as e:
        logger.error(f"TTS initialization failed: {e}")
        # Continue - TTS will show error status
    
    try:
        logger.info("Initializing STT engine...")
        await initialize_stt_engine()
        logger.info("STT engine initialization completed")
    except Exception as e:
        logger.error(f"STT initialization failed: {e}")
        # Continue - STT will show error status
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Hominio Voice application...")
    
    # Cleanup resources
    global kokoro_engine, stream, stt_engine, stt_message_queue
    try:
        if stt_engine:
            logger.info("Cleaning up STT recorder...")
            stt_engine.shutdown()
            stt_engine = None
    except Exception as e:
        logger.error(f"Error cleaning up STT: {e}")
    
    try:
        if kokoro_engine:
            logger.info("Cleaning up TTS engine...")
            # KokoroEngine cleanup if needed
            kokoro_engine = None
    except Exception as e:
        logger.error(f"Error cleaning up TTS: {e}")
    
    logger.info("Application shutdown completed")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/js", StaticFiles(directory="js"), name="js")

@app.get("/")
async def serve_index():
    """Serve the main web interface"""
    return FileResponse("index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Hominio Voice API with KokoroEngine TTS and RealtimeSTT", 
        "tts_engine": "kokoro", 
        "stt_engine": "whisper-tiny",
        "language": "English"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "tts_engine": "kokoro", "stt_engine": "whisper-tiny"}

@app.get("/model-status")
async def get_model_status():
    """Get real-time model loading status"""
    return {
        "tts": kokoro_status,
        "stt": stt_status
    }

@app.websocket("/ws/stt")
async def stt_websocket_endpoint(websocket: WebSocket):
    """STT WebSocket endpoint - receives audio and sends transcriptions"""
    await websocket.accept()
    logger.info("STT WebSocket client connected")
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "status",
            "message": "STT engine ready for audio processing"
        }))
        
        # Create a task to broadcast messages from the queue
        async def message_broadcaster():
            """Broadcast STT messages to the WebSocket client"""
            try:
                while True:
                    # Get message from queue
                    message = await stt_message_queue.get()
                    await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error in STT message broadcaster: {e}")
        
        # Start the broadcaster task
        broadcaster_task = asyncio.create_task(message_broadcaster())
        
        # Audio processing functions
        def decode_and_resample(audio_data, original_sample_rate, target_sample_rate=16000):
            """Resample audio to target sample rate if needed"""
            if original_sample_rate == target_sample_rate:
                return audio_data
            
            try:
                import numpy as np
                from scipy.signal import resample
                
                # Decode 16-bit PCM data to numpy array
                audio_np = np.frombuffer(audio_data, dtype=np.int16)
                
                # Calculate the number of samples after resampling
                num_original_samples = len(audio_np)
                num_target_samples = int(num_original_samples * target_sample_rate / original_sample_rate)
                
                # Resample the audio
                resampled_audio = resample(audio_np, num_target_samples)
                
                return resampled_audio.astype(np.int16).tobytes()
            except Exception as e:
                logger.error(f"Error resampling audio: {e}")
                return audio_data
        
        def preprocess_text(text):
            """Clean up transcribed text following RealtimeSTT server example"""
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
            return text
        
        # Main message processing loop
        while True:
            try:
                # Receive message from client
                message = await websocket.receive()
                
                if message["type"] == "websocket.receive":
                    if "bytes" in message:
                        # Binary message - audio data
                        audio_data = message["bytes"]
                        
                        try:
                            # Parse the message format: [4 bytes length][metadata JSON][audio data]
                            metadata_length = int.from_bytes(audio_data[:4], byteorder='little')
                            metadata_json = audio_data[4:4+metadata_length].decode('utf-8')
                            metadata = json.loads(metadata_json)
                            sample_rate = metadata.get('sampleRate', 16000)
                            
                            # Extract audio chunk
                            chunk = audio_data[4+metadata_length:]
                            
                            # Resample if necessary
                            if sample_rate != 16000:
                                chunk = decode_and_resample(chunk, sample_rate, 16000)
                            
                            # Feed audio to STT engine
                            if stt_engine:
                                stt_engine.feed_audio(chunk)
                                logger.debug(f"Fed audio chunk: {len(chunk)} bytes")
                            else:
                                logger.warning("STT engine not available")
                                
                        except Exception as e:
                            logger.error(f"Error processing audio data: {e}")
                            continue
                    
                    elif "text" in message:
                        # Text message - control commands
                        try:
                            data = json.loads(message["text"])
                            command = data.get("command")
                            
                            if command == "start":
                                logger.info("STT recording started")
                                await websocket.send_text(json.dumps({
                                    "type": "status",
                                    "message": "Recording started"
                                }))
                            elif command == "stop":
                                logger.info("STT recording stopped")
                                await websocket.send_text(json.dumps({
                                    "type": "status", 
                                    "message": "Recording stopped"
                                }))
                            else:
                                logger.warning(f"Unknown STT command: {command}")
                                
                        except json.JSONDecodeError:
                            logger.warning("Invalid JSON in STT text message")
                            continue
                
            except Exception as e:
                logger.error(f"Error in STT WebSocket message processing: {e}")
                break
                
    except Exception as e:
        logger.error(f"STT WebSocket error: {e}")
    finally:
        # Clean up
        if 'broadcaster_task' in locals():
            broadcaster_task.cancel()
        logger.info("STT WebSocket client disconnected")

@app.websocket("/ws/model-status")
async def model_status_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time model status updates"""
    await websocket.accept()
    logger.info("Model status WebSocket connection established")
    
    try:
        last_sent_status = None
        while True:
            # Combine TTS and STT status
            combined_status = {
                "tts": kokoro_status,
                "stt": stt_status
            }
            
            # Only send updates when status changes
            if combined_status != last_sent_status:
                await websocket.send_json(combined_status)
                last_sent_status = combined_status.copy()
            
            # If both models are ready or errored, we can slow down updates
            if (kokoro_status["status"] in ["ready", "error"] and 
                stt_status in ["ready", "error"]):
                await asyncio.sleep(30)  # Check every 30 seconds
            else:
                await asyncio.sleep(2)   # Check every 2 seconds during loading
                
    except Exception as e:
        logger.error(f"Model status WebSocket error: {e}")
    finally:
        logger.info("Model status WebSocket connection closed")

@app.websocket("/ws/tts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Check if model is ready before processing
            if kokoro_status["status"] != "ready" or not kokoro_engine or not stream:
                await websocket.send_json({
                    "type": "status",
                    "message": f"Engine is {kokoro_status['status']}: {kokoro_status['message']}",
                    "progress": kokoro_status["progress"]
                })
                await asyncio.sleep(5)
                continue
            
            # Receive text from client
            data = await websocket.receive_text()
            logger.info(f"Received text: {data}")
            
            # Synthesize audio using KokoroEngine for real-time streaming
            try:
                # Create a new stream for this synthesis to avoid conflicts
                synthesis_stream = TextToAudioStream(kokoro_engine, muted=True)
                
                # Store chunks to send after synthesis completes
                audio_chunks = []
                header_sent = False
                
                def collect_audio_chunk(chunk):
                    nonlocal header_sent
                    # Collect chunks to send later (thread-safe)
                    if not header_sent:
                        # Add WAV header for first chunk
                        wav_header = create_wave_header_for_engine(kokoro_engine)
                        audio_chunks.append(("header", wav_header))
                        header_sent = True
                    audio_chunks.append(("chunk", chunk))
                
                # Start synthesis and collect chunks
                logger.info("🎵 Starting synthesis...")
                synthesis_stream.feed(data).play(
                    on_audio_chunk=collect_audio_chunk,
                    muted=True
                )
                
                # Send all collected audio chunks
                logger.info(f"📊 Sending {len(audio_chunks)} audio chunks...")
                for chunk_type, chunk_data in audio_chunks:
                    await websocket.send_bytes(chunk_data)
                    if chunk_type == "header":
                        logger.info("📊 Sent WAV header")
                    else:
                        logger.info(f"📊 Sent audio chunk: {len(chunk_data)} bytes")
                
                # Send end marker
                await websocket.send_text("END")
                logger.info("✅ Synthesis complete")
                
            except Exception as e:
                logger.error(f"Synthesis error: {e}")
                await websocket.send_text(f"ERROR: {str(e)}")
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 