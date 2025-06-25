(function () {
  const originalLog = console.log.bind(console);
  console.log = (...args) => {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");
    const ms = String(now.getMilliseconds()).padStart(3, "0");
    originalLog(`[${hh}:${mm}:${ss}.${ms}]`, ...args);
  };
})();

// UI Elements
const messagesDiv = document.getElementById("messages");
const voiceInterface = document.getElementById("voiceInterface");
const chatContainer = document.getElementById("chatContainer");
const voiceAvatar = document.getElementById("voiceAvatar");
const statusText = document.getElementById("statusText");
const chatStatus = document.getElementById("chatStatus");
const viewToggle = document.getElementById("viewToggle");

// System Stats Elements
const cpuUsageValue = document.getElementById("cpuUsageValue");
const cpuUsageBar = document.getElementById("cpuUsageBar");
const cpuCoresInfo = document.getElementById("cpuCoresInfo");
const cpuFreqValue = document.getElementById("cpuFreqValue");
const cpuTempValue = document.getElementById("cpuTempValue");
const cpuTempBar = document.getElementById("cpuTempBar");
const cpuTempItem = document.getElementById("cpuTempItem");

const memoryUsageValue = document.getElementById("memoryUsageValue");
const memoryUsageBar = document.getElementById("memoryUsageBar");
const memoryAvailableValue = document.getElementById("memoryAvailableValue");

const gpuUtilValue = document.getElementById("gpuUtilValue");
const gpuUtilBar = document.getElementById("gpuUtilBar");
const gpuMemoryValue = document.getElementById("gpuMemoryValue");
const gpuMemoryBar = document.getElementById("gpuMemoryBar");
const gpuTempValue = document.getElementById("gpuTempValue");
const gpuTempBar = document.getElementById("gpuTempBar");
const gpuSection = document.getElementById("gpuSection");

const systemInfo = document.getElementById("systemInfo");
const statusDot = document.getElementById("statusDot");
const connectionText = document.getElementById("connectionText");

// Session Elements
const sessionsPanel = document.getElementById("sessionsPanel");
const sessionsList = document.getElementById("sessionsList");
const totalSessionsCount = document.getElementById("totalSessionsCount");
const activeSessionsCount = document.getElementById("activeSessionsCount");

// Toggle buttons for both views
const toggleBtn = document.getElementById("toggleBtn");
const toggleBtn2 = document.getElementById("toggleBtn2");
const clearBtn = document.getElementById("clearBtn");
const clearBtn2 = document.getElementById("clearBtn2");

// State
let socket = null;
let audioContext = null;
let mediaStream = null;
let micWorkletNode = null;
let ttsWorkletNode = null;
let isTTSPlaying = false;
let ignoreIncomingTTS = false;
let chatHistory = [];
let typingUser = "";
let typingAssistant = "";
let isVoiceView = true; // Default to voice bubble view
let isConnected = false; // Track connection state

// System Stats State
let systemStatsConnected = false;

// Session Management State
let sessionId = null;
let sessionsData = { sessions: { total_sessions: 0, active_sessions: 0 } };

// --- batching + fixed 8‑byte header setup ---
const BATCH_SAMPLES = 2048;
const HEADER_BYTES = 8;
const FRAME_BYTES = BATCH_SAMPLES * 2;
const MESSAGE_BYTES = HEADER_BYTES + FRAME_BYTES;

const bufferPool = [];
let batchBuffer = null;
let batchView = null;
let batchInt16 = null;
let batchOffset = 0;

function initBatch() {
  if (!batchBuffer) {
    batchBuffer = bufferPool.pop() || new ArrayBuffer(MESSAGE_BYTES);
    batchView = new DataView(batchBuffer);
    batchInt16 = new Int16Array(batchBuffer, HEADER_BYTES);
    batchOffset = 0;
  }
}

function flushBatch() {
  const ts = Date.now() & 0xffffffff;
  batchView.setUint32(0, ts, false);
  const flags = isTTSPlaying ? 1 : 0;
  batchView.setUint32(4, flags, false);

  socket.send(batchBuffer);

  bufferPool.push(batchBuffer);
  batchBuffer = null;
}

function flushRemainder() {
  if (batchOffset > 0) {
    for (let i = batchOffset; i < BATCH_SAMPLES; i++) {
      batchInt16[i] = 0;
    }
    flushBatch();
  }
}

