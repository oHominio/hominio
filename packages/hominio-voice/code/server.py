# server.py
from queue import Queue, Empty
import logging
from logsetup import setup_logging
setup_logging(logging.INFO)
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    logger.info("🖥️👋 Welcome to local real-time voice chat")

from upsample_overlap import UpsampleOverlap
from datetime import datetime
from colors import Colors
import uvicorn
import asyncio
import struct
import json
import time
import threading # Keep threading for SpeechPipelineManager internals and AbortWorker
import sys
import os # Added for environment variable access

from typing import Any, Dict, Optional, Callable # Added for type hints in docstrings
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, Response, FileResponse

# GPU Monitoring imports
from system_monitor import SystemMonitor, SystemStatsStreamer

# Session management imports
from session_manager import SessionManager
from session_state import SessionStatus

# Memory & Thread management imports
from memory_manager import get_memory_monitor, get_resource_tracker, QueueManager
from thread_manager import get_thread_manager, create_managed_thread

USE_SSL = False
TTS_START_ENGINE = "kokoro"
TTS_ORPHEUS_MODEL = "Orpheus_3B-1BaseGGUF/mOrpheus_3B-1Base_Q4_K_M.gguf"
TTS_ORPHEUS_MODEL = "orpheus-3b-0.1-ft-Q8_0-GGUF/orpheus-3b-0.1-ft-q8_0.gguf"

LLM_START_PROVIDER = "openai"
LLM_START_MODEL = "phala/llama-3.3-70b-instruct"
# LLM_START_PROVIDER = "lmstudio"
# LLM_START_MODEL = "Qwen3-30B-A3B-GGUF/Qwen3-30B-A3B-Q3_K_L.gguf"
NO_THINK = False
DIRECT_STREAM = TTS_START_ENGINE=="kokoro"  # Kokoro supports streaming through RealtimeTTS

if __name__ == "__main__":
    logger.info(f"🖥️⚙️ {Colors.apply('[PARAM]').blue} Starting engine: {Colors.apply(TTS_START_ENGINE).blue}")
    logger.info(f"🖥️⚙️ {Colors.apply('[PARAM]').blue} Direct streaming: {Colors.apply('ON' if DIRECT_STREAM else 'OFF').blue}")

# Define the maximum allowed size for the incoming audio queue
try:
    MAX_AUDIO_QUEUE_SIZE = int(os.getenv("MAX_AUDIO_QUEUE_SIZE", 50))
    if __name__ == "__main__":
        logger.info(f"🖥️⚙️ {Colors.apply('[PARAM]').blue} Audio queue size limit set to: {Colors.apply(str(MAX_AUDIO_QUEUE_SIZE)).blue}")
except ValueError:
    if __name__ == "__main__":
        logger.warning("🖥️⚠️ Invalid MAX_AUDIO_QUEUE_SIZE env var. Using default: 50")
    MAX_AUDIO_QUEUE_SIZE = 50


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#from handlerequests import LanguageProcessor
#from audio_out import AudioOutProcessor
from audio_in import AudioInputProcessor
from audio_input_pool import AudioInputProcessorPool
from speech_pipeline_manager import SpeechPipelineManager
from colors import Colors

# Connection rate limiting to prevent cascade failures during load testing
_CONNECTION_LIMITER = {
    'connections': {},  # Track recent connections by IP
    'max_connections_per_ip': 10,  # Max concurrent connections per IP
    'connection_window': 60.0,  # Time window in seconds
}

def check_connection_rate_limit(client_host: str) -> bool:
    """
    Check if the client IP has exceeded connection rate limits.
    
    Args:
        client_host: Client IP address
        
    Returns:
        True if connection is allowed, False if rate limited
    """
    current_time = time.time()
    
    if client_host not in _CONNECTION_LIMITER['connections']:
        _CONNECTION_LIMITER['connections'][client_host] = []
    
    # Clean old connections outside the window
    connections = _CONNECTION_LIMITER['connections'][client_host]
    cutoff_time = current_time - _CONNECTION_LIMITER['connection_window']
    _CONNECTION_LIMITER['connections'][client_host] = [
        conn_time for conn_time in connections if conn_time > cutoff_time
    ]
    
    # Check if under limit
    current_connections = len(_CONNECTION_LIMITER['connections'][client_host])
    if current_connections >= _CONNECTION_LIMITER['max_connections_per_ip']:
        logger.warning(f"🖥️⚠️ Rate limit exceeded for IP {client_host}: {current_connections} connections")
        return False
    
    # Add current connection
    _CONNECTION_LIMITER['connections'][client_host].append(current_time)
    return True

LANGUAGE = "en"
# TTS_FINAL_TIMEOUT = 0.5 # unsure if 1.0 is needed for stability
TTS_FINAL_TIMEOUT = 1.0 # unsure if 1.0 is needed for stability

# --------------------------------------------------------------------
# Custom no-cache StaticFiles
# --------------------------------------------------------------------
class NoCacheStaticFiles(StaticFiles):
    """
    Serves static files without allowing client-side caching.

    Overrides the default Starlette StaticFiles to add 'Cache-Control' headers
    that prevent browsers from caching static assets. Useful for development.
    """
    async def get_response(self, path: str, scope: Dict[str, Any]) -> Response:
        """
        Gets the response for a requested path, adding no-cache headers.

        Args:
            path: The path to the static file requested.
            scope: The ASGI scope dictionary for the request.

        Returns:
            A Starlette Response object with cache-control headers modified.
        """
        response: Response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        # These might not be strictly necessary with no-store, but belt and suspenders
        if "etag" in response.headers:
             response.headers.__delitem__("etag")
        if "last-modified" in response.headers:
             response.headers.__delitem__("last-modified")
        return response

