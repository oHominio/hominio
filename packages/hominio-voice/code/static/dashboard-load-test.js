// Load Test JavaScript
class VoiceChatLoadTester {
  constructor() {
    this.testUsers = new Map();
    this.isTestRunning = false;
    this.testStartTime = null;
    this.testDuration = 3; // minutes
    this.stats = {
      activeUsers: 0,
      totalMessages: 0,
      totalAudioChunks: 0,
      latencies: [],
    };

    // Pre-recorded audio prompts using your existing MP3 files
    this.audioPrompts = [
      {
        text: "Test prompt 1",
        file: "/static/test-audio/test1.mp3",
        duration: null,
      },
      {
        text: "Test prompt 2",
        file: "/static/test-audio/test2.mp3",
        duration: null,
      },
      {
        text: "Test prompt 3",
        file: "/static/test-audio/test3.mp3",
        duration: null,
      },
      {
        text: "Test prompt 4",
        file: "/static/test-audio/test4.mp3",
        duration: null,
      },
      {
        text: "Test prompt 5",
        file: "/static/test-audio/test5.mp3",
        duration: null,
      },
      {
        text: "Test prompt 6",
        file: "/static/test-audio/test6.mp3",
        duration: null,
      },
    ];

    this.loadedAudioBuffers = new Map(); // Cache for decoded audio

    this.initializeUI();
    this.setupEventListeners();
  }

  initializeUI() {
    // Update slider values
    const userCountSlider = document.getElementById("userCount");
    const userCountValue = document.getElementById("userCountValue");
    const testDurationSlider = document.getElementById("testDuration");
    const testDurationValue = document.getElementById("testDurationValue");

    userCountSlider.addEventListener("input", (e) => {
      userCountValue.textContent = e.target.value;
    });

    testDurationSlider.addEventListener("input", (e) => {
      testDurationValue.textContent = e.target.value;
      this.testDuration = parseInt(e.target.value);
    });
  }

  setupEventListeners() {
    document
      .getElementById("startTest")
      .addEventListener("click", () => this.startLoadTest());
    document
      .getElementById("stopTest")
      .addEventListener("click", () => this.stopLoadTest());
  }

  async startLoadTest() {
    const userCount = parseInt(document.getElementById("userCount").value);
    this.testDuration = parseInt(document.getElementById("testDuration").value);

    this.log(
      "info",
      `Starting load test with ${userCount} users for ${this.testDuration} minutes`
    );

    // Load audio files first
    this.log("info", "Loading audio files...");
    await this.loadAudioFiles();

    this.isTestRunning = true;
    this.testStartTime = Date.now();

    // Update UI
    document.getElementById("startTest").style.display = "none";
    document.getElementById("stopTest").style.display = "inline-block";

    // Create test users
    for (let i = 0; i < userCount; i++) {
      await this.createTestUser(i);
      // Stagger user creation to avoid overwhelming the server
      await this.sleep(200);
    }

    // Start test scenario
    this.runTestScenario();

    // Auto-stop after test duration
    setTimeout(
      () => {
        if (this.isTestRunning) {
          this.stopLoadTest();
        }
      },
      this.testDuration * 60 * 1000
    );
  }

  async createTestUser(userId) {
    const testUser = new TestUser(userId, this);
    try {
      await testUser.connect();
      this.testUsers.set(userId, testUser);
      this.stats.activeUsers++;
      this.updateStats();
      this.updateUserList();
      this.log("success", `Test user ${userId} connected successfully`);
    } catch (error) {
      this.log(
        "error",
        `Failed to connect test user ${userId}: ${error.message}`
      );
    }
  }

  async runTestScenario() {
    // Each user runs their own independent conversation loop
    const userPromises = [];

    for (const [userId, user] of this.testUsers) {
      userPromises.push(this.runUserConversationLoop(user));
    }

    // Wait for all user conversation loops to complete
    await Promise.all(userPromises);
  }

