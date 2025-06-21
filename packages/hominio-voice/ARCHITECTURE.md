# Hominio Voice - Modular Architecture

## Overview

The Hominio Voice application has been refactored from a monolithic `main.py` (759 lines) into a clean, modular architecture inspired by the RealtimeVoiceChat reference implementation.

## Directory Structure

```
packages/hominio-voice/
├── main.py                     # Original monolithic file (deprecated)
├── main_new.py                 # New modular main application
├── core/                       # Core application functionality
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── logging_setup.py       # Logging configuration
│   └── lifespan.py            # Application lifespan (future)
├── engines/                    # Engine management modules
│   ├── __init__.py
│   ├── tts_engine.py          # TTS engine management
│   ├── stt_engine.py          # STT engine management (future)
│   └── llm_client.py          # LLM client management
├── services/                   # Application services
│   ├── __init__.py
│   ├── audio_processor.py     # Audio processing (future)
│   ├── conversation_manager.py # Conversation flow with interruption
│   └── websocket_manager.py   # WebSocket management (future)
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── audio_utils.py         # Audio utility functions
│   └── signal_handlers.py    # Signal handling for graceful shutdown
└── js/                        # Frontend JavaScript modules
    ├── services/
    ├── core/
    └── app.js
```

## Key Modules

### Core Modules

#### `core/config.py`
- **Purpose**: Centralized configuration management
- **Features**:
  - Environment variable setup for headless operation
  - Configuration classes with sensible defaults
  - STT/TTS/LLM configuration builders
  - Audio processing settings

#### `core/logging_setup.py`
- **Purpose**: Logging configuration and management
- **Features**:
  - Structured logging setup
  - Console output formatting
  - Logger instance management
  - Suppression of noisy third-party loggers

### Engine Modules

#### `engines/tts_engine.py`
- **Purpose**: TTS engine lifecycle management
- **Features**:
  - KokoroEngine initialization and testing
  - Headless operation support
  - Audio synthesis with chunk collection
  - Status tracking and health monitoring
  - Graceful shutdown

#### `engines/llm_client.py`
- **Purpose**: LLM client management
- **Features**:
  - OpenAI-compatible API client setup
  - RedPill API integration
  - Streaming and non-streaming responses
  - Error handling and fallbacks
  - Health checking

### Service Modules

#### `services/conversation_manager.py`
- **Purpose**: Conversation flow with advanced interruption handling
- **Features**:
  - **Interruption Detection**: Detects when user starts speaking during TTS
  - **State Management**: Tracks speaking/listening states
  - **Thread Management**: Handles synthesis threads with clean cancellation
  - **WebSocket Coordination**: Manages active connections
  - **Conversation History**: Maintains dialogue context
  - **Generation Tracking**: Unique IDs for each synthesis operation

### Utility Modules

#### `utils/signal_handlers.py`
- **Purpose**: Graceful shutdown handling
- **Features**:
  - Signal handler registration (SIGINT, SIGTERM, SIGABRT)
  - Shutdown callback management
  - Clean resource cleanup

#### `utils/audio_utils.py`
- **Purpose**: Audio processing utilities
- **Features**:
  - WAV header generation
  - Audio resampling with scipy
  - Duration calculation
  - Silence detection
  - Format conversion helpers

## Key Improvements

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Clear interfaces between components
- Easy to test and maintain individual components

### 2. **Interruption Handling**
- **Thread-Safe Interruption**: Uses threading.Event for clean cancellation
- **Generation Tracking**: Each synthesis has a unique ID
- **State Coordination**: Proper state management between listening/speaking
- **WebSocket Signaling**: Client receives interruption notifications

### 3. **Resource Management**
- **Graceful Shutdown**: Signal handlers with cleanup callbacks
- **Engine Lifecycle**: Proper initialization and shutdown sequences
- **Memory Management**: Clean resource cleanup and reference clearing

### 4. **Configuration Management**
- **Environment Setup**: Centralized environment variable management
- **Headless Operation**: Proper ALSA/audio suppression
- **Configurable Parameters**: Easy to adjust STT/TTS/LLM settings

### 5. **Error Handling**
- **Robust Error Recovery**: Graceful handling of engine failures
- **Health Monitoring**: Status tracking for all components
- **Fallback Mechanisms**: Error responses when services unavailable

## Migration Path

### Phase 1: Basic Modularization ✅
- [x] Extract configuration management
- [x] Create engine managers
- [x] Implement conversation manager
- [x] Add utility modules
- [x] Create new main.py

### Phase 2: Advanced Features (Next Steps)
- [ ] Complete STT engine integration with RealtimeSTT
- [ ] Implement VAD (Voice Activity Detection)
- [ ] Add turn detection logic
- [ ] Enhance frontend with AudioWorklets
- [ ] Add conversation context management

### Phase 3: Production Features
- [ ] Add metrics and monitoring
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Performance optimization
- [ ] Docker optimization

## Usage

### Running the Modular Version
```bash
# Use the new modular main file
python main_new.py

# Or update main.py to use the modular architecture
mv main.py main_old.py
mv main_new.py main.py
```

### Configuration
Environment variables can be set in `.env` or directly:
```bash
export REDPILL_API_KEY="your-api-key"
export LOG_LEVEL="INFO"
```

### Development
Each module can be imported and tested independently:
```python
from engines.tts_engine import tts_manager
from services.conversation_manager import conversation_manager

# Test TTS engine
await tts_manager.initialize()
audio_chunks = await tts_manager.synthesize_text("Hello world")

# Test conversation flow
await conversation_manager.process_user_input("What's the weather?")
```

## Benefits

1. **Maintainability**: Much easier to understand and modify individual components
2. **Testability**: Each module can be unit tested in isolation
3. **Scalability**: Easy to add new features without affecting existing code
4. **Reusability**: Modules can be reused in other projects
5. **Debugging**: Easier to isolate and fix issues
6. **Documentation**: Each module has clear purpose and interfaces

## Future Enhancements

Based on the RealtimeVoiceChat reference, we can add:

1. **Advanced VAD**: Sophisticated silence detection and turn management
2. **Audio Worklets**: Better frontend audio processing
3. **Context Management**: Conversation history with similarity-based pruning
4. **Performance Monitoring**: Real-time metrics and health checks
5. **Multi-Model Support**: Easy switching between different TTS/LLM models 