/**
 * DOM Elements Manager
 * Centralized access to DOM elements with error handling
 */
export class DOMElements {
  constructor() {
    this.elements = {};
    this.initializeElements();
  }

  initializeElements() {
    const elementIds = [
      // TTS elements (manual input removed - only automatic push)
      "statusText",
      "audioPlayer",
      "voiceAvatar",
      "checkStatusButton",

      // STT elements
      "recordButton",
      "clearTranscriptButton",
      "transcriptContent",
      "realtimeText",
      "finalText",
      "sttStatusText",

      // Status elements
      "connectionStatus",
      "voiceEngineStatus",
      "engineStatusText",
    ];

    elementIds.forEach((id) => {
      const element = document.getElementById(id);
      if (!element) {
        console.warn(`Element with ID '${id}' not found`);
      }
      this.elements[id] = element;
    });
  }

  get(elementId) {
    if (!this.elements[elementId]) {
      console.warn(`Element '${elementId}' not available`);
      return null;
    }
    return this.elements[elementId];
  }

  // Convenience getters for commonly used elements
  get recordButton() {
    return this.get("recordButton");
  }
  get statusText() {
    return this.get("statusText");
  }
  get connectionStatus() {
    return this.get("connectionStatus");
  }
  get voiceEngineStatus() {
    return this.get("voiceEngineStatus");
  }
  get engineStatusText() {
    return this.get("engineStatusText");
  }
  get audioPlayer() {
    return this.get("audioPlayer");
  }
  get voiceAvatar() {
    return this.get("voiceAvatar");
  }
  get transcriptContent() {
    return this.get("transcriptContent");
  }
  get realtimeText() {
    return this.get("realtimeText");
  }
  get finalText() {
    return this.get("finalText");
  }
  get sttStatusText() {
    return this.get("sttStatusText");
  }
  get clearTranscriptButton() {
    return this.get("clearTranscriptButton");
  }

  // Static methods for external services
  static getRecordButton() {
    return document.getElementById("recordButton");
  }
}

// Export singleton instance
export const domElements = new DOMElements();
