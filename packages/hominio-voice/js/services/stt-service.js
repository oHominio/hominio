import { domElements } from "../core/dom-elements.js";
import { uiState } from "../core/ui-state.js";
import { wsManager } from "./websocket-manager.js";

/**
 * STT (Speech-to-Text) Service
 * Handles real-time audio recording and WebSocket streaming to backend
 * Now includes potential sentence detection for early LLM processing
 */
export class STTService {
  constructor() {
    this.isConnected = false;
    this.isRecording = false;
    this.isConversationActive = false;
    this.conversationStartTime = null;
    this.audioStream = null;
    this.audioContext = null;
    this.source = null;
    this.processor = null;
    this.sentenceEndPattern = /[.!?]+\s*$/;
    this.sentenceHashes = new Set();

    // Message router reference (set by router during initialization)
    this.messageRouter = null;

    // Callback functions
    this.onPartialTranscription = null;
    this.onFinalTranscription = null;
    this.onError = null;
    this.onStatusChange = null;
    this.onPotentialSentence = null;

    this.setupEventListeners();
  }

  /**
   * Set message router reference (called by message router)
   */
  setMessageRouter(router) {
    this.messageRouter = router;
    console.log("✅ [STT] Message router reference set");
  }

  clearTranscript() {
    console.log("🗑️ Clearing transcript display");

    const realtimeElement = document.getElementById("realtimeText");
    const finalElement = document.getElementById("finalText");

    if (realtimeElement) {
      realtimeElement.textContent = "";
    }

    if (finalElement) {
      finalElement.innerHTML = "";
    }

    this.updateStatus("Transcript cleared");
  }

  async clearConversation() {
    console.log("🧹 Clearing conversation history");

    try {
      const response = await fetch("/clear-conversation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const result = await response.json();
        console.log("✅ Conversation cleared:", result.message);
        this.updateStatus("Conversation history cleared");

        // Also clear the transcript display
        this.clearTranscript();
      } else {
        console.error("❌ Failed to clear conversation:", response.statusText);
        this.updateStatus("Failed to clear conversation");
      }
    } catch (error) {
      console.error("❌ Error clearing conversation:", error);
      this.updateStatus("Error clearing conversation");
    }
  }

  setupEventListeners() {
    // Conversation button event listeners - Start/Stop conversation
    const recordButton = domElements.get("recordButton");
    if (recordButton) {
      // Simple click toggle for start/stop conversation
      recordButton.addEventListener("click", (e) => {
        e.preventDefault();
        this.toggleConversation();
      });
    }

    // Clear transcript button event listener
    const clearButton = document.getElementById("clearTranscriptButton");
    if (clearButton) {
      clearButton.addEventListener("click", (e) => {
        e.preventDefault();
        this.clearTranscript();
      });
    }

    // Clear conversation button event listener
    const clearConversationButton = document.getElementById(
      "clearConversationButton"
    );
    if (clearConversationButton) {
      clearConversationButton.addEventListener("click", (e) => {
        e.preventDefault();
        this.clearConversation();
      });
    }
  }

  /**
   * Handle WebSocket connection through message router only
   */
  async connectWebSocket() {
    // STT service doesn't manage connections - message router does
    if (this.messageRouter && this.messageRouter.isConnected) {
      console.log("🔌 [STT] Using message router's WebSocket connection");
      this.isConnected = true;
      this.updateStatus("Connected through message router");
      return true;
    } else {
      console.log("🔌 [STT] Waiting for message router connection...");
      this.updateStatus("Waiting for message router connection");

      // Wait for message router to be ready (with reduced timeout)
      let attempts = 0;
      const maxAttempts = 5; // Reduced from 10

      while (
        attempts < maxAttempts &&
        (!this.messageRouter || !this.messageRouter.isConnected)
      ) {
        await new Promise((resolve) => setTimeout(resolve, 200)); // Reduced from 500ms
        attempts++;
        console.log(
          `🔌 [STT] Waiting for message router... (${attempts}/${maxAttempts})`
        );
      }

      if (this.messageRouter && this.messageRouter.isConnected) {
        console.log("✅ [STT] Message router connection established");
        this.isConnected = true;
        this.updateStatus("Connected through message router");
        return true;
      } else {
        console.warn(
          "⚠️ [STT] Message router connection timeout - will proceed with local processing"
        );
        this.updateStatus("Local processing only - WebSocket not connected");
        this.isConnected = false;
        return false;
      }
    }
  }

