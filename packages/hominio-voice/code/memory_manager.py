"""
Memory Management Utilities for Voice Chat System

Handles buffer cleanup, queue overflow management, and memory monitoring
to prevent memory leaks in multi-user scenarios.
"""

import logging
import threading
import time
import gc
import queue
import os
from typing import Dict, List, Optional, Any, Callable
from collections import deque
from dataclasses import dataclass

# Optional psutil import for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - memory monitoring will be limited")

logger = logging.getLogger(__name__)

@dataclass
class MemoryStats:
    """Memory usage statistics."""
    rss_mb: float
    vms_mb: float
    percent: float
    available_mb: float
    timestamp: float

class BufferManager:
    """
    Manages buffers with automatic cleanup and size limits.
    Prevents memory leaks from growing audio/text buffers.
    """
    
    def __init__(self, max_size: int = 2000, max_age_seconds: float = 30.0):
        self.max_size = max_size
        self.max_age_seconds = max_age_seconds
        self.buffer: deque = deque()
        self.timestamps: deque = deque()
        self.lock = threading.RLock()
        self._total_size = 0
        
    def add(self, item: Any) -> bool:
        """
        Add item to buffer with automatic cleanup.
        Returns False if buffer is full and item was rejected.
        """
        with self.lock:
            current_time = time.time()
            
            # Clean old items first
            self._cleanup_old_items(current_time)
            
            # Check size limit
            if len(self.buffer) >= self.max_size:
                # logger.warning(f"Buffer at max size ({self.max_size}), dropping oldest item")  # Commented out to reduce log noise
                if self.buffer:
                    self.buffer.popleft()
                    self.timestamps.popleft()
                    
            # Add new item
            self.buffer.append(item)
            self.timestamps.append(current_time)
            
            # Update size tracking
            if hasattr(item, '__len__'):
                self._total_size += len(item)
            else:
                self._total_size += 1
                
            return True
    
    def get_all(self) -> List[Any]:
        """Get all items and clear buffer."""
        with self.lock:
            items = list(self.buffer)
            self.clear()
            return items
    
    def clear(self):
        """Clear all items from buffer."""
        with self.lock:
            self.buffer.clear()
            self.timestamps.clear()
            self._total_size = 0
    
    def _cleanup_old_items(self, current_time: float):
        """Remove items older than max_age_seconds."""
        cutoff_time = current_time - self.max_age_seconds
        
        while self.timestamps and self.timestamps[0] < cutoff_time:
            self.timestamps.popleft()
            old_item = self.buffer.popleft()
            
            # Update size tracking
            if hasattr(old_item, '__len__'):
                self._total_size -= len(old_item)
            else:
                self._total_size -= 1
    
    def size(self) -> int:
        """Get current buffer size."""
        with self.lock:
            return len(self.buffer)
    
    def total_data_size(self) -> int:
        """Get total data size in buffer."""
        with self.lock:
            return self._total_size

