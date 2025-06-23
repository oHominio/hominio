/**
 * Text-to-Speech Service
 * Handles TTS WebSocket communication and model status
 */
import { wsManager } from "./websocket-manager.js";
import { audioService } from "./audio-service.js";
import { uiState } from "../core/ui-state.js";
import { domElements } from "../core/dom-elements.js";
import { messageRouter } from "./message-router.js";

export class TTSService {
  constructor() {
    this.isInitialized = false;
    this.modelStatus = "unknown";
    this.isConnectedForPush = false;
  }

  /**
   * Initialize TTS service
   */
  async initialize() {
    if (this.isInitialized) return;

    // Create unified WebSocket connection for all communication
    wsManager.createConnection("unified", "/ws", {
      onOpen: () => {
        console.log("🔊 [TTS] Connected to unified WebSocket service");
        this.isConnectedForPush = true;
        uiState.updateConnectionStatus("Connected", true);
        uiState.showReady();
      },
      onMessage: (event) => this.handleUnifiedMessage(event),
      onClose: () => {
        console.log("🔊 [TTS] Unified WebSocket service disconnected");
        this.isConnectedForPush = false;
        uiState.updateConnectionStatus("Disconnected");
        uiState.updateStatusText("Connection lost. Reconnecting...");
      },
      onError: (error) => {
        console.error("🔊 [TTS] Unified WebSocket Error:", error);
        this.isConnectedForPush = false;
        uiState.updateConnectionStatus("Error");
        uiState.updateStatusText("Connection error");
      },
      autoReconnect: true,
    });

    // Check initial model status
    await this.checkModelStatus();

    this.isInitialized = true;
  }

  /**
   * Handle unified WebSocket messages - routes through message router
   */
  handleUnifiedMessage(event) {
    try {
      if (typeof event.data === "string") {
        // Check for special string messages first
        if (messageRouter.handleSpecialString(event.data)) {
          return;
        }

        // Try to parse as JSON and route
        try {
          const data = JSON.parse(event.data);
          messageRouter.routeMessage(data);
        } catch (e) {
          console.log("🔊 [TTS] Non-JSON message:", event.data);
        }
      } else {
        // Binary audio data - route through message router
        messageRouter.handleBinaryData(event.data);
      }
    } catch (error) {
      console.error("🔊 [TTS] Error handling unified message:", error);
      uiState.showError("Message processing error");
    }
  }

  /**
   * Handle TTS-specific messages (called by message router)
   */
  handleMessage(data) {
    switch (data.type) {
      case "model-status":
        console.log("🔊 [TTS] Model status update:", data.data);
        const ttsStatus = data.data?.tts || data.data;
        if (ttsStatus) {
          this.modelStatus = ttsStatus.status;
          uiState.updateModelStatus(ttsStatus);
        }
        break;

      case "tts-error":
        console.error("🔊 [TTS] TTS Error:", data.message);
        uiState.showError(`TTS Error: ${data.message}`);
        break;

      default:
        console.log("🔊 [TTS] Unhandled message type:", data.type);
        break;
    }
  }

  /**
   * Handle binary data (called by message router)
   */
  handleBinaryData(data) {
    console.log("🔊 [TTS] Received audio chunk, buffering...");
    uiState.showSpeaking("AI is responding...");
    audioService.addAudioChunk(data);
  }

  /**
   * Handle special string messages (called by message router)
   */
  handleSpecialMessage(message) {
    if (message === "END") {
      console.log("🔊 [TTS] Audio stream ended, playing accumulated audio");
      audioService
        .playAudioChunks()
        .then(() => {
          console.log("🔊 [TTS] Audio playback completed");
          uiState.showListening(
            "Conversation active - listening for speech..."
          );
        })
        .catch((error) => {
          console.error("🔊 [TTS] Audio playback failed:", error);
          uiState.showError("Audio playback failed");
        });
    } else if (message === "ERROR") {
      console.error("🔊 [TTS] Audio generation error");
      uiState.showError("Audio generation failed");
    }
  }

  /**
   * Send TTS synthesis request through unified WebSocket
   */
  async synthesizeText(text) {
    if (!text || !text.trim()) {
      console.warn("🔊 [TTS] Empty text provided for synthesis");
      return;
    }

    const connection = wsManager.connections.get("unified");
    if (
      !connection ||
      !connection.websocket ||
      connection.websocket.readyState !== WebSocket.OPEN
    ) {
      console.error("🔊 [TTS] Unified WebSocket not ready for synthesis");
      uiState.showError("TTS connection not ready");
      return;
    }

    try {
      const message = {
        type: "tts-synthesize",
        text: text.trim(),
      };

      console.log(
        "🔊 [TTS] Sending synthesis request:",
        text.substring(0, 50) + "..."
      );
      connection.websocket.send(JSON.stringify(message));
    } catch (error) {
      console.error("🔊 [TTS] Error sending synthesis request:", error);
      uiState.showError("Failed to send TTS request");
    }
  }

  /**
   * Check model status via HTTP
   */
  async checkModelStatus() {
    try {
      const response = await fetch("/model-status");
      const data = await response.json();
      const ttsStatus = data.tts || data;
      this.modelStatus = ttsStatus.status;
      uiState.updateModelStatus(ttsStatus);
      return ttsStatus;
    } catch (error) {
      console.error("Error checking model status:", error);
      uiState.updateModelStatus({
        status: "error",
        progress: 0,
      });
      return null;
    }
  }

  /**
   * Get current service status
   */
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      modelStatus: this.modelStatus,
      unifiedConnectionStatus: wsManager.getConnectionStatus("unified"),
      isConnectedForPush: this.isConnectedForPush,
    };
  }

  /**
   * Shutdown TTS service
   */
  shutdown() {
    wsManager.close("unified");
    audioService.stopAudio();
    this.isInitialized = false;
    this.isConnectedForPush = false;
  }
}

// Export singleton instance
export const ttsService = new TTSService();
