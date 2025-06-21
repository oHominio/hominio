"""
Hominio Voice - Main Application
A modular voice interface with STT, LLM, and TTS integration
"""
import json
import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import our modular components
from core.config import setup_environment, Config
from core.logging_setup import setup_logging, get_logger
from engines.tts_engine import tts_manager
from engines.llm_client import llm_manager
from services.conversation_manager import conversation_manager
from utils.signal_handlers import signal_handler
from utils.audio_utils import decode_and_resample

# Setup environment and logging
setup_environment()
setup_logging(logging.INFO)
logger = get_logger(__name__)

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Hominio Voice application...")
    
    # Register shutdown callbacks
    signal_handler.add_shutdown_callback(lambda: tts_manager.shutdown())
    signal_handler.add_shutdown_callback(lambda: llm_manager.shutdown())
    signal_handler.add_shutdown_callback(lambda: conversation_manager.shutdown())
    
    # Initialize engines
    logger.info("⚙️ Initializing engines...")
    
    # Initialize TTS engine
    if not await tts_manager.initialize():
        logger.error("❌ Failed to initialize TTS engine")
    
    # Initialize LLM client
    if not await llm_manager.initialize():
        logger.error("❌ Failed to initialize LLM client")
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🔌 Shutting down application...")
    conversation_manager.shutdown()
    tts_manager.shutdown()
    llm_manager.shutdown()
    logger.info("👋 Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Hominio Voice",
    description="Voice interface with STT, LLM, and TTS integration",
    version="1.0.0",
    lifespan=lifespan
)

# Serve static files
app.mount("/js", StaticFiles(directory="js"), name="js")

# Routes
@app.get("/")
async def serve_index():
    """Serve the main HTML page"""
    return FileResponse("index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Hominio Voice API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/model-status")
async def get_model_status():
    """Get status of all engines"""
    return {
        "tts": tts_manager.get_status(),
        "llm": {
            "status": "ready" if llm_manager.is_ready() else "not_ready",
            "model": Config.LLM_MODEL
        },
        "conversation": conversation_manager.get_state(),
        "timestamp": datetime.now().isoformat()
    }

# WebSocket endpoints
@app.websocket("/ws/model-status")
async def model_status_websocket(websocket: WebSocket):
    """WebSocket for real-time model status updates"""
    await websocket.accept()
    logger.info("📡 Model status WebSocket connected")
    
    try:
        while True:
            # Send status every 5 seconds
            status = {
                "tts": tts_manager.get_status(),
                "llm": {
                    "status": "ready" if llm_manager.is_ready() else "not_ready",
                    "model": Config.LLM_MODEL
                },
                "conversation": conversation_manager.get_state(),
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(status))
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("📡 Model status WebSocket disconnected")
    except Exception as e:
        logger.error(f"Model status WebSocket error: {e}")

@app.websocket("/ws/tts")
async def tts_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for TTS synthesis"""
    await websocket.accept()
    logger.info("🔊 TTS WebSocket connected")
    
    # Set this as the active TTS connection
    conversation_manager.set_active_tts_websocket(websocket)
    
    try:
        while True:
            # Wait for text messages to synthesize
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "synthesize":
                text = data.get("text", "")
                if text:
                    logger.info(f"🔊 Received TTS request: '{text[:50]}...'")
                    
                    if not tts_manager.is_ready():
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "TTS engine not ready"
                        }))
                        continue
                    
                    try:
                        # Send WAV header
                        wav_header = tts_manager.get_wave_header()
                        await websocket.send_bytes(wav_header)
                        
                        # Synthesize and send audio chunks
                        audio_chunks = await tts_manager.synthesize_text(text)
                        
                        for chunk in audio_chunks:
                            await websocket.send_bytes(chunk)
                        
                        # Send completion signal
                        await websocket.send_text("END")
                        logger.info("✅ TTS synthesis completed")
                        
                    except Exception as e:
                        logger.error(f"TTS synthesis error: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": str(e)
                        }))
            
    except WebSocketDisconnect:
        logger.info("🔊 TTS WebSocket disconnected")
    except Exception as e:
        logger.error(f"TTS WebSocket error: {e}")
    finally:
        # Clear the active TTS connection
        if conversation_manager.active_tts_ws == websocket:
            conversation_manager.set_active_tts_websocket(None)

@app.websocket("/ws/stt")
async def stt_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for STT processing"""
    await websocket.accept()
    logger.info("🎤 STT WebSocket connected")
    
    # Set this as the active TTS connection for responses
    conversation_manager.set_active_tts_websocket(websocket)
    
    try:
        while True:
            # Handle different message types
            try:
                message = await websocket.receive()
                
                if message["type"] == "websocket.receive":
                    if "text" in message:
                        # Handle text messages (control commands)
                        data = json.loads(message["text"])
                        
                        if data.get("type") == "start":
                            logger.info("🎤 STT recording started")
                            conversation_manager.start_listening()
                            
                            # Interrupt any current TTS
                            conversation_manager.interrupt_if_speaking()
                            
                        elif data.get("type") == "stop":
                            logger.info("🎤 STT recording stopped")
                            conversation_manager.stop_listening()
                    
                    elif "bytes" in message:
                        # Handle audio data
                        if conversation_manager.is_listening:
                            audio_data = message["bytes"]
                            
                            # For now, we'll simulate STT processing
                            # In a full implementation, this would feed to RealtimeSTT
                            logger.debug(f"📥 Received audio chunk: {len(audio_data)} bytes")
                            
                            # TODO: Implement actual STT processing
                            # This would involve:
                            # 1. Decoding and resampling audio
                            # 2. Feeding to RealtimeSTT engine
                            # 3. Processing real-time and final transcriptions
                            # 4. Calling conversation_manager.process_user_input() on final transcription
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON message"
                }))
            
    except WebSocketDisconnect:
        logger.info("🎤 STT WebSocket disconnected")
    except Exception as e:
        logger.error(f"STT WebSocket error: {e}")
    finally:
        # Clear the active TTS connection
        if conversation_manager.active_tts_ws == websocket:
            conversation_manager.set_active_tts_websocket(None)

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Additional imports for async
    import asyncio
    
    logger.info("🎯 Starting Hominio Voice server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    ) 