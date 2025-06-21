"""
Hominio Voice - Main Application
A modular voice interface with STT, LLM, and TTS integration
"""
import json
import logging
import asyncio
import signal
import sys
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
from engines.stt_engine import stt_manager
from services.conversation_manager import conversation_manager
from utils.signal_handlers import signal_handler
from utils.audio_utils import decode_and_resample

# CRITICAL: Setup environment FIRST before any other imports
try:
    setup_environment()
    setup_logging(logging.INFO)
    logger = get_logger(__name__)
    logger.info("🚀 Environment setup completed successfully")
except Exception as e:
    print(f"❌ CRITICAL: Environment setup failed: {e}")
    sys.exit(1)

# Graceful shutdown handler
def handle_shutdown_signal(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"📡 Received shutdown signal {signum}")
    try:
        # Cleanup managers
        conversation_manager.shutdown()
        stt_manager.shutdown()
        tts_manager.shutdown()
        llm_manager.shutdown()
        logger.info("✅ Graceful shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    finally:
        sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Hominio Voice application...")
    
    try:
        # Register shutdown callbacks
        signal_handler.add_shutdown_callback(lambda: tts_manager.shutdown())
        signal_handler.add_shutdown_callback(lambda: llm_manager.shutdown())
        signal_handler.add_shutdown_callback(lambda: stt_manager.shutdown())
        signal_handler.add_shutdown_callback(lambda: conversation_manager.shutdown())
        
        # Set up conversation manager callbacks for visual state management
        def on_state_change(new_state, message=None):
            """Handle conversation state changes for WebSocket clients and STT management"""
            logger.info(f"🎭 Conversation state changed to: {new_state}")
            
            # Automatically manage STT engine based on conversation state
            if new_state == "listening":
                # Automatically start STT when conversation enters listening mode
                if not stt_manager.is_listening:
                    stt_manager.start_listening()
                    logger.info("🔄 Auto-started STT engine for listening mode")
            elif new_state == "speaking":
                # Keep STT running during speaking for potential interruptions
                pass
            # Don't automatically stop STT to allow for continuous conversation
        
        conversation_manager.set_state_change_callback(on_state_change)
        
        # Initialize engines with proper error handling
        logger.info("⚙️ Initializing engines...")
        
        # Initialize TTS engine
        logger.info("🔊 Initializing TTS engine...")
        if not await tts_manager.initialize():
            logger.error("❌ Failed to initialize TTS engine")
            raise RuntimeError("TTS engine initialization failed")
        
        # Initialize LLM client
        logger.info("🤖 Initializing LLM client...")
        if not await llm_manager.initialize():
            logger.error("❌ Failed to initialize LLM client")
            raise RuntimeError("LLM client initialization failed")
        
        # Initialize STT engine with VAD callbacks
        logger.info("🎤 Initializing STT engine...")
        stt_callbacks = {
            'on_vad_detect_start': conversation_manager.on_vad_detected,
            'on_vad_detect_stop': conversation_manager.on_vad_stopped,
            'on_final_transcription': conversation_manager.process_user_input,
        }
        stt_manager.set_callbacks(stt_callbacks)
        
        if not await stt_manager.initialize():
            logger.error("❌ Failed to initialize STT engine")
            raise RuntimeError("STT engine initialization failed")
        
        logger.info("✅ Application startup complete")
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Application startup failed: {e}")
        # Attempt cleanup
        try:
            conversation_manager.shutdown()
            stt_manager.shutdown()
            tts_manager.shutdown()
            llm_manager.shutdown()
        except:
            pass
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("🔌 Shutting down application...")
    try:
        conversation_manager.shutdown()
        stt_manager.shutdown()
        tts_manager.shutdown()
        llm_manager.shutdown()
        logger.info("👋 Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

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
    try:
        # Check engine status
        tts_ready = tts_manager.is_ready()
        stt_ready = stt_manager.is_ready()
        llm_ready = llm_manager.is_ready()
        
        status = "healthy" if all([tts_ready, stt_ready, llm_ready]) else "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "engines": {
                "tts": "ready" if tts_ready else "not_ready",
                "stt": "ready" if stt_ready else "not_ready", 
                "llm": "ready" if llm_ready else "not_ready"
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/model-status")
async def get_model_status():
    """Get status of all engines"""
    try:
        return {
            "tts": tts_manager.get_status(),
            "stt": stt_manager.get_status(),
            "llm": {
                "status": "ready" if llm_manager.is_ready() else "not_ready",
                "model": Config.LLM_MODEL
            },
            "conversation": conversation_manager.get_state(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Model status error: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

# WebSocket endpoints
@app.websocket("/ws/model-status")
async def model_status_websocket(websocket: WebSocket):
    """WebSocket for real-time model status updates"""
    await websocket.accept()
    logger.info("📡 Model status WebSocket connected")
    
    try:
        while True:
            # Send status every 5 seconds
            try:
                status = {
                    "tts": tts_manager.get_status(),
                    "stt": stt_manager.get_status(),
                    "llm": {
                        "status": "ready" if llm_manager.is_ready() else "not_ready",
                        "model": Config.LLM_MODEL
                    },
                    "conversation": conversation_manager.get_state(),
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_text(json.dumps(status))
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error sending model status: {e}")
                break
            
    except WebSocketDisconnect:
        logger.info("📡 Model status WebSocket disconnected")
    except Exception as e:
        logger.error(f"Model status WebSocket error: {e}")

@app.websocket("/ws/tts-push")
async def tts_push_websocket_endpoint(websocket: WebSocket):
    """TTS Push WebSocket endpoint - for server-initiated audio streaming (LLM integration)"""
    await websocket.accept()
    logger.info("🔊 TTS Push WebSocket client connected")
    
    # Set this as the active TTS connection for automatic responses
    conversation_manager.set_active_tts_websocket(websocket)
    
    try:
        # Keep the connection alive, waiting for the server to push audio
        while True:
            # This is a keep-alive loop for server-push audio
            # The server will push audio via conversation_manager
            try:
                await websocket.receive_text()  # Just keep connection alive
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        logger.info("🔊 TTS Push WebSocket client disconnected")
    except Exception as e:
        logger.error(f"TTS Push WebSocket error: {e}")
    finally:
        # Clear the active TTS connection
        if conversation_manager.active_tts_ws == websocket:
            conversation_manager.set_active_tts_websocket(None)
        logger.info("🔊 Cleaned up TTS Push WebSocket connection")

@app.websocket("/ws/stt")
async def stt_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for STT processing with enhanced VAD"""
    await websocket.accept()
    logger.info("🎤 STT WebSocket connected")
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "status",
            "message": "STT engine ready for audio processing"
        }))
        
        # Create a task to broadcast STT messages to the WebSocket client
        async def message_broadcaster():
            """Broadcast STT messages to the WebSocket client"""
            try:
                message_queue = stt_manager.get_message_queue()
                if not message_queue:
                    logger.warning("STT message queue not available")
                    return
                
                while True:
                    # Get message from queue
                    message = await message_queue.get()
                    if isinstance(message, dict):
                        await websocket.send_text(json.dumps(message))
                    else:
                        await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error in STT message broadcaster: {e}")
        
        # Start the broadcaster task
        broadcaster_task = asyncio.create_task(message_broadcaster())
        
        # Main message processing loop
        while True:
            try:
                message = await websocket.receive()
                
                if message["type"] == "websocket.receive":
                    if "text" in message:
                        # Handle text messages (control commands)
                        data = json.loads(message["text"])
                        command = data.get("command")  # Fixed: use "command" not "type"
                        
                        if command == "start":
                            logger.info("🎤 STT conversation started")
                            conversation_manager.start_listening()
                            stt_manager.start_listening()
                            
                            # Interrupt any current TTS
                            conversation_manager.interrupt_if_speaking()
                            
                            await websocket.send_text(json.dumps({
                                "type": "status",
                                "message": "Recording started"
                            }))
                            
                        elif command == "stop":
                            logger.info("🎤 STT conversation paused (will auto-resume for continuous conversation)")
                            # Only pause conversation manager, don't stop STT engine completely
                            # This allows for continuous multi-turn conversation
                            conversation_manager.stop_listening()
                            # Note: NOT calling stt_manager.stop_listening() to keep STT active
                            
                            await websocket.send_text(json.dumps({
                                "type": "status", 
                                "message": "Recording paused (auto-resume enabled)"
                            }))
                        else:
                            logger.warning(f"Unknown STT command: {command}")
                    
                    elif "bytes" in message:
                        # Handle audio data
                        if stt_manager.is_ready() and conversation_manager.is_listening:
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
                                stt_manager.feed_audio(chunk)
                                logger.debug(f"📥 Fed audio chunk: {len(chunk)} bytes")
                                
                            except Exception as e:
                                logger.error(f"Error processing audio data: {e}")
                                continue
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON message"
                }))
            except Exception as e:
                logger.error(f"Error in STT WebSocket message processing: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("🎤 STT WebSocket disconnected")
    except Exception as e:
        logger.error(f"STT WebSocket error: {e}")
    finally:
        # Clean up
        if 'broadcaster_task' in locals():
            broadcaster_task.cancel()
        
        logger.info("🎤 STT WebSocket cleanup completed")

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    try:
        logger.info("🎯 Starting Hominio Voice server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info",
            access_log=False  # Reduce log noise
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1) 