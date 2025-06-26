// stats.js - Session metadata and system statistics management

class StatsManager {
  constructor() {
    // System Stats Elements
    this.cpuUsageValue = document.getElementById("cpuUsageValue");
    this.cpuUsageBar = document.getElementById("cpuUsageBar");
    this.cpuCoresInfo = document.getElementById("cpuCoresInfo");
    this.cpuFreqValue = document.getElementById("cpuFreqValue");
    this.cpuTempValue = document.getElementById("cpuTempValue");
    this.cpuTempBar = document.getElementById("cpuTempBar");
    this.cpuTempItem = document.getElementById("cpuTempItem");

    this.memoryUsageValue = document.getElementById("memoryUsageValue");
    this.memoryUsageBar = document.getElementById("memoryUsageBar");
    this.memoryAvailableValue = document.getElementById("memoryAvailableValue");

    this.gpuUtilValue = document.getElementById("gpuUtilValue");
    this.gpuUtilBar = document.getElementById("gpuUtilBar");
    this.gpuMemoryValue = document.getElementById("gpuMemoryValue");
    this.gpuMemoryBar = document.getElementById("gpuMemoryBar");
    this.gpuTempValue = document.getElementById("gpuTempValue");
    this.gpuTempBar = document.getElementById("gpuTempBar");
    this.gpuSection = document.getElementById("gpuSection");

    this.systemInfo = document.getElementById("systemInfo");
    this.statusDot = document.getElementById("statusDot");
    this.connectionText = document.getElementById("connectionText");

    // Session Elements
    this.sessionsList = document.getElementById("sessionsList");
    this.totalSessionsCount = document.getElementById("totalSessionsCount");
    this.activeSessionsCount = document.getElementById("activeSessionsCount");

    // State
    this.systemStatsConnected = false;
    this.sessionId = null;
    this.sessionsData = { sessions: { total_sessions: 0, active_sessions: 0 } };
  }

  // System Stats Functions
  updateSystemStats(data) {
    // Update CPU stats
    if (this.cpuUsageValue) {
      this.cpuUsageValue.textContent = `${data.cpu_percent}%`;
    }
    if (this.cpuUsageBar) {
      this.cpuUsageBar.style.width = `${Math.max(0, Math.min(100, data.cpu_percent))}%`;
    }
    if (this.cpuCoresInfo) {
      this.cpuCoresInfo.textContent = `${data.cpu_count} cores`;
    }
    if (this.cpuFreqValue) {
      if (data.cpu_freq_current) {
        this.cpuFreqValue.textContent = `${Math.round(data.cpu_freq_current)} MHz`;
      } else {
        this.cpuFreqValue.textContent = "N/A";
      }
    }

    // Update CPU temperature if available
    if (data.cpu_temp !== null && data.cpu_temp !== undefined) {
      if (this.cpuTempItem) this.cpuTempItem.style.display = "block";
      if (this.cpuTempValue) {
        this.cpuTempValue.textContent = `${Math.round(data.cpu_temp)}°C`;
      }
      if (this.cpuTempBar) {
        const tempPercent = Math.max(
          0,
          Math.min(100, (data.cpu_temp / 100) * 100)
        );
        this.cpuTempBar.style.width = `${tempPercent}%`;

        // Update temperature bar color
        this.cpuTempBar.className = "stat-bar-fill temp";
        if (data.cpu_temp >= 80) {
          this.cpuTempBar.classList.add("critical");
        } else if (data.cpu_temp >= 70) {
          this.cpuTempBar.classList.add("hot");
        }
      }
    } else {
      if (this.cpuTempItem) this.cpuTempItem.style.display = "none";
    }

    // Update memory stats
    if (this.memoryUsageValue) {
      this.memoryUsageValue.textContent = `${data.memory_used} MB / ${data.memory_total} MB`;
    }
    if (this.memoryUsageBar) {
      this.memoryUsageBar.style.width = `${Math.max(0, Math.min(100, data.memory_percent))}%`;
    }
    if (this.memoryAvailableValue) {
      this.memoryAvailableValue.textContent = `${data.memory_available} MB`;
    }

    // Update GPU stats
    if (data.gpu_available) {
      if (this.gpuSection) this.gpuSection.style.display = "block";

      if (this.gpuUtilValue) {
        this.gpuUtilValue.textContent = `${data.gpu_utilization}%`;
      }
      if (this.gpuUtilBar) {
        this.gpuUtilBar.style.width = `${Math.max(0, Math.min(100, data.gpu_utilization))}%`;
      }

      if (this.gpuMemoryValue) {
        this.gpuMemoryValue.textContent = `${data.gpu_memory_used} MB / ${data.gpu_memory_total} MB`;
      }
      if (this.gpuMemoryBar) {
        this.gpuMemoryBar.style.width = `${Math.max(0, Math.min(100, data.gpu_memory_percent))}%`;
      }

      if (this.gpuTempValue) {
        this.gpuTempValue.textContent = `${data.gpu_temperature}°C`;
      }
      if (this.gpuTempBar) {
        const tempPercent = Math.max(
          0,
          Math.min(100, (data.gpu_temperature / 100) * 100)
        );
        this.gpuTempBar.style.width = `${tempPercent}%`;

        // Update temperature bar color
        this.gpuTempBar.className = "stat-bar-fill temp";
        if (data.gpu_temperature >= 80) {
          this.gpuTempBar.classList.add("critical");
        } else if (data.gpu_temperature >= 70) {
          this.gpuTempBar.classList.add("hot");
        }
      }
    } else {
      // Hide GPU section if not available
      if (this.gpuSection) this.gpuSection.style.display = "none";
    }

    // Update system info
    if (this.systemInfo) {
      let infoLines = [];

      if (data.gpu_available) {
        infoLines.push(data.gpu_name);
        if (data.gpu_power_usage !== null) {
          infoLines.push(`Power: ${data.gpu_power_usage}W`);
        }
      }

      if (data.uptime > 0) {
        const hours = Math.floor(data.uptime / 3600);
        const minutes = Math.floor((data.uptime % 3600) / 60);
        infoLines.push(`Uptime: ${hours}h ${minutes}m`);
      }

      this.systemInfo.textContent = infoLines.join(" • ");
    }

    this.updateSystemConnectionStatus(true);
  }

