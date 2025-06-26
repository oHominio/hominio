# ACTION PLAN: Multi-User Voice Chat Scaling

## 🚨 CRITICAL: PRE-SCALING FIXES REQUIRED

**These issues MUST be resolved before implementing multi-user support, as they will be amplified with concurrent users:**

### MEMORY LEAK FIXES (Priority 1)

- [ ] **Fix Thread Join Deadlocks**
  - Location: `speech_pipeline_manager.py:1102`
  - Issue: Threads not joining cleanly become zombie processes
  - Fix: Add force termination after timeout, ensure all threads are daemon threads
  - Risk: Each user connection could leave zombie threads consuming memory

- [ ] **Audio Buffer Memory Leaks**
  - Location: `audio_module.py:265-396`
  - Issue: Audio buffers grow indefinitely when synthesis fails/interrupts
  - Fix: Add buffer size limits, guaranteed cleanup in finally blocks
  - Risk: With 20+ users, audio buffers could consume gigabytes of RAM

- [ ] **Queue Overflow Cleanup**
  - Location: `server.py:364-375`, `audio_module.py` TTS queues
  - Issue: Full queues don't drain old data, causing memory bloat
  - Fix: Implement LRU eviction when queues approach limits
  - Risk: Each user's audio queue could grow to hundreds of MBs

- [ ] **LLM Generator Resource Leaks**
  - Location: `llm_module.py` active requests tracking
  - Issue: Generators not properly closed on cancellation
  - Fix: Ensure proper close() calls in all code paths
  - Risk: GPU memory leaks scale linearly with concurrent users

- [ ] **TTS Engine GPU Memory**
  - Location: TTS engine initialization/cleanup
  - Issue: Models loaded but not unloaded properly
  - Fix: Implement proper model lifecycle management
  - Risk: GPU VRAM exhaustion with multiple users

### THREADING SAFETY FIXES (Priority 2)

- [ ] **Race Conditions in Callback Assignment**
  - Location: `server.py:930-944` (websocket handler)
  - Issue: Callbacks overwritten between users
  - Fix: Use session-specific callback routing
  - Risk: Users interfering with each other's audio/text processing

- [ ] **Shared State Mutations**
  - Location: `speech_pipeline_manager.py` global state
  - Issue: Multiple threads accessing shared variables without proper locking
  - Fix: Add proper synchronization primitives
  - Risk: Data corruption and unpredictable behavior under load

### PERFORMANCE BOTTLENECKS (Priority 3)

- [ ] **Queue Processing Efficiency**
  - Location: Various queue.get() operations with timeouts
  - Issue: Polling-based queue processing wastes CPU
  - Fix: Use event-driven processing where possible
  - Risk: High CPU usage with many concurrent users

- [ ] **Audio Processing Optimization**
  - Location: PCM data processing in multiple locations
  - Issue: Inefficient buffer management and copying
  - Fix: Implement zero-copy buffer sharing where possible
  - Risk: CPU bottleneck during high concurrent audio load

## 1. DECONSTRUCT PROBLEM

### Current Status Quo Analysis - Problematic Weak Points:

**Global State Contamination:**
- `SpeechPipelineManager` created as singleton in `app.state` (line 116-126 in server.py)
- Single `running_generation` shared across all users (speech_pipeline_manager.py:157)
- Global worker threads processing all requests sequentially (lines 204-212)
- Shared `AudioInputProcessor` with callbacks overwritten by each connection (lines 926-941)

**Resource Contention Issues:**
- Single LLM instance shared across users causing blocking (llm_module.py:1269)
- GPU memory not partitioned per user
- TTS synthesis workers not isolated per session
- No request queuing or rate limiting for concurrent access

**Thread Safety Violations:**
- Callback assignment race conditions in websocket handler (server.py:930-944)
- Shared state mutation without proper locking
- Worker threads accessing global state without coordination
- Event objects shared between sessions causing interference

**Memory Management Failures:**
- No session cleanup mechanism for abandoned connections
- Indefinite memory growth with conversation history (speech_pipeline_manager.py:155)
- Audio buffers accumulating without bounds
- No garbage collection for completed generations

**Scalability Bottlenecks:**
- Single request processing queue causing head-of-line blocking
- Synchronous abort logic blocking all other users
- No connection pooling for LLM backends
- Fixed batch sizes not optimized for concurrent load

## 2. SOLUTION ARCHITECTURE

### Target Multi-User System Design:

**Per-Session Isolation:**
- Individual `SpeechPipelineManager` instances per WebSocket connection
- Dedicated worker thread pools isolated by session ID
- Private conversation history and state management
- Independent audio processing pipelines

**Resource Pool Management:**
- Shared LLM connection pool with request routing
- GPU memory partitioning for concurrent TTS synthesis  
- Dynamic worker scaling based on active sessions
- Request queuing with priority and rate limiting

**Fault Isolation:**
- Session-specific error handling without affecting others
- Circuit breakers for resource protection
- Automatic cleanup of failed/abandoned sessions
- Graceful degradation under high load

## 3. WRITTEN RESPONSE FORMAT

### Detailed Execution Plan: Single-User to Multi-User Transformation

## MILESTONE 1: Session Management Foundation
**Goal:** Establish per-connection state isolation

### Tasks:
- [ ] **1.1 Create SessionManager Class**
  - Location: `code/session_manager.py`
  - Purpose: Manage individual user sessions with unique IDs
  - Features: Session creation, cleanup, health monitoring
  - Integration: WebSocket connection lifecycle

