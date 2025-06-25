# session_state.py
import time
from enum import Enum
from typing import Optional, Any, Dict
from dataclasses import dataclass, field

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
    
    # Connection info
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