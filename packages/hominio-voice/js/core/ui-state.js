/**
 * UI State Manager
 * Handles all UI state updates and visual feedback
 */
import { domElements } from "./dom-elements.js";

export class UIState {
  constructor() {
    this.currentVoiceState = "";
    this.currentConnectionState = "disconnected";
    this.currentConversationState = "standby"; // New conversation state tracking
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
   * Update conversation state with visual feedback
   * States: standby, listening, vad-detected, thinking, speaking
   */
  updateConversationState(state, message = null) {
    this.currentConversationState = state;

    // Update visual state
    this.updateVoiceState(state);

    // Update status message based on state
    const statusMessages = {
      standby: "Ready to listen...",
      listening: "Listening... (speak now)",
      "vad-detected": "Voice detected! 🎤",
      thinking: "Processing your request...",
      speaking: "Speaking...",
    };

    const statusMessage = message || statusMessages[state] || "Ready";
    this.updateStatusText(statusMessage);

    // Log state change for debugging
    console.log(`🎭 Conversation state: ${state}`);
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
        // Only update to ready if we're not in an active conversation
        if (this.currentConversationState === "standby") {
          this.updateStatusText("Ready to assist you");
        }
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
    this.currentConversationState = "error";
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
    this.updateConversationState("standby", message);
  }

  // New conversation state methods

  /**
   * Set listening state - AI is ready to hear user
   */
  showListening() {
    this.updateConversationState("listening");
  }

  /**
   * Set recording state - user is actively recording
   */
  showRecording(message = "Recording... Click to stop") {
    this.updateConversationState("listening", message);
  }

  /**
   * Set VAD detected state - voice activity detected
   */
  showVADDetected() {
    this.updateConversationState("vad-detected");
  }

  /**
   * Set thinking state - processing transcription and LLM
   */
  showThinking(message = "Processing your request...") {
    this.updateConversationState("thinking", message);
  }

  /**
   * Set speaking state - TTS is playing
   */
  showSpeaking(message = "Speaking...") {
    this.updateConversationState("speaking", message);
  }

  /**
   * Set standby state - default ready state
   */
  showStandby(message = "Ready to listen...") {
    this.updateConversationState("standby", message);
  }

  /**
   * Set interruption state - VAD detected and audio stopped
   * CRITICAL: Shows immediate user feedback when VAD triggers audio interruption
   */
  showInterrupted(reason = "Voice detected") {
    console.log(`🎭🛑 [UI] INTERRUPTION STATE: ${reason}`);

    // Update to interrupted state with visual feedback
    this.updateConversationState("interrupted", `Interrupted: ${reason}`);

    // Set special interrupted avatar class for distinct visual feedback
    const voiceAvatar = domElements.voiceAvatar;
    if (voiceAvatar) {
      voiceAvatar.className = "voice-avatar interrupted";
    }

    // Auto-transition back to listening after brief feedback
    setTimeout(() => {
      if (this.currentConversationState === "interrupted") {
        this.showListening();
        console.log(
          "🎭🔄 [UI] Auto-transitioning from interrupted to listening"
        );
      }
    }, 800); // Brief interruption feedback
  }

  /**
   * Handle audio buffer clear notification
   * Called when backend/frontend clears audio buffers
   */
  handleAudioBufferCleared(source = "unknown") {
    console.log(`🎭🧹 [UI] Audio buffers cleared by: ${source}`);

    // Show brief visual feedback
    const currentMessage = domElements.statusText?.textContent || "";
    this.updateStatusText(`Audio cleared (${source})`, "standby");

    // Reset to appropriate state after brief feedback
    setTimeout(() => {
      if (this.currentConversationState === "standby") {
        this.showListening();
      }
    }, 500);
  }

  /**
   * Get current states
   */
  getCurrentStates() {
    return {
      voiceState: this.currentVoiceState,
      connectionState: this.currentConnectionState,
      conversationState: this.currentConversationState,
    };
  }
}

// Export singleton instance
export const uiState = new UIState();