- [ ] **1.2 Refactor SpeechPipelineManager**
  - Convert from singleton to per-session instances
  - Remove global state dependencies
  - Add session ID to all operations
  - Isolate worker threads per session

- [ ] **1.3 Update WebSocket Handler**
  - Modify `websocket_endpoint()` to create session-specific components
  - Replace global callback assignments with session-specific ones
  - Add session cleanup on disconnect

- [ ] **1.4 Session State Storage**
  - Implement in-memory session registry
  - Add session timeout and cleanup mechanisms
  - Create session health monitoring

**Testable Milestone:** Multiple users can connect simultaneously without state interference

## MILESTONE 2: Resource Pool Architecture
**Goal:** Share expensive resources efficiently across sessions

### Tasks:
- [ ] **2.1 LLM Connection Pool**
  - Location: `code/llm_pool.py`
  - Implement connection pooling for LLM backends
  - Add request routing and load balancing
  - Integrate with existing `llm_module.py`

- [ ] **2.2 TTS Resource Manager** 
  - Create shared TTS engine pool
  - Implement GPU memory partitioning
  - Add synthesis queue management
  - Prevent resource starvation

- [ ] **2.3 STT Process Pool**
  - Isolate RealtimeSTT instances per session
  - Implement efficient audio processing queues
  - Add model sharing optimizations

- [ ] **2.4 Request Rate Limiting**
  - Implement per-session rate limits
  - Add global capacity management
  - Create backpressure mechanisms

**Testable Milestone:** 10 concurrent users without resource contention

## MILESTONE 3: Memory & Performance Optimization
**Goal:** Optimize for 20-30 concurrent users

### Tasks:
- [ ] **3.1 Memory Management**
  - Implement conversation history limits
  - Add audio buffer cleanup
  - Create automatic garbage collection for sessions
  - Monitor memory usage per session

- [ ] **3.2 Performance Optimization**
  - Optimize audio chunk processing
  - Implement efficient serialization
  - Add caching for repeated operations
  - Profile and optimize hot paths

- [ ] **3.3 Load Balancing**
  - Implement dynamic worker scaling
  - Add session migration capabilities
  - Create health-based routing
  - Optimize resource allocation

- [ ] **3.4 Monitoring & Metrics**
  - Add per-session metrics collection
  - Implement system health monitoring
  - Create performance dashboards
  - Add alerting for resource limits

**Testable Milestone:** 20-30 concurrent users with acceptable performance

## MILESTONE 4: Frontend Scalability
**Goal:** Ensure client-side handles multiple user scenarios

### Tasks:
- [ ] **4.1 Client Connection Management**
  - Add automatic reconnection logic
  - Implement connection health monitoring
  - Add graceful degradation for poor connections
  - Create client-side error handling

- [ ] **4.2 Audio Processing Optimization**
  - Optimize AudioWorklet performance
  - Reduce memory usage in audio buffers
  - Implement adaptive quality settings
  - Add bandwidth optimization

- [ ] **4.3 UI Responsiveness**
  - Prevent UI blocking during processing
  - Add loading states and progress indicators
  - Implement optimistic UI updates
  - Create error recovery flows

- [ ] **4.4 Client Resource Management**
  - Optimize memory usage in browser
  - Implement audio buffer management
  - Add client-side rate limiting
  - Create resource usage monitoring

**Testable Milestone:** Client remains responsive under concurrent load

## MILESTONE 5: Production Readiness
**Goal:** Deploy-ready multi-user system

### Tasks:
- [ ] **5.1 Configuration Management**
  - Add environment-based configuration
  - Implement feature flags for scaling
  - Create deployment configurations
  - Add configuration validation

- [ ] **5.2 Error Handling & Recovery**
  - Implement comprehensive error handling
  - Add automatic recovery mechanisms
  - Create graceful shutdown procedures
  - Implement data persistence for sessions

- [ ] **5.3 Security & Authorization**
  - Add session authentication
  - Implement request validation
  - Create rate limiting by user
  - Add audit logging

- [ ] **5.4 Deployment & Scaling**
  - Create production Docker configurations
  - Add horizontal scaling capabilities
  - Implement load balancer integration
  - Create deployment automation

**Testable Milestone:** Production-ready deployment supporting 30 concurrent users

## Implementation Priority & Dependencies:

1. **CRITICAL PATH:** Milestone 1 → Milestone 2 → Milestone 3
2. **PARALLEL TRACK:** Milestone 4 can start after Milestone 1
3. **FINAL INTEGRATION:** Milestone 5 requires completion of all previous milestones

## Resource Requirements:

- **Development Time:** 6-8 weeks for complete implementation
- **Hardware:** GPU with 16GB+ VRAM for 30 concurrent users
- **Memory:** 32GB+ RAM recommended for full user load
- **Network:** High-bandwidth connection for WebSocket streaming
- **Storage:** Sufficient space for model caching and session data

## Risk Mitigation:

- **Performance Degradation:** Implement graceful degradation and load shedding
- **Memory Exhaustion:** Add memory monitoring and automatic cleanup
- **Connection Issues:** Implement robust reconnection and recovery
- **Resource Starvation:** Create fair resource allocation algorithms

This plan transforms a single-user voice chat system into a robust multi-user platform capable of supporting 20-30 concurrent users while maintaining performance and reliability. 