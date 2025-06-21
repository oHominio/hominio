/**
 * Audio Service
 * Handles audio playback and processing with visual state integration
 */
import { domElements } from "../core/dom-elements.js";
import { uiState } from "../core/ui-state.js";

export class AudioService {
  constructor() {
    this.audioChunks = [];
    this.isReceivingAudio = false;
    this.currentAudioUrl = null;
    this.lastPlayedText = "";
    this.lastPlayedTimestamp = 0;
  }

  /**
   * Check if we should skip audio to prevent looping
   */
  shouldSkipAudio(identifier = null) {
    const currentTime = Date.now();

    // If we have an identifier (like text hash), check for duplicates
    if (identifier) {
      if (
        identifier === this.lastPlayedText &&
        currentTime - this.lastPlayedTimestamp < 5000
      ) {
        // 5 second window
        console.warn("🔄 Skipping duplicate audio playback");
        return true;
      }
      this.lastPlayedText = identifier;
    }

    this.lastPlayedTimestamp = currentTime;
    return false;
  }

  /**
   * Add audio chunk to buffer
   */
  addAudioChunk(chunk) {
    if (!this.isReceivingAudio) {
      this.isReceivingAudio = true;
      this.audioChunks = [];
      // Update to speaking state when we start receiving audio
      uiState.showSpeaking("Receiving voice data...");
    }
    this.audioChunks.push(chunk);
  }

  /**
   * Play accumulated audio chunks
   */
  async playAudioChunks() {
    if (this.audioChunks.length === 0) {
      uiState.showStandby("No audio data received");
      return false;
    }

    // Check for duplicate audio (simple check based on chunk count and size)
    const audioIdentifier = `${this.audioChunks.length}_${this.audioChunks[0]?.byteLength || 0}`;
    if (this.shouldSkipAudio(audioIdentifier)) {
      uiState.showStandby("Duplicate audio skipped");
      this.resetAudioState();
      return false;
    }

    const audioPlayer = domElements.audioPlayer;
    if (!audioPlayer) {
      console.error("Audio player element not found");
      uiState.showStandby("Audio player not found");
      return false;
    }

    try {
      // Clean up previous audio URL
      this.cleanupAudioUrl();

      // Create new audio blob
      const audioBlob = new Blob(this.audioChunks, { type: "audio/wav" });
      this.currentAudioUrl = URL.createObjectURL(audioBlob);

      // Set up audio player
      audioPlayer.src = this.currentAudioUrl;
      audioPlayer.style.display = "block";

      // Update to speaking state
      uiState.showSpeaking("Playing audio");

      // Play audio
      await audioPlayer.play();

      // Set up event listeners
      this.setupAudioEventListeners(audioPlayer);

      return true;
    } catch (error) {
      console.error("Error playing audio:", error);
      uiState.showStandby("Audio playback error");
      this.resetAudioState();
      return false;
    }
  }

  /**
   * Set up audio player event listeners
   */
  setupAudioEventListeners(audioPlayer) {
    // Remove existing listeners to prevent duplicates
    audioPlayer.onended = null;
    audioPlayer.onerror = null;

    audioPlayer.onended = () => {
      console.log("🔊 Audio playback ended");
      this.cleanupAudioUrl();
      audioPlayer.style.display = "none";

      // Return to standby state after audio ends
      uiState.showStandby();
      this.resetAudioState();
    };

    audioPlayer.onerror = (error) => {
      console.error("Audio playback error:", error);
      uiState.showStandby("Audio playback failed");
      this.resetAudioState();
    };

    // Add additional event listeners for better state tracking
    audioPlayer.onplay = () => {
      console.log("🔊 Audio playback started");
      uiState.showSpeaking("Audio playing");
    };

    audioPlayer.onpause = () => {
      console.log("🔊 Audio playback paused");
      uiState.showStandby("Audio paused");
    };
  }

  /**
   * Clean up audio URL to prevent memory leaks
   */
  cleanupAudioUrl() {
    if (this.currentAudioUrl) {
      URL.revokeObjectURL(this.currentAudioUrl);
      this.currentAudioUrl = null;
    }
  }

  /**
   * Reset audio state
   */
  resetAudioState() {
    this.audioChunks = [];
    this.isReceivingAudio = false;
    this.cleanupAudioUrl();
  }

  /**
   * Stop current audio playback
   */
  stopAudio() {
    const audioPlayer = domElements.audioPlayer;
    if (audioPlayer && !audioPlayer.paused) {
      audioPlayer.pause();
      audioPlayer.currentTime = 0;
    }
    this.resetAudioState();
    uiState.showStandby("Audio stopped");
  }

  /**
   * Check if audio is currently playing
   */
  isPlaying() {
    const audioPlayer = domElements.audioPlayer;
    return audioPlayer && !audioPlayer.paused;
  }

  /**
   * Get audio processing state
   */
  getState() {
    return {
      isReceivingAudio: this.isReceivingAudio,
      chunksCount: this.audioChunks.length,
      isPlaying: this.isPlaying(),
      hasCurrentUrl: !!this.currentAudioUrl,
    };
  }
}

// Export singleton instance
export const audioService = new AudioService();
