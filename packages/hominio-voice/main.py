from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from RealtimeTTS import TextToAudioStream, KokoroEngine
import logging
import asyncio
import os
import time
import wave
import io
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global status tracking
model_status = {
    "status": "starting",  # starting, loading, ready, error
    "progress": 0,
    "message": "Initializing Kokoro TTS engine...",
    "start_time": datetime.now().isoformat(),
    "last_updated": datetime.now().isoformat(),
    "error": None
}

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
    global model_status, engine, stream
    
    try:
        model_status.update({
            "status": "loading",
            "progress": 20,
            "message": "Loading Kokoro TTS model...",
            "last_updated": datetime.now().isoformat()
        })
        
        # Initialize KokoroEngine with American English voice
        engine = KokoroEngine(voice="af_heart")  # American female voice
        
        model_status.update({
            "status": "loading",
            "progress": 60,
            "message": "Setting up audio stream...",
            "last_updated": datetime.now().isoformat()
        })
        
        # Create TextToAudioStream
        stream = TextToAudioStream(engine, muted=True)
        
        model_status.update({
            "status": "loading",
            "progress": 80,
            "message": "Prewarming engine...",
            "last_updated": datetime.now().isoformat()
        })
        
        # Prewarm the engine with a short text
        stream.feed("Warm up").play(muted=True)
        
        model_status.update({
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
        model_status.update({
            "status": "error",
            "progress": 0,
            "message": f"Failed to initialize Kokoro engine: {str(e)}",
            "last_updated": datetime.now().isoformat(),
            "error": str(e)
        })

# Initialize engine and stream as None
engine = None
stream = None

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Start background initialization task"""
    asyncio.create_task(initialize_kokoro_engine())

@app.get("/")
async def serve_index():
    """Serve the main web interface"""
    return FileResponse("index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {"message": "Hominio Voice API with KokoroEngine", "engine": "kokoro", "language": "English"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "kokoro"}

@app.get("/model-status")
async def get_model_status():
    """Get real-time model loading status"""
    return model_status

@app.websocket("/ws/model-status")
async def model_status_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time model status updates"""
    await websocket.accept()
    logger.info("Model status WebSocket connection established")
    
    try:
        last_sent_status = None
        while True:
            # Only send updates when status changes
            if model_status != last_sent_status:
                await websocket.send_json(model_status)
                last_sent_status = model_status.copy()
            
            # If model is ready or errored, we can slow down updates
            if model_status["status"] in ["ready", "error"]:
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
            if model_status["status"] != "ready" or not engine or not stream:
                await websocket.send_json({
                    "type": "status",
                    "message": f"Engine is {model_status['status']}: {model_status['message']}",
                    "progress": model_status["progress"]
                })
                await asyncio.sleep(5)
                continue
            
            # Receive text from client
            data = await websocket.receive_text()
            logger.info(f"Received text: {data}")
            
            # Synthesize audio using KokoroEngine for real-time streaming
            try:
                # Create a new stream for this synthesis to avoid conflicts
                synthesis_stream = TextToAudioStream(engine, muted=True)
                
                # Store chunks to send after synthesis completes
                audio_chunks = []
                header_sent = False
                
                def collect_audio_chunk(chunk):
                    nonlocal header_sent
                    # Collect chunks to send later (thread-safe)
                    if not header_sent:
                        # Add WAV header for first chunk
                        wav_header = create_wave_header_for_engine(engine)
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