# --------------------------------------------------------------------
# Lifespan management
# --------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan, initializing and shutting down resources.

    Initializes global components like SpeechPipelineManager, Upsampler, and
    AudioInputProcessor and stores them in `app.state`. Handles cleanup on shutdown.

    Args:
        app: The FastAPI application instance.
    """
    logger.info("🖥️▶️ Server starting up")
    
    # Initialize memory and thread management
    logger.info("🖥️🧠 Initializing memory and thread management...")
    app.state.MemoryMonitor = get_memory_monitor()
    app.state.ResourceTracker = get_resource_tracker()
    app.state.ThreadManager = get_thread_manager()
    
    # Start background monitoring
    app.state.MemoryMonitor.start_monitoring()
    app.state.ThreadManager.start_monitoring()
    logger.info("🖥️🧠 Memory and thread monitoring started")
    
    # Initialize session management
    app.state.SessionManager = SessionManager()
    await app.state.SessionManager.start_cleanup_task()
    
    # Initialize system monitoring
    app.state.SystemMonitor = SystemMonitor()
    system_initialized = await app.state.SystemMonitor.initialize()
    if system_initialized:
        app.state.SystemStatsStreamer = SystemStatsStreamer(app.state.SystemMonitor, update_interval=0.5)
        await app.state.SystemStatsStreamer.start_streaming()
        logger.info("🖥️📊 System monitoring initialized and streaming started")
    else:
        app.state.SystemStatsStreamer = None
        logger.warning("🖥️⚠️ System monitoring not available")
    
    # Initialize global components - these will be shared by sessions but accessed safely
    app.state.SpeechPipelineManager = SpeechPipelineManager(
        tts_engine=TTS_START_ENGINE,
        llm_provider=LLM_START_PROVIDER,
        llm_model=LLM_START_MODEL,
        no_think=NO_THINK,
        orpheus_model=TTS_ORPHEUS_MODEL,
    )

    app.state.Upsampler = UpsampleOverlap()
    
    # Initialize AudioInputProcessor pool for multi-user concurrency
    # Auto-adjust pool size based on available GPU memory
    try:
        import torch
        if torch.cuda.is_available():
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            # Conservative sizing: ~1GB per concurrent user (STT + TurnDetection models)
            max_concurrent_users = max(3, min(int(gpu_memory_gb * 0.6), 50))
            initial_pool_size = min(3, max_concurrent_users)
            logger.info(f"🖥️🎯 Auto-sizing pool: {initial_pool_size} initial, {max_concurrent_users} max (GPU: {gpu_memory_gb:.1f}GB)")
        else:
            max_concurrent_users = 10  # CPU fallback
            initial_pool_size = 3
            logger.info(f"🖥️🎯 CPU mode: {initial_pool_size} initial, {max_concurrent_users} max")
    except Exception as e:
        logger.warning(f"🖥️⚠️ Failed to detect GPU memory, using defaults: {e}")
        max_concurrent_users = 10
        initial_pool_size = 3
    
    app.state.AudioInputProcessorPool = AudioInputProcessorPool(
        initial_size=initial_pool_size,
        max_size=max_concurrent_users,
        language=LANGUAGE,
        is_orpheus=TTS_START_ENGINE=="orpheus",
        pipeline_latency=app.state.SpeechPipelineManager.full_output_pipeline_latency / 1000, # seconds
    )
    
    app.state.Aborting = False # Keep this? Its usage isn't clear in the provided snippet. Minimizing changes.

    yield

    logger.info("🖥️⏹️ Server shutting down")
    
    # Shutdown memory and thread management first
    if hasattr(app.state, 'MemoryMonitor'):
        app.state.MemoryMonitor.stop_monitoring()
        logger.info("🖥️🧠 Memory monitoring stopped")
        
    if hasattr(app.state, 'ThreadManager'):
        app.state.ThreadManager.stop_monitoring()
        logger.info("🖥️🧠 Thread monitoring stopped")
    
    # Shutdown session management
    if hasattr(app.state, 'SessionManager'):
        await app.state.SessionManager.shutdown()
        logger.info("🖥️🏢 Session manager shutdown")
    
    # Shutdown system monitoring
    if hasattr(app.state, 'SystemStatsStreamer') and app.state.SystemStatsStreamer:
        await app.state.SystemStatsStreamer.stop_streaming()
        logger.info("🖥️📊 System stats streaming stopped")
        
    if hasattr(app.state, 'SystemMonitor'):
        await app.state.SystemMonitor.shutdown()
        logger.info("🖥️📊 System monitor shutdown")
    
    # Shutdown AudioInputProcessor pool
    if hasattr(app.state, 'AudioInputProcessorPool'):
        app.state.AudioInputProcessorPool.shutdown()
        logger.info("🖥️🏊‍♂️ AudioInputProcessor pool shutdown")

# --------------------------------------------------------------------
# FastAPI app instance
# --------------------------------------------------------------------
app = FastAPI(lifespan=lifespan)

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with no cache
app.mount("/static", NoCacheStaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    """Health check endpoint for Fly.io deployment"""
    try:
        # Quick health check - verify key components are initialized
        if (hasattr(app.state, 'SpeechPipelineManager') and 
            app.state.SpeechPipelineManager is not None):
            return {"status": "healthy", "kokoro": "ready", "message": "All systems operational"}
        else:
            return {"status": "initializing", "kokoro": "loading", "message": "System still starting up"}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Health check failed"}

@app.get("/sessions")
async def session_stats():
    """
    Returns session statistics for monitoring multi-user usage.

    Returns:
        dict: Session statistics including active users, total sessions, etc.
    """
    try:
        stats = app.state.SessionManager.get_session_stats()
        return {
            "status": "OK",
            "timestamp": time.time(),
            "sessions": stats
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to get session stats"}

@app.get("/pool")
async def pool_stats():
    """
    Returns AudioInputProcessor pool statistics for monitoring resource usage.

    Returns:
        dict: Pool statistics including allocation counts, utilization, etc.
    """
    try:
        if hasattr(app.state, 'AudioInputProcessorPool'):
            pool_status = app.state.AudioInputProcessorPool.get_pool_status()
            return {
                "status": "OK",
                "timestamp": time.time(),
                "pool": pool_status
            }
        else:
            return {"status": "error", "message": "AudioInputProcessor pool not available"}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Failed to get pool stats"}

@app.get("/favicon.ico")
async def favicon():
    """
    Serves the favicon.ico file.

    Returns:
        A FileResponse containing the favicon.
    """
    return FileResponse("static/favicon.ico")

@app.get("/")
async def get_index() -> HTMLResponse:
    """
    Serves the main index.html page.

    Reads the content of static/index.html and returns it as an HTML response.

    Returns:
        An HTMLResponse containing the content of index.html.
    """
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/dashboard")
async def get_dashboard() -> HTMLResponse:
    """
    Serves the dashboard interface for load testing and system monitoring.

    Returns:
        An HTMLResponse containing the dashboard interface.
    """
    try:
        with open("static/dashboard.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html><head><title>Dashboard</title></head>
        <body><h1>Dashboard Page Not Found</h1></body></html>
        """, status_code=404)

