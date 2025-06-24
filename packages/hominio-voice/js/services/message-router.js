/**
 * Message Router (Master Coordinator)
 * Single source of truth for all WebSocket communication
 * Owns the WebSocket connection and routes all messages
 */
import { uiState } from "../core/ui-state.js";
import { wsManager } from "./websocket-manager.js";

export class MessageRouter {
  constructor() {
    this.sttService = null;
    this.ttsService = null;
    this.isConnected = false;
  }

  /**
   * Set service references and establish proper coordination
   */
  setServices(sttService, ttsService) {
    this.sttService = sttService;
    this.ttsService = ttsService;

    // Set message router reference in each service (single source of truth)
    if (this.sttService && this.sttService.setMessageRouter) {
      this.sttService.setMessageRouter(this);
    }
    if (this.ttsService && this.ttsService.setMessageRouter) {
      this.ttsService.setMessageRouter(this);
    }

    console.log(
      "✅ [Router] Service coordination established - router is master coordinator"
    );
  }

  /**
   * Initialize and connect to unified WebSocket endpoint (master connection)
   */
  async connectToUnifiedEndpoint() {
    try {
      console.log("🔗 [Router] Connecting to unified WebSocket endpoint...");
      uiState.updateConnectionStatus("Connecting...", false);

      // Create the master WebSocket connection
      const connection = wsManager.createConnection("unified", "/ws", {
        onOpen: () => {
          console.log("🔗 [Router] Master WebSocket connection established");
          this.isConnected = true;
          uiState.updateConnectionStatus("Connected", true);

          // Notify services that connection is ready
          if (this.sttService) {
            this.sttService.isConnected = true;
            this.sttService.updateStatus("Connected through message router");
          }
        },
        onMessage: (event) => this.handleMessage(event),
        onClose: () => {
          console.log("🔗 [Router] Master WebSocket connection closed");
          this.isConnected = false;
          uiState.updateConnectionStatus("Disconnected", false);

          // Notify services of disconnection
          if (this.sttService) {
            this.sttService.isConnected = false;
            this.sttService.updateStatus("Disconnected");
          }
        },
        onError: (error) => {
          console.error("🔗 [Router] Master WebSocket error:", error);
          this.isConnected = false;
          uiState.updateConnectionStatus("Error", false);

          // Notify services of error
          if (this.sttService) {
            this.sttService.isConnected = false;
            this.sttService.updateStatus("Connection error");
          }
        },
        autoReconnect: true,
      });

      console.log(
        "✅ [Router] Master WebSocket connection created. Current state:",
        wsManager.getConnectionStatus("unified")
      );
      return true;
    } catch (error) {
      console.error(
        "❌ [Router] Failed to connect to unified endpoint:",
        error
      );
      return false;
    }
  }

  /**
   * Master message handler - routes all WebSocket messages
   */
  handleMessage(event) {
    try {
      if (typeof event.data === "string") {
        try {
          const data = JSON.parse(event.data);
          this.routeMessage(data);
        } catch (e) {
          // Ignore non-JSON messages
          console.log("🔗 [Router] Non-JSON message received:", event.data);
        }
      } else {
        // Binary data - route to STT service
        console.log("🔗 [Router] Binary data received, routing to STT");
        if (this.sttService && this.sttService.handleBinaryData) {
          this.sttService.handleBinaryData(event.data);
        }
      }
    } catch (error) {
      console.error("❌ [Router] Error handling message:", error);
    }
  }

  /**
   * Route incoming messages to appropriate services
   */
  routeMessage(message) {
    if (!message || typeof message !== "object") {
      console.warn("⚠️ [Router] Invalid message format:", message);
      return false;
    }

    const { type, ...data } = message;
    // console.log("🔗 [Router] Routing message:", type, data); // Too noisy

    // Route message to appropriate service
    switch (type) {
      case "stt-result":
      case "stt-status":
      case "stt-error":
      case "status":
      case "model-status":
      case "vad_detect_start":
      case "vad_detect_stop":
      case "realtime":
      case "fullSentence":
      case "intelligent_interrupt":
      case "clear_audio_buffers":
      case "pong":
      case "error":
        if (this.sttService) {
          this.sttService.handleWebSocketMessage(message);
        }
        return true;

      case "tts_chunk":
        if (this.ttsService) {
          // this.ttsService.handleTtsChunk(message.content); // Logging is inside the handler
          this.ttsService.handleTtsChunk(message.content);
        }
        return true;

      case "streamingToken":
        // LLM is streaming tokens - this is normal flow, just log for debugging
        console.log("🤖 [Router] LLM streaming token received");
        return true;

      case "quickContext":
        // Quick context detected - first part of response ready for TTS
        console.log(
          "⚡ [Router] Quick context detected - first TTS phase starting"
        );
        return true;

      case "text":
        // Text message from LLM streaming - part of the generation process
        console.log("📝 [Router] LLM text chunk received");
        return true;

      case "streamingComplete":
        // LLM streaming is complete - final TTS should continue until all audio is sent
        console.log(
          "✅ [Router] LLM streaming complete - waiting for final TTS to finish"
        );
        return true;

      default:
        console.warn(`⚠️ [Router] Unknown message type: ${type}`);
        return false;
    }
  }

  /**
   * Send message through master WebSocket connection (single source of truth)
   */
  sendMessage(message) {
    if (!this.isConnected) {
      console.error("❌ [Router] Cannot send message - not connected");
      return false;
    }

    try {
      const messageStr =
        typeof message === "string" ? message : JSON.stringify(message);
      const sent = wsManager.send("unified", messageStr);
      if (sent) {
        console.log(`📤 [Router] Sent message: ${message.type || "string"}`);
      }
      return sent;
    } catch (error) {
      console.error("❌ [Router] Error sending message:", error);
      return false;
    }
  }

  /**
   * Send binary data through master WebSocket connection (single source of truth)
   */
  sendBinaryData(data) {
    if (!this.isConnected) {
      console.error("❌ [Router] Cannot send binary data - not connected");
      return false;
    }

    try {
      const connection = wsManager.connections.get("unified");
      if (connection && connection.websocket) {
        connection.websocket.send(data);
        // console.log("📤 [Router] Sent binary data"); // Too noisy
        return true;
      }
      return false;
    } catch (error) {
      console.error("❌ [Router] Error sending binary data:", error);
      return false;
    }
  }

  /**
   * Handle general status messages
   */
  handleGeneralStatus(data) {
    if (data.status) {
      uiState.updateStatusText(data.status);
    }
    if (data.message) {
      uiState.updateStatusText(data.message);
    }
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      wsStatus: wsManager.getConnectionStatus("unified"),
      hasServices: !!(this.sttService && this.ttsService),
      coordination: "master",
      role: "single_source_of_truth",
    };
  }

  /**
   * Close master connection
   */
  disconnect() {
    console.log("🔗 [Router] Disconnecting master WebSocket");
    wsManager.close("unified");
    this.isConnected = false;

    // Notify services of disconnection
    if (this.sttService) {
      this.sttService.isConnected = false;
      this.sttService.updateStatus("Disconnected");
    }
  }
}

// Create and export singleton instance
export const messageRouter = new MessageRouter();