  handleWebSocketMessage(data) {
    console.log("📨 [STT] Received message from server:", data);
    console.log("📨 [STT] Message type:", data.type, "Text:", data.text);

    switch (data.type) {
      case "status":
        console.log("ℹ️ [STT] Status update:", data.message);
        this.updateStatus(data.message);
        break;

      case "stt-status":
        console.log("ℹ️ [STT] STT Status update:", data.message);
        this.updateStatus(data.message);
        break;

      case "model-status":
        console.log("ℹ️ [WebSocket] Model status update:", data.data);
        // Handle model status updates
        break;

      case "vad_detect_start":
        console.log("🎤 [STT] VAD: Voice activity detected");
        uiState.showVADDetected();
        break;

      case "vad_detect_stop":
        console.log("🎤 [STT] VAD: Voice activity stopped");
        if (uiState.getCurrentStates().conversationState === "vad-detected") {
          uiState.showListening();
        }
        break;

      case "realtime":
        console.log("⚡ [STT] Real-time transcription:", data.text);
        // Show thinking state when we get real-time transcription
        if (data.text && data.text.trim()) {
          uiState.showThinking("Processing speech...");

          // Check for potential sentence endings for early LLM processing
          this.checkPotentialSentenceEnd(data.text);
        }
        // Partial/real-time transcription (gray, italic)
        this.displayPartialTranscription(data.text);
        if (this.onPartialTranscription) {
          this.onPartialTranscription(data.text);
        }
        break;

      case "fullSentence":
        console.log("📝 [STT] Final transcription received:", data.text);
        // Show thinking state for LLM processing
        uiState.showThinking("Processing your request...");
        // Complete sentence transcription (simplified backend)
        this.displayFinalTranscription(data.text);
        if (this.onFinalTranscription) {
          this.onFinalTranscription(data.text);
        }
        break;

      case "pong":
        console.log("🏓 [WebSocket] Pong received");
        break;

      case "error":
        console.error("❌ [STT] Server error:", data.message);
        this.handleError(data.message);
        break;

      default:
        console.warn("⚠️ [STT] Unknown message type:", data.type, data);
    }
  }

  updateStatus(message) {
    console.log("STT Status:", message);

    // Update STT status in UI
    const sttStatusElement = document.getElementById("sttStatusText");
    if (sttStatusElement) {
      sttStatusElement.textContent = message;
    }

    if (this.onStatusChange) {
      this.onStatusChange(message);
    }
  }

  displayPartialTranscription(text) {
    const realtimeElement = document.getElementById("realtimeText");
    if (realtimeElement) {
      realtimeElement.textContent = text;
    }
  }

  displayFinalTranscription(text) {
    const finalElement = document.getElementById("finalText");
    const realtimeElement = document.getElementById("realtimeText");

    if (finalElement && text.trim()) {
      // Add to final text with timestamp
      const timestamp = new Date().toLocaleTimeString();
      const transcriptLine = document.createElement("div");
      transcriptLine.className = "transcript-line";
      transcriptLine.style.padding = "0.5rem";
      transcriptLine.style.borderRadius = "8px";
      transcriptLine.style.marginBottom = "0.5rem";
      transcriptLine.textContent = `[${timestamp}] ${text}`;

      // Click-to-copy functionality removed - only automatic STT → LLM → TTS flow

      finalElement.appendChild(transcriptLine);

      // Scroll to bottom
      const transcriptDisplay = document.getElementById("transcriptContent");
      if (transcriptDisplay) {
        transcriptDisplay.scrollTop = transcriptDisplay.scrollHeight;
      }
    }

    // Clear realtime text
    if (realtimeElement) {
      realtimeElement.textContent = "";
    }
  }

