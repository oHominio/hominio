# session_manager.py
import uuid
import time
import logging
import asyncio
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from threading import Lock
from enum import Enum

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Enumeration of possible session states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    IDLE = "idle"
    DISCONNECTED = "disconnected"
    INACTIVE = "inactive"

@dataclass
class SessionState:
    """Tracks the current state and activity of a session."""
    session_id: str
    status: SessionStatus = SessionStatus.CONNECTING
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    last_status_change: float = field(default_factory=time.time)
    
    # Activity counters
    messages_sent: int = 0
    messages_received: int = 0
    audio_chunks_processed: int = 0
    tts_chunks_sent: int = 0
    
    # Current activity
    is_recording: bool = False
    is_speaking: bool = False
    is_processing: bool = False
    is_active: bool = True
    
    # Connection info
    websocket: Optional[Any] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    def update_status(self, new_status: SessionStatus):
        """Update the session status and timestamp."""
        if self.status != new_status:
            self.status = new_status
            self.last_status_change = time.time()
            self.last_activity = time.time()
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = time.time()
    
    def increment_message_sent(self):
        """Increment sent message counter."""
        self.messages_sent += 1
        self.update_activity()
    
    def increment_message_received(self):
        """Increment received message counter."""
        self.messages_received += 1
        self.update_activity()
    
    def increment_audio_chunk(self):
        """Increment audio chunk counter."""
        self.audio_chunks_processed += 1
        self.update_activity()
    
    def increment_tts_chunk(self):
        """Increment TTS chunk counter."""
        self.tts_chunks_sent += 1
        self.update_activity()
    
    def set_recording(self, is_recording: bool):
        """Set recording state."""
        self.is_recording = is_recording
        if is_recording:
            self.update_status(SessionStatus.LISTENING)
        self.update_activity()
    
    def set_speaking(self, is_speaking: bool):
        """Set speaking state."""
        self.is_speaking = is_speaking
        if is_speaking:
            self.update_status(SessionStatus.SPEAKING)
        elif self.status == SessionStatus.SPEAKING:
            self.update_status(SessionStatus.IDLE)
        self.update_activity()
    
    def set_processing(self, is_processing: bool):
        """Set processing state."""
        self.is_processing = is_processing
        if is_processing:
            self.update_status(SessionStatus.PROCESSING)
        self.update_activity()
    
    def get_duration_seconds(self) -> float:
        """Get session duration in seconds."""
        return time.time() - self.created_at
    
    def get_idle_seconds(self) -> float:
        """Get seconds since last activity."""
        return time.time() - self.last_activity
    
    def get_status_duration_seconds(self) -> float:
        """Get seconds since last status change."""
        return time.time() - self.last_status_change
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "last_status_change": self.last_status_change,
            "duration_seconds": self.get_duration_seconds(),
            "idle_seconds": self.get_idle_seconds(),
            "status_duration_seconds": self.get_status_duration_seconds(),
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "audio_chunks_processed": self.audio_chunks_processed,
            "tts_chunks_sent": self.tts_chunks_sent,
            "is_recording": self.is_recording,
            "is_speaking": self.is_speaking,
            "is_processing": self.is_processing,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address
        }

