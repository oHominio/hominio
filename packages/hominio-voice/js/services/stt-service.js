import { domElements } from "../core/dom-elements.js";
import { uiState } from "../core/ui-state.js";

/**
 * STT (Speech-to-Text) Service
 * Handles real-time audio recording and WebSocket streaming to backend
 * Now includes potential sentence detection for early LLM processing
 */
export class STTService {
  constructor() {
    this.websocket = null;
    this.audioStream = null;
    this.audioContext = null;
    this.source = null;
    this.processor = null;
    this.isRecording = false;
    this.isConnected = false;
    this.isConversationActive = false; // New: tracks if conversation session is active

    // Callbacks
    this.onPartialTranscription = null;
    this.onFinalTranscription = null;
    this.onError = null;
    this.onStatusChange = null;
    this.onPotentialSentence = null; // New callback for potential sentence detection

    // Potential sentence detection
    this.lastPartialText = "";
    this.sentenceEndPattern = /[.!?]+\s*$/; // Pattern for sentence endings
    this.potentialSentenceCache = new Set(); // Cache to avoid duplicates

    this.setupEventListeners();
  }

  clearTranscript() {
    const finalElement = document.getElementById("finalText");
    const realtimeElement = document.getElementById("realtimeText");

    if (finalElement) {
      finalElement.innerHTML = "";
    }
    if (realtimeElement) {
      realtimeElement.textContent = "";
    }

    this.updateStatus("Transcript cleared");
  }

  setupEventListeners() {
    // Conversation button event listeners - Start/Stop conversation session
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
  }

  async connectWebSocket() {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/ws/stt`;

      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log("🔌 STT WebSocket connected");
        this.isConnected = true;
        this.updateStatus("Connected to STT service");
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error("Error parsing STT WebSocket message:", error);
        }
      };

      this.websocket.onclose = () => {
        console.log("🔌 STT WebSocket disconnected");
        this.isConnected = false;
        this.updateStatus("Disconnected from STT service");
      };

      this.websocket.onerror = (error) => {
        console.error("STT WebSocket error:", error);
        this.handleError("WebSocket connection failed");
      };
    } catch (error) {
      console.error("Failed to connect STT WebSocket:", error);
      this.handleError("Failed to connect to STT service");
    }
  }

  handleWebSocketMessage(data) {
    console.log("📨 [STT] Received message from server:", data);

    switch (data.type) {
      case "status":
        console.log("ℹ️ [STT] Status update:", data.message);
        this.updateStatus(data.message);
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

    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }

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
      if (this.potentialSentenceCache.has(textHash)) {
        return;
      }

      // Add to cache with TTL
      this.potentialSentenceCache.add(textHash);
      setTimeout(() => {
        this.potentialSentenceCache.delete(textHash);
      }, 5000); // 5 second TTL

      console.log("🎯 [STT] Potential sentence end detected:", trimmedText);

      // Trigger early LLM processing callback
      if (this.onPotentialSentence) {
        this.onPotentialSentence(trimmedText);
      }
    }

    this.lastPartialText = trimmedText;
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

      // Connect WebSocket if not connected
      if (!this.isConnected) {
        console.log("🔌 [STT] Connecting to WebSocket...");
        await this.connectWebSocket();
        // Wait a bit for connection to establish
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      console.log("🎙️ [STT] Requesting microphone access for conversation...");
      // Request microphone access for VAD-based recording
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      console.log("✅ [STT] Microphone access granted for conversation");

      // Set up audio processing for VAD
      this.audioContext = new AudioContext();
      this.source = this.audioContext.createMediaStreamSource(this.audioStream);
      this.processor = this.audioContext.createScriptProcessor(256, 1, 1);

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);

      console.log(
        "🎤 Conversation started - VAD will automatically detect speech"
      );
      this.isConversationActive = true;
      this.updateConversationUI(true);

      // Send start command to enable VAD on server
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        console.log("📤 [STT] Enabling VAD for conversation...");
        this.websocket.send(JSON.stringify({ command: "start" }));
      } else {
        console.error("❌ [STT] WebSocket not ready for conversation start");
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

        // Send audio data for VAD processing
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
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

          this.websocket.send(combinedData);
        }
      };
    } catch (error) {
      console.error("❌ [STT] Failed to start conversation:", error);
      this.handleError("Failed to start conversation");
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

      // Send stop command to disable VAD
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        console.log("📤 [STT] Disabling VAD for conversation...");
        this.websocket.send(JSON.stringify({ command: "stop" }));
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
