/**
 * Text-to-Speech Service
 * Handles TTS WebSocket communication and model status
 */
import { wsManager } from "./websocket-manager.js";
import { audioService } from "./audio-service.js";
import { uiState } from "../core/ui-state.js";
import { domElements } from "../core/dom-elements.js";

export class TTSService {
  constructor() {
    this.isInitialized = false;
    this.modelStatus = "unknown";
  }

  /**
   * Initialize TTS service
   */
  async initialize() {
    if (this.isInitialized) return;

    // Create TTS WebSocket connection
    wsManager.createConnection("tts", "/ws/tts", {
      onOpen: () => {
        uiState.updateConnectionStatus("Connected", true);
        uiState.showReady();
      },
      onMessage: (event) => this.handleTTSMessage(event),
      onClose: () => {
        uiState.updateConnectionStatus("Disconnected");
        uiState.updateStatusText("Connection lost. Reconnecting...");
      },
      onError: (error) => {
        console.error("TTS WebSocket Error:", error);
        uiState.updateConnectionStatus("Error");
        uiState.updateStatusText("Connection error");
      },
    });

    // Create model status WebSocket connection
    wsManager.createConnection("model-status", "/ws/model-status", {
      onMessage: (event) => this.handleModelStatusMessage(event),
      autoReconnect: true,
    });

    // Check initial model status
    await this.checkModelStatus();

    this.isInitialized = true;
  }

  /**
   * Handle TTS WebSocket messages
   */
  handleTTSMessage(event) {
    if (typeof event.data === "string") {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "status") {
          uiState.updateStatusText(data.message);
          return;
        }
      } catch (e) {
        // Handle non-JSON string messages
        if (event.data === "END") {
          uiState.updateStatusText("Voice synthesis complete");
          uiState.updateVoiceState("");
          audioService.playAudioChunks();
        } else if (event.data.startsWith("ERROR:")) {
          uiState.updateStatusText(event.data);
          uiState.updateVoiceState("");
        }
      }
    } else if (event.data instanceof Blob) {
      // Handle audio chunks
      audioService.addAudioChunk(event.data);
    }
  }

  /**
   * Handle model status WebSocket messages
   */
  handleModelStatusMessage(event) {
    try {
      const data = JSON.parse(event.data);
      // Handle nested structure: {tts: {...}, stt: {...}}
      const ttsStatus = data.tts || data;
      this.modelStatus = ttsStatus.status;
      uiState.updateModelStatus(ttsStatus);
    } catch (e) {
      console.error("Error parsing model status:", e);
    }
  }

  /**
   * Send text for TTS synthesis
   */
  async sendText(text) {
    if (!text || !text.trim()) {
      uiState.updateStatusText("Please enter some text to speak");
      return false;
    }

    if (wsManager.getConnectionStatus("tts") !== "connected") {
      uiState.updateStatusText("Not connected to voice engine");
      return false;
    }

    if (this.modelStatus !== "ready") {
      uiState.updateStatusText("Voice engine not ready");
      return false;
    }

    // Reset audio state and send text
    audioService.resetAudioState();

    const success = wsManager.send("tts", text);
    if (success) {
      uiState.updateStatusText("Synthesizing voice...", "listening");
    } else {
      uiState.updateStatusText("Failed to send text");
    }

    return success;
  }

  /**
   * Check model status via HTTP
   */
  async checkModelStatus() {
    try {
      const response = await fetch("/model-status");
      const data = await response.json();
      // Handle nested structure: {tts: {...}, stt: {...}}
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
      connectionStatus: wsManager.getConnectionStatus("tts"),
      modelConnectionStatus: wsManager.getConnectionStatus("model-status"),
    };
  }

  /**
   * Shutdown TTS service
   */
  shutdown() {
    wsManager.close("tts");
    wsManager.close("model-status");
    audioService.stopAudio();
    this.isInitialized = false;
  }
}

// Export singleton instance
export const ttsService = new TTSService();