  handleError(error) {
    console.error("STT Error:", error);
    this.updateStatus(`Error: ${error}`);

    if (this.onError) {
      this.onError(error);
    }

    // Stop recording on error
    if (this.isRecording) {
      this.stopRecording();
    }
  }

  // Set callback functions
  setOnPartialTranscription(callback) {
    this.onPartialTranscription = callback;
  }

  setOnFinalTranscription(callback) {
    this.onFinalTranscription = callback;
  }

  setOnError(callback) {
    this.onError = callback;
  }

  setOnStatusChange(callback) {
    this.onStatusChange = callback;
  }

  // Cleanup
  disconnect() {
    if (this.isRecording) {
      this.stopRecording();
    }

    // STT service doesn't manage WebSocket - message router does
    this.isConnected = false;
  }

  /**
   * Check for potential sentence endings in real-time transcription
   * This enables early LLM processing for faster response times
   */
  checkPotentialSentenceEnd(text) {
    if (!text || text.trim().length < 10) {
      return; // Too short to be meaningful
    }

    const trimmedText = text.trim();

    // Check if text ends with sentence punctuation
    if (this.sentenceEndPattern.test(trimmedText)) {
      // Avoid processing the same sentence multiple times
      const textHash = this.hashText(trimmedText);
      if (this.sentenceHashes.has(textHash)) {
        return;
      }

      // Add to cache with TTL
      this.sentenceHashes.add(textHash);
      setTimeout(() => {
        this.sentenceHashes.delete(textHash);
      }, 5000); // 5 second TTL

      console.log("🎯 [STT] Potential sentence end detected:", trimmedText);

      // Trigger early LLM processing callback
      if (this.onPotentialSentence) {
        this.onPotentialSentence(trimmedText);
      }
    }
  }

  /**
   * Simple hash function for text deduplication
   */
  hashText(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }

  /**
   * Set callback for potential sentence detection
   */
  setOnPotentialSentence(callback) {
    this.onPotentialSentence = callback;
  }

  /**
   * Toggle conversation session - start if stopped, stop if active
   * Recording is automatic based on VAD when conversation is active
   */
  toggleConversation() {
    if (this.isConversationActive) {
      this.stopConversation();
    } else {
      this.startConversation();
    }
  }

