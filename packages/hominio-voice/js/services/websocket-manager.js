/**
 * WebSocket Manager
 * Handles WebSocket connections with automatic reconnection
 */
import { uiState } from "../core/ui-state.js";

export class WebSocketManager {
  constructor() {
    this.connections = new Map();
    this.reconnectAttempts = new Map();
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  /**
   * Create a new WebSocket connection
   */
  createConnection(name, path, options = {}) {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${proto}//${window.location.host}${path}`;

    const connection = {
      name,
      url: wsUrl,
      websocket: null,
      options: {
        autoReconnect: true,
        onOpen: null,
        onMessage: null,
        onClose: null,
        onError: null,
        ...options,
      },
    };

    this.connections.set(name, connection);
    this.reconnectAttempts.set(name, 0);

    this.connect(name);
    return connection;
  }

  /**
   * Connect to WebSocket
   */
  connect(name) {
    const connection = this.connections.get(name);
    if (!connection) {
      console.error(`Connection '${name}' not found`);
      return;
    }

    try {
      connection.websocket = new WebSocket(connection.url);

      connection.websocket.onopen = (event) => {
        console.log(`WebSocket '${name}' connected`);
        this.reconnectAttempts.set(name, 0);

        if (connection.options.onOpen) {
          connection.options.onOpen(event);
        }
      };

      connection.websocket.onmessage = (event) => {
        if (connection.options.onMessage) {
          connection.options.onMessage(event);
        }
      };

      connection.websocket.onclose = (event) => {
        console.log(`WebSocket '${name}' closed`);

        if (connection.options.onClose) {
          connection.options.onClose(event);
        }

        if (connection.options.autoReconnect) {
          this.handleReconnect(name);
        }
      };

      connection.websocket.onerror = (error) => {
        console.error(`WebSocket '${name}' error:`, error);

        if (connection.options.onError) {
          connection.options.onError(error);
        }
      };
    } catch (error) {
      console.error(`Failed to create WebSocket '${name}':`, error);
      if (connection.options.autoReconnect) {
        this.handleReconnect(name);
      }
    }
  }

  /**
   * Handle reconnection logic
   */
  handleReconnect(name) {
    const attempts = this.reconnectAttempts.get(name) || 0;

    if (attempts >= this.maxReconnectAttempts) {
      console.error(`Max reconnection attempts reached for '${name}'`);
      return;
    }

    this.reconnectAttempts.set(name, attempts + 1);

    console.log(
      `Reconnecting '${name}' in ${this.reconnectDelay}ms (attempt ${attempts + 1})`
    );

    setTimeout(() => {
      this.connect(name);
    }, this.reconnectDelay);
  }

  /**
   * Send message to WebSocket
   */
  send(name, message) {
    const connection = this.connections.get(name);
    if (!connection || !connection.websocket) {
      console.error(`Connection '${name}' not available`);
      return false;
    }

    if (connection.websocket.readyState !== WebSocket.OPEN) {
      console.error(`Connection '${name}' not ready`);
      return false;
    }

    try {
      connection.websocket.send(message);
      return true;
    } catch (error) {
      console.error(`Failed to send message to '${name}':`, error);
      return false;
    }
  }

  /**
   * Close WebSocket connection
   */
  close(name) {
    const connection = this.connections.get(name);
    if (!connection) return;

    connection.options.autoReconnect = false;

    if (connection.websocket) {
      connection.websocket.close();
    }

    this.connections.delete(name);
    this.reconnectAttempts.delete(name);
  }

  /**
   * Get connection status
   */
  getConnectionStatus(name) {
    const connection = this.connections.get(name);
    if (!connection || !connection.websocket) {
      return "disconnected";
    }

    switch (connection.websocket.readyState) {
      case WebSocket.CONNECTING:
        return "connecting";
      case WebSocket.OPEN:
        return "connected";
      case WebSocket.CLOSING:
        return "closing";
      case WebSocket.CLOSED:
        return "disconnected";
      default:
        return "unknown";
    }
  }

  /**
   * Close all connections
   */
  closeAll() {
    for (const name of this.connections.keys()) {
      this.close(name);
    }
  }
}

// Export singleton instance
export const wsManager = new WebSocketManager();
