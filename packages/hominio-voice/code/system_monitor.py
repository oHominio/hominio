# system_monitor.py (renamed from gpu_monitor.py)
import asyncio
import logging
import json
import psutil
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import pynvml
    NVIDIA_ML_AVAILABLE = True
except ImportError:
    NVIDIA_ML_AVAILABLE = False
    logger.warning("nvidia-ml-py not available. GPU monitoring disabled.")

@dataclass
class SystemStats:
    """Container for complete system statistics"""
    # GPU Stats
    gpu_available: bool = False
    gpu_utilization: int = 0  # GPU utilization percentage (0-100)
    gpu_memory_used: int = 0  # GPU memory used in MB
    gpu_memory_total: int = 0  # GPU total memory in MB
    gpu_memory_percent: int = 0  # GPU memory usage percentage
    gpu_temperature: int = 0  # GPU temperature in Celsius
    gpu_name: str = "No GPU"
    gpu_driver_version: str = "Unknown"
    gpu_power_usage: Optional[int] = None  # GPU power usage in Watts
    
    # CPU Stats
    cpu_percent: float = 0.0  # Overall CPU usage percentage
    cpu_count: int = 0  # Number of CPU cores
    cpu_freq_current: float = 0.0  # Current CPU frequency in MHz
    cpu_freq_max: float = 0.0  # Maximum CPU frequency in MHz
    cpu_temp: Optional[float] = None  # CPU temperature if available
    
    # System Memory Stats
    memory_total: int = 0  # Total system memory in MB
    memory_used: int = 0  # Used system memory in MB
    memory_percent: float = 0.0  # Memory usage percentage
    memory_available: int = 0  # Available system memory in MB
    
    # System Info
    uptime: float = 0.0  # System uptime in seconds

class SystemMonitor:
    """Comprehensive system monitoring including GPU, CPU, and memory"""
    
    def __init__(self, gpu_device_id: int = 0):
        self.gpu_device_id = gpu_device_id
        self.gpu_handle = None
        self.gpu_initialized = False
        self.stats = SystemStats()
        
    async def initialize(self) -> bool:
        """Initialize system monitoring including GPU if available"""
        logger.info("🖥️⚡ Initializing system monitoring...")
        
        # Initialize basic system info
        self.stats.cpu_count = psutil.cpu_count()
        
        # Try to get CPU frequency info
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                self.stats.cpu_freq_max = cpu_freq.max
        except Exception:
            pass
        
        # Try to initialize GPU monitoring
        gpu_success = await self._initialize_gpu()
        
        logger.info(f"🖥️💾 System monitoring initialized - CPU cores: {self.stats.cpu_count}")
        if gpu_success:
            logger.info(f"🖥️⚡ GPU monitoring: {self.stats.gpu_name}")
        else:
            logger.info("🖥️⚡ GPU monitoring: Not available")
            
        return True
        
    async def _initialize_gpu(self) -> bool:
        """Initialize GPU monitoring if available"""
        if not NVIDIA_ML_AVAILABLE:
            return False
            
        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_device_id)
            
            # Get static GPU info
            gpu_name = pynvml.nvmlDeviceGetName(self.gpu_handle)
            self.stats.gpu_name = gpu_name.decode('utf-8') if isinstance(gpu_name, bytes) else gpu_name
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            self.stats.gpu_driver_version = driver_version.decode('utf-8') if isinstance(driver_version, bytes) else driver_version
            
            # Get total GPU memory
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            self.stats.gpu_memory_total = memory_info.total // (1024 * 1024)  # Convert to MB
            
            self.stats.gpu_available = True
            self.gpu_initialized = True
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize GPU monitoring: {e}")
            return False
    
    async def get_stats(self) -> SystemStats:
        """Get current complete system statistics"""
        
        # Get CPU stats
        try:
            self.stats.cpu_percent = psutil.cpu_percent(interval=None)
            
            # Get CPU frequency
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    self.stats.cpu_freq_current = cpu_freq.current
            except Exception:
                pass
                
            # Try to get CPU temperature (platform dependent)
            try:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps and temps['coretemp']:
                    # Average of all core temperatures
                    core_temps = [temp.current for temp in temps['coretemp'] if 'Core' in temp.label]
                    if core_temps:
                        self.stats.cpu_temp = sum(core_temps) / len(core_temps)
                elif 'cpu_thermal' in temps and temps['cpu_thermal']:
                    # For some ARM systems
                    self.stats.cpu_temp = temps['cpu_thermal'][0].current
            except Exception:
                pass  # Temperature monitoring not available on all systems
                
        except Exception as e:
            logger.error(f"Error getting CPU stats: {e}")
        
        # Get memory stats
        try:
            memory = psutil.virtual_memory()
            self.stats.memory_total = memory.total // (1024 * 1024)  # Convert to MB
            self.stats.memory_used = memory.used // (1024 * 1024)
            self.stats.memory_percent = memory.percent
            self.stats.memory_available = memory.available // (1024 * 1024)
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
        
        # Get system uptime
        try:
            import time
            self.stats.uptime = time.time() - psutil.boot_time()
        except Exception:
            pass
        
        # Get GPU stats if available
        if self.gpu_initialized and NVIDIA_ML_AVAILABLE:
            try:
                # Get GPU utilization
                utilization = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
                self.stats.gpu_utilization = utilization.gpu
                
                # Get GPU memory info
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
                self.stats.gpu_memory_used = memory_info.used // (1024 * 1024)  # Convert to MB
                self.stats.gpu_memory_percent = int((memory_info.used / memory_info.total) * 100)
                
                # Get GPU temperature
                try:
                    self.stats.gpu_temperature = pynvml.nvmlDeviceGetTemperature(
                        self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU
                    )
                except Exception:
                    self.stats.gpu_temperature = 0
                    
                # Get GPU power usage (optional)
                try:
                    self.stats.gpu_power_usage = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle) // 1000  # Convert to Watts
                except Exception:
                    self.stats.gpu_power_usage = None
                    
            except Exception as e:
                logger.error(f"Error getting GPU stats: {e}")
                self.stats.gpu_available = False
                
        return self.stats
    
    def to_dict(self) -> Dict:
        """Convert current stats to dictionary for JSON serialization"""
        return {
            # GPU stats
            "gpu_available": self.stats.gpu_available,
            "gpu_utilization": self.stats.gpu_utilization,
            "gpu_memory_used": self.stats.gpu_memory_used,
            "gpu_memory_total": self.stats.gpu_memory_total,
            "gpu_memory_percent": self.stats.gpu_memory_percent,
            "gpu_temperature": self.stats.gpu_temperature,
            "gpu_name": self.stats.gpu_name,
            "gpu_driver_version": self.stats.gpu_driver_version,
            "gpu_power_usage": self.stats.gpu_power_usage,
            
            # CPU stats
            "cpu_percent": round(self.stats.cpu_percent, 1),
            "cpu_count": self.stats.cpu_count,
            "cpu_freq_current": round(self.stats.cpu_freq_current, 1) if self.stats.cpu_freq_current else None,
            "cpu_freq_max": round(self.stats.cpu_freq_max, 1) if self.stats.cpu_freq_max else None,
            "cpu_temp": round(self.stats.cpu_temp, 1) if self.stats.cpu_temp else None,
            
            # Memory stats
            "memory_total": self.stats.memory_total,
            "memory_used": self.stats.memory_used,
            "memory_percent": round(self.stats.memory_percent, 1),
            "memory_available": self.stats.memory_available,
            
            # System info
            "uptime": round(self.stats.uptime, 0) if self.stats.uptime else 0
        }
    
    async def shutdown(self):
        """Cleanup system monitoring"""
        if self.gpu_initialized and NVIDIA_ML_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
                logger.info("🖥️⚡ GPU monitor shutdown complete")
            except Exception as e:
                logger.error(f"Error during GPU monitor shutdown: {e}")

