from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, WebSocketDisconnect, Depends, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging
import asyncio
import os
import signal
import sys
import time
import tempfile
import threading
import secrets
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

# Import CUDA environment setup and Config from the new config
from core.config import setup_environment, Config

# Import service classes
from services.stt_service import STTService
from services.tts_service import TTSService
from services.llm_service import LLMService
from services.message_router import MessageRouter
from services.speech_pipeline import SpeechPipeline

# CRITICAL: Setup environment FIRST before any other imports
try:
    setup_environment()
    print("🚀 Environment setup completed successfully")
except Exception as e:
    print(f"❌ CRITICAL: Environment setup failed: {e}")
    sys.exit(1)

# Password protection configuration - REQUIRED environment variable
PROTECTED_PASSWORD = os.getenv("HOMINIO_PASSWORD")
if not PROTECTED_PASSWORD:
    print("❌ CRITICAL: HOMINIO_PASSWORD environment variable is required!")
    print("💡 Set it with: export HOMINIO_PASSWORD='your-secure-password'")
    sys.exit(1)

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify password for API access (username can be anything)"""
    is_correct_password = secrets.compare_digest(credentials.password, PROTECTED_PASSWORD)
    
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

print(f"🔐 Password protection enabled - Password loaded from environment variable")
print(f"💡 Password length: {len(PROTECTED_PASSWORD)} characters")
if len(PROTECTED_PASSWORD) < 8:
    print("⚠️  WARNING: Password is shorter than 8 characters - consider using a stronger password")
print(f"🛡️  Security: All API endpoints protected with HTTP Basic Authentication")

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

# Configure logging with detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable debug logging for our services to see pipeline activity
logging.getLogger('services.speech_pipeline').setLevel(logging.INFO)
logging.getLogger('services.message_router').setLevel(logging.INFO)
logging.getLogger('services.tts_service').setLevel(logging.INFO)
logging.getLogger('services.llm_service').setLevel(logging.INFO)
logging.getLogger('services.stt_service').setLevel(logging.INFO)

# CUDA validation is now handled by setup_environment() - no need to repeat
logger.info("✅ CUDA validation completed during environment setup")

# Initialize service instances
stt_service = STTService()
tts_service = TTSService()
llm_service = LLMService()
message_router = MessageRouter()
speech_pipeline = SpeechPipeline()  # The orchestrator

# Legacy global variables for backward compatibility
kokoro_engine = None
stt_engine = None
stt_message_queue = None
llm_client = None

# Initialize status dictionaries - now using service status
kokoro_status = {}
stt_status = "initializing"
stt_ready_event = asyncio.Event()

# Global variable to hold the active TTS WebSocket connection
active_tts_ws: WebSocket = None

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    # Cleanup global variables and services
    global stt_service, tts_service, llm_service
    try:
        if stt_service and stt_service.stt_engine:
            stt_service.stt_engine.shutdown()
    except:
        pass
    try:
        if tts_service:
            tts_service.kokoro_engine = None
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

async def initialize_kokoro_engine():
    """Initialize KokoroEngine using TTS service"""
    global kokoro_status, kokoro_engine
    
    await tts_service.initialize_kokoro_engine()
    kokoro_status = tts_service.get_status()
    kokoro_engine = tts_service.kokoro_engine  # For backward compatibility
    
async def initialize_stt_engine():
    """Initialize RealtimeSTT engine using STT service with message router"""
    global stt_engine, stt_status, stt_message_queue
    
    try:
        print("🎤 Initializing STT engine...")
        stt_status = "initializing"
        
        # Reset conversation history and processed sentences on initialization
        llm_service.clear_conversation()
        
        # Create message queue for STT WebSocket communication
        stt_message_queue = asyncio.Queue()

        # Get the current event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()

        # Initialize services with complex pipeline architecture
        await stt_service.initialize_stt_engine()
        await tts_service.initialize_kokoro_engine()
        await llm_service.initialize_llm_client()
        
        # Set up complex pipeline architecture coordination
        # 1. Speech pipeline coordinates all services (complex orchestrator with threading)
        speech_pipeline.set_services(stt_service, tts_service, llm_service)
        speech_pipeline.set_message_router(message_router)
        
        # 2. Message router handles all communication (pure communication hub)
        message_router.initialize_services(stt_service, tts_service, llm_service, speech_pipeline)
        message_router.set_websocket_queue(stt_message_queue, loop)
        
        logger.info("✅ Complex pipeline architecture initialized - Speech pipeline orchestrates with threading, Message router communicates")
        
        # Start transcription worker thread
        def transcription_worker():
            """Worker thread that continuously processes transcriptions"""
            print("🔄 Starting STT transcription worker thread...")
            
            while True:
                try:
                    # Get text from STT engine
                    text = stt_service.stt_engine.text()
                    if text and text.strip():
                        print(f"🎤 STT detected text: '{text}'")
                        # FIXED: Use STT service callback system to trigger speech pipeline
                        asyncio.run_coroutine_threadsafe(
                            stt_service.process_full_sentence(text),
                            loop
                        )
                    else:
                        # Log periodically to show the worker is alive
                        import time
                        if int(time.time()) % 30 == 0:  # Every 30 seconds
                            print("🔄 STT transcription worker is running...")
                except Exception as e:
                    print(f"❌ STT transcription error: {e}")
                    time.sleep(0.1)
        
        # Start the transcription worker thread
        transcription_thread = threading.Thread(target=transcription_worker, daemon=True)
        transcription_thread.start()
        
        stt_status = "ready"
        stt_ready_event.set()
        stt_engine = stt_service.stt_engine  # For backward compatibility
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
    # Initialize LLM client
    try:
        await llm_service.initialize_llm_client()
        global llm_client
        llm_client = llm_service.llm_client  # For backward compatibility
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        raise
    
    # Initialize STT and TTS engines
    try:
        await initialize_kokoro_engine()
        await initialize_stt_engine()
    except Exception as e:
        logger.error(f"Failed to initialize engines: {e}")
        raise
    
    logger.info("🚀 All services initialized successfully")
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down services...")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/js", StaticFiles(directory="js"), name="js")

@app.get("/")
async def serve_index(user: str = Depends(verify_credentials)):
    """Serve the main web interface - requires authentication"""
    return FileResponse("index.html")

@app.get("/api")
async def api_info(user: str = Depends(verify_credentials)):
    """API information endpoint"""
    return {
        "message": "Hominio Voice API with KokoroEngine TTS and RealtimeSTT", 
        "tts_engine": "kokoro", 
        "stt_engine": "whisper-base.en",
        "language": "English"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - unprotected for Fly.io monitoring"""
    return {"status": "healthy", "tts_engine": "kokoro", "stt_engine": "whisper-base.en"}

