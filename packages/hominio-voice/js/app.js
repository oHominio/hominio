/**
 * Main Application Entry Point
 * Orchestrates all services and handles user interactions
 */

// Debug logging for module loading
console.log("🚀 Loading Hominio Voice App...");

// Import modules with error handling
try {
  console.log("📦 Importing modules...");
} catch (error) {
  console.error("❌ Error importing modules:", error);
}

import { domElements } from "./core/dom-elements.js";
import { uiState } from "./core/ui-state.js";
import { ttsService } from "./services/tts-service.js";
import { wsManager } from "./services/websocket-manager.js";
import { STTService } from "./services/stt-service.js";

console.log("✅ All modules imported successfully");

class HominiVoiceApp {
  constructor() {
    this.isInitialized = false;
    this.eventListeners = [];
    this.sttService = new STTService();
  }

  /**
   * Initialize the application
   */
  async initialize() {
    if (this.isInitialized) return;

    console.log("Initializing Hominio Voice App...");

    try {
      // Initialize UI state (sets greeting)
      uiState.initializeGreeting();

      // Initialize TTS service
      await ttsService.initialize();

      // Initialize STT service
      this.initializeSTTService();

      // Set up event listeners
      this.setupEventListeners();

      // Set up global error handling
      this.setupErrorHandling();

      this.isInitialized = true;
      console.log("Hominio Voice App initialized successfully");
    } catch (error) {
      console.error("Failed to initialize Hominio Voice App:", error);
      uiState.showError("Failed to initialize voice interface");
    }
  }

  /**
   * Set up event listeners for UI interactions
   */
  setupEventListeners() {
    // Send button click
    const sendButton = domElements.sendButton;
    if (sendButton) {
      const sendHandler = () => this.handleSendMessage();
      sendButton.addEventListener("click", sendHandler);
      this.eventListeners.push({
        element: sendButton,
        event: "click",
        handler: sendHandler,
      });
    }

    // Check status button click
    const checkStatusButton = domElements.get("checkStatusButton");
    if (checkStatusButton) {
      const statusHandler = () => this.handleCheckStatus();
      checkStatusButton.addEventListener("click", statusHandler);
      this.eventListeners.push({
        element: checkStatusButton,
        event: "click",
        handler: statusHandler,
      });
    }

    // Enter key in textarea
    const messageText = domElements.messageText;
    if (messageText) {
      const keyHandler = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          this.handleSendMessage();
        }
      };
      messageText.addEventListener("keydown", keyHandler);
      this.eventListeners.push({
        element: messageText,
        event: "keydown",
        handler: keyHandler,
      });
    }

    // Window beforeunload for cleanup
    const unloadHandler = () => this.shutdown();
    window.addEventListener("beforeunload", unloadHandler);
    this.eventListeners.push({
      element: window,
      event: "beforeunload",
      handler: unloadHandler,
    });

    console.log("Event listeners set up successfully");
  }

  /**
   * Initialize STT Service
   */
  initializeSTTService() {
    // Set up STT callbacks - transcriptions are now displayed directly in STT interface
    this.sttService.setOnPartialTranscription((text) => {
      console.log("Partial:", text);
      // Display is handled automatically by STT service
    });

    this.sttService.setOnFinalTranscription((text) => {
      console.log("Final:", text);
      // Display is handled automatically by STT service
      // Optionally could also copy to TTS input if user wants
    });

    this.sttService.setOnError((error) => {
      uiState.showError(`STT Error: ${error}`);
    });

    this.sttService.setOnStatusChange((status) => {
      console.log("STT Status:", status);
    });

    console.log("STT Service initialized");
  }

  /**
   * Set up global error handling
   */
  setupErrorHandling() {
    window.addEventListener("error", (event) => {
      console.error("Global error:", event.error);
      uiState.showError("An unexpected error occurred");
    });

    window.addEventListener("unhandledrejection", (event) => {
      console.error("Unhandled promise rejection:", event.reason);
      uiState.showError("An unexpected error occurred");
    });
  }

  /**
   * Handle send message button click
   */
  async handleSendMessage() {
    const messageText = domElements.messageText;
    if (!messageText) return;

    const text = messageText.value.trim();
    if (!text) {
      uiState.updateStatusText("Please enter some text to speak");
      return;
    }

    try {
      const success = await ttsService.sendText(text);
      if (!success) {
        uiState.showError("Failed to send message");
      }
    } catch (error) {
      console.error("Error sending message:", error);
      uiState.showError("Error sending message");
    }
  }

  /**
   * Handle check status button click
   */
  async handleCheckStatus() {
    try {
      uiState.showLoading("Checking status...");
      await ttsService.checkModelStatus();
    } catch (error) {
      console.error("Error checking status:", error);
      uiState.showError("Error checking status");
    }
  }

  /**
   * Get application status
   */
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      ttsService: ttsService.getStatus(),
      uiState: uiState.getCurrentStates(),
    };
  }

  /**
   * Shutdown the application
   */
  shutdown() {
    console.log("Shutting down Hominio Voice App...");

    // Remove event listeners
    this.eventListeners.forEach(({ element, event, handler }) => {
      element.removeEventListener(event, handler);
    });
    this.eventListeners = [];

    // Shutdown services
    ttsService.shutdown();
    this.sttService.disconnect();
    wsManager.closeAll();

    this.isInitialized = false;
    console.log("Hominio Voice App shut down");
  }
}

// Create and export app instance
export const app = new HominiVoiceApp();

// Global functions for backward compatibility (if needed)
window.sendMessage = () => app.handleSendMessage();
window.checkModelStatus = () => app.handleCheckStatus();

// Auto-initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => app.initialize());
} else {
  app.initialize();
}