# --------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------
def parse_json_message(text: str) -> dict:
    """
    Safely parses a JSON string into a dictionary.

    Logs a warning if the JSON is invalid and returns an empty dictionary.

    Args:
        text: The JSON string to parse.

    Returns:
        A dictionary representing the parsed JSON, or an empty dictionary on error.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("🖥️⚠️ Ignoring client message with invalid JSON")
        return {}

def format_timestamp_ns(timestamp_ns: int) -> str:
    """
    Formats a nanosecond timestamp into a human-readable HH:MM:SS.fff string.

    Args:
        timestamp_ns: The timestamp in nanoseconds since the epoch.

    Returns:
        A string formatted as hours:minutes:seconds.milliseconds.
    """
    # Split into whole seconds and the nanosecond remainder
    seconds = timestamp_ns // 1_000_000_000
    remainder_ns = timestamp_ns % 1_000_000_000

    # Convert seconds part into a datetime object (local time)
    dt = datetime.fromtimestamp(seconds)

    # Format the main time as HH:MM:SS
    time_str = dt.strftime("%H:%M:%S")

    # For instance, if you want milliseconds, divide the remainder by 1e6 and format as 3-digit
    milliseconds = remainder_ns // 1_000_000
    formatted_timestamp = f"{time_str}.{milliseconds:03d}"

    return formatted_timestamp

# --------------------------------------------------------------------
# WebSocket data processing
# --------------------------------------------------------------------

async def process_incoming_data(ws: WebSocket, app: FastAPI, incoming_chunks: asyncio.Queue, callbacks: 'TranscriptionCallbacks', session_id: str) -> None:
    """
    Receives messages via WebSocket, processes audio and text messages.

    Handles binary audio chunks with queue overflow protection, extracting metadata 
    (timestamp, flags) and putting the audio PCM data with metadata into the 
    `incoming_chunks` queue. Applies back-pressure if the queue is full.
    Parses text messages (assumed JSON) and triggers actions based on message type
    (e.g., updates client TTS state via `callbacks`, clears history, sets speed).

    Args:
        ws: The WebSocket connection instance.
        app: The FastAPI application instance (for accessing global state if needed).
        incoming_chunks: An asyncio queue to put processed audio metadata dictionaries into.
        callbacks: The TranscriptionCallbacks instance for this connection to manage state.
        session_id: The unique session identifier for this WebSocket connection.
    """
    try:
        while True:
            msg = await ws.receive()
            # Update session activity on any message
            app.state.SessionManager.update_activity(session_id)
            
            if "bytes" in msg and msg["bytes"]:
                raw = msg["bytes"]

                # Ensure we have at least an 8‑byte header: 4 bytes timestamp_ms + 4 bytes flags
                if len(raw) < 8:
                    logger.warning("🖥️⚠️ Received packet too short for 8‑byte header.")
                    continue

                # Unpack big‑endian uint32 timestamp (ms) and uint32 flags
                timestamp_ms, flags = struct.unpack("!II", raw[:8])
                client_sent_ns = timestamp_ms * 1_000_000

                # Build metadata using fixed fields
                metadata = {
                    "client_sent_ms":           timestamp_ms,
                    "client_sent":              client_sent_ns,
                    "client_sent_formatted":    format_timestamp_ns(client_sent_ns),
                    "isTTSPlaying":             bool(flags & 1),
                }

                # Record server receive time
                server_ns = time.time_ns()
                metadata["server_received"] = server_ns
                metadata["server_received_formatted"] = format_timestamp_ns(server_ns)

                # The rest of the payload is raw PCM bytes
                metadata["pcm"] = raw[8:]

                # Check queue size with overflow protection
                current_qsize = incoming_chunks.qsize()
                if current_qsize < MAX_AUDIO_QUEUE_SIZE:
                    # Put data into the queue
                    await incoming_chunks.put(metadata)
                    
                    # Update session state - audio chunk received
                    session_state = app.state.SessionManager.get_session_state(session_id)
                    if session_state:
                        session_state.increment_audio_chunk()
                elif current_qsize >= MAX_AUDIO_QUEUE_SIZE * 0.9:  # At 90% capacity, start dropping old items
                    # Emergency eviction - remove old items to make space
                    evicted_count = 0
                    while incoming_chunks.qsize() > MAX_AUDIO_QUEUE_SIZE * 0.7 and evicted_count < 10:
                        try:
                            incoming_chunks.get_nowait()
                            evicted_count += 1
                        except asyncio.QueueEmpty:
                            break
                    
                    if evicted_count > 0:
                        logger.warning(f"🖥️🧹 Evicted {evicted_count} old audio chunks to prevent overflow")
                    
                    # Try to put the new item
                    try:
                        await asyncio.wait_for(incoming_chunks.put(metadata), timeout=0.01)
                        # Update session state - audio chunk received
                        session_state = app.state.SessionManager.get_session_state(session_id)
                        if session_state:
                            session_state.increment_audio_chunk()
                    except asyncio.TimeoutError:
                        logger.warning(f"🖥️⚠️ Audio queue timeout, dropping chunk for session {session_id}")
                else:
                    # Queue is completely full, drop the chunk
                    logger.warning(
                        f"🖥️⚠️ Audio queue full ({current_qsize}/{MAX_AUDIO_QUEUE_SIZE}); dropping chunk for session {session_id}"
                    )

            elif "text" in msg and msg["text"]:
                # Text-based message: parse JSON
                data = parse_json_message(msg["text"])
                msg_type = data.get("type")
                # Only log important incoming messages, skip partial requests to reduce noise
                if msg_type not in ("partial_user_request", "get_system_stats"):
                    logger.info(Colors.apply(f"🖥️📥 ←←Client: {data}").orange)


                if msg_type == "tts_start":
                    logger.info("🖥️ℹ️ Received tts_start from client.")
                    # Update connection-specific state via callbacks
                    callbacks.tts_client_playing = True
                elif msg_type == "tts_stop":
                    logger.info("🖥️ℹ️ Received tts_stop from client.")
                    # Update connection-specific state via callbacks
                    callbacks.tts_client_playing = False
                # Add to the handleJSONMessage function in server.py
                elif msg_type == "clear_history":
                    logger.info("🖥️ℹ️ Received clear_history from client.")
                    # Use per-user speech pipeline manager instead of global
                    if callbacks.audio_processor and hasattr(callbacks.audio_processor, 'speech_pipeline_manager'):
                        callbacks.audio_processor.speech_pipeline_manager.reset()
                    else:
                        # Fallback to global manager if per-user not available yet
                        app.state.SpeechPipelineManager.reset()
                elif msg_type == "set_speed":
                    speed_value = data.get("speed", 0)
                    speed_factor = speed_value / 100.0  # Convert 0-100 to 0.0-1.0
                    # Get session-specific audio processor
                    audio_processor = app.state.SessionManager.get_session_component(session_id, "audio_processor")
                    if audio_processor and audio_processor.transcriber.turn_detection:
                        audio_processor.transcriber.turn_detection.update_settings(speed_factor)
                        logger.info(f"🖥️⚙️ Updated turn detection settings to factor: {speed_factor:.2f}")


    except asyncio.CancelledError:
        pass # Task cancellation is expected on disconnect
    except WebSocketDisconnect as e:
        logger.warning(f"🖥️⚠️ {Colors.apply('WARNING').red} disconnect in process_incoming_data: {repr(e)}")
    except RuntimeError as e:  # Often raised on closed transports
        logger.error(f"🖥️💥 {Colors.apply('RUNTIME_ERROR').red} in process_incoming_data: {repr(e)}")
    except Exception as e:
        logger.exception(f"🖥️💥 {Colors.apply('EXCEPTION').red} in process_incoming_data: {repr(e)}")

async def send_text_messages(ws: WebSocket, message_queue: asyncio.Queue) -> None:
    """
    Continuously sends outgoing text messages (excluding TTS chunks) to the WebSocket client.

    Retrieves messages from the provided asyncio queue and sends them as JSON through the
    WebSocket connection. Handles connection errors and task cancellation gracefully.

    Args:
        ws: The WebSocket connection instance.
        message_queue: An asyncio queue yielding dictionaries to be sent as JSON.
    """
    try:
        while True:
            await asyncio.sleep(0.001) # Yield control
            data = await message_queue.get()
            msg_type = data.get("type")
            # Only log important messages, skip noisy partial messages and stats to reduce noise
            if msg_type not in ("tts_chunk", "session_stats", "partial_assistant_answer", "partial_user_request"):
                logger.info(Colors.apply(f"🖥️📤 →→Client: {data}").orange)
            await ws.send_json(data)
    except asyncio.CancelledError:
        pass # Task cancellation is expected on disconnect
    except WebSocketDisconnect as e:
        logger.warning(f"🖥️⚠️ {Colors.apply('WARNING').red} disconnect in send_text_messages: {repr(e)}")
    except RuntimeError as e:  # Often raised on closed transports
        logger.error(f"🖥️💥 {Colors.apply('RUNTIME_ERROR').red} in send_text_messages: {repr(e)}")
    except Exception as e:
        logger.exception(f"🖥️💥 {Colors.apply('EXCEPTION').red} in send_text_messages: {repr(e)}")

async def _reset_interrupt_flag_async(app: FastAPI, callbacks: 'TranscriptionCallbacks'):
    """
    Resets the microphone interruption flag after a delay (async version).

    Waits for 1 second, then checks if the session-specific AudioInputProcessor is still marked
    as interrupted. If so, resets the flag on both the processor and the
    connection-specific callbacks instance.

    Args:
        app: The FastAPI application instance.
        callbacks: The TranscriptionCallbacks instance for the connection.
    """
    await asyncio.sleep(1)
    # Check the session-specific AudioInputProcessor's interrupted state
    if callbacks.audio_processor and callbacks.audio_processor.interrupted:
        logger.info(f"{Colors.apply('🖥️🎙️ ▶️ Microphone continued (async reset)').cyan}")
        callbacks.audio_processor.interrupted = False
        # Reset connection-specific interruption time via callbacks
        callbacks.interruption_time = 0
        logger.info(Colors.apply("🖥️🎙️ interruption flag reset after TTS chunk (async)").cyan)

async def send_tts_chunks(app: FastAPI, message_queue: asyncio.Queue, callbacks: 'TranscriptionCallbacks') -> None:
    """
    Continuously sends TTS audio chunks from the SpeechPipelineManager to the client.

    Monitors the state of the current speech generation (if any) and the client
    connection (via `callbacks`). Retrieves audio chunks from the active generation's
    queue, upsamples/encodes them, and puts them onto the outgoing `message_queue`
    for the client. Handles the end-of-generation logic and state resets.

    Args:
        app: The FastAPI application instance (to access global components).
        message_queue: An asyncio queue to put outgoing TTS chunk messages onto.
        callbacks: The TranscriptionCallbacks instance managing this connection's state.
    """
    try:
        logger.info("🖥️🔊 Starting TTS chunk sender")
        last_quick_answer_chunk = 0
        last_chunk_sent = 0
        prev_status = None
        last_status_log_time = 0  # Add throttling for status logs

        while True:
            await asyncio.sleep(0.001) # Yield control

            # Use connection-specific interruption_time via callbacks
            if callbacks.audio_processor and callbacks.audio_processor.interrupted and callbacks.interruption_time and time.time() - callbacks.interruption_time > 2.0:
                callbacks.audio_processor.interrupted = False
                callbacks.interruption_time = 0 # Reset via callbacks
                logger.info(Colors.apply("🖥️🎙️ interruption flag reset after 2 seconds").cyan)

            # Use per-user speech pipeline manager instead of global
            speech_manager = None
            if callbacks.audio_processor and hasattr(callbacks.audio_processor, 'speech_pipeline_manager'):
                speech_manager = callbacks.audio_processor.speech_pipeline_manager
            else:
                # Fallback to global manager if per-user not available yet
                speech_manager = app.state.SpeechPipelineManager
                
            is_tts_finished = speech_manager.is_valid_gen() and speech_manager.running_generation.audio_quick_finished

            def log_status():
                nonlocal prev_status, last_status_log_time
                current_time = time.time()
                last_quick_answer_chunk_decayed = (
                    last_quick_answer_chunk
                    and time.time() - last_quick_answer_chunk > TTS_FINAL_TIMEOUT
                    and time.time() - last_chunk_sent > TTS_FINAL_TIMEOUT
                )

                curr_status = (
                    # Access connection-specific state via callbacks
                    int(callbacks.tts_to_client),
                    int(callbacks.tts_client_playing),
                    int(callbacks.tts_chunk_sent),
                    1, # Placeholder?
                    int(callbacks.is_hot), # from callbacks
                    int(callbacks.synthesis_started), # from callbacks
                    int(speech_manager.running_generation is not None), # Per-user manager state
                    int(speech_manager.is_valid_gen()), # Per-user manager state
                    int(is_tts_finished), # Calculated local variable
                    int(callbacks.audio_processor.interrupted if callbacks.audio_processor else False) # Input processor state
                )

                # State logging removed to reduce noise
                prev_status = curr_status

            # Use connection-specific state via callbacks
            if not callbacks.tts_to_client:
                await asyncio.sleep(0.001)
                log_status()
                continue

            if not speech_manager.running_generation:
                await asyncio.sleep(0.001)
                log_status()
                continue

            if speech_manager.running_generation.abortion_started:
                await asyncio.sleep(0.001)
                log_status()
                continue

            if not speech_manager.running_generation.audio_quick_finished:
                speech_manager.running_generation.tts_quick_allowed_event.set()

            if not speech_manager.running_generation.quick_answer_first_chunk_ready:
                await asyncio.sleep(0.001)
                log_status()
                continue

            chunk = None
            try:
                chunk = speech_manager.running_generation.audio_chunks.get_nowait()
                if chunk:
                    last_quick_answer_chunk = time.time()
            except Empty:
                final_expected = speech_manager.running_generation.quick_answer_provided
                audio_final_finished = speech_manager.running_generation.audio_final_finished

                if not final_expected or audio_final_finished:
                    logger.info("🖥️🏁 Sending of TTS chunks and 'user request/assistant answer' cycle finished.")
                    callbacks.send_final_assistant_answer() # Callbacks method

                    assistant_answer = speech_manager.running_generation.quick_answer + speech_manager.running_generation.final_answer                    
                    speech_manager.running_generation = None

                    callbacks.tts_chunk_sent = False # Reset via callbacks
                    callbacks.reset_state() # Reset connection state via callbacks

                await asyncio.sleep(0.001)
                log_status()
                continue

            base64_chunk = app.state.Upsampler.get_base64_chunk(chunk)
            message_queue.put_nowait({
                "type": "tts_chunk",
                "content": base64_chunk
            })
            last_chunk_sent = time.time()

            # Use connection-specific state via callbacks
            if not callbacks.tts_chunk_sent:
                # Use the async helper function instead of a thread
                asyncio.create_task(_reset_interrupt_flag_async(app, callbacks))

            callbacks.tts_chunk_sent = True # Set via callbacks
            
            # Update session state - TTS chunk sent
            session_state = app.state.SessionManager.get_session_state(callbacks.session_id)
            if session_state:
                session_state.increment_tts_chunk()
                session_state.set_speaking(True)
                app.state.SessionManager.update_session_status(callbacks.session_id, SessionStatus.SPEAKING)

    except asyncio.CancelledError:
        pass # Task cancellation is expected on disconnect
    except WebSocketDisconnect as e:
        logger.warning(f"🖥️⚠️ {Colors.apply('WARNING').red} disconnect in send_tts_chunks: {repr(e)}")
    except RuntimeError as e:
        logger.error(f"🖥️💥 {Colors.apply('RUNTIME_ERROR').red} in send_tts_chunks: {repr(e)}")
    except Exception as e:
        logger.exception(f"🖥️💥 {Colors.apply('EXCEPTION').red} in send_tts_chunks: {repr(e)}")


# --------------------------------------------------------------------
# Callback class to handle transcription events
# --------------------------------------------------------------------
class TranscriptionCallbacks:
    """
    Manages state and callbacks for a single WebSocket connection's transcription lifecycle.

    This class holds connection-specific state flags (like TTS status, user interruption)
    and implements callback methods triggered by the `AudioInputProcessor` and
    `SpeechPipelineManager`. It sends messages back to the client via the provided
    `message_queue` and manages interaction logic like interruptions and final answer delivery.
    It also includes a threaded worker to handle abort checks based on partial transcription.
    """
    def __init__(self, app: FastAPI, message_queue: asyncio.Queue, session_id: str):
        """
        Initializes the TranscriptionCallbacks instance for a WebSocket connection.

        Args:
            app: The FastAPI application instance (to access global components).
            message_queue: An asyncio queue for sending messages back to the client.
            session_id: Unique identifier for this session.
        """
        self.app = app
        self.message_queue = message_queue
        self.session_id = session_id
        self.audio_processor: Optional[AudioInputProcessor] = None  # Session-specific processor
        self.final_transcription = ""
        self.abort_text = ""
        self.last_abort_text = ""

        # Initialize connection-specific state flags here
        self.tts_to_client: bool = False
        self.user_interrupted: bool = False
        self.tts_chunk_sent: bool = False
        self.tts_client_playing: bool = False
        self.interruption_time: float = 0.0

        # These were already effectively instance variables or reset logic existed
        self.silence_active: bool = True
        self.is_hot: bool = False
        self.user_finished_turn: bool = False
        self.synthesis_started: bool = False
        self.assistant_answer: str = ""
        self.final_assistant_answer: str = ""
        self.is_processing_potential: bool = False
        self.is_processing_final: bool = False
        self.last_inferred_transcription: str = ""
        self.final_assistant_answer_sent: bool = False
        self.partial_transcription: str = "" # Added for clarity

        self.reset_state() # Call reset to ensure consistency

        self.abort_request_event = threading.Event()
        self.abort_worker_thread = create_managed_thread(target=self._abort_worker, name="AbortWorker", daemon=True)
        # Note: Thread starts automatically when created (auto_start=True by default)


    def reset_state(self):
        """Resets connection-specific state flags and variables to their initial values."""
        # Reset all connection-specific state flags
        self.tts_to_client = False
        self.user_interrupted = False
        self.tts_chunk_sent = False
        # Don't reset tts_client_playing here, it reflects client state reports
        self.interruption_time = 0.0

        # Reset other state variables
        self.silence_active = True
        self.is_hot = False
        self.user_finished_turn = False
        self.synthesis_started = False
        self.assistant_answer = ""
        self.final_assistant_answer = ""
        self.is_processing_potential = False
        self.is_processing_final = False
        self.last_inferred_transcription = ""
        self.final_assistant_answer_sent = False
        self.partial_transcription = ""

        # Keep the abort call related to the audio processor/pipeline manager
        if self.audio_processor:
            self.audio_processor.abort_generation()


    def _abort_worker(self):
        """Background thread worker to check for abort conditions based on partial text."""
        while True:
            was_set = self.abort_request_event.wait(timeout=0.1) # Check every 100ms
            if was_set:
                self.abort_request_event.clear()
                # Only trigger abort check if the text actually changed
                if self.last_abort_text != self.abort_text:
                    self.last_abort_text = self.abort_text
                    logger.debug(f"🖥️🧠 Abort check triggered by partial: '{self.abort_text}'")
                    # Use per-user speech pipeline manager instead of global
                    if self.audio_processor and hasattr(self.audio_processor, 'speech_pipeline_manager'):
                        self.audio_processor.speech_pipeline_manager.check_abort(self.abort_text, False, "on_partial")
                    else:
                        # Fallback to global manager if per-user not available yet
                        self.app.state.SpeechPipelineManager.check_abort(self.abort_text, False, "on_partial")

    def on_partial(self, txt: str):
        """
        Callback invoked when a partial transcription result is available.

        Updates internal state, sends the partial result to the client,
        and signals the abort worker thread to check for potential interruptions.

        Args:
            txt: The partial transcription text.
        """
        self.final_assistant_answer_sent = False # New user speech invalidates previous final answer sending state
        self.final_transcription = "" # Clear final transcription as this is partial
        self.partial_transcription = txt
        self.message_queue.put_nowait({"type": "partial_user_request", "content": txt})
        self.abort_text = txt # Update text used for abort check
        self.abort_request_event.set() # Signal the abort worker
        
        # Update session state
        session_state = self.app.state.SessionManager.get_session_state(self.session_id)
        if session_state:
            session_state.set_recording(True)
            session_state.increment_message_received()

    def safe_abort_running_syntheses(self, reason: str):
        """Placeholder for safely aborting syntheses (currently does nothing)."""
        # TODO: Implement actual abort logic if needed, potentially interacting with SpeechPipelineManager
        pass

    def on_tts_allowed_to_synthesize(self):
        """Callback invoked when the system determines TTS synthesis can proceed."""
        # Use per-user speech pipeline manager instead of global
        speech_manager = None
        if self.audio_processor and hasattr(self.audio_processor, 'speech_pipeline_manager'):
            speech_manager = self.audio_processor.speech_pipeline_manager
        else:
            # Fallback to global manager if per-user not available yet
            speech_manager = self.app.state.SpeechPipelineManager
            
        if speech_manager.running_generation and not speech_manager.running_generation.abortion_started:
            logger.debug(f"🖥️🔊 TTS ALLOWED (Session: {self.session_id})")
            speech_manager.running_generation.tts_quick_allowed_event.set()

    def on_potential_sentence(self, txt: str):
        """
        Callback invoked when a potentially complete sentence is detected by the STT.

        Triggers the preparation of a speech generation based on this potential sentence.

        Args:
            txt: The potential sentence text.
        """
        logger.debug(f"🖥️🧠 Potential sentence: '{txt}'")
        # Use per-user speech pipeline manager instead of global
        if self.audio_processor and hasattr(self.audio_processor, 'speech_pipeline_manager'):
            self.audio_processor.speech_pipeline_manager.prepare_generation(txt)
        else:
            # Fallback to global manager if per-user not available yet
            self.app.state.SpeechPipelineManager.prepare_generation(txt)

    def on_potential_final(self, txt: str):
        """
        Callback invoked when a potential *final* transcription is detected (hot state).

        Logs the potential final transcription.

        Args:
            txt: The potential final transcription text.
        """
        logger.info(f"{Colors.apply('🖥️🧠 HOT: ').magenta}{txt}")

    def on_potential_abort(self):
        """Callback invoked if the STT detects a potential need to abort based on user speech."""
        # Placeholder: Currently logs nothing, could trigger abort logic.
        pass

    def on_before_final(self, audio: bytes, txt: str):
        """
        Callback invoked just before the final STT result for a user turn is confirmed.

        Sets flags indicating user finished, allows TTS if pending, interrupts microphone input,
        releases TTS stream to client, sends final user request and any pending partial
        assistant answer to the client, and adds user request to history.

        Args:
            audio: The raw audio bytes corresponding to the final transcription. (Currently unused)
            txt: The transcription text (might be slightly refined in on_final).
        """
        logger.info(Colors.apply('🖥️🏁 =================== USER TURN END ===================').light_gray)
        self.user_finished_turn = True
        self.user_interrupted = False # Reset connection-specific flag (user finished, not interrupted)
        
        # Use per-user speech pipeline manager instead of global
        speech_manager = None
        if self.audio_processor and hasattr(self.audio_processor, 'speech_pipeline_manager'):
            speech_manager = self.audio_processor.speech_pipeline_manager
        else:
            # Fallback to global manager if per-user not available yet
            speech_manager = self.app.state.SpeechPipelineManager
            
        if speech_manager.is_valid_gen():
            logger.debug(f"🖥️🔊 TTS ALLOWED (before final, Session: {self.session_id})")
            speech_manager.running_generation.tts_quick_allowed_event.set()

        # first block further incoming audio (Audio processor's state)
        if self.audio_processor and not self.audio_processor.interrupted:
            logger.info(f"{Colors.apply('🖥️🎙️ ⏸️ Microphone interrupted (end of turn)').cyan}")
            self.audio_processor.interrupted = True
            self.interruption_time = time.time() # Set connection-specific flag

        logger.info(f"{Colors.apply('🖥️🔊 TTS STREAM RELEASED').blue}")
        self.tts_to_client = True # Set connection-specific flag

        # Send final user request (using the reliable final_transcription OR current partial if final isn't set yet)
        user_request_content = self.final_transcription if self.final_transcription else self.partial_transcription
        self.message_queue.put_nowait({
            "type": "final_user_request",
            "content": user_request_content
        })

        if speech_manager.is_valid_gen():
            # Send partial assistant answer (if available) to the client
            # Use connection-specific user_interrupted flag
            if speech_manager.running_generation.quick_answer and not self.user_interrupted:
                self.assistant_answer = speech_manager.running_generation.quick_answer
                self.message_queue.put_nowait({
                    "type": "partial_assistant_answer",
                    "content": self.assistant_answer
                })

        logger.info(f"🖥️🧠 Adding user request to history: '{user_request_content}'")
        # Use per-user speech pipeline manager's history instead of global
        speech_manager.history.append({"role": "user", "content": user_request_content})

    def on_final(self, txt: str):
        """
        Callback invoked when the final transcription result for a user turn is available.

        Logs the final transcription and stores it.

        Args:
            txt: The final transcription text.
        """
        logger.info(f"\n{Colors.apply('🖥️✅ FINAL USER REQUEST (STT Callback): ').green}{txt}")
        if not self.final_transcription: # Store it if not already set by on_before_final logic
             self.final_transcription = txt
        
        # Trigger immediate GPU stats update after STT processing
        asyncio.create_task(self.app.state.SystemMonitor.trigger_immediate_update("STT completed"))
        
        # Update session state - user finished speaking
        session_state = self.app.state.SessionManager.get_session_state(self.session_id)
        if session_state:
            session_state.set_recording(False)
            self.app.state.SessionManager.update_session_status(self.session_id, SessionStatus.PROCESSING)

    def abort_generations(self, reason: str):
        """
        Triggers the abortion of any ongoing speech generation process.

        Logs the reason and calls the SpeechPipelineManager's abort method.

        Args:
            reason: A string describing why the abortion is triggered.
        """
        logger.info(f"{Colors.apply('🖥️🛑 Aborting generation:').blue} {reason}")
        # Use per-user speech pipeline manager instead of global
        if self.audio_processor and hasattr(self.audio_processor, 'speech_pipeline_manager'):
            self.audio_processor.speech_pipeline_manager.abort_generation(reason=f"server.py abort_generations: {reason}")
        else:
            # Fallback to global manager if per-user not available yet
            self.app.state.SpeechPipelineManager.abort_generation(reason=f"server.py abort_generations: {reason}")

    def on_silence_active(self, silence_active: bool):
        """
        Callback invoked when the silence detection state changes.

        Updates the internal silence_active flag.

        Args:
            silence_active: True if silence is currently detected, False otherwise.
        """
        # logger.debug(f"🖥️🎙️ Silence active: {silence_active}") # Optional: Can be noisy
        self.silence_active = silence_active

    def on_partial_assistant_text(self, txt: str):
        """
        Callback invoked when a partial text result from the assistant (LLM) is available.

        Updates the internal assistant answer state and sends the partial answer to the client,
        unless the user has interrupted.

        Args:
            txt: The partial assistant text.
        """
        # logger.info(f"{Colors.apply('🖥️💬 PARTIAL ASSISTANT ANSWER: ').green}{txt}")
        # Use connection-specific user_interrupted flag
        if not self.user_interrupted:
            self.assistant_answer = txt
            # Use connection-specific tts_to_client flag
            if self.tts_to_client:
                self.message_queue.put_nowait({
                    "type": "partial_assistant_answer",
                    "content": txt
                })

    def on_recording_start(self):
        """
        Callback invoked when the audio input processor starts recording user speech.

        If client-side TTS is playing, it triggers an interruption: stops server-side
        TTS streaming, sends stop/interruption messages to the client, aborts ongoing
        generation, sends any final assistant answer generated so far, and resets relevant state.
        """
        logger.info(f"{Colors.ORANGE}🖥️🎙️ Recording started.{Colors.RESET} TTS Client Playing: {self.tts_client_playing}")
        
        # Update session state - user started speaking/recording
        session_state = self.app.state.SessionManager.get_session_state(self.session_id)
        if session_state:
            session_state.set_recording(True)
            self.app.state.SessionManager.update_session_status(self.session_id, SessionStatus.LISTENING)
        
        # Use connection-specific tts_client_playing flag
        if self.tts_client_playing:
            self.tts_to_client = False # Stop server sending TTS
            self.user_interrupted = True # Mark connection as user interrupted
            logger.info(f"{Colors.apply('🖥️❗ INTERRUPTING TTS due to recording start').blue}")

            # Send final assistant answer *if* one was generated and not sent
            logger.info(Colors.apply("🖥️✅ Sending final assistant answer (forced on interruption)").pink)
            self.send_final_assistant_answer(forced=True)

            # Minimal reset for interruption:
            self.tts_chunk_sent = False # Reset chunk sending flag
            # self.assistant_answer = "" # Optional: Clear partial answer if needed

            logger.info("🖥️🛑 Sending stop_tts to client.")
            self.message_queue.put_nowait({
                "type": "stop_tts", # Client handles this to mute/ignore
                "content": ""
            })

            logger.info(f"{Colors.apply('🖥️🛑 RECORDING START ABORTING GENERATION').red}")
            self.abort_generations("on_recording_start, user interrupts, TTS Playing")

            logger.info("🖥️❗ Sending tts_interruption to client.")
            self.message_queue.put_nowait({ # Tell client to stop playback and clear buffer
                "type": "tts_interruption",
                "content": ""
            })

            # Reset state *after* performing actions based on the old state
            # Be careful what exactly needs reset vs persists (like tts_client_playing)
            # self.reset_state() # Might clear too much, like user_interrupted prematurely

    def send_final_assistant_answer(self, forced=False):
        """
        Sends the final (or best available) assistant answer to the client.

        Constructs the full answer from quick and final parts if available.
        If `forced` and no full answer exists, uses the last partial answer.
        Cleans the text and sends it as 'final_assistant_answer' if not already sent.

        Args:
            forced: If True, attempts to send the last partial answer if no complete
                    final answer is available. Defaults to False.
        """
        final_answer = ""
        
        # Use per-user speech pipeline manager instead of global
        speech_manager = None
        if self.audio_processor and hasattr(self.audio_processor, 'speech_pipeline_manager'):
            speech_manager = self.audio_processor.speech_pipeline_manager
        else:
            # Fallback to global manager if per-user not available yet
            speech_manager = self.app.state.SpeechPipelineManager
            
        if speech_manager.is_valid_gen():
            final_answer = speech_manager.running_generation.quick_answer + speech_manager.running_generation.final_answer

        if not final_answer: # Check if constructed answer is empty
            # If forced, try using the last known partial answer from this connection
            if forced and self.assistant_answer:
                 final_answer = self.assistant_answer
                 logger.warning(f"🖥️⚠️ Using partial answer as final (forced): '{final_answer}'")
            else:
                logger.warning(f"🖥️⚠️ Final assistant answer was empty, not sending.")
                return# Nothing to send

        logger.debug(f"🖥️✅ Attempting to send final answer: '{final_answer}' (Sent previously: {self.final_assistant_answer_sent})")

        if not self.final_assistant_answer_sent and final_answer:
            import re
            # Clean up the final answer text
            cleaned_answer = re.sub(r'[\r\n]+', ' ', final_answer)
            cleaned_answer = re.sub(r'\s+', ' ', cleaned_answer).strip()
            cleaned_answer = cleaned_answer.replace('\\n', ' ')
            cleaned_answer = re.sub(r'\s+', ' ', cleaned_answer).strip()

            if cleaned_answer: # Ensure it's not empty after cleaning
                logger.info(f"\n{Colors.apply('🖥️✅ FINAL ASSISTANT ANSWER (Sending): ').green}{cleaned_answer}")
                self.message_queue.put_nowait({
                    "type": "final_assistant_answer",
                    "content": cleaned_answer
                })
                # Use per-user speech pipeline manager's history instead of global
                speech_manager.history.append({"role": "assistant", "content": cleaned_answer})
                self.final_assistant_answer_sent = True
                self.final_assistant_answer = cleaned_answer # Store the sent answer
                
                # Trigger immediate GPU stats update after LLM+TTS processing
                asyncio.create_task(self.app.state.SystemMonitor.trigger_immediate_update("LLM+TTS completed"))
            else:
                logger.warning(f"🖥️⚠️ {Colors.YELLOW}Final assistant answer was empty after cleaning.{Colors.RESET}")
                self.final_assistant_answer_sent = False # Don't mark as sent
                self.final_assistant_answer = "" # Clear the stored answer
        elif forced and not final_answer: # Should not happen due to earlier check, but safety
            logger.warning(f"🖥️⚠️ {Colors.YELLOW}Forced send of final assistant answer, but it was empty.{Colors.RESET}")
            self.final_assistant_answer = "" # Clear the stored answer


# --------------------------------------------------------------------
# Main WebSocket endpoint
# --------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    Handles the main WebSocket connection for real-time voice chat.

    Accepts a connection, sets up connection-specific state via `TranscriptionCallbacks`,
    initializes audio/message queues, and creates asyncio tasks for handling
    incoming data, audio processing, outgoing text messages, and outgoing TTS chunks.
    Manages the lifecycle of these tasks and cleans up on disconnect.

    Args:
        ws: The WebSocket connection instance provided by FastAPI.
    """
    # Rate limiting check before accepting connection
    client_host = ws.client.host if ws.client else "unknown"
    if not check_connection_rate_limit(client_host):
        logger.warning(f"🖥️🚫 Connection from {client_host} rate limited")
        await ws.close(code=1008, reason="Rate limit exceeded")
        return
    
    await ws.accept()
    logger.info(f"🖥️✅ Client connected via WebSocket from {client_host}")

    # Create session
    session_id = app.state.SessionManager.create_session(ws)
    
    try:
        message_queue = asyncio.Queue()
        audio_chunks = asyncio.Queue()

        # Set up callback manager - THIS NOW HOLDS THE CONNECTION-SPECIFIC STATE
        callbacks = TranscriptionCallbacks(app, message_queue, session_id)

        # Store session-specific components
        app.state.SessionManager.set_session_component(session_id, "callbacks", callbacks)
        app.state.SessionManager.set_session_component(session_id, "message_queue", message_queue)
        app.state.SessionManager.set_session_component(session_id, "audio_chunks", audio_chunks)
        app.state.SessionManager.set_session_component(session_id, "websocket", ws)

        # Send session info to client
        session_info_msg = {
            "type": "session_info",
            "content": {
                "session_id": session_id,
                "status": "connected"
            }
        }
        await message_queue.put(session_info_msg)

        # Register for system stats updates if available
        if hasattr(app.state, 'SystemStatsStreamer') and app.state.SystemStatsStreamer:
            app.state.SystemStatsStreamer.add_client(ws)
            logger.info("🖥️📊 Client registered for system stats updates")

        # Allocate dedicated AudioInputProcessor instance for this session
        audio_processor = app.state.AudioInputProcessorPool.allocate_instance(session_id)
        if not audio_processor:
            logger.error(f"🖥️💥 Failed to allocate AudioInputProcessor for session {session_id[:8]}")
            await ws.close(code=1013, reason="Server overloaded - no available processors")
            return
        
        # Store the allocated instance in session components and callbacks
        app.state.SessionManager.set_session_component(session_id, "audio_processor", audio_processor)
        callbacks.audio_processor = audio_processor  # Store reference in callbacks
        
        # Assign callbacks to the session-specific AudioInputProcessor
        audio_processor.realtime_callback = callbacks.on_partial
        audio_processor.transcriber.potential_sentence_end = callbacks.on_potential_sentence
        audio_processor.transcriber.on_tts_allowed_to_synthesize = callbacks.on_tts_allowed_to_synthesize
        audio_processor.transcriber.potential_full_transcription_callback = callbacks.on_potential_final
        audio_processor.transcriber.potential_full_transcription_abort_callback = callbacks.on_potential_abort
        audio_processor.transcriber.full_transcription_callback = callbacks.on_final
        audio_processor.transcriber.before_final_sentence = callbacks.on_before_final
        audio_processor.recording_start_callback = callbacks.on_recording_start
        audio_processor.silence_active_callback = callbacks.on_silence_active

        # Assign callback to the per-user SpeechPipelineManager instead of global
        if callbacks.audio_processor and hasattr(callbacks.audio_processor, 'speech_pipeline_manager'):
            callbacks.audio_processor.speech_pipeline_manager.on_partial_assistant_text = callbacks.on_partial_assistant_text
        else:
            # Fallback to global manager if per-user not available yet
            app.state.SpeechPipelineManager.on_partial_assistant_text = callbacks.on_partial_assistant_text

        # Create tasks for handling different responsibilities
        # Pass the 'callbacks' instance to tasks that need connection-specific state
        tasks = [
            asyncio.create_task(process_incoming_data(ws, app, audio_chunks, callbacks, session_id)), # Pass session_id
            asyncio.create_task(audio_processor.process_chunk_queue(audio_chunks)),  # Use session-specific processor
            asyncio.create_task(send_text_messages(ws, message_queue)),
            asyncio.create_task(send_tts_chunks(app, message_queue, callbacks)), # Pass callbacks
        ]

        try:
            # Wait for any task to complete (e.g., client disconnect)
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                if not task.done():
                    task.cancel()
            # Await cancelled tasks to let them clean up if needed
            await asyncio.gather(*pending, return_exceptions=True)
        except Exception as e:
            logger.error(f"🖥️💥 {Colors.apply('ERROR').red} in WebSocket session {session_id[:8]}: {repr(e)}")
        finally:
            logger.info(f"🖥️🧹 Cleaning up WebSocket tasks for session {session_id[:8]}...")
            
            # Unregister from system stats updates
            if hasattr(app.state, 'SystemStatsStreamer') and app.state.SystemStatsStreamer:
                app.state.SystemStatsStreamer.remove_client(ws)
                logger.info("🖥️📊 Client unregistered from system stats updates")
            
            for task in tasks:
                if not task.done():
                    task.cancel()
            # Ensure all tasks are awaited after cancellation
            # Use return_exceptions=True to prevent gather from stopping on first error during cleanup
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"🖥️❌ WebSocket session {session_id[:8]} ended.")
    
    finally:
        # Return AudioInputProcessor instance to pool before session cleanup
        app.state.AudioInputProcessorPool.return_instance(session_id)
        
        # Always clean up session, even if errors occurred
        app.state.SessionManager.remove_session(session_id)

# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------
if __name__ == "__main__":

    # Run the server without SSL
    if not USE_SSL:
        logger.info("🖥️▶️ Starting server without SSL.")
        uvicorn.run("server:app", host="0.0.0.0", port=8000, log_config=None)

    else:
        logger.info("🖥️🔒 Attempting to start server with SSL.")
        # Check if cert files exist
        cert_file = "127.0.0.1+1.pem"
        key_file = "127.0.0.1+1-key.pem"
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
             logger.error(f"🖥️💥 SSL cert file ({cert_file}) or key file ({key_file}) not found.")
             logger.error("🖥️💥 Please generate them using mkcert:")
             logger.error("🖥️💥   choco install mkcert") # Assuming Windows based on earlier check, adjust if needed
             logger.error("🖥️💥   mkcert -install")
             logger.error("🖥️💥   mkcert 127.0.0.1 YOUR_LOCAL_IP") # Remind user to replace with actual IP if needed
             logger.error("🖥️💥 Exiting.")
             sys.exit(1)

        # Run the server with SSL
        logger.info(f"🖥️▶️ Starting server with SSL (cert: {cert_file}, key: {key_file}).")
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=8000,
            log_config=None,
            ssl_certfile=cert_file,
            ssl_keyfile=key_file,
        )