  async runUserConversationLoop(user) {
    const conversationsPerSession = 3 + Math.floor(Math.random() * 4); // 3-6 conversations
    this.log(
      "info",
      `User ${user.userId} will have ${conversationsPerSession} conversations`
    );

    for (let i = 0; i < conversationsPerSession && this.isTestRunning; i++) {
      try {
        // Send audio prompt and wait for complete response
        await user.sendRandomAudioPromptAndWaitForResponse();

        // Random pause between conversations (5-25 seconds)
        const pauseDuration = 5000 + Math.random() * 20000; // 5-25 seconds

        this.log(
          "info",
          `User ${user.userId} pausing ${(pauseDuration / 1000).toFixed(1)}s before next prompt`
        );
        await this.sleep(pauseDuration);
      } catch (error) {
        this.log(
          "error",
          `User ${user.userId} conversation error: ${error.message}`
        );
        break;
      }
    }

    this.log("info", `User ${user.userId} completed conversation session`);
  }

  stopLoadTest() {
    this.log("warning", "Stopping load test...");
    this.isTestRunning = false;

    // Disconnect all test users
    for (const [userId, user] of this.testUsers) {
      user.disconnect();
    }

    this.testUsers.clear();
    this.stats.activeUsers = 0;
    this.updateStats();
    this.updateUserList();

    // Update UI
    document.getElementById("startTest").style.display = "inline-block";
    document.getElementById("stopTest").style.display = "none";

    // Update UI
    document.getElementById("startTest").disabled = false;
    document.getElementById("stopTest").disabled = true;

    this.log("info", "Load test stopped");
  }

  updateStats() {
    document.getElementById("activeUsers").textContent = this.stats.activeUsers;
    document.getElementById("totalMessages").textContent =
      this.stats.totalMessages;
    document.getElementById("totalAudio").textContent =
      this.stats.totalAudioChunks;

    const avgLatency =
      this.stats.latencies.length > 0
        ? Math.round(
            this.stats.latencies.reduce((a, b) => a + b, 0) /
              this.stats.latencies.length
          )
        : 0;
    document.getElementById("avgLatency").textContent = `${avgLatency}ms`;
  }

  updateUserList() {
    const userList = document.getElementById("userList");

    if (this.testUsers.size === 0) {
      userList.innerHTML =
        '<div style="text-align: center; color: #6c757d; padding: 20px;">No test users active</div>';
      return;
    }

    const usersHtml = Array.from(this.testUsers.values())
      .map(
        (user) => `
            <div class="user-item">
                <div class="user-info">
                    <div class="user-id">Test User ${user.userId}</div>
                    <div class="user-status">${user.status} • ${user.messagesSent} msgs sent</div>
                </div>
                <div class="status-dot ${user.statusClass}"></div>
            </div>
        `
      )
      .join("");

    userList.innerHTML = usersHtml;
  }

  recordLatency(latency) {
    this.stats.latencies.push(latency);
    // Keep only last 100 measurements
    if (this.stats.latencies.length > 100) {
      this.stats.latencies.shift();
    }
  }

