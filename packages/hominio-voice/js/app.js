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
import { messageRouter } from "./services/message-router.js";

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
      await this.initializeSTTService();

      // Initialize message router with services
      messageRouter.initialize(this.sttService, ttsService);

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
   * Initialize STT Service with enhanced visual state integration
   */
  async initializeSTTService() {
    // Set up STT callbacks with visual state management
    this.sttService.setOnPartialTranscription((text) => {
      console.log("Partial:", text);
      // Show thinking state when we get partial transcription
      if (text && text.trim()) {
        uiState.showThinking("Processing speech...");
      }
    });

    this.sttService.setOnFinalTranscription((text) => {
      console.log("Final:", text);
      // Show thinking state for LLM processing
      uiState.showThinking("Processing your request...");
    });

    // NEW: Set up potential sentence detection for early LLM processing
    this.sttService.setOnPotentialSentence((text) => {
      console.log("🎯 Potential sentence detected for early processing:", text);
      // This would trigger early LLM processing on the backend
      // The backend conversation manager handles the actual early processing
      uiState.showThinking("Early processing detected sentence...");
    });

    this.sttService.setOnError((error) => {
      uiState.showError(`STT Error: ${error}`);
    });

    this.sttService.setOnStatusChange((status) => {
      console.log("STT Status:", status);
      // Update status without changing conversation state if we're in an active conversation
      const currentState = uiState.getCurrentStates().conversationState;
      if (currentState === "standby") {
        uiState.updateStatusText(status);
      }
    });

    // Connect STT service to WebSocket (this will register message handlers)
    await this.sttService.connectWebSocket();

    console.log(
      "STT Service initialized with visual state integration and early sentence detection"
    );
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

  // Manual message sending removed - only automatic STT → LLM → TTS flow

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

// Make app instance globally available for service communication
window.app = app;

// Global functions for backward compatibility (if needed)
window.checkModelStatus = () => app.handleCheckStatus();

// Auto-initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => app.initialize());
} else {
  app.initialize();
}