@app.get("/status")
async def status_check():
    """Basic status endpoint - unprotected for monitoring"""
    return {
        "status": "running",
        "service": "hominio-voice",
        "auth": "enabled"
    }

@app.get("/model-status")
async def get_model_status(user: str = Depends(verify_credentials)):
    """Get real-time model loading status"""
    return {
        "tts": tts_service.get_status(),
        "stt": stt_service.get_status(),
        "llm": {"status": "ready" if llm_service.is_ready() else "error", "model": "phala/llama-3.3-70b-instruct"}
    }

@app.post("/clear-conversation")
async def clear_conversation(user: str = Depends(verify_credentials)):
    """Clear conversation history and processed sentences"""
    llm_service.clear_conversation()
    logger.info("🧹 Conversation history and processed sentences cleared")
    return {"status": "cleared", "message": "Conversation history has been reset"}

@app.get("/conversation-status")
async def get_conversation_status(user: str = Depends(verify_credentials)):
    """Get current conversation status"""
    return {
        "conversation_length": len(llm_service.conversation_history),
        "processed_sentences_count": len(llm_service.processed_sentences),
        "conversation_history": llm_service.conversation_history[-10:] if llm_service.conversation_history else []  # Last 10 messages for preview
    }

@app.websocket("/ws")
async def unified_websocket_endpoint(websocket: WebSocket):
    """Unified WebSocket endpoint - handles STT, TTS, and model status communication"""
    global active_tts_ws
    
    # WebSocket authentication: Simplified approach
    if not PROTECTED_PASSWORD:
        # No password protection configured
        user = "anonymous"
    else:
        # For WebSocket connections, we'll be more permissive since the user
        # has already authenticated to access the page. We'll still check for
        # explicit authentication but won't require it if the connection
        # comes from the same origin.
        
        auth_token = websocket.query_params.get("token")
        auth_header = websocket.headers.get("authorization")
        
        authenticated = False
        user = "web_authenticated"
        
        # Method 1: Query parameter authentication
        if auth_token:
            try:
                import base64
                decoded_token = base64.b64decode(auth_token).decode('utf-8')
                if ":" in decoded_token:
                    username, password = decoded_token.split(":", 1)
                else:
                    username, password = "user", decoded_token
                
                if password == PROTECTED_PASSWORD:
                    authenticated = True
                    user = username if username else "token_authenticated"
            except Exception as e:
                logger.error(f"WebSocket token authentication error: {e}")
        
        # Method 2: Authorization header
        elif auth_header and auth_header.startswith("Basic "):
            try:
                import base64
                encoded_credentials = auth_header.split(" ")[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                
                if ":" in decoded_credentials:
                    username, password = decoded_credentials.split(":", 1)
                else:
                    username, password = "user", decoded_credentials
                
                if password == PROTECTED_PASSWORD:
                    authenticated = True
                    user = username if username else "header_authenticated"
            except Exception as e:
                logger.error(f"WebSocket header authentication error: {e}")
        
        # Method 3: Same-origin assumption (fallback)
        # If no explicit auth provided, we'll allow the connection since
        # the user has already authenticated to access the page
        if not authenticated:
            # Check if the connection is from the same origin
            origin = websocket.headers.get("origin")
            host = websocket.headers.get("host")
            
            if origin and host and (origin.endswith(host) or origin.endswith(f"://{host}")):
                authenticated = True
                user = "same_origin_authenticated"
                logger.info(f"🔗 [WebSocket] Allowing same-origin connection from {origin}")
            else:
                logger.warning(f"🔗 [WebSocket] Rejecting connection - no auth and different origin: {origin} vs {host}")
                await websocket.close(code=1008, reason="Authentication required")
                return
    
    await websocket.accept()
    logger.info(f"Unified WebSocket client connected (authenticated as: {user})")
    
    # Set this as the active TTS connection for server-initiated audio
    active_tts_ws = websocket
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "status",
            "message": "WebSocket connected - all services ready"
        }))
        
        # Create background tasks
        async def message_broadcaster():
            """Broadcast messages to the WebSocket client"""
            try:
                while True:
                    # Get message from queue
                    message = await stt_message_queue.get()
                    await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error in message broadcaster: {e}")
        
        async def status_broadcaster():
            """Broadcast model status updates"""
            try:
                last_sent_status = None
                while True:
                    # Combine all service statuses
                    combined_status = {
                        "type": "model-status",
                        "data": {
                            "tts": tts_service.get_status(),
                            "stt": stt_service.get_status(),
                            "llm": {"status": "ready" if llm_service.is_ready() else "error", "model": "phala/llama-3.3-70b-instruct"}
                        }
                    }
                    
                    # Only send updates when status changes
                    if combined_status != last_sent_status:
                        await websocket.send_text(json.dumps(combined_status))
                        last_sent_status = combined_status.copy()
                    
                    # Adjust polling frequency based on status
                    tts_status = tts_service.get_status()
                    stt_status = stt_service.get_status()
                    if (tts_status.get("status") in ["ready", "error"] and 
                        stt_status.get("status") in ["ready", "error"]):
                        await asyncio.sleep(30)  # Check every 30 seconds when stable
                    else:
                        await asyncio.sleep(2)   # Check every 2 seconds during loading
            except Exception as e:
                logger.error(f"Error in status broadcaster: {e}")
        
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
        
        # Start background tasks
        broadcaster_task = asyncio.create_task(message_broadcaster())
        status_task = asyncio.create_task(status_broadcaster())
        
        # Main message processing loop
        while True:
            try:
                # Receive message from client
                message = await websocket.receive()
                
                if message["type"] == "websocket.receive":
                    if "bytes" in message:
                        # Binary message - audio data for STT
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
                            if stt_service.is_ready():
                                stt_service.stt_engine.feed_audio(chunk)
                                print(f"🎵 Fed audio chunk: {len(chunk)} bytes, sample_rate: {sample_rate}")
                            else:
                                logger.warning("STT engine not available")
                                
                        except Exception as e:
                            logger.error(f"Error processing audio data: {e}")
                            continue
                
                    elif "text" in message:
                        # Text message - handle different message types
                        try:
                            data = json.loads(message["text"])
                            message_type = data.get("type", "unknown")
                            
                            logger.info(f"📥 WebSocket message received: {message_type} - {data}")
                            
                            # Route all messages through the message router (clean architecture)
                            await message_router.handle_websocket_message(data)
                            
                        except json.JSONDecodeError:
                            logger.error(f"❌ Invalid JSON received: {message}")
                        except Exception as e:
                            logger.error(f"❌ Error handling message: {e}")
                
            except Exception as e:
                logger.error(f"Error in WebSocket message processing: {e}")
                break
                
    except Exception as e:
        logger.error(f"Unified WebSocket error: {e}")
    finally:
        # Clean up background tasks
        if 'broadcaster_task' in locals():
            broadcaster_task.cancel()
        if 'status_task' in locals():
            status_task.cancel()
        
        # Clear active TTS connection
        if active_tts_ws == websocket:
            active_tts_ws = None
            
        logger.info("Unified WebSocket client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 