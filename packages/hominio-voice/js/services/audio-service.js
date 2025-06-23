/**
 * Audio Service (Reference Implementation Only)
 * Handles AudioWorklet for direct PCM streaming exactly like RealtimeVoiceChat
 */
import { uiState } from "../core/ui-state.js";

export class AudioService {
  constructor() {
    // Reference-style AudioWorklet implementation only
    this.audioContext = null;
    this.ttsWorkletNode = null;
    this.isAudioInitialized = false;
    this.isInitializing = false; // Lock to prevent concurrent initialization
    this.isPlayingTTS = false;
  }

  /**
   * Initialize audio service (main initialization method)
   */
  async initialize() {
    try {
      console.log("🎵 [Audio] Initializing audio service...");

      // Initialize AudioWorklet for PCM streaming
      const success = await this.initializeAudioWorklet();

      if (success) {
        console.log("✅ [Audio] Audio service initialized successfully");
        return true;
      } else {
        console.error("❌ [Audio] Failed to initialize audio service");
        return false;
      }
    } catch (error) {
      console.error("❌ [Audio] Error initializing audio service:", error);
      return false;
    }
  }

  /**
   * Initialize AudioWorklet for PCM audio streaming (reference implementation)
   */
  async initializeAudioWorklet() {
    if (this.isAudioInitialized) {
      return true;
    }

    // Prevent concurrent initialization
    if (this.isInitializing) {
      console.log(
        "🎵 [Audio] AudioWorklet initialization already in progress, waiting..."
      );
      // Wait for current initialization to complete
      while (this.isInitializing && !this.isAudioInitialized) {
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      return this.isAudioInitialized;
    }

    this.isInitializing = true;

    try {
      console.log("🎵 [Audio] Initializing AudioWorklet for PCM streaming...");

      // Check if AudioWorklet is supported and we're in a secure context
      if (!window.AudioContext && !window.webkitAudioContext) {
        throw new Error("AudioContext not supported in this browser");
      }

      if (
        !window.isSecureContext &&
        location.protocol !== "http:" &&
        location.hostname !== "localhost"
      ) {
        console.warn(
          "⚠️ [Audio] AudioWorklet requires a secure context (HTTPS or localhost)"
        );
      }

      // Create AudioContext
      this.audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();

      // Check if AudioWorklet is available
      if (!this.audioContext.audioWorklet) {
        throw new Error("AudioWorklet not supported in this browser");
      }

      // Resume context if needed (required for some browsers)
      if (this.audioContext.state === "suspended") {
        await this.audioContext.resume();
      }

      // Add TTS processor to AudioWorklet
      await this.addTTSProcessor();

      // Create the worklet node (timing fix: ensure processor is loaded first)
      try {
        this.ttsWorkletNode = new AudioWorkletNode(
          this.audioContext,
          "tts-playback-processor"
        );
      } catch (nodeError) {
        console.warn(
          "❌ [Audio] First attempt to create worklet node failed, retrying...",
          nodeError
        );
        // Wait a bit more and retry
        await new Promise((resolve) => setTimeout(resolve, 200));
        this.ttsWorkletNode = new AudioWorkletNode(
          this.audioContext,
          "tts-playback-processor"
        );
      }

      // Set up message handling from worklet
      this.ttsWorkletNode.port.onmessage = (event) => {
        const { type } = event.data;
        if (type === "ttsPlaybackStarted") {
          console.log("🎵 [Audio] TTS playback started");
          this.isPlayingTTS = true;
          uiState.showSpeaking("Audio playing");
        } else if (type === "ttsPlaybackStopped") {
          console.log("🎵 [Audio] TTS playback stopped");
          this.isPlayingTTS = false;
          uiState.showListening("Ready for speech");
        }
      };

      // Connect to audio output
      this.ttsWorkletNode.connect(this.audioContext.destination);

      this.isAudioInitialized = true;
      console.log("✅ [Audio] AudioWorklet initialized successfully");
      return true;
    } catch (error) {
      console.error("❌ [Audio] Failed to initialize AudioWorklet:", error);
      this.isAudioInitialized = false;
      return false;
    } finally {
      this.isInitializing = false;
    }
  }

  /**
   * Add TTS processor to AudioWorklet (reference implementation)
   */
  async addTTSProcessor() {
    const processorCode = `
class TTSPlaybackProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bufferQueue = [];
    this.readOffset = 0;
    this.samplesRemaining = 0;
    this.isPlaying = false;

    // Listen for incoming messages
    this.port.onmessage = (event) => {
      // Check if this is a control message (object with a "type" property)
      if (event.data && typeof event.data === "object" && event.data.type === "clear") {
        // Clear the TTS buffer and reset playback state
        this.bufferQueue = [];
        this.readOffset = 0;
        this.samplesRemaining = 0;
        this.isPlaying = false;
        return;
      }
      
      // Otherwise assume it's a PCM chunk (e.g., an Int16Array)
      if (event.data && event.data.length > 0) {
        this.bufferQueue.push(event.data);
        this.samplesRemaining += event.data.length;
      }
    };
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];
    
    // Ensure we have at least one output channel
    if (!output || output.length === 0) {
      return true;
    }
    
    const outputChannel = output[0];

    if (this.samplesRemaining === 0) {
      // Fill with silence
      outputChannel.fill(0);
      if (this.isPlaying) {
        this.isPlaying = false;
        this.port.postMessage({ type: 'ttsPlaybackStopped' });
      }
      return true;
    }

    if (!this.isPlaying) {
      this.isPlaying = true;
      this.port.postMessage({ type: 'ttsPlaybackStarted' });
    }

    let outIdx = 0;
    while (outIdx < outputChannel.length && this.bufferQueue.length > 0) {
      const currentBuffer = this.bufferQueue[0];
      
      // Convert PCM16 to float32 (-1.0 to 1.0 range)
      const sampleValue = currentBuffer[this.readOffset] / 32768.0;
      outputChannel[outIdx++] = sampleValue;

      this.readOffset++;
      this.samplesRemaining--;

      // Move to next buffer when current one is exhausted
      if (this.readOffset >= currentBuffer.length) {
        this.bufferQueue.shift();
        this.readOffset = 0;
      }
    }

    // Fill remaining samples with silence
    while (outIdx < outputChannel.length) {
      outputChannel[outIdx++] = 0;
    }

    // Keep processor alive
    return true;
  }
}

registerProcessor('tts-playback-processor', TTSPlaybackProcessor);
    `;

    try {
      // Create blob URL for the processor
      const blob = new Blob([processorCode], {
        type: "application/javascript",
      });
      const processorUrl = URL.createObjectURL(blob);

      // Add module to AudioWorklet
      await this.audioContext.audioWorklet.addModule(processorUrl);

      // Clean up blob URL immediately after loading
      URL.revokeObjectURL(processorUrl);

      // Small delay to ensure processor is fully registered
      await new Promise((resolve) => setTimeout(resolve, 50));

      console.log("✅ [Audio] TTS processor registered successfully");
    } catch (error) {
      console.error("❌ [Audio] Failed to add TTS processor:", error);
      throw error;
    }
  }

  /**
   * Clear audio buffer (reference implementation)
   */
  clearAudio() {
    if (this.ttsWorkletNode) {
      this.ttsWorkletNode.port.postMessage({ type: "clear" });
      console.log("🎵 [Audio] Audio buffer cleared");
    }
  }

  /**
   * Check if audio is currently playing
   */
  isPlaying() {
    return this.isPlayingTTS;
  }

  /**
   * Get audio service state
   */
  getState() {
    return {
      isInitialized: this.isAudioInitialized,
      isPlaying: this.isPlayingTTS,
      contextState: this.audioContext?.state || "unknown",
    };
  }
}

// Create and export singleton instance
export const audioService = new AudioService();