function initAudioContext() {
  if (!audioContext) {
    audioContext = new AudioContext();
  }
}

function base64ToInt16Array(b64) {
  const raw = atob(b64);
  const buf = new ArrayBuffer(raw.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < raw.length; i++) {
    view[i] = raw.charCodeAt(i);
  }
  return new Int16Array(buf);
}

async function startRawPcmCapture() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: { ideal: 24000 },
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });
    mediaStream = stream;
    initAudioContext();
    await audioContext.audioWorklet.addModule("/static/pcmWorkletProcessor.js");
    micWorkletNode = new AudioWorkletNode(
      audioContext,
      "pcm-worklet-processor"
    );

    micWorkletNode.port.onmessage = ({ data }) => {
      const incoming = new Int16Array(data);
      let read = 0;
      while (read < incoming.length) {
        initBatch();
        const toCopy = Math.min(
          incoming.length - read,
          BATCH_SAMPLES - batchOffset
        );
        batchInt16.set(incoming.subarray(read, read + toCopy), batchOffset);
        batchOffset += toCopy;
        read += toCopy;
        if (batchOffset === BATCH_SAMPLES) {
          flushBatch();
        }
      }
    };

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(micWorkletNode);
    updateStatus("Recording...");
    setVoiceAvatarState("listening");
  } catch (err) {
    updateStatus("Mic access denied.");
    console.error(err);
  }
}

async function setupTTSPlayback() {
  await audioContext.audioWorklet.addModule("/static/ttsPlaybackProcessor.js");
  ttsWorkletNode = new AudioWorkletNode(audioContext, "tts-playback-processor");

  ttsWorkletNode.port.onmessage = (event) => {
    const { type } = event.data;
    if (type === "ttsPlaybackStarted") {
      if (!isTTSPlaying && socket && socket.readyState === WebSocket.OPEN) {
        isTTSPlaying = true;
        setVoiceAvatarState("speaking");
        console.log(
          "TTS playback started. Reason: ttsWorkletNode Event ttsPlaybackStarted."
        );
        socket.send(JSON.stringify({ type: "tts_start" }));
      }
    } else if (type === "ttsPlaybackStopped") {
      if (isTTSPlaying && socket && socket.readyState === WebSocket.OPEN) {
        isTTSPlaying = false;
        setVoiceAvatarState("standby");
        console.log(
          "TTS playback stopped. Reason: ttsWorkletNode Event ttsPlaybackStopped."
        );
        socket.send(JSON.stringify({ type: "tts_stop" }));
      }
    }
  };
  ttsWorkletNode.connect(audioContext.destination);
}

