# session_manager.py
import uuid
import time
import logging
import asyncio
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from threading import Lock
from session_state import SessionState, SessionStatus

logger = logging.getLogger(__name__)

@dataclass
class SessionInfo:
    """Holds metadata and state for an individual user session."""
    session_id: str
    created_at: float
    last_activity: float
    websocket: Any  # WebSocket connection
    is_active: bool = True
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

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
        self.sessions: Dict[str, SessionInfo] = {}
        self.session_states: Dict[str, SessionState] = {}
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
        current_time = time.time()
        
        with self._lock:
            session_info = SessionInfo(
                session_id=session_id,
                created_at=current_time,
                last_activity=current_time,
                websocket=websocket,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            self.sessions[session_id] = session_info
            self.session_components[session_id] = {}
            
            # Create session state tracking
            session_state = SessionState(
                session_id=session_id,
                user_agent=user_agent,
                ip_address=ip_address
            )
            session_state.update_status(SessionStatus.CONNECTED)
            self.session_states[session_id] = session_state
            
        logger.debug(f"🏢✨ Created session {session_id[:8]} (Total sessions: {len(self.sessions)})")
        
        # Broadcast update (async)
        import asyncio
        try:
            asyncio.create_task(self.broadcast_session_update())
        except RuntimeError:
            # No event loop running, skip broadcast
            pass
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session info by ID."""
        with self._lock:
            return self.sessions.get(session_id)
    
    def update_activity(self, session_id: str):
        """Update the last activity timestamp for a session."""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].last_activity = time.time()
            if session_id in self.session_states:
                self.session_states[session_id].update_activity()
        
        # Broadcast update (async)
        import asyncio
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
            session_info = self.sessions.pop(session_id, None)
            session_state = self.session_states.pop(session_id, None)
            components = self.session_components.pop(session_id, {})
            
        if session_info is None:
            logger.warning(f"🏢⚠️ Attempted to remove non-existent session {session_id[:8]}")
            return False
        
        # Cleanup session components
        await self._cleanup_session_components(session_id, components)
        
        session_duration = time.time() - session_info.created_at
        logger.debug(f"🏢🗑️ Removed session {session_id[:8]} (Duration: {session_duration:.1f}s, Total sessions: {len(self.sessions)})")
        
        # Broadcast update (async)
        import asyncio
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
    
    def get_all_session_ids(self) -> list[str]:
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
            for session_id, session_info in self.sessions.items():
                if (not session_info.is_active and 
                    current_time - session_info.last_activity > self.session_timeout):
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
                avg_duration = sum(current_time - s.created_at for s in self.sessions.values()) / total_count
                oldest_session = min(s.created_at for s in self.sessions.values())
                newest_session = max(s.created_at for s in self.sessions.values())
            else:
                avg_duration = 0
                oldest_session = current_time
                newest_session = current_time
            
            # Get detailed session list
            detailed_sessions = []
            for session_id, session_state in self.session_states.items():
                if session_id in self.sessions:  # Only active sessions
                    detailed_sessions.append(session_state.to_dict())
            
            return {
                "total_sessions": total_count,
                "active_sessions": active_count,
                "inactive_sessions": total_count - active_count,
                "average_duration_seconds": avg_duration,
                "oldest_session_age_seconds": current_time - oldest_session,
                "newest_session_age_seconds": current_time - newest_session,
                "sessions": detailed_sessions  # Add detailed session list
            }

    def get_session_state(self, session_id: str) -> Optional[SessionState]:
        """Get the session state for a specific session."""
        with self._lock:
            return self.session_states.get(session_id)

    def update_session_status(self, session_id: str, status: SessionStatus):
        """Update the status of a session."""
        with self._lock:
            if session_id in self.session_states:
                self.session_states[session_id].update_status(status)
        
        # Broadcast update (async) - keeping original logic
        import asyncio
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
                            import asyncio
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