  updateSystemConnectionStatus(connected) {
    this.systemStatsConnected = connected;

    if (this.statusDot) {
      if (connected) {
        this.statusDot.classList.add("connected");
      } else {
        this.statusDot.classList.remove("connected");
      }
    }

    if (this.connectionText) {
      this.connectionText.textContent = connected
        ? "Connected"
        : "Disconnected";
    }
  }

  // Session Management Functions
  setSessionId(sessionId) {
    this.sessionId = sessionId;
    this.updateSessionsDisplay();
  }

  updateSessionsData(data) {
    this.sessionsData = { sessions: data };
    this.updateSessionsDisplay();
  }

  updateSessionsDisplay() {
    const stats = this.sessionsData.sessions || {};

    // Update summary stats
    if (this.totalSessionsCount) {
      this.totalSessionsCount.textContent = stats.total_sessions || 0;
    }
    if (this.activeSessionsCount) {
      this.activeSessionsCount.textContent = stats.active_sessions || 0;
    }

    // Display all sessions in full format for left panel
    if (this.sessionsList) {
      const sessions = stats.sessions || [];

      if (sessions.length > 0) {
        const sessionsHtml = sessions
          .map((session) => {
            const isCurrentSession = session.session_id === this.sessionId;
            const statusClass = this.getSessionStatusClassFromState(
              session.status
            );
            const statusText = this.formatSessionStatus(session.status);
            const duration = this.formatSessionDuration(
              session.duration_seconds
            );
            const lastActivity =
              session.idle_time_seconds > 0
                ? `${Math.round(session.idle_time_seconds)}s ago`
                : "Active now";

            return `
            <div class="session-item${isCurrentSession ? " current" : ""}">
              <div class="session-id">
                ${session.session_id.substring(0, 8)}...${isCurrentSession ? " (You)" : ""}
              </div>
              <div class="session-status">
                <div class="session-status-dot ${statusClass}"></div>
                <span>${statusText}</span>
              </div>
              <div class="session-details">
                <div class="session-detail-row">
                  <span>Duration:</span>
                  <span>${duration}</span>
                </div>
                <div class="session-detail-row">
                  <span>Last Activity:</span>
                  <span>${lastActivity}</span>
                </div>
                <div class="session-detail-row">
                  <span>Messages:</span>
                  <span>${session.message_count || 0}</span>
                </div>
                <div class="session-detail-row">
                  <span>Audio Chunks:</span>
                  <span>${session.audio_chunks || 0}</span>
                </div>
              </div>
            </div>
          `;
          })
          .join("");

        this.sessionsList.innerHTML = sessionsHtml;
      } else {
        this.sessionsList.innerHTML =
          '<div style="text-align: center; color: #7f8c8d; padding: 1rem;">No active sessions</div>';
      }
    }
  }

  getSessionStatusClassFromState(status) {
    switch (status) {
      case "speaking":
        return "speaking";
      case "listening":
        return "listening";
      case "processing":
        return "processing";
      case "connected":
        return "active";
      case "idle":
        return "active";
      case "disconnected":
        return "inactive";
      case "inactive":
        return "inactive";
      default:
        return "active";
    }
  }

  formatSessionStatus(status) {
    switch (status) {
      case "speaking":
        return "Speaking";
      case "listening":
        return "Listening";
      case "processing":
        return "Processing";
      case "connected":
        return "Connected";
      case "idle":
        return "Idle";
      case "disconnected":
        return "Disconnected";
      case "inactive":
        return "Inactive";
      default:
        return "Active";
    }
  }

  formatSessionDuration(seconds) {
    if (!seconds || seconds < 1) return "0s";

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  }

  // Handle incoming JSON messages related to stats
  handleStatsMessage(type, content) {
    if (type === "session_info") {
      // Received session info from server
      if (content.session_id) {
        this.setSessionId(content.session_id);
      }
      return true; // Message handled
    }

    if (type === "session_stats") {
      // Received real-time session statistics
      this.updateSessionsData(content);
      return true; // Message handled
    }

    if (type === "system_stats") {
      // Handle system stats updates (includes CPU, memory, and GPU)
      this.updateSystemStats(content);
      return true; // Message handled
    }

    if (type === "gpu_stats") {
      // Legacy support - convert to system stats format
      const systemData = {
        cpu_percent: 0,
        cpu_count: 0,
        cpu_freq_current: null,
        cpu_temp: null,
        memory_total: 0,
        memory_used: 0,
        memory_percent: 0,
        memory_available: 0,
        gpu_available: content.available,
        gpu_utilization: content.utilization,
        gpu_memory_used: content.memory_used,
        gpu_memory_total: content.memory_total,
        gpu_memory_percent: content.memory_percent,
        gpu_temperature: content.temperature,
        gpu_name: content.name,
        gpu_power_usage: content.power_usage,
        uptime: 0,
      };
      this.updateSystemStats(systemData);
      return true; // Message handled
    }

    return false; // Message not handled by this manager
  }
}

// Export for use in other files
window.StatsManager = StatsManager;
