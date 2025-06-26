"""
AudioInputProcessor Pool Management for Multi-User Concurrency

This module provides the AudioInputProcessorPool class that manages a pool of
AudioInputProcessor instances, enabling multiple concurrent users to each get
their own dedicated STT processing pipeline.
"""

import asyncio
import logging
import threading
import time
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
from queue import Queue

from audio_in import AudioInputProcessor
from memory_manager import get_resource_tracker
from thread_manager import create_managed_thread

logger = logging.getLogger(__name__)

# Global cache for pre-warmed STT models to prevent CUDA conflicts
_STT_MODEL_CACHE = {}

class InstanceState(Enum):
    """State of a pool instance."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    INITIALIZING = "initializing"
    FAILED = "failed"
    SHUTTING_DOWN = "shutting_down"

@dataclass
class PoolInstance:
    """Information about a pooled AudioInputProcessor instance."""
    instance: Optional[AudioInputProcessor]
    state: InstanceState
    session_id: Optional[str] = None
    allocated_at: Optional[float] = None
    last_activity: Optional[float] = None
    failure_count: int = 0
    instance_id: str = ""

class AudioInputProcessorPool:
    """
    Manages a pool of AudioInputProcessor instances for multi-user concurrency.
    
    This pool provides dedicated AudioInputProcessor instances to sessions,
    ensuring complete isolation between users while maximizing resource
    utilization through reuse.
    """
    
    def __init__(
        self,
        initial_size: int = 3,
        max_size: int = 50,
        max_idle_time: float = 300.0,  # 5 minutes
        health_check_interval: float = 60.0,  # 1 minute
        language: str = "en",
        is_orpheus: bool = False,
        pipeline_latency: float = 0.5,
    ):
        """
        Initialize the AudioInputProcessor pool.
        
        Args:
            initial_size: Number of instances to create initially
            max_size: Maximum number of instances in the pool
            max_idle_time: Maximum time an instance can be idle before cleanup
            health_check_interval: Interval between health checks
            language: Default language for AudioInputProcessor instances
            is_orpheus: Default Orpheus flag for instances
            pipeline_latency: Default pipeline latency for instances
        """
        self.initial_size = initial_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval
        
        # Default parameters for AudioInputProcessor creation
        self.default_params = {
            'language': language,
            'is_orpheus': is_orpheus,
            'pipeline_latency': pipeline_latency,
        }
        
        # Pool management
        self.instances: Dict[str, PoolInstance] = {}
        self.allocation_queue: List[str] = []  # Queue for waiting sessions
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'total_allocations': 0,
            'total_returns': 0,
            'failed_allocations': 0,
            'current_allocated': 0,
            'peak_allocated': 0,
            'average_session_duration': 0.0,
        }
        
        # Resource tracking
        self.resource_tracker = get_resource_tracker()
        self.resource_tracker.track_resource("global", "AudioInputProcessorPool", f"pool_{id(self)}")
        
        # Health monitoring
        self.shutdown_event = threading.Event()
        self.health_monitor_thread: Optional[threading.Thread] = None
        
        # Initialize the pool
        self._initialize_pool()
        self._start_health_monitor()
        
        logger.debug(f"🏊‍♂️ AudioInputProcessorPool initialized with {initial_size} instances (max: {max_size})")
    
    def _initialize_pool(self) -> None:
        """Initialize the pool with the specified number of instances."""
        logger.info(f"🏊‍♂️🔧 Initializing pool with {self.initial_size} instances...")
        
        # Pre-warm Silero VAD cache to prevent race conditions
        if not _prewarm_silero_cache():
            logger.error("🏊‍♂️💥 Failed to pre-warm Silero VAD cache - instances may fail to initialize")
        
        # Pre-warm TurnDetection model to prevent CUDA conflicts
        logger.info("🏊‍♂️🔥 Pre-warming TurnDetection model...")
        try:
            from turndetect import TurnDetection
            # Trigger model loading by calling the class method
            TurnDetection._ensure_model_loaded(local=True)
            logger.info("🏊‍♂️✅ TurnDetection model pre-warmed successfully")
        except Exception as e:
            logger.error(f"🏊‍♂️💥 Failed to pre-warm TurnDetection model: {e}")
        
        # Pre-warm STT Whisper models to prevent CUDA conflicts
        logger.info("🏊‍♂️🔥 Pre-warming STT Whisper models...")
        try:
            import torch
            from faster_whisper import WhisperModel
            
            # Pre-load the main STT model (same as used in transcribe.py)
            logger.info("🏊‍♂️🔥 Loading main Whisper model (base.en)...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "default"
            
            main_model = WhisperModel(
                model_size_or_path="base.en",
                device=device,
                compute_type=compute_type
            )
            
            # Since both main and realtime use the same model, share the reference
            logger.info("🏊‍♂️✅ STT model pre-warmed (base.en), sharing between main and realtime")
            
            # Store references to prevent garbage collection
            _STT_MODEL_CACHE['shared_model'] = main_model
            _STT_MODEL_CACHE['device'] = device
            _STT_MODEL_CACHE['compute_type'] = compute_type
            
            # Perform a quick warmup inference to ensure model is ready
            import numpy as np
            warmup_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
            segments, info = main_model.transcribe(warmup_audio, language="en", beam_size=1)
            list(segments)  # Consume generator to complete warmup
            
            logger.info("🏊‍♂️✅ STT Whisper model pre-warmed and tested successfully")
        except Exception as e:
            logger.error(f"🏊‍♂️💥 Failed to pre-warm STT models: {e}")
            import traceback
            logger.error(f"🏊‍♂️💥 STT pre-warming traceback: {traceback.format_exc()}")
        
        # Create instances sequentially to avoid any remaining race conditions
        for i in range(self.initial_size):
            instance_id = f"instance_{i}_{int(time.time())}"
            pool_instance = PoolInstance(
                instance=None,
                state=InstanceState.INITIALIZING,
                instance_id=instance_id
            )
            self.instances[instance_id] = pool_instance
            
            # Create instance in background thread with health validation
            create_managed_thread(
                target=self._create_and_validate_instance_async,
                args=(instance_id,),
                name=f"PoolInstanceCreator_{instance_id}",
                daemon=True
            )
        
        logger.debug(f"🏊‍♂️✅ Pool initialization started for {self.initial_size} instances")
    
    def _create_and_validate_instance_async(self, instance_id: str) -> None:
        """Create an AudioInputProcessor instance and validate its health."""
        try:
            # Debug logging removed to reduce noise
            
            # Add small delay for any remaining timing issues
            import random
            delay = random.uniform(0.1, 0.3)  # Reduced delay since cache is pre-warmed
            # Debug timing log removed to reduce noise
            time.sleep(delay)
            
            # Create the AudioInputProcessor instance
            instance = AudioInputProcessor(**self.default_params)
            
            # Validate that the instance is healthy (has working recorder)
            if not self._validate_instance_health(instance):
                logger.error(f"🏊‍♂️💥 Instance {instance_id} failed health validation")
                with self.lock:
                    if instance_id in self.instances:
                        self.instances[instance_id].state = InstanceState.FAILED
                        self.instances[instance_id].failure_count += 1
                # Shut down the unhealthy instance
                if hasattr(instance, 'shutdown'):
                    instance.shutdown()
                return
            
            with self.lock:
                if instance_id in self.instances:
                    self.instances[instance_id].instance = instance
                    self.instances[instance_id].state = InstanceState.AVAILABLE
                    self.instances[instance_id].last_activity = time.time()
                    logger.info(f"🏊‍♂️✅ Instance {instance_id} created and validated successfully")
                else:
                    # Instance was removed while we were creating it
                    logger.warning(f"🏊‍♂️⚠️ Instance {instance_id} was removed during creation, shutting down")
                    if hasattr(instance, 'shutdown'):
                        instance.shutdown()
                    
        except Exception as e:
            logger.error(f"🏊‍♂️💥 Failed to create instance {instance_id}: {e}", exc_info=True)
            with self.lock:
                if instance_id in self.instances:
                    self.instances[instance_id].state = InstanceState.FAILED
                    self.instances[instance_id].failure_count += 1
    
    def _validate_instance_health(self, instance: AudioInputProcessor) -> bool:
        """
        Validate that an AudioInputProcessor instance is healthy and ready to use.
        
        Args:
            instance: The AudioInputProcessor instance to validate
            
        Returns:
            True if instance is healthy, False otherwise
        """
        try:
            # Check that the instance has a transcriber
            if not hasattr(instance, 'transcriber') or instance.transcriber is None:
                logger.error("🏊‍♂️❌ Instance validation failed: No transcriber")
                return False
            
            # Check that the transcriber has a recorder
            if not hasattr(instance.transcriber, 'recorder') or instance.transcriber.recorder is None:
                logger.error("🏊‍♂️❌ Instance validation failed: No recorder in transcriber")
                return False
            
            logger.debug("🏊‍♂️✅ Instance passed health validation")
            return True
            
        except Exception as e:
            logger.error(f"🏊‍♂️❌ Instance validation error: {e}")
            return False
    
    def allocate_instance(
        self,
        session_id: str,
        **kwargs
    ) -> Optional[AudioInputProcessor]:
        """
        Allocate an AudioInputProcessor instance to a session.
        
        Args:
            session_id: Unique identifier for the session
            **kwargs: Additional parameters to override defaults
            
        Returns:
            AudioInputProcessor instance or None if allocation failed
        """
        with self.lock:
            # Check if session already has an instance
            for pool_instance in self.instances.values():
                if pool_instance.session_id == session_id:
                    logger.warning(f"🏊‍♂️⚠️ Session {session_id} already has an allocated instance")
                    return pool_instance.instance
            
            # Find available instance
            available_instance_id = None
            for instance_id, pool_instance in self.instances.items():
                if pool_instance.state == InstanceState.AVAILABLE and pool_instance.instance:
                    # Additional health check before allocation
                    if self._validate_instance_health(pool_instance.instance):
                        available_instance_id = instance_id
                        break
                    else:
                        # Mark unhealthy instance as failed
                        logger.warning(f"🏊‍♂️⚠️ Instance {instance_id} failed health check during allocation")
                        pool_instance.state = InstanceState.FAILED
                        pool_instance.failure_count += 1
            
            if available_instance_id:
                # Allocate existing instance
                pool_instance = self.instances[available_instance_id]
                pool_instance.state = InstanceState.ALLOCATED
                pool_instance.session_id = session_id
                pool_instance.allocated_at = time.time()
                pool_instance.last_activity = time.time()
                
                # Update statistics
                self.stats['total_allocations'] += 1
                self.stats['current_allocated'] += 1
                self.stats['peak_allocated'] = max(self.stats['peak_allocated'], self.stats['current_allocated'])
                
                logger.info(f"🏊‍♂️📤 Allocated instance {available_instance_id} to session {session_id}")
                return pool_instance.instance
            
            else:
                # Try to create new instance if under max_size
                if len(self.instances) < self.max_size:
                    instance_id = f"instance_{len(self.instances)}_{int(time.time())}"
                    
                    # Create instance with custom parameters if provided
                    params = self.default_params.copy()
                    params.update(kwargs)
                    
                    try:
                        # Add small delay to prevent simultaneous Silero VAD model loading
                        # This prevents race conditions when multiple instances try to access
                        # the same cached model files simultaneously
                        import random
                        delay = random.uniform(0.1, 0.5)  # Random delay between 100-500ms
                        # Debug timing log removed to reduce noise
                        time.sleep(delay)
                        
                        instance = AudioInputProcessor(**params)
                        
                        # Validate that the instance is healthy before allocating
                        if not self._validate_instance_health(instance):
                            logger.error(f"🏊‍♂️💥 On-demand instance {instance_id} failed health validation")
                            if hasattr(instance, 'shutdown'):
                                instance.shutdown()
                            self.stats['failed_allocations'] += 1
                            return None
                        
                        pool_instance = PoolInstance(
                            instance=instance,
                            state=InstanceState.ALLOCATED,
                            session_id=session_id,
                            allocated_at=time.time(),
                            last_activity=time.time(),
                            instance_id=instance_id
                        )
                        self.instances[instance_id] = pool_instance
                        
                        # Update statistics
                        self.stats['total_allocations'] += 1
                        self.stats['current_allocated'] += 1
                        self.stats['peak_allocated'] = max(self.stats['peak_allocated'], self.stats['current_allocated'])
                        
                        logger.info(f"🏊‍♂️🆕 Created and allocated new instance {instance_id} to session {session_id}")
                        return instance
                        
                    except Exception as e:
                        logger.error(f"🏊‍♂️💥 Failed to create instance for session {session_id}: {e}", exc_info=True)
                        self.stats['failed_allocations'] += 1
                        return None
                
                else:
                    # Pool is at capacity, add to queue
                    if session_id not in self.allocation_queue:
                        self.allocation_queue.append(session_id)
                        logger.info(f"🏊‍♂️⏳ Pool at capacity, queued session {session_id} (position: {len(self.allocation_queue)})")
                    
                    self.stats['failed_allocations'] += 1
                    return None
    
    def return_instance(self, session_id: str) -> bool:
        """
        Return an AudioInputProcessor instance to the pool.
        
        Args:
            session_id: Session identifier that owns the instance
            
        Returns:
            True if instance was successfully returned, False otherwise
        """
        with self.lock:
            # Find the instance for this session
            instance_id = None
            for id_key, pool_instance in self.instances.items():
                if pool_instance.session_id == session_id:
                    instance_id = id_key
                    break
            
            if not instance_id:
                logger.warning(f"🏊‍♂️⚠️ No instance found for session {session_id}")
                return False
            
            pool_instance = self.instances[instance_id]
            
            # Calculate session duration for statistics
            if pool_instance.allocated_at:
                session_duration = time.time() - pool_instance.allocated_at
                # Update average session duration
                total_returns = self.stats['total_returns']
                current_avg = self.stats['average_session_duration']
                self.stats['average_session_duration'] = (current_avg * total_returns + session_duration) / (total_returns + 1)
            
            # Reset instance state
            pool_instance.state = InstanceState.AVAILABLE
            pool_instance.session_id = None
            pool_instance.allocated_at = None
            pool_instance.last_activity = time.time()
            
            # Update statistics
            self.stats['total_returns'] += 1
            self.stats['current_allocated'] -= 1
            
            logger.info(f"🏊‍♂️📥 Returned instance {instance_id} from session {session_id}")
            
            # Process allocation queue
            self._process_allocation_queue()
            
            return True
    
    def _process_allocation_queue(self) -> None:
        """Process waiting sessions in the allocation queue."""
        while self.allocation_queue:
            # Find available instance
            available_instance_id = None
            for instance_id, pool_instance in self.instances.items():
                if pool_instance.state == InstanceState.AVAILABLE and pool_instance.instance:
                    available_instance_id = instance_id
                    break
            
            if not available_instance_id:
                break  # No available instances
            
            # Allocate to next session in queue
            waiting_session_id = self.allocation_queue.pop(0)
            pool_instance = self.instances[available_instance_id]
            pool_instance.state = InstanceState.ALLOCATED
            pool_instance.session_id = waiting_session_id
            pool_instance.allocated_at = time.time()
            pool_instance.last_activity = time.time()
            
            # Update statistics
            self.stats['total_allocations'] += 1
            self.stats['current_allocated'] += 1
            self.stats['peak_allocated'] = max(self.stats['peak_allocated'], self.stats['current_allocated'])
            
            logger.info(f"🏊‍♂️📤 Allocated queued instance {available_instance_id} to session {waiting_session_id}")
            
            # TODO: Notify session that instance is now available
            # This would require integration with the session management system
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status and statistics."""
        with self.lock:
            status = {
                'total_instances': len(self.instances),
                'available_instances': sum(1 for p in self.instances.values() if p.state == InstanceState.AVAILABLE),
                'allocated_instances': sum(1 for p in self.instances.values() if p.state == InstanceState.ALLOCATED),
                'failed_instances': sum(1 for p in self.instances.values() if p.state == InstanceState.FAILED),
                'queue_length': len(self.allocation_queue),
                'statistics': self.stats.copy(),
                'max_capacity': self.max_size,
                'utilization_percent': (self.stats['current_allocated'] / len(self.instances)) * 100 if self.instances else 0,
            }
            return status
    
    def _start_health_monitor(self) -> None:
        """Start the health monitoring thread."""
        def health_monitor():
            while not self.shutdown_event.wait(self.health_check_interval):
                try:
                    self._perform_health_check()
                except Exception as e:
                    logger.error(f"🏊‍♂️💥 Health monitor error: {e}", exc_info=True)
        
        self.health_monitor_thread = create_managed_thread(
            target=health_monitor,
            name="AudioInputPool_HealthMonitor",
            daemon=True
        )
        logger.debug("🏊‍♂️🩺 Health monitor started")
    
    def _perform_health_check(self) -> None:
        """Perform health check on pool instances."""
        current_time = time.time()
        instances_to_cleanup = []
        
        with self.lock:
            for instance_id, pool_instance in self.instances.items():
                # Check for idle instances
                if (pool_instance.state == InstanceState.AVAILABLE and 
                    pool_instance.last_activity and
                    current_time - pool_instance.last_activity > self.max_idle_time and
                    len(self.instances) > self.initial_size):
                    
                    instances_to_cleanup.append(instance_id)
                
                # Check for failed instances
                elif pool_instance.state == InstanceState.FAILED and pool_instance.failure_count > 3:
                    instances_to_cleanup.append(instance_id)
        
        # Cleanup instances outside of lock
        for instance_id in instances_to_cleanup:
            self._cleanup_instance(instance_id)
        
        # Log health status
        status = self.get_pool_status()
        logger.debug(f"🏊‍♂️🩺 Health check: {status['allocated_instances']}/{status['total_instances']} allocated, "
                    f"{status['queue_length']} queued, {status['utilization_percent']:.1f}% utilization")
    
    def _cleanup_instance(self, instance_id: str) -> None:
        """Clean up a specific instance."""
        with self.lock:
            if instance_id not in self.instances:
                return
            
            pool_instance = self.instances[instance_id]
            pool_instance.state = InstanceState.SHUTTING_DOWN
            
            logger.info(f"🏊‍♂️🗑️ Cleaning up instance {instance_id}")
            
            # Shutdown the instance
            if pool_instance.instance:
                try:
                    pool_instance.instance.shutdown()
                except Exception as e:
                    logger.error(f"🏊‍♂️💥 Error shutting down instance {instance_id}: {e}")
            
            # Remove from pool
            del self.instances[instance_id]
    
    def shutdown(self) -> None:
        """Shutdown the entire pool."""
        logger.info("🏊‍♂️🛑 Shutting down AudioInputProcessorPool...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for health monitor to stop
        if self.health_monitor_thread:
            self.health_monitor_thread.join(timeout=5.0)
        
        # Shutdown all instances
        with self.lock:
            instance_ids = list(self.instances.keys())
        
        for instance_id in instance_ids:
            self._cleanup_instance(instance_id)
        
        # Clear allocation queue
        with self.lock:
            self.allocation_queue.clear()
        
        # Untrack resource
        self.resource_tracker.untrack_resource("global", "AudioInputProcessorPool", f"pool_{id(self)}")
        
        logger.info("🏊‍♂️👋 AudioInputProcessorPool shutdown complete")

def _prewarm_silero_cache():
    """
    Pre-warm the Silero VAD model cache to prevent race conditions.
    This ensures the cache is properly initialized before creating multiple instances.
    """
    try:
        logger.info("🏊‍♂️🔥 Pre-warming Silero VAD cache...")
        import torch
        
        # Force download/cache the Silero VAD model
        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False,
            trust_repo=True
        )
        logger.info("🏊‍♂️✅ Silero VAD cache pre-warmed successfully")
        return True
        
    except Exception as e:
        logger.error(f"🏊‍♂️💥 Failed to pre-warm Silero VAD cache: {e}")
        return False 