  /**
   * Start conversation session - enables automatic VAD-based recording
   */
  async startConversation() {
    if (this.isConversationActive) return;

    console.log("🎤 [STT] Starting conversation session...");

    try {
      // Update UI to listening state
      uiState.showListening("Conversation active - listening for speech...");

      // Ensure message router connection is ready
      if (!this.isConnected) {
        console.log(
          "🔌 [STT] Message router not connected, attempting connection..."
        );
        await this.connectWebSocket();

        // If still not connected after waiting, continue anyway for local audio processing
        if (!this.isConnected) {
          console.warn("⚠️ [STT] Proceeding with local audio processing only");
          uiState.updateStatusText(
            "Audio processing only - WebSocket not connected"
          );
        }
      }

      console.log("🎙️ [STT] Requesting microphone access for conversation...");

      // Request microphone access for VAD-based recording
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,
        },
      });
      console.log("✅ [STT] Microphone access granted for conversation");

      // Set up audio processing for VAD
      this.audioContext = new AudioContext();

      // Resume context if suspended (required for autoplay policy)
      if (this.audioContext.state === "suspended") {
        await this.audioContext.resume();
        console.log("🎵 [STT] AudioContext resumed");
      }

      this.source = this.audioContext.createMediaStreamSource(this.audioStream);

      // Use ScriptProcessor with proper error handling
      try {
        console.log("🎤 [STT] Setting up audio processing...");
        this.processor = this.audioContext.createScriptProcessor(4096, 1, 1); // Larger buffer for stability
      } catch (error) {
        console.error("❌ [STT] Failed to create audio processor:", error);
        throw error;
      }

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);

      console.log(
        "🎤 Conversation started - VAD will automatically detect speech"
      );
      this.isConversationActive = true;
      this.updateConversationUI(true);

      // Send start command through message router (if available)
      if (this.messageRouter && this.messageRouter.isConnected) {
        console.log("📤 [STT] Enabling VAD for conversation...");
        this.messageRouter.sendMessage({
          type: "stt-command",
          command: "start",
        });
      } else {
        console.warn(
          "⚠️ [STT] Message router not available - audio processing only"
        );
      }

      let audioChunkCount = 0;
      let totalAudioBytes = 0;

      // Process audio data for VAD (server handles recording start/stop)
      this.processor.onaudioprocess = (e) => {
        if (!this.isConversationActive) return;

        const inputData = e.inputBuffer.getChannelData(0);
        const outputData = new Int16Array(inputData.length);

        // Convert to 16-bit PCM
        for (let i = 0; i < inputData.length; i++) {
          outputData[i] = Math.max(
            -32768,
            Math.min(32767, Math.floor(inputData[i] * 32768))
          );
        }

        audioChunkCount++;
        totalAudioBytes += outputData.buffer.byteLength;

        // Send audio data through message router (if available)
        if (this.messageRouter && this.messageRouter.isConnected) {
          try {
            const metadata = JSON.stringify({
              sampleRate: this.audioContext.sampleRate,
            });
            const metadataBytes = new TextEncoder().encode(metadata);
            const metadataLength = new ArrayBuffer(4);
            const metadataLengthView = new DataView(metadataLength);
            metadataLengthView.setInt32(0, metadataBytes.byteLength, true);

            const combinedData = new Blob([
              metadataLength,
              metadataBytes,
              outputData.buffer,
            ]);

            // Send binary data through message router
            this.messageRouter.sendBinaryData(combinedData);
          } catch (error) {
            console.error("❌ [STT] Error sending audio data:", error);
          }
        }

        // Log audio processing status periodically
        if (audioChunkCount % 100 === 0) {
          console.log(
            `🎤 [STT] Processed ${audioChunkCount} audio chunks (${totalAudioBytes} bytes)`
          );
        }
      };

      // Update status
      uiState.updateStatusText("Conversation active - listening for speech");
    } catch (error) {
      console.error("❌ [STT] Failed to start conversation:", error);
      this.handleError("Failed to start conversation: " + error.message);

      // Clean up on error
      this.isConversationActive = false;
      this.updateConversationUI(false);
      uiState.showError("Failed to start conversation");
    }
  }

  /**
   * Stop conversation session - disables VAD and cleans up
   */
  stopConversation() {
    if (!this.isConversationActive) return;

    try {
      console.log("🛑 [STT] Stopping conversation session...");
      this.isConversationActive = false;
      this.isRecording = false; // Also stop any active recording
      this.updateConversationUI(false);

      // Update UI to standby state
      uiState.showStandby("Conversation ended");

      // Send stop command through message router (single source of truth)
      if (this.messageRouter && this.messageRouter.isConnected) {
        console.log("📤 [STT] Disabling VAD for conversation...");
        this.messageRouter.sendMessage({
          type: "stt-command",
          command: "stop",
        });
      }

      console.log("🧹 [STT] Cleaning up conversation resources...");
      // Clean up audio processing
      if (this.processor) {
        this.processor.disconnect();
        this.processor = null;
      }
      if (this.source) {
        this.source.disconnect();
        this.source = null;
      }
      if (this.audioContext) {
        this.audioContext.close();
        this.audioContext = null;
      }
      if (this.audioStream) {
        this.audioStream.getTracks().forEach((track) => track.stop());
        this.audioStream = null;
      }
      console.log("✅ [STT] Conversation cleanup completed");
    } catch (error) {
      console.error("❌ [STT] Error stopping conversation:", error);
    }
  }

  /**
   * Update UI for conversation session state
   */
  updateConversationUI(isActive) {
    const recordButton = domElements.get("recordButton");
    if (recordButton) {
      if (isActive) {
        recordButton.classList.add("recording");
        recordButton.textContent = "🛑 Stop Conversation";
        recordButton.style.background = "#ef4444";
        recordButton.style.color = "white";
      } else {
        recordButton.classList.remove("recording");
        recordButton.textContent = "🎤 Start Conversation";
        recordButton.style.background = "";
        recordButton.style.color = "";
      }
    }
  }
}
