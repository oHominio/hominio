import { domElements } from "../core/dom-elements.js";
import { uiState } from "../core/ui-state.js";

/**
 * STT (Speech-to-Text) Service
 * Handles real-time audio recording and WebSocket streaming to backend
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

    // Callbacks
    this.onPartialTranscription = null;
    this.onFinalTranscription = null;
    this.onError = null;
    this.onStatusChange = null;

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
    // Record button event listeners
    const recordButton = domElements.get("recordButton");
    if (recordButton) {
      // Mouse events for desktop
      recordButton.addEventListener("mousedown", (e) => {
        e.preventDefault();
        this.startRecording();
      });

      recordButton.addEventListener("mouseup", (e) => {
        e.preventDefault();
        this.stopRecording();
      });

      recordButton.addEventListener("mouseleave", (e) => {
        e.preventDefault();
        if (this.isRecording) {
          this.stopRecording();
        }
      });

      // Touch events for mobile
      recordButton.addEventListener("touchstart", (e) => {
        e.preventDefault();
        this.startRecording();
      });

      recordButton.addEventListener("touchend", (e) => {
        e.preventDefault();
        this.stopRecording();
      });

      recordButton.addEventListener("touchcancel", (e) => {
        e.preventDefault();
        if (this.isRecording) {
          this.stopRecording();
        }
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

      case "realtime":
        console.log("⚡ [STT] Real-time transcription:", data.text);
        // Partial/real-time transcription (gray, italic)
        this.displayPartialTranscription(data.text);
        if (this.onPartialTranscription) {
          this.onPartialTranscription(data.text);
        }
        break;

      case "fullSentence":
        console.log("📝 [STT] Final transcription received:", data.text);
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

  async startRecording() {
    if (this.isRecording) return;

    console.log("🎤 [STT] Starting recording process...");

    try {
      // Connect WebSocket if not connected
      if (!this.isConnected) {
        console.log("🔌 [STT] Connecting to WebSocket...");
        await this.connectWebSocket();
        // Wait a bit for connection to establish
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      console.log("🎙️ [STT] Requesting microphone access...");
      // Request microphone access (following browser client example exactly)
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      console.log("✅ [STT] Microphone access granted");

      // Create AudioContext for raw PCM processing (like browser client example)
      this.audioContext = new AudioContext();
      console.log(
        `🔊 [STT] AudioContext created, sample rate: ${this.audioContext.sampleRate}Hz`
      );

      this.source = this.audioContext.createMediaStreamSource(this.audioStream);
      this.processor = this.audioContext.createScriptProcessor(256, 1, 1);

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);

      console.log("🎤 Recording started");
      this.isRecording = true;
      this.updateRecordingUI(true);

      // Send start command
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        console.log("📤 [STT] Sending start command to server...");
        this.websocket.send(JSON.stringify({ type: "start" }));
      } else {
        console.error("❌ [STT] WebSocket not ready for start command");
      }

      let audioChunkCount = 0;
      let totalAudioBytes = 0;

      // Process audio data exactly like browser client example
      this.processor.onaudioprocess = (e) => {
        if (!this.isRecording) return;

        const inputData = e.inputBuffer.getChannelData(0);
        const outputData = new Int16Array(inputData.length);

        // Convert to 16-bit PCM (exactly like browser client example)
        for (let i = 0; i < inputData.length; i++) {
          outputData[i] = Math.max(
            -32768,
            Math.min(32767, Math.floor(inputData[i] * 32768))
          );
        }

        audioChunkCount++;
        totalAudioBytes += outputData.buffer.byteLength;

        // Log every 50th chunk to avoid spam
        if (audioChunkCount % 50 === 0) {
          console.log(
            `🎵 [STT] Processed ${audioChunkCount} audio chunks, ${totalAudioBytes} bytes total`
          );
        }

        // Send the 16-bit PCM data to the server (exactly like browser client example)
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
          // Create a JSON string with metadata
          const metadata = JSON.stringify({
            sampleRate: this.audioContext.sampleRate,
          });
          // Convert metadata to a byte array
          const metadataBytes = new TextEncoder().encode(metadata);
          // Create a buffer for metadata length (4 bytes for 32-bit integer)
          const metadataLength = new ArrayBuffer(4);
          const metadataLengthView = new DataView(metadataLength);
          // Set the length of the metadata in the first 4 bytes
          metadataLengthView.setInt32(0, metadataBytes.byteLength, true); // true for little-endian
          // Combine metadata length, metadata, and audio data into a single message
          const combinedData = new Blob([
            metadataLength,
            metadataBytes,
            outputData.buffer,
          ]);

          // Log first few chunks in detail
          if (audioChunkCount <= 3) {
            console.log(`📤 [STT] Sending audio chunk ${audioChunkCount}:`, {
              metadataLength: metadataBytes.byteLength,
              audioLength: outputData.buffer.byteLength,
              totalSize: combinedData.size,
              sampleRate: this.audioContext.sampleRate,
            });
          }

          this.websocket.send(combinedData);
        } else {
          console.error("❌ [STT] WebSocket not ready for audio data");
        }
      };
    } catch (error) {
      console.error("❌ [STT] Failed to start recording:", error);
      this.handleError("Failed to access microphone");
    }
  }

  stopRecording() {
    if (!this.isRecording) return;

    try {
      console.log("🛑 [STT] Stopping recording...");
      this.isRecording = false;
      this.updateRecordingUI(false);

      // Send stop command
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        console.log("📤 [STT] Sending stop command to server...");
        this.websocket.send(JSON.stringify({ type: "stop" }));
      } else {
        console.error("❌ [STT] WebSocket not ready for stop command");
      }

      console.log("🧹 [STT] Cleaning up audio resources...");
      // Clean up audio processing (following browser client example)
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
      console.log("✅ [STT] Audio cleanup completed");
    } catch (error) {
      console.error("❌ [STT] Error stopping recording:", error);
    }
  }

  updateRecordingUI(isRecording) {
    const recordButton = domElements.get("recordButton");
    if (recordButton) {
      if (isRecording) {
        recordButton.classList.add("recording");
        recordButton.textContent = "🔴 Recording...";
        recordButton.style.background = "#ef4444";
      } else {
        recordButton.classList.remove("recording");
        recordButton.textContent = "🎤 Hold to Record";
        recordButton.style.background = "";
      }
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
      // Add to final text with timestamp and clickable styling
      const timestamp = new Date().toLocaleTimeString();
      const transcriptLine = document.createElement("div");
      transcriptLine.className = "transcript-line";
      transcriptLine.style.cursor = "pointer";
      transcriptLine.style.padding = "0.5rem";
      transcriptLine.style.borderRadius = "8px";
      transcriptLine.style.marginBottom = "0.5rem";
      transcriptLine.style.transition = "background-color 0.2s";
      transcriptLine.textContent = `[${timestamp}] ${text}`;

      // Add hover effect
      transcriptLine.addEventListener("mouseenter", () => {
        transcriptLine.style.backgroundColor = "rgba(126, 212, 173, 0.1)";
      });
      transcriptLine.addEventListener("mouseleave", () => {
        transcriptLine.style.backgroundColor = "";
      });

      // Add click handler to copy to TTS input
      transcriptLine.addEventListener("click", () => {
        const messageText = document.getElementById("messageText");
        if (messageText) {
          messageText.value = text.trim();
          messageText.focus();

          // Visual feedback
          transcriptLine.style.backgroundColor = "rgba(126, 212, 173, 0.2)";
          setTimeout(() => {
            transcriptLine.style.backgroundColor = "";
          }, 1000);
        }
      });

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
}
