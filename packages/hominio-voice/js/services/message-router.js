/**
 * Frontend Message Router
 * Routes WebSocket messages to appropriate services (STT, TTS, etc.)
 */
import { uiState } from "../core/ui-state.js";

export class MessageRouter {
  constructor() {
    this.sttService = null;
    this.ttsService = null;
    this.messageHandlers = new Map();

    // Register default handlers
    this.registerHandler("realtime", (data) => this.routeToSTT(data));
    this.registerHandler("fullSentence", (data) => this.routeToSTT(data));
    this.registerHandler("stt-status", (data) => this.routeToSTT(data));
    this.registerHandler("vad_detect_start", (data) => this.routeToSTT(data));
    this.registerHandler("vad_detect_stop", (data) => this.routeToSTT(data));

    this.registerHandler("tts-error", (data) => this.routeToTTS(data));
    this.registerHandler("model-status", (data) => this.routeToTTS(data));
    this.registerHandler("status", (data) => this.handleGeneralStatus(data));
    this.registerHandler("pong", (data) => this.handlePong(data));
  }

  /**
   * Initialize with service references
   */
  initialize(sttService, ttsService) {
    this.sttService = sttService;
    this.ttsService = ttsService;
    console.log("✅ Frontend message router initialized");
  }

  /**
   * Register a message handler for a specific message type
   */
  registerHandler(messageType, handler) {
    this.messageHandlers.set(messageType, handler);
  }

  /**
   * Route incoming WebSocket message to appropriate handler
   */
  routeMessage(data) {
    if (!data || !data.type) {
      console.warn("⚠️ [Router] Invalid message format:", data);
      return false;
    }

    const handler = this.messageHandlers.get(data.type);
    if (handler) {
      console.log(`🔄 [Router] Routing ${data.type} message`);
      try {
        handler(data);
        return true;
      } catch (error) {
        console.error(`❌ [Router] Error handling ${data.type}:`, error);
        return false;
      }
    }

    console.warn(`⚠️ [Router] No handler for message type: ${data.type}`);
    return false;
  }

  /**
   * Route message to STT service
   */
  routeToSTT(data) {
    if (this.sttService && this.sttService.handleWebSocketMessage) {
      console.log(`📥 [Router] → STT: ${data.type}`);
      this.sttService.handleWebSocketMessage(data);
    } else {
      console.warn("⚠️ [Router] STT service not available");
    }
  }

  /**
   * Route message to TTS service
   */
  routeToTTS(data) {
    if (this.ttsService && this.ttsService.handleMessage) {
      console.log(`📥 [Router] → TTS: ${data.type}`);
      this.ttsService.handleMessage(data);
    } else {
      console.warn("⚠️ [Router] TTS service not available");
    }
  }

  /**
   * Handle general status messages
   */
  handleGeneralStatus(data) {
    console.log("ℹ️ [Router] General status:", data.message);
    uiState.updateStatusText(data.message);
  }

  /**
   * Handle pong messages
   */
  handlePong(data) {
    console.log("🏓 [Router] Pong received");
  }

  /**
   * Handle binary data (audio)
   */
  handleBinaryData(data) {
    // Route binary data to TTS service (audio chunks)
    if (this.ttsService && this.ttsService.handleBinaryData) {
      console.log("🔊 [Router] → TTS: Binary audio data");
      this.ttsService.handleBinaryData(data);
    } else {
      console.warn("⚠️ [Router] TTS service not available for binary data");
    }
  }

  /**
   * Handle special string messages (END, ERROR)
   */
  handleSpecialString(message) {
    if (message === "END" || message === "ERROR") {
      // Route to TTS service
      if (this.ttsService && this.ttsService.handleSpecialMessage) {
        console.log(`🔊 [Router] → TTS: ${message}`);
        this.ttsService.handleSpecialMessage(message);
      }
      return true;
    }
    return false;
  }

  /**
   * Get router status
   */
  getStatus() {
    return {
      sttConnected: !!this.sttService,
      ttsConnected: !!this.ttsService,
      handlersCount: this.messageHandlers.size,
      registeredTypes: Array.from(this.messageHandlers.keys()),
    };
  }
}

// Export singleton instance
export const messageRouter = new MessageRouter();
