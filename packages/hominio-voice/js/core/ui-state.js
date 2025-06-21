/**
 * UI State Manager
 * Handles all UI state updates and visual feedback
 */
import { domElements } from "./dom-elements.js";

export class UIState {
  constructor() {
    this.currentVoiceState = "";
    this.currentConnectionState = "disconnected";
    this.initializeGreeting();
  }

  /**
   * Update connection status display
   */
  updateConnectionStatus(status, connected = false) {
    const connectionStatus = domElements.connectionStatus;
    if (!connectionStatus) return;

    connectionStatus.textContent = status;
    connectionStatus.className = `connection-status ${connected ? "connected" : ""}`;
    this.currentConnectionState = connected ? "connected" : "disconnected";
  }

  /**
   * Update voice avatar state with animation
   */
  updateVoiceState(state) {
    const voiceAvatar = domElements.voiceAvatar;
    if (!voiceAvatar) return;

    this.currentVoiceState = state;
    voiceAvatar.className = `voice-avatar ${state}`;
  }

  /**
   * Update status text with optional state
   */
  updateStatusText(message, voiceState = null) {
    const statusText = domElements.statusText;
    if (!statusText) return;

    statusText.textContent = message;

    if (voiceState) {
      this.updateVoiceState(voiceState);
    }
  }

  /**
   * Update model status display
   */
  updateModelStatus(status) {
    const sendButton = domElements.sendButton;
    const voiceEngineStatus = domElements.voiceEngineStatus;
    const engineStatusText = domElements.engineStatusText;

    if (sendButton) {
      sendButton.disabled = status.status !== "ready";
    }

    if (voiceEngineStatus) {
      // Remove existing status classes
      voiceEngineStatus.className = "voice-engine-status";

      if (status.status === "ready") {
        voiceEngineStatus.classList.add("ready");
        if (engineStatusText) engineStatusText.textContent = "Ready";
        this.updateStatusText("Ready to assist you");
      } else if (status.status === "error") {
        voiceEngineStatus.classList.add("error");
        if (engineStatusText) engineStatusText.textContent = "Error";
        this.updateStatusText("Voice engine error");
      } else {
        voiceEngineStatus.classList.add("loading");
        if (engineStatusText)
          engineStatusText.textContent = `${Math.round(status.progress)}%`;
        this.updateStatusText("Preparing voice engine...");
      }
    }
  }

  /**
   * Initialize time-based greeting
   */
  initializeGreeting() {
    const greeting = domElements.greeting;
    if (!greeting) return;

    const hour = new Date().getHours();

    if (hour < 12) {
      greeting.textContent = "Good morning";
    } else if (hour < 17) {
      greeting.textContent = "Good afternoon";
    } else {
      greeting.textContent = "Good evening";
    }
  }

  /**
   * Show error state
   */
  showError(message) {
    this.updateStatusText(message);
    this.updateVoiceState("error");
  }

  /**
   * Show loading state
   */
  showLoading(message) {
    this.updateStatusText(message);
    this.updateVoiceState("loading");
  }

  /**
   * Show ready state
   */
  showReady(message = "Ready to assist you") {
    this.updateStatusText(message);
    this.updateVoiceState("");
  }

  /**
   * Get current states
   */
  getCurrentStates() {
    return {
      voiceState: this.currentVoiceState,
      connectionState: this.currentConnectionState,
    };
  }
}

// Export singleton instance
export const uiState = new UIState();
