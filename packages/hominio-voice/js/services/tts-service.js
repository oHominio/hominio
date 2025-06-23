/**
 * TTS Service
 * Handles text-to-speech synthesis and audio playback using reference implementation
 */
import { uiState } from "../core/ui-state.js";
import { audioService } from "./audio-service.js";

export class TTSService {
  constructor() {
    this.isInitialized = false;
    this.modelStatus = "initializing";

    // Message router reference (set by router during initialization)
    this.messageRouter = null;
  }

  /**
   * Set message router reference (called by message router)
   */
  setMessageRouter(router) {
    this.messageRouter = router;
    console.log("✅ [TTS] Message router reference set");
  }

  /**
   * Initialize TTS service
   */
  async initialize() {
    try {
      console.log("🔊 [TTS] Initializing TTS service...");

      // Initialize audio service for playback
      await audioService.initialize();

      this.isInitialized = true;
      console.log("✅ [TTS] TTS service initialized");
    } catch (error) {
      console.error("❌ [TTS] Failed to initialize:", error);
      throw error;
    }
  }

  /**
   * Handle tts_chunk messages (reference implementation)
   */
  handleTtsChunk(base64Content) {
    try {
      // Validate input
      if (!base64Content || typeof base64Content !== "string") {
        console.error(
          "❌ [TTS] Invalid base64Content:",
          typeof base64Content,
          base64Content
        );
        return;
      }

      // Log chunk info for debugging
      console.log(
        `🔊 [TTS] Processing chunk: length=${base64Content.length}, first10=${base64Content.substring(0, 10)}`
      );

      // Convert base64 to Int16Array (reference format)
      const binaryString = atob(base64Content);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const int16Array = new Int16Array(bytes.buffer);

      console.log(
        `🔊 [TTS] Converted to Int16Array: length=${int16Array.length}`
      );

      // Send directly to AudioWorklet (reference-style)
      if (audioService.ttsWorkletNode) {
        audioService.ttsWorkletNode.port.postMessage(int16Array);
        console.log(
          `🔊 [TTS] Sent ${int16Array.length} samples to AudioWorklet`
        );
      } else {
        console.log("🔊 [TTS] AudioWorklet not ready, initializing...");
        // Initialize AudioWorklet if not ready
        audioService.initializeAudioWorklet().then(() => {
          if (audioService.ttsWorkletNode) {
            audioService.ttsWorkletNode.port.postMessage(int16Array);
            console.log(
              `🔊 [TTS] Sent ${int16Array.length} samples to AudioWorklet (after init)`
            );
          }
        });
      }
    } catch (error) {
      console.error("❌ [TTS] Error processing tts_chunk:", error);
    }
  }

  /**
   * Handle model status updates
   */
  handleModelStatus(data) {
    const ttsStatus = data.data?.tts || data.data;
    if (ttsStatus) {
      this.modelStatus = ttsStatus.status;
      uiState.updateModelStatus(ttsStatus);
    }
  }

  /**
   * Get service status
   */
  getStatus() {
    return {
      status: this.isInitialized ? "ready" : "initializing",
      modelStatus: this.modelStatus,
      isInitialized: this.isInitialized,
    };
  }

  /**
   * Check if service is ready
   */
  isReady() {
    return this.isInitialized && this.modelStatus === "ready";
  }
}

// Export singleton instance
export const ttsService = new TTSService();
