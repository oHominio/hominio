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

// Initialize stats manager if elements are present
let statsManager = null;
if (typeof StatsManager !== "undefined") {
  statsManager = new StatsManager();
}

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

// Session ID for voice interface (separate from stats manager)
let sessionId = null;

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
  // Try to handle stats-related messages first
  if (statsManager && statsManager.handleStatsMessage(type, content)) {
    return; // Message was handled by stats manager
  }

  if (type === "session_info") {
    // Received session info from server
    if (content.session_id) {
      sessionId = content.session_id;
    }
    return;
  }

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
}

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
