/**
 * Audio Service
 * Handles audio playback and processing
 */
import { domElements } from "../core/dom-elements.js";
import { uiState } from "../core/ui-state.js";

export class AudioService {
  constructor() {
    this.audioChunks = [];
    this.isReceivingAudio = false;
    this.currentAudioUrl = null;
  }

  /**
   * Add audio chunk to buffer
   */
  addAudioChunk(chunk) {
    if (!this.isReceivingAudio) {
      this.isReceivingAudio = true;
      this.audioChunks = [];
      uiState.updateStatusText("Receiving voice data...", "active");
    }
    this.audioChunks.push(chunk);
  }

  /**
   * Play accumulated audio chunks
   */
  async playAudioChunks() {
    if (this.audioChunks.length === 0) {
      uiState.updateStatusText("No audio data received");
      return false;
    }

    const audioPlayer = domElements.audioPlayer;
    if (!audioPlayer) {
      console.error("Audio player element not found");
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

      // Play audio
      await audioPlayer.play();

      uiState.updateStatusText("Playing audio", "active");

      // Set up event listeners
      this.setupAudioEventListeners(audioPlayer);

      return true;
    } catch (error) {
      console.error("Error playing audio:", error);
      uiState.updateStatusText("Audio playback error");
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
      this.cleanupAudioUrl();
      audioPlayer.style.display = "none";
      uiState.showReady();
      this.resetAudioState();
    };

    audioPlayer.onerror = (error) => {
      console.error("Audio playback error:", error);
      uiState.updateStatusText("Audio playback failed");
      this.resetAudioState();
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
    };
  }
}

// Export singleton instance
export const audioService = new AudioService();
