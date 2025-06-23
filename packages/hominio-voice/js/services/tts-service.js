/**
 * TTS Service (Simplified Reference Implementation)
 * Handles text-to-speech synthesis and audio playback exactly like RealtimeVoiceChat
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
   * Handle tts_chunk messages (exact reference implementation)
   */
  handleTtsChunk(base64Content) {
    if (!this.isInitialized) {
      console.warn(
        "🔊 [TTS] Received chunk but service not initialized. Initializing now..."
      );
      this.initialize().then(() => this.processTtsChunk(base64Content));
      return;
    }
    this.processTtsChunk(base64Content);
  }

  processTtsChunk(base64Content) {
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

      // Log chunk info for debugging - REMOVED as too noisy
      // console.log(`🔊 [TTS] Processing chunk: length=${base64Content.length}`);

      // Convert base64 to Int16Array (exact reference implementation)
      const int16Data = this.base64ToInt16Array(base64Content);

      if (!int16Data || int16Data.length === 0) {
        // console.warn("🔊 [TTS] Empty or invalid audio data after conversion"); // Also too noisy
        return;
      }

      // console.log(
      //   `🔊 [TTS] Converted to Int16Array: length=${int16Data.length}`
      // );

      // Send directly to AudioWorklet (reference-style)
      if (audioService.ttsWorkletNode) {
        audioService.ttsWorkletNode.port.postMessage(int16Data);
        // console.log(
        //   `🔊 [TTS] Sent ${int16Data.length} samples to AudioWorklet`
        // );
      } else {
        console.log("🔊 [TTS] AudioWorklet not ready, initializing...");
        // Initialize AudioWorklet if not ready
        audioService.initializeAudioWorklet().then(() => {
          if (audioService.ttsWorkletNode) {
            audioService.ttsWorkletNode.port.postMessage(int16Data);
            // console.log(
            //   `🔊 [TTS] Sent ${int16Data.length} samples to AudioWorklet (after init)`
            // );
          }
        });
      }
    } catch (error) {
      console.error("❌ [TTS] Error processing tts_chunk:", error);
    }
  }

  /**
   * Convert base64 to Int16Array (exact reference implementation)
   */
  base64ToInt16Array(base64String) {
    try {
      if (!base64String) {
        console.warn("🔊 [TTS] base64ToInt16Array received empty string.");
        return new Int16Array(0);
      }
      // Decode base64 to binary string
      const binaryString = atob(base64String);

      // Create Uint8Array from binary string
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Convert to Int16Array (PCM audio data)
      const int16Array = new Int16Array(bytes.buffer);

      return int16Array;
    } catch (error) {
      console.error("❌ [TTS] Error converting base64 to Int16Array:", error);
      return null;
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