class SessionManager:
    """
    Manages individual user sessions for multi-user voice chat.
    
    Provides session lifecycle management, health monitoring, and automatic cleanup
    while maintaining thread safety for concurrent access.
    """
    
    def __init__(self, session_timeout: float = 3600.0, cleanup_interval: float = 300.0):
        """
        Initialize the SessionManager.
        
        Args:
            session_timeout: Session timeout in seconds (default: 1 hour)
            cleanup_interval: Cleanup check interval in seconds (default: 5 minutes)
        """
        self.session_timeout = session_timeout
        self.cleanup_interval = cleanup_interval
        self.sessions: Dict[str, SessionState] = {}
        self.session_components: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown = False
        
        logger.info(f"🏢 SessionManager initialized (timeout: {session_timeout}s, cleanup: {cleanup_interval}s)")
    
    def create_session(self, websocket: Any, user_agent: Optional[str] = None, 
                      ip_address: Optional[str] = None) -> str:
        """
        Create a new session for a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection object
            user_agent: Optional user agent string
            ip_address: Optional client IP address
            
        Returns:
            Unique session ID string
        """
        session_id = str(uuid.uuid4())
        
        with self._lock:
            # Create session state with all necessary info
            session_state = SessionState(
                session_id=session_id,
                websocket=websocket,
                user_agent=user_agent,
                ip_address=ip_address
            )
            session_state.update_status(SessionStatus.CONNECTED)
            
            self.sessions[session_id] = session_state
            self.session_components[session_id] = {}
            
        logger.debug(f"🏢✨ Created session {session_id[:8]} (Total sessions: {len(self.sessions)})")
        
        # Broadcast update (async)
        try:
            asyncio.create_task(self.broadcast_session_update())
        except RuntimeError:
            # No event loop running, skip broadcast
            pass
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state by ID."""
        with self._lock:
            return self.sessions.get(session_id)
    
    def update_activity(self, session_id: str):
        """Update the last activity timestamp for a session."""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].update_activity()
        
        # Broadcast update (async)
        try:
            asyncio.create_task(self.broadcast_session_update())
        except RuntimeError:
            # No event loop running, skip broadcast
            pass
    
    def set_session_component(self, session_id: str, component_name: str, component: Any):
        """Store a component (like SpeechPipelineManager) for a session."""
        with self._lock:
            if session_id in self.session_components:
                self.session_components[session_id][component_name] = component
                logger.debug(f"🏢🔧 Set {component_name} for session {session_id[:8]}")
    
    def get_session_component(self, session_id: str, component_name: str) -> Optional[Any]:
        """Retrieve a component for a session."""
        with self._lock:
            return self.session_components.get(session_id, {}).get(component_name)
    
    async def remove_session(self, session_id: str) -> bool:
        """
        Remove a session and clean up all its associated components.
        
        This method is now a coroutine to handle async cleanup.
        """
        with self._lock:
            session_state = self.sessions.pop(session_id, None)
            components = self.session_components.pop(session_id, {})
            
        if session_state is None:
            logger.warning(f"🏢⚠️ Attempted to remove non-existent session {session_id[:8]}")
            return False
        
        # Cleanup session components
        await self._cleanup_session_components(session_id, components)
        
        session_duration = session_state.get_duration_seconds()
        logger.debug(f"🏢🗑️ Removed session {session_id[:8]} (Duration: {session_duration:.1f}s, Total sessions: {len(self.sessions)})")
        
        # Broadcast update (async)
        try:
            asyncio.create_task(self.broadcast_session_update())
        except RuntimeError:
            # No event loop running, skip broadcast
            pass
        
        return True
    
    async def _cleanup_session_components(self, session_id: str, components: Dict[str, Any]):
        """Clean up components for a session."""
        for component_name, component in components.items():
            try:
                # Try to shutdown component if it has a shutdown method
                if hasattr(component, 'shutdown'):
                    logger.debug(f"🏢🧹 Shutting down {component_name} for session {session_id[:8]}")
                    component.shutdown()
                elif hasattr(component, 'close') and asyncio.iscoroutinefunction(component.close):
                    logger.debug(f"🏢🧹 Closing {component_name} for session {session_id[:8]}")
                    await component.close()
                elif hasattr(component, 'close'):
                    logger.debug(f"🏢🧹 Closing {component_name} for session {session_id[:8]} (sync)")
                    component.close()
            except Exception as e:
                logger.error(f"🏢💥 Error cleaning up {component_name} for session {session_id[:8]}: {e}")
    
    def get_active_session_count(self) -> int:
        """Get the number of active sessions."""
        with self._lock:
            return len([s for s in self.sessions.values() if s.is_active])
    
    def get_all_session_ids(self) -> List[str]:
        """Get all session IDs."""
        with self._lock:
            return list(self.sessions.keys())
    
    def mark_session_inactive(self, session_id: str):
        """Mark a session as inactive but don't remove it yet."""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].is_active = False
                logger.debug(f"🏢⏸️ Marked session {session_id[:8]} as inactive")
    
    async def start_cleanup_task(self):
        """Start the automatic cleanup task."""
        if self._cleanup_task is not None:
            return
        
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("🏢🧹 Started session cleanup task")
    
    async def stop_cleanup_task(self):
        """Stop the automatic cleanup task."""
        if self._cleanup_task:
            self._shutdown = True
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("🏢🛑 Stopped session cleanup task")
    
    async def _cleanup_loop(self):
        """Main cleanup loop that runs periodically."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"🏢💥 Error in cleanup loop: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = time.time()
        expired_sessions = []
        
        with self._lock:
            for session_id, session_state in self.sessions.items():
                if (not session_state.is_active and 
                    current_time - session_state.last_activity > self.session_timeout):
                    expired_sessions.append(session_id)
        
        if expired_sessions:
            logger.info(f"🏢🧹 Cleaning up {len(expired_sessions)} expired sessions")
            for session_id in expired_sessions:
                await self.remove_session(session_id)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get detailed statistics about current sessions."""
        with self._lock:
            current_time = time.time()
            active_count = sum(1 for s in self.sessions.values() if s.is_active)
            total_count = len(self.sessions)
            
            if total_count > 0:
                avg_duration = sum(s.get_duration_seconds() for s in self.sessions.values()) / total_count
                oldest_session = min(s.created_at for s in self.sessions.values())
                newest_session = max(s.created_at for s in self.sessions.values())
            else:
                avg_duration = 0
                oldest_session = current_time
                newest_session = current_time
            
            # Get detailed session list
            detailed_sessions = [session_state.to_dict() for session_state in self.sessions.values()]
            
            return {
                "total_sessions": total_count,
                "active_sessions": active_count,
                "inactive_sessions": total_count - active_count,
                "average_duration_seconds": avg_duration,
                "oldest_session_age_seconds": current_time - oldest_session,
                "newest_session_age_seconds": current_time - newest_session,
                "sessions": detailed_sessions
            }

    def get_session_state(self, session_id: str) -> Optional[SessionState]:
        """Get the session state for a specific session."""
        with self._lock:
            return self.sessions.get(session_id)

    def update_session_status(self, session_id: str, status: SessionStatus):
        """Update the status of a session."""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].update_status(status)
        
        # Broadcast update (async)
        try:
            asyncio.create_task(self.broadcast_session_update())
        except RuntimeError:
            # No event loop running, skip broadcast
            pass
    
    async def broadcast_session_update(self):
        """Broadcast session statistics to all connected clients."""
        stats = self.get_session_stats()
        update_message = {
            "type": "session_stats",
            "content": stats
        }
        
        # Get all active WebSocket connections
        websockets_to_remove = []
        with self._lock:
            for session_id, components in self.session_components.items():
                websocket = components.get("websocket")
                message_queue = components.get("message_queue")
                if websocket and message_queue:
                    try:
                        # Put the update in the message queue (non-blocking)
                        if hasattr(message_queue, 'put_nowait'):
                            message_queue.put_nowait(update_message)
                        else:
                            # For asyncio queues
                            asyncio.create_task(message_queue.put(update_message))
                    except Exception as e:
                        logger.warning(f"🏢⚠️ Failed to send session update to {session_id[:8]}: {e}")
                        websockets_to_remove.append(session_id)
        
        # Clean up dead connections
        for session_id in websockets_to_remove:
            self.mark_session_inactive(session_id)

    async def shutdown(self):
        """Shutdown the session manager and clean up all sessions."""
        logger.info("🏢🔌 Shutting down SessionManager...")
        
        await self.stop_cleanup_task()
        
        # Get all session IDs to clean up
        session_ids = self.get_all_session_ids()
        
        # Clean up all sessions
        for session_id in session_ids:
            await self.remove_session(session_id)
        
        logger.info("🏢✅ SessionManager shutdown complete") 