  log(level, message) {
    const logPanel = document.getElementById("logPanel");
    if (!logPanel) {
      // Fallback to console if logPanel doesn't exist
      console.log(`[${level.toUpperCase()}] ${message}`);
      return;
    }

    const timestamp = new Date().toLocaleTimeString();
    const entry = document.createElement("div");
    entry.className = "log-entry";
    entry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-${level}">${message}</span>
        `;
    logPanel.appendChild(entry);
    logPanel.scrollTop = logPanel.scrollHeight;
  }

  async loadAudioFiles() {
    const audioContext = new AudioContext();

    for (const prompt of this.audioPrompts) {
      try {
        this.log("info", `Loading ${prompt.file}...`);

        // Fetch the MP3 file
        const response = await fetch(prompt.file);
        if (!response.ok) {
          throw new Error(`Failed to fetch ${prompt.file}: ${response.status}`);
        }

        const arrayBuffer = await response.arrayBuffer();

        // Decode MP3 to PCM audio data
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        // Convert to 48kHz mono PCM (Int16Array) to match server expectations (48kHz -> 16kHz resample ratio 3:1)
        const targetSampleRate = 48000;
        const duration = audioBuffer.duration;
        prompt.duration = duration * 1000; // Store duration in milliseconds

        // Resample and convert to mono if needed
        const pcmData = this.convertToPCM48kMono(audioBuffer, targetSampleRate);

        this.loadedAudioBuffers.set(prompt.file, {
          pcmData: pcmData,
          duration: duration,
          sampleRate: targetSampleRate,
        });

        this.log(
          "success",
          `Loaded ${prompt.file} (${duration.toFixed(1)}s, ${pcmData.length} samples)`
        );
      } catch (error) {
        this.log("error", `Failed to load ${prompt.file}: ${error.message}`);
      }
    }

    audioContext.close();
  }

  convertToPCM48kMono(audioBuffer, targetSampleRate) {
    // Get source data
    const sourceRate = audioBuffer.sampleRate;
    const sourceData = audioBuffer.getChannelData(0); // Use first channel (mono)

    // Calculate resample ratio
    const resampleRatio = targetSampleRate / sourceRate;
    const outputLength = Math.floor(sourceData.length * resampleRatio);

    // Simple linear interpolation resampling
    const resampledData = new Float32Array(outputLength);
    for (let i = 0; i < outputLength; i++) {
      const sourceIndex = i / resampleRatio;
      const index = Math.floor(sourceIndex);
      const fraction = sourceIndex - index;

      if (index + 1 < sourceData.length) {
        resampledData[i] =
          sourceData[index] * (1 - fraction) + sourceData[index + 1] * fraction;
      } else {
        resampledData[i] = sourceData[index] || 0;
      }
    }

    // Convert to Int16Array (PCM 16-bit)
    const pcmData = new Int16Array(outputLength);
    for (let i = 0; i < outputLength; i++) {
      // Clamp and convert float [-1, 1] to int16 [-32768, 32767]
      const sample = Math.max(-1, Math.min(1, resampledData[i]));
      pcmData[i] = Math.round(sample * 32767);
    }

    return pcmData;
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

class TestUser {
  constructor(userId, tester) {
    this.userId = userId;
    this.tester = tester;
    this.socket = null;
    this.status = "disconnected";
    this.statusClass = "idle";
    this.messagesSent = 0;
    this.audioContext = null;
    this.lastAudioDuration = 0;
    this.waitingForResponse = false;
    this.responsePromise = null;
    this.responseResolve = null;

    // Each user will choose completely random audio files during the session
  }

  getRandomAudioPrompt() {
    // Choose a completely random audio file each time
    const randomIndex = Math.floor(
      Math.random() * this.tester.audioPrompts.length
    );
    const prompt = this.tester.audioPrompts[randomIndex];

    this.tester.log(
      "info",
      `User ${this.userId} randomly selected: "${prompt.text}"`
    );
    return prompt;
  }

  async connect() {
    return new Promise((resolve, reject) => {
      const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
      this.socket = new WebSocket(`${wsProto}//${location.host}/ws`);

      this.socket.onopen = () => {
        this.status = "connected";
        this.statusClass = "connected";
        this.tester.log("info", `User ${this.userId} connected`);
        resolve();
      };

      this.socket.onmessage = (event) => {
        this.handleMessage(event);
      };

      this.socket.onclose = () => {
        this.status = "disconnected";
        this.statusClass = "idle";
        this.tester.log("warning", `User ${this.userId} disconnected`);
      };

      this.socket.onerror = (error) => {
        this.tester.log("error", `User ${this.userId} error: ${error}`);
        reject(error);
      };

      // Timeout after 10 seconds
      setTimeout(() => {
        if (this.socket.readyState !== WebSocket.OPEN) {
          reject(new Error("Connection timeout"));
        }
      }, 10000);
    });
  }

  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case "session_info":
          this.sessionId = message.content.session_id;
          this.tester.log(
            "info",
            `User ${this.userId} got session: ${this.sessionId.substring(0, 8)}`
          );
          break;

        case "partial_assistant_answer":
          this.status = "receiving response";
          this.statusClass = "listening";
          break;

        case "final_assistant_answer":
          this.status = "response complete";
          this.statusClass = "connected";
          this.tester.log(
            "info",
            `User ${this.userId} received final response: "${message.content.substring(0, 50)}..."`
          );

          // Response received - resolve the waiting promise
          if (this.waitingForResponse && this.responseResolve) {
            this.waitingForResponse = false;
            this.responseResolve();
            this.responseResolve = null;
          }
          break;

        case "tts_chunk":
          // Simulate TTS playback
          this.status = "playing audio";
          this.statusClass = "speaking";
          break;
      }

      this.tester.updateUserList();
    } catch (error) {
      this.tester.log(
        "error",
        `User ${this.userId} message parse error: ${error.message}`
      );
    }
  }

  async sendRandomAudioPromptAndWaitForResponse() {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("Socket not connected");
    }

    const prompt = this.getRandomAudioPrompt();

    this.status = "sending audio";
    this.statusClass = "processing";
    this.lastAudioDuration = prompt.duration || 5000;

    this.tester.log(
      "info",
      `User ${this.userId} starting conversation with: "${prompt.text}" (${(this.lastAudioDuration / 1000).toFixed(1)}s)`
    );

    // Set up response waiting
    this.waitingForResponse = true;
    this.responsePromise = new Promise((resolve, reject) => {
      this.responseResolve = resolve;

      // Timeout after 20 seconds if no response
      setTimeout(() => {
        if (this.waitingForResponse) {
          this.waitingForResponse = false;
          this.responseResolve = null;
          reject(new Error("Response timeout"));
        }
      }, 20000);
    });

    // Send the audio
    await this.simulateAudioSending(prompt);

    this.messagesSent++;
    this.tester.stats.totalMessages++;
    this.tester.updateStats();
    this.tester.updateUserList();

    // Wait for the AI response
    this.tester.log("info", `User ${this.userId} waiting for AI response...`);
    await this.responsePromise;

    this.tester.log("info", `User ${this.userId} conversation turn complete`);
  }

  // Keep the old method for backward compatibility (if needed)
  async sendRandomAudioPrompt() {
    return this.sendRandomAudioPromptAndWaitForResponse();
  }

  async simulateAudioSending(prompt) {
    const startTime = Date.now();

    // Get the loaded audio buffer for this prompt
    const audioBuffer = this.tester.loadedAudioBuffers.get(prompt.file);
    if (!audioBuffer) {
      this.tester.log("error", `Audio buffer not found for ${prompt.file}`);
      return;
    }

    const pcmData = audioBuffer.pcmData;
    const chunkSize = 2048; // samples per chunk
    const sampleRate = 48000;
    const bytesPerSample = 2;
    const chunkDuration = (chunkSize / sampleRate) * 1000; // ms per chunk

    // Store the actual duration for realistic pauses
    this.lastAudioDuration = audioBuffer.duration * 1000; // Convert to milliseconds

    this.tester.log(
      "info",
      `User ${this.userId} streaming ${pcmData.length} samples (${audioBuffer.duration.toFixed(1)}s)`
    );

    let sampleIndex = 0;

    // Stream the real audio data in chunks like a fake microphone
    while (
      sampleIndex < pcmData.length &&
      this.socket &&
      this.socket.readyState === WebSocket.OPEN
    ) {
      // Create audio chunk with header
      const audioData = new ArrayBuffer(8 + chunkSize * bytesPerSample);
      const view = new DataView(audioData);
      const pcmView = new Int16Array(audioData, 8); // Audio data starts after 8-byte header

      // Set timestamp (big-endian uint32)
      view.setUint32(0, Date.now() & 0xffffffff, false);
      // Set flags (not TTS playing = 0)
      view.setUint32(4, 0, false);

      // Copy real PCM audio data into the chunk
      const samplesThisChunk = Math.min(
        chunkSize,
        pcmData.length - sampleIndex
      );
      for (let i = 0; i < samplesThisChunk; i++) {
        pcmView[i] = pcmData[sampleIndex + i];
      }

      // Pad with silence if needed
      for (let i = samplesThisChunk; i < chunkSize; i++) {
        pcmView[i] = 0;
      }

      // Send the real audio chunk
      this.socket.send(audioData);
      this.tester.stats.totalAudioChunks++;

      sampleIndex += samplesThisChunk;

      // Wait for the chunk duration to simulate real-time streaming
      await this.tester.sleep(chunkDuration);
    }

    // Record latency
    const latency = Date.now() - startTime;
    this.tester.recordLatency(latency);

    this.status = "waiting for response";
    this.statusClass = "listening";
    this.tester.log(
      "info",
      `User ${this.userId} finished streaming audio (${latency}ms)`
    );
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
    if (this.audioContext) {
      this.audioContext.close();
    }
  }
}

// Initialize the load tester when page loads
document.addEventListener("DOMContentLoaded", () => {
  window.loadTester = new VoiceChatLoadTester();
});