class SystemStatsStreamer:
    """Streams complete system stats to WebSocket clients"""
    
    def __init__(self, monitor: SystemMonitor, update_interval: float = 1.0):
        self.monitor = monitor
        self.update_interval = update_interval
        self.clients = set()
        self.running = False
        self.task = None
        
    def add_client(self, websocket):
        """Add a WebSocket client for system stats updates"""
        self.clients.add(websocket)
        logger.info(f"🖥️📊 System stats client added. Total clients: {len(self.clients)}")
        
    def remove_client(self, websocket):
        """Remove a WebSocket client"""
        self.clients.discard(websocket)
        logger.info(f"🖥️📊 System stats client removed. Total clients: {len(self.clients)}")
        
    async def start_streaming(self):
        """Start streaming system stats to all connected clients"""
        if self.running:
            return
            
        self.running = True
        self.task = asyncio.create_task(self._stream_loop())
        logger.info("🖥️📊 System stats streaming started")
        
    async def stop_streaming(self):
        """Stop streaming system stats"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("🖥️📊 System stats streaming stopped")
        
    async def _stream_loop(self):
        """Main streaming loop"""
        while self.running:
            try:
                if self.clients:
                    # Get current system stats
                    await self.monitor.get_stats()
                    stats_dict = self.monitor.to_dict()
                    
                    # Create message
                    message = json.dumps({
                        "type": "system_stats",
                        "content": stats_dict
                    })
                    
                    # Send to all connected clients
                    disconnected_clients = set()
                    for client in self.clients.copy():
                        try:
                            await client.send_text(message)
                        except Exception as e:
                            logger.warning(f"Failed to send system stats to client: {e}")
                            disconnected_clients.add(client)
                    
                    # Remove disconnected clients
                    for client in disconnected_clients:
                        self.remove_client(client)
                        
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system stats streaming: {e}")
                await asyncio.sleep(self.update_interval)

# Keep backward compatibility
GPUMonitor = SystemMonitor
GPUStatsStreamer = SystemStatsStreamer 