function cleanupAudio() {
  if (micWorkletNode) {
    micWorkletNode.disconnect();
    micWorkletNode = null;
  }
  if (ttsWorkletNode) {
    ttsWorkletNode.disconnect();
    ttsWorkletNode = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  if (mediaStream) {
    mediaStream.getAudioTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
}

function updateStatus(message) {
  if (statusText) statusText.textContent = message;
  if (chatStatus) chatStatus.textContent = message;
}

function setVoiceAvatarState(state) {
  if (!voiceAvatar) return;

  // Remove all state classes
  voiceAvatar.className = "voice-avatar";

  // Add the specific state class
  if (state !== "standby") {
    voiceAvatar.classList.add(state);
  }

  // Update status text based on state
  const stateMessages = {
    listening: "Listening...",
    thinking: "Thinking...",
    speaking: "Speaking...",
    standby: "Ready to chat",
  };

  if (statusText && stateMessages[state]) {
    statusText.textContent = stateMessages[state];
  }
}

function toggleView() {
  isVoiceView = !isVoiceView;

  if (isVoiceView) {
    // Switch to voice bubble view
    voiceInterface.style.display = "flex";
    chatContainer.style.display = "none";
    viewToggle.textContent = "Chat";
  } else {
    // Switch to chat view
    voiceInterface.style.display = "none";
    chatContainer.style.display = "flex";
    viewToggle.textContent = "Voice";
  }
}

function renderMessages() {
  if (!messagesDiv) return;

  messagesDiv.innerHTML = "";
  chatHistory.forEach((msg) => {
    const bubble = document.createElement("div");
    bubble.className = `bubble ${msg.role}`;
    bubble.textContent = msg.content;
    messagesDiv.appendChild(bubble);
  });
  if (typingUser) {
    const typing = document.createElement("div");
    typing.className = "bubble user typing";
    typing.innerHTML = typingUser + '<span style="opacity:.6;">✏️</span>';
    messagesDiv.appendChild(typing);
  }
  if (typingAssistant) {
    const typing = document.createElement("div");
    typing.className = "bubble assistant typing";
    typing.innerHTML = typingAssistant + '<span style="opacity:.6;">✏️</span>';
    messagesDiv.appendChild(typing);
    setVoiceAvatarState("thinking");
  }
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function handleJSONMessage({ type, content }) {
  if (type === "session_info") {
    // Received session info from server
    if (content.session_id) {
      sessionId = content.session_id;
      updateSessionsDisplay();
    }
    return;
  }

  if (type === "session_stats") {
    // Received real-time session statistics
    sessionsData = { sessions: content };
    updateSessionsDisplay();
    return;
  }

  // Update session display when we receive messages (for real-time status)
  updateSessionsDisplay();

  if (type === "partial_user_request") {
    typingUser = content?.trim() ? escapeHtml(content) : "";
    setVoiceAvatarState("listening");
    renderMessages();
    return;
  }
  if (type === "final_user_request") {
    if (content?.trim()) {
      chatHistory.push({ role: "user", content, type: "final" });
    }
    typingUser = "";
    setVoiceAvatarState("thinking");
    renderMessages();
    return;
  }
  if (type === "partial_assistant_answer") {
    typingAssistant = content?.trim() ? escapeHtml(content) : "";
    setVoiceAvatarState("thinking");
    renderMessages();
    return;
  }
  if (type === "final_assistant_answer") {
    if (content?.trim()) {
      chatHistory.push({ role: "assistant", content, type: "final" });
    }
    typingAssistant = "";
    setVoiceAvatarState("standby");
    renderMessages();
    return;
  }
  if (type === "tts_chunk") {
    if (ignoreIncomingTTS) return;
    const int16Data = base64ToInt16Array(content);
    if (ttsWorkletNode) {
      ttsWorkletNode.port.postMessage(int16Data);
    }
    return;
  }
  if (type === "tts_interruption") {
    if (ttsWorkletNode) {
      ttsWorkletNode.port.postMessage({ type: "clear" });
    }
    isTTSPlaying = false;
    ignoreIncomingTTS = false;
    setVoiceAvatarState("standby");
    return;
  }
  if (type === "stop_tts") {
    if (ttsWorkletNode) {
      ttsWorkletNode.port.postMessage({ type: "clear" });
    }
    isTTSPlaying = false;
    ignoreIncomingTTS = true;
    setVoiceAvatarState("standby");
    console.log("TTS playback stopped. Reason: tts_interruption.");
    socket.send(JSON.stringify({ type: "tts_stop" }));
    return;
  }
  if (type === "system_stats") {
    // Handle system stats updates (includes CPU, memory, and GPU)
    updateSystemStats(content);
    return;
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
    updateSystemStats(systemData);
    return;
  }
}

// System Stats Functions
function updateSystemStats(data) {
  // Update CPU stats
  if (cpuUsageValue) {
    cpuUsageValue.textContent = `${data.cpu_percent}%`;
  }
  if (cpuUsageBar) {
    cpuUsageBar.style.width = `${Math.max(0, Math.min(100, data.cpu_percent))}%`;
  }
  if (cpuCoresInfo) {
    cpuCoresInfo.textContent = `${data.cpu_count} cores`;
  }
  if (cpuFreqValue) {
    if (data.cpu_freq_current) {
      cpuFreqValue.textContent = `${Math.round(data.cpu_freq_current)} MHz`;
    } else {
      cpuFreqValue.textContent = "N/A";
    }
  }

  // Update CPU temperature if available
  if (data.cpu_temp !== null && data.cpu_temp !== undefined) {
    if (cpuTempItem) cpuTempItem.style.display = "block";
    if (cpuTempValue) {
      cpuTempValue.textContent = `${Math.round(data.cpu_temp)}°C`;
    }
    if (cpuTempBar) {
      const tempPercent = Math.max(
        0,
        Math.min(100, (data.cpu_temp / 100) * 100)
      );
      cpuTempBar.style.width = `${tempPercent}%`;

      // Update temperature bar color
      cpuTempBar.className = "stat-bar-fill temp";
      if (data.cpu_temp >= 80) {
        cpuTempBar.classList.add("critical");
      } else if (data.cpu_temp >= 70) {
        cpuTempBar.classList.add("hot");
      }
    }
  } else {
    if (cpuTempItem) cpuTempItem.style.display = "none";
  }

  // Update memory stats
  if (memoryUsageValue) {
    memoryUsageValue.textContent = `${data.memory_used} MB / ${data.memory_total} MB`;
  }
  if (memoryUsageBar) {
    memoryUsageBar.style.width = `${Math.max(0, Math.min(100, data.memory_percent))}%`;
  }
  if (memoryAvailableValue) {
    memoryAvailableValue.textContent = `${data.memory_available} MB`;
  }

  // Update GPU stats
  if (data.gpu_available) {
    if (gpuSection) gpuSection.style.display = "block";

    if (gpuUtilValue) {
      gpuUtilValue.textContent = `${data.gpu_utilization}%`;
    }
    if (gpuUtilBar) {
      gpuUtilBar.style.width = `${Math.max(0, Math.min(100, data.gpu_utilization))}%`;
    }

    if (gpuMemoryValue) {
      gpuMemoryValue.textContent = `${data.gpu_memory_used} MB / ${data.gpu_memory_total} MB`;
    }
    if (gpuMemoryBar) {
      gpuMemoryBar.style.width = `${Math.max(0, Math.min(100, data.gpu_memory_percent))}%`;
    }

    if (gpuTempValue) {
      gpuTempValue.textContent = `${data.gpu_temperature}°C`;
    }
    if (gpuTempBar) {
      const tempPercent = Math.max(
        0,
        Math.min(100, (data.gpu_temperature / 100) * 100)
      );
      gpuTempBar.style.width = `${tempPercent}%`;

      // Update temperature bar color
      gpuTempBar.className = "stat-bar-fill temp";
      if (data.gpu_temperature >= 80) {
        gpuTempBar.classList.add("critical");
      } else if (data.gpu_temperature >= 70) {
        gpuTempBar.classList.add("hot");
      }
    }
  } else {
    // Hide GPU section if not available
    if (gpuSection) gpuSection.style.display = "none";
  }

  // Update system info
  if (systemInfo) {
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

    systemInfo.textContent = infoLines.join(" • ");
  }

  updateSystemConnectionStatus(true);
}

function updateSystemConnectionStatus(connected) {
  systemStatsConnected = connected;

  if (statusDot) {
    if (connected) {
      statusDot.classList.add("connected");
    } else {
      statusDot.classList.remove("connected");
    }
  }

  if (connectionText) {
    connectionText.textContent = connected ? "Connected" : "Disconnected";
  }
}

// Session Management Functions (Real-time via WebSocket)

function updateSessionsDisplay() {
  const stats = sessionsData.sessions || {};

  // Update summary stats
  if (totalSessionsCount) {
    totalSessionsCount.textContent = stats.total_sessions || 0;
  }
  if (activeSessionsCount) {
    activeSessionsCount.textContent = stats.active_sessions || 0;
  }

  // Display all sessions
  if (sessionsList) {
    const sessions = stats.sessions || [];

    if (sessions.length > 0) {
      const sessionsHtml = sessions
        .map((session) => {
          const isCurrentSession = session.session_id === sessionId;
          const statusClass = getSessionStatusClassFromState(session.status);
          const durationText = formatSessionDuration(session.duration_seconds);
          const statusText = formatSessionStatus(session.status);
          const lastActivity =
            session.idle_time_seconds > 0
              ? `${Math.round(session.idle_time_seconds)}s ago`
              : "Now";

          return `
          <div class="session-item ${isCurrentSession ? "current" : ""}">
            <div class="session-id">
              ${session.session_id.substring(0, 8)}...
              ${isCurrentSession ? " (You)" : ""}
            </div>
            <div class="session-status">
              <div class="session-status-dot ${statusClass}"></div>
              <span>${statusText}</span>
            </div>
            <div class="session-details">
              <div class="session-detail-row">
                <span>Duration:</span>
                <span>${durationText}</span>
              </div>
              <div class="session-detail-row">
                <span>Activity:</span>
                <span>${lastActivity}</span>
              </div>
              <div class="session-detail-row">
                <span>Messages:</span>
                <span>${session.messages_received || 0}</span>
              </div>
                             <div class="session-detail-row">
                 <span>Audio chunks:</span>
                 <span>${session.audio_chunks_received || 0}</span>
               </div>
            </div>
          </div>
        `;
        })
        .join("");

      sessionsList.innerHTML = sessionsHtml;
    } else {
      sessionsList.innerHTML =
        '<div style="text-align: center; color: #7f8c8d; font-size: 0.8rem; padding: 1rem;">No active sessions</div>';
    }
  }
}

function getSessionStatusClass() {
  if (!isConnected) return "inactive";
  if (isTTSPlaying) return "speaking";
  if (mediaStream) return "listening";
  return "active";
}

function getSessionStatusText() {
  if (!isConnected) return "Disconnected";
  if (isTTSPlaying) return "Speaking";
  if (mediaStream) return "Listening";
  return "Connected";
}

function getSessionDuration() {
  // This is a placeholder - in a real implementation, you'd track session start time
  return "Active";
}

function getSessionStatusClassFromState(status) {
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

function formatSessionStatus(status) {
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

function formatSessionDuration(seconds) {
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

// Polling functions removed - now using real-time WebSocket updates

function escapeHtml(str) {
  return (str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function clearConversation() {
  chatHistory = [];
  typingUser = typingAssistant = "";
  renderMessages();
  setVoiceAvatarState("standby");
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "clear_history" }));
  }
}

async function startConnection() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    updateStatus("Already recording.");
    return;
  }

  // Update buttons to show connecting state
  updateStatus("Initializing connection...");
  const buttons = [toggleBtn, toggleBtn2];
  buttons.forEach((btn) => {
    if (btn) {
      btn.textContent = "Connecting...";
      btn.disabled = true;
    }
  });

  const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
  socket = new WebSocket(`${wsProto}//${location.host}/ws`);

  socket.onopen = async () => {
    updateStatus("Connected. Activating mic and TTS…");
    await startRawPcmCapture();
    await setupTTSPlayback();
    isConnected = true;

    // Session ID will be provided by the server via session_info message
    // No need for polling anymore - we get real-time updates via WebSocket

    // Re-enable buttons
    buttons.forEach((btn) => {
      if (btn) btn.disabled = false;
    });
    updateToggleButtons();
  };

  socket.onmessage = (evt) => {
    if (typeof evt.data === "string") {
      try {
        const msg = JSON.parse(evt.data);
        handleJSONMessage(msg);
      } catch (e) {
        console.error("Error parsing message:", e);
      }
    }
  };

  socket.onclose = () => {
    updateStatus("Connection closed.");
    setVoiceAvatarState("standby");
    flushRemainder();
    cleanupAudio();
    isConnected = false;
    sessionId = null;

    // Clear session display
    updateSessionsDisplay();

    // Re-enable buttons
    const buttons = [toggleBtn, toggleBtn2];
    buttons.forEach((btn) => {
      if (btn) btn.disabled = false;
    });
    updateToggleButtons();
  };

  socket.onerror = (err) => {
    updateStatus("Connection error.");
    setVoiceAvatarState("standby");
    cleanupAudio();
    console.error(err);
    isConnected = false;
    sessionId = null;

    // Clear session display
    updateSessionsDisplay();

    // Re-enable buttons
    const buttons = [toggleBtn, toggleBtn2];
    buttons.forEach((btn) => {
      if (btn) btn.disabled = false;
    });
    updateToggleButtons();
  };
}

function stopConnection() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    flushRemainder();
    socket.close();
  }
  cleanupAudio();
  updateStatus("Stopped.");
  setVoiceAvatarState("standby");
  isConnected = false;
  updateToggleButtons();
}

function updateToggleButtons() {
  const buttons = [toggleBtn, toggleBtn2];
  buttons.forEach((btn) => {
    if (!btn) return;

    if (isConnected) {
      btn.textContent = "Stop";
      btn.className = "btn btn-secondary";
    } else {
      btn.textContent = "Start";
      btn.className = "btn btn-primary";
    }
  });
}

async function toggleConnection() {
  if (isConnected) {
    stopConnection();
  } else {
    await startConnection();
  }
}

// Event Listeners

// View toggle
viewToggle.addEventListener("click", toggleView);

// Toggle buttons
toggleBtn.addEventListener("click", toggleConnection);
if (toggleBtn2) toggleBtn2.addEventListener("click", toggleConnection);

// Voice view buttons
clearBtn.addEventListener("click", clearConversation);

// Chat view buttons
clearBtn2.addEventListener("click", clearConversation);

// Initialize
renderMessages();
setVoiceAvatarState("standby");
updateStatus("Ready to start");
