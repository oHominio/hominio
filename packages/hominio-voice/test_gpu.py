#!/usr/bin/env python3
"""
System monitoring test script - tests CPU, memory, and GPU monitoring
"""

import asyncio
import sys
import os

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

from system_monitor import SystemMonitor

async def test_system_monitoring():
    print("🖥️📊 Testing comprehensive system monitoring...")
    
    # Initialize system monitor
    monitor = SystemMonitor()
    
    # Try to initialize
    success = await monitor.initialize()
    
    if not success:
        print("❌ System monitoring initialization failed")
        return False
    
    print("✅ System monitoring initialized successfully")
    
    # Get stats a few times
    for i in range(5):
        stats = await monitor.get_stats()
        stats_dict = monitor.to_dict()
        
        print(f"\n📊 System Stats (iteration {i+1}):")
        
        # CPU Stats
        print(f"  🖥️ CPU:")
        print(f"    Usage: {stats_dict['cpu_percent']}%")
        print(f"    Cores: {stats_dict['cpu_count']}")
        if stats_dict['cpu_freq_current']:
            print(f"    Frequency: {stats_dict['cpu_freq_current']} MHz")
        if stats_dict['cpu_temp']:
            print(f"    Temperature: {stats_dict['cpu_temp']}°C")
        
        # Memory Stats
        print(f"  💾 Memory:")
        print(f"    Used: {stats_dict['memory_used']} MB / {stats_dict['memory_total']} MB ({stats_dict['memory_percent']}%)")
        print(f"    Available: {stats_dict['memory_available']} MB")
        
        # GPU Stats
        if stats_dict['gpu_available']:
            print(f"  ⚡ GPU: {stats_dict['gpu_name']}")
            print(f"    Utilization: {stats_dict['gpu_utilization']}%")
            print(f"    Memory: {stats_dict['gpu_memory_used']} MB / {stats_dict['gpu_memory_total']} MB ({stats_dict['gpu_memory_percent']}%)")
            print(f"    Temperature: {stats_dict['gpu_temperature']}°C")
            if stats_dict['gpu_power_usage'] is not None:
                print(f"    Power: {stats_dict['gpu_power_usage']}W")
        else:
            print(f"  ⚡ GPU: Not available")
        
        # System Info
        if stats_dict['uptime'] > 0:
            hours = int(stats_dict['uptime'] // 3600)
            minutes = int((stats_dict['uptime'] % 3600) // 60)
            print(f"  ⏱️ Uptime: {hours}h {minutes}m")
        
        await asyncio.sleep(1)
    
    # Shutdown
    await monitor.shutdown()
    print("\n✅ System monitoring test completed successfully")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_system_monitoring())
        if result:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 