class QueueManager:
    """
    Manages queues with overflow protection and automatic cleanup.
    Implements LRU eviction when queues approach capacity limits.
    """
    
    def __init__(self, queue_obj: queue.Queue, max_size: int = 500, 
                 evict_ratio: float = 0.1):
        self.queue = queue_obj
        self.max_size = max_size
        self.evict_count = max(1, int(max_size * evict_ratio))
        self.lock = threading.Lock()
        self.dropped_count = 0
        
    def put_safe(self, item: Any, timeout: Optional[float] = None) -> bool:
        """
        Put item in queue with overflow protection.
        Returns False if item was dropped due to overflow.
        """
        try:
            # Check if queue is approaching limit
            current_size = self.queue.qsize()
            
            if current_size >= self.max_size:
                # Evict old items
                self._evict_old_items()
                
            # Try to put the item
            if timeout is not None:
                self.queue.put(item, timeout=timeout)
            else:
                self.queue.put_nowait(item)
                
            return True
            
        except queue.Full:
            self.dropped_count += 1
            logger.warning(f"Queue full, dropped item. Total dropped: {self.dropped_count}")
            return False
    
    def _evict_old_items(self):
        """Remove old items from queue to make space."""
        evicted = 0
        while evicted < self.evict_count and not self.queue.empty():
            try:
                self.queue.get_nowait()
                evicted += 1
            except queue.Empty:
                break
                
        if evicted > 0:
            logger.debug(f"Evicted {evicted} old items from queue")
    
    def clear(self):
        """Clear all items from queue."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break

class MemoryMonitor:
    """
    Monitors system memory usage and triggers cleanup actions
    when memory usage exceeds thresholds.
    """
    
    def __init__(self, warning_threshold: float = 80.0, 
                 critical_threshold: float = 90.0):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.cleanup_callbacks: List[Callable] = []
        self.stats_history: deque = deque(maxlen=100)
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        
    def add_cleanup_callback(self, callback: Callable):
        """Add callback to be called when memory usage is high."""
        self.cleanup_callbacks.append(callback)
    
    def start_monitoring(self, interval: float = 5.0):
        """Start background memory monitoring."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.shutdown_event.clear()
        
        def monitor_loop():
            while not self.shutdown_event.wait(interval):
                try:
                    stats = self.get_memory_stats()
                    self.stats_history.append(stats)
                    
                    if stats.percent >= self.critical_threshold:
                        logger.error(f"CRITICAL: Memory usage at {stats.percent:.1f}%")
                        self._trigger_cleanup("critical")
                    elif stats.percent >= self.warning_threshold:
                        logger.warning(f"WARNING: Memory usage at {stats.percent:.1f}%")
                        self._trigger_cleanup("warning")
                        
                except Exception as e:
                    logger.error(f"Error in memory monitoring: {e}")
                    
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop background memory monitoring."""
        if not self.monitoring:
            return
            
        self.monitoring = False
        self.shutdown_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
            
        logger.info("Memory monitoring stopped")
    
    def get_memory_stats(self) -> MemoryStats:
        """Get current memory usage statistics."""
        if not PSUTIL_AVAILABLE:
            # Fallback to basic memory info without psutil
            return MemoryStats(
                rss_mb=0.0,
                vms_mb=0.0,
                percent=0.0,
                available_mb=0.0,
                timestamp=time.time()
            )
        
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # System memory
        system_memory = psutil.virtual_memory()
        
        return MemoryStats(
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            percent=memory_percent,
            available_mb=system_memory.available / 1024 / 1024,
            timestamp=time.time()
        )
    
    def _trigger_cleanup(self, level: str):
        """Trigger cleanup callbacks."""
        logger.info(f"Triggering {level} memory cleanup")
        
        # Run callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback(level)
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")
        
        # Force garbage collection
        gc.collect()

class ResourceTracker:
    """
    Tracks resource usage per session/component for debugging leaks.
    """
    
    def __init__(self):
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
    def track_resource(self, session_id: str, resource_type: str, 
                      resource_id: str, data: Any = None):
        """Track a resource allocation."""
        with self.lock:
            if session_id not in self.resources:
                self.resources[session_id] = {}
            if resource_type not in self.resources[session_id]:
                self.resources[session_id][resource_type] = {}
                
            self.resources[session_id][resource_type][resource_id] = {
                'data': data,
                'created_at': time.time(),
                'size': len(data) if hasattr(data, '__len__') else 1
            }
    
    def untrack_resource(self, session_id: str, resource_type: str, resource_id: str):
        """Untrack a resource (when properly cleaned up)."""
        with self.lock:
            try:
                del self.resources[session_id][resource_type][resource_id]
                
                # Clean up empty containers
                if not self.resources[session_id][resource_type]:
                    del self.resources[session_id][resource_type]
                if not self.resources[session_id]:
                    del self.resources[session_id]
                    
            except KeyError:
                pass  # Resource already cleaned up
    
    def get_leaked_resources(self, max_age: float = 300.0) -> Dict[str, Any]:
        """Get resources that might be leaked (old and not cleaned up)."""
        cutoff_time = time.time() - max_age
        leaked = {}
        
        with self.lock:
            for session_id, session_resources in self.resources.items():
                for resource_type, type_resources in session_resources.items():
                    for resource_id, resource_info in type_resources.items():
                        if resource_info['created_at'] < cutoff_time:
                            if session_id not in leaked:
                                leaked[session_id] = {}
                            if resource_type not in leaked[session_id]:
                                leaked[session_id][resource_type] = {}
                            leaked[session_id][resource_type][resource_id] = resource_info
                            
        return leaked
    
    def cleanup_session_resources(self, session_id: str):
        """Clean up all resources for a session."""
        with self.lock:
            if session_id in self.resources:
                del self.resources[session_id]
                logger.info(f"Cleaned up all tracked resources for session {session_id}")

# Global instances
_memory_monitor = MemoryMonitor()
_resource_tracker = ResourceTracker()

def get_memory_monitor() -> MemoryMonitor:
    """Get global memory monitor instance."""
    return _memory_monitor

def get_resource_tracker() -> ResourceTracker:
    """Get global resource tracker instance."""
    return _resource_tracker

def cleanup_memory():
    """Force memory cleanup - can be called manually or by monitor."""
    logger.info("Performing manual memory cleanup")
    
    # Force garbage collection
    gc.collect()
    
    # Try to clear Python caches
    try:
        import sys
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
    except:
        pass
    
    logger.info("Memory cleanup completed") 