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
    this.isConnectedForPush = false; // Track TTS push connection
  }

  /**
   * Initialize TTS service
   */
  async initialize() {
    if (this.isInitialized) return;

    // Create TTS push WebSocket connection for automatic conversation responses
    wsManager.createConnection("tts-push", "/ws/tts-push", {
      onOpen: () => {
        console.log("🔊 [TTS] Connected to TTS push service");
        this.isConnectedForPush = true;
      },
      onMessage: (event) => this.handleTTSPushMessage(event),
      onClose: () => {
        console.log("🔊 [TTS] TTS push service disconnected");
        this.isConnectedForPush = false;
      },
      onError: (error) => {
        console.error("🔊 [TTS] TTS push WebSocket Error:", error);
        this.isConnectedForPush = false;
      },
      autoReconnect: true,
    });

    // Create model status WebSocket connection
    wsManager.createConnection("model-status", "/ws/model-status", {
      onOpen: () => {
        uiState.updateConnectionStatus("Connected", true);
        uiState.showReady();
      },
      onMessage: (event) => this.handleModelStatusMessage(event),
      onClose: () => {
        uiState.updateConnectionStatus("Disconnected");
        uiState.updateStatusText("Connection lost. Reconnecting...");
      },
      onError: (error) => {
        console.error("Model Status WebSocket Error:", error);
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
   * Handle TTS push WebSocket messages (automatic conversation responses)
   */
  handleTTSPushMessage(event) {
    try {
      if (typeof event.data === "string") {
        if (event.data === "END") {
          console.log("🔊 [TTS] Audio stream ended, playing accumulated audio");
          // Play all accumulated audio chunks when stream ends
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
          return;
        }

        if (event.data === "ERROR") {
          console.error("🔊 [TTS] Audio generation error");
          uiState.showError("Audio generation failed");
          return;
        }

        try {
          const data = JSON.parse(event.data);
          if (data.type === "status") {
            console.log("🔊 [TTS] Status:", data.message);
            uiState.updateStatusText(data.message);
          }
        } catch (e) {
          console.log("🔊 [TTS] Non-JSON message:", event.data);
        }
      } else {
        // Binary audio data - add to buffer
        console.log("🔊 [TTS] Received audio chunk, buffering...");
        uiState.showSpeaking("AI is responding...");
        audioService.addAudioChunk(event.data);
      }
    } catch (error) {
      console.error("🔊 [TTS] Error handling TTS push message:", error);
      uiState.showError("Audio processing error");
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

  // Manual TTS synthesis removed - only automatic push from STT → LLM → TTS

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
      modelConnectionStatus: wsManager.getConnectionStatus("model-status"),
      pushConnectionStatus: wsManager.getConnectionStatus("tts-push"),
      isConnectedForPush: this.isConnectedForPush,
    };
  }

  /**
   * Shutdown TTS service
   */
  shutdown() {
    wsManager.close("model-status");
    wsManager.close("tts-push");
    audioService.stopAudio();
    this.isInitialized = false;
    this.isConnectedForPush = false;
  }
}

// Export singleton instance
export const ttsService = new TTSService();
