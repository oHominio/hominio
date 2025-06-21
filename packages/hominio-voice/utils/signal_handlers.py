"""
Signal handling utilities for graceful shutdown
"""
import signal
import sys
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class SignalHandler:
    """Handles application signals for graceful shutdown"""
    
    def __init__(self):
        self.shutdown_callbacks = []
        self.setup_signal_handlers()
    
    def add_shutdown_callback(self, callback: Callable):
        """Add a callback to be called on shutdown"""
        self.shutdown_callbacks.append(callback)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            signal.signal(signal.SIGABRT, self._signal_handler)
        except:
            # SIGABRT may not be available on all systems
            pass
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        
        # Call all shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in shutdown callback: {e}")
        
        sys.exit(0)


# Global signal handler instance
signal_handler = SignalHandler() 