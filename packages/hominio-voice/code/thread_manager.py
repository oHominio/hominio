"""
Thread Management Utilities for Voice Chat System

Handles proper thread lifecycle, cleanup, and monitoring to prevent
zombie threads and resource leaks in multi-user scenarios.
"""

import logging
import threading
import time
import signal
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ThreadState(Enum):
    """Thread lifecycle states."""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    ZOMBIE = "zombie"

@dataclass
class ThreadInfo:
    """Information about a managed thread."""
    thread: threading.Thread
    name: str
    state: ThreadState
    created_at: float
    started_at: Optional[float] = None
    stopped_at: Optional[float] = None
    shutdown_event: Optional[threading.Event] = None
    cleanup_callback: Optional[Callable] = None
    force_timeout: float = 10.0

class ManagedThread:
    """
    A thread wrapper that ensures proper lifecycle management and cleanup.
    """
    
    def __init__(self, target: Callable, name: str, args: tuple = (), 
                 kwargs: dict = None, shutdown_event: threading.Event = None,
                 cleanup_callback: Callable = None, force_timeout: float = 10.0,
                 daemon: bool = True):
        self.target = target
        self.name = name
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.shutdown_event = shutdown_event or threading.Event()
        self.cleanup_callback = cleanup_callback
        self.force_timeout = force_timeout
        
        # Create the actual thread
        self.thread = threading.Thread(
            target=self._wrapped_target,
            name=name,
            daemon=daemon
        )
        
        self.info = ThreadInfo(
            thread=self.thread,
            name=name,
            state=ThreadState.CREATED,
            created_at=time.time(),
            shutdown_event=self.shutdown_event,
            cleanup_callback=cleanup_callback,
            force_timeout=force_timeout
        )
        
        self._started = False
        self._exception: Optional[Exception] = None
    
    def _wrapped_target(self):
        """Wrapper that handles thread lifecycle and cleanup."""
        try:
            self.info.state = ThreadState.RUNNING
            self.info.started_at = time.time()
            logger.debug(f"Thread {self.name} starting")
            
            # Run the actual target function
            self.target(*self.args, **self.kwargs)
            
            self.info.state = ThreadState.STOPPED
            logger.debug(f"Thread {self.name} completed normally")
            
        except Exception as e:
            self._exception = e
            self.info.state = ThreadState.FAILED
            logger.error(f"Thread {self.name} failed with exception: {e}", exc_info=True)
            
        finally:
            self.info.stopped_at = time.time()
            
            # Run cleanup callback if provided
            if self.cleanup_callback:
                try:
                    self.cleanup_callback()
                    logger.debug(f"Cleanup callback completed for thread {self.name}")
                except Exception as e:
                    logger.error(f"Cleanup callback failed for thread {self.name}: {e}")
    
    def start(self):
        """Start the thread."""
        if self._started:
            raise RuntimeError(f"Thread {self.name} already started")
            
        self.info.state = ThreadState.STARTING
        self.thread.start()
        self._started = True
        logger.debug(f"Thread {self.name} started")
    
    def stop(self, timeout: Optional[float] = None) -> bool:
        """
        Stop the thread gracefully.
        Returns True if stopped successfully, False if forced termination needed.
        """
        if not self._started or not self.thread.is_alive():
            return True
        
        logger.debug(f"Stopping thread {self.name}")
        self.info.state = ThreadState.STOPPING
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for graceful shutdown
        join_timeout = timeout or self.force_timeout
        self.thread.join(timeout=join_timeout)
        
        if self.thread.is_alive():
            logger.warning(f"Thread {self.name} did not stop gracefully within {join_timeout}s")
            self.info.state = ThreadState.ZOMBIE
            return False
        else:
            logger.debug(f"Thread {self.name} stopped gracefully")
            return True
    
    def force_stop(self):
        """
        Force stop the thread (this is platform-specific and may not work).
        Should only be used as a last resort.
        """
        if not self.thread.is_alive():
            return
        
        logger.warning(f"Force stopping zombie thread {self.name}")
        
        # This is a dangerous operation and may not work on all platforms
        try:
            # Try to interrupt the thread (Python doesn't have built-in thread termination)
            # This is more of a documentation of the attempt than a real solution
            # In practice, zombie threads will be cleaned up when the process exits
            pass
        except Exception as e:
            logger.error(f"Failed to force stop thread {self.name}: {e}")
    
    @property
    def is_alive(self) -> bool:
        """Check if thread is alive."""
        return self.thread.is_alive() if self.thread else False
    
    @property
    def exception(self) -> Optional[Exception]:
        """Get exception that caused thread to fail."""
        return self._exception

class ThreadManager:
    """
    Manages a collection of threads with automatic cleanup and monitoring.
    """
    
    def __init__(self, max_zombie_age: float = 60.0):
        self.threads: Dict[str, ManagedThread] = {}
        self.lock = threading.RLock()
        self.max_zombie_age = max_zombie_age
        
        # Background cleanup
        self.cleanup_interval = 30.0
        self.cleanup_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        
    def create_thread(self, target: Callable, name: str, args: tuple = (),
                     kwargs: dict = None, shutdown_event: threading.Event = None,
                     cleanup_callback: Callable = None, force_timeout: float = 10.0,
                     daemon: bool = True, auto_start: bool = True) -> ManagedThread:
        """
        Create and optionally start a managed thread.
        """
        with self.lock:
            # Ensure unique name
            base_name = name
            counter = 1
            while name in self.threads:
                name = f"{base_name}_{counter}"
                counter += 1
            
            # Create managed thread
            managed_thread = ManagedThread(
                target=target,
                name=name,
                args=args,
                kwargs=kwargs,
                shutdown_event=shutdown_event,
                cleanup_callback=cleanup_callback,
                force_timeout=force_timeout,
                daemon=daemon
            )
            
            self.threads[name] = managed_thread
            
            if auto_start:
                managed_thread.start()
            
            logger.debug(f"Created managed thread: {name}")
            return managed_thread
    
    def stop_thread(self, name: str, timeout: Optional[float] = None) -> bool:
        """Stop a specific thread by name."""
        with self.lock:
            if name not in self.threads:
                logger.warning(f"Thread {name} not found")
                return True
            
            thread = self.threads[name]
            return thread.stop(timeout)
    
    def stop_all(self, timeout: Optional[float] = None) -> Dict[str, bool]:
        """
        Stop all managed threads.
        Returns dict of thread_name -> success_status.
        """
        results = {}
        
        with self.lock:
            thread_names = list(self.threads.keys())
        
        for name in thread_names:
            success = self.stop_thread(name, timeout)
            results[name] = success
            
        return results
    
    def cleanup_stopped_threads(self):
        """Remove stopped threads from management."""
        with self.lock:
            to_remove = []
            for name, thread in self.threads.items():
                if not thread.is_alive and thread.info.state in [
                    ThreadState.STOPPED, ThreadState.FAILED
                ]:
                    to_remove.append(name)
            
            for name in to_remove:
                del self.threads[name]
                logger.debug(f"Cleaned up stopped thread: {name}")
    
    def get_zombie_threads(self) -> List[ManagedThread]:
        """Get threads that are zombies (didn't stop gracefully)."""
        zombies = []
        current_time = time.time()
        
        with self.lock:
            for thread in self.threads.values():
                if (thread.info.state == ThreadState.ZOMBIE and 
                    thread.info.stopped_at and
                    current_time - thread.info.stopped_at > self.max_zombie_age):
                    zombies.append(thread)
        
        return zombies
    
    def force_cleanup_zombies(self):
        """Force cleanup of zombie threads."""
        zombies = self.get_zombie_threads()
        
        for zombie in zombies:
            logger.warning(f"Force cleaning up zombie thread: {zombie.name}")
            zombie.force_stop()
            
            # Remove from management
            with self.lock:
                if zombie.name in self.threads:
                    del self.threads[zombie.name]
    
    def get_thread_stats(self) -> Dict[str, Any]:
        """Get statistics about managed threads."""
        with self.lock:
            total = len(self.threads)
            by_state = {}
            
            for thread in self.threads.values():
                state = thread.info.state.value
                by_state[state] = by_state.get(state, 0) + 1
            
            alive_count = sum(1 for t in self.threads.values() if t.is_alive)
            
        return {
            'total': total,
            'alive': alive_count,
            'by_state': by_state,
            'zombie_count': by_state.get(ThreadState.ZOMBIE.value, 0)
        }
    
    def start_monitoring(self):
        """Start background thread monitoring and cleanup."""
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            return
        
        def monitor_loop():
            while not self.shutdown_event.wait(self.cleanup_interval):
                try:
                    # Clean up stopped threads
                    self.cleanup_stopped_threads()
                    
                    # Force cleanup zombies if they're too old
                    self.force_cleanup_zombies()
                    
                    # Log stats periodically
                    stats = self.get_thread_stats()
                    if stats['total'] > 0:
                        logger.debug(f"Thread stats: {stats}")
                        
                except Exception as e:
                    logger.error(f"Error in thread monitoring: {e}")
        
        self.cleanup_thread = threading.Thread(
            target=monitor_loop,
            name="ThreadManager_Monitor",
            daemon=True
        )
        self.cleanup_thread.start()
        logger.info("Thread monitoring started")
    
    def stop_monitoring(self):
        """Stop background thread monitoring."""
        self.shutdown_event.set()
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5.0)
            
        logger.info("Thread monitoring stopped")
    
    def shutdown(self, timeout: float = 10.0):
        """Shutdown the thread manager and all managed threads."""
        logger.info("Shutting down thread manager")
        
        # Stop monitoring first
        self.stop_monitoring()
        
        # Stop all managed threads
        results = self.stop_all(timeout)
        
        # Log any failures
        failed_threads = [name for name, success in results.items() if not success]
        if failed_threads:
            logger.warning(f"Failed to stop threads gracefully: {failed_threads}")
            
            # Force cleanup zombies
            self.force_cleanup_zombies()
        
        logger.info("Thread manager shutdown complete")

# Global thread manager instance
_global_thread_manager = ThreadManager()

def get_thread_manager() -> ThreadManager:
    """Get the global thread manager instance."""
    return _global_thread_manager

def create_managed_thread(target: Callable, name: str, **kwargs) -> ManagedThread:
    """Create a managed thread using the global manager."""
    return _global_thread_manager.create_thread(target, name, **kwargs)

def shutdown_all_threads(timeout: float = 10.0):
    """Shutdown all managed threads."""
    _global_thread_manager.shutdown(timeout) 