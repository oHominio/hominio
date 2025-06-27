/**
 * Hominio Voice SDK - Mock Implementation
 *
 * This is a mock implementation for API design and DX demonstration.
 * The real SDK would connect to actual voice processing servers.
 */

export class HominioVoice {
	constructor(options = {}) {
		// Zero-config defaults with optional overrides
		this.apiKey = options.apiKey || 'demo-hominio-key';
		this.serverUrl = options.serverUrl || 'wss://api.hominio.com/voice';
		this.systemPrompt = options.systemPrompt || 'You are a helpful AI assistant.';

		// Instance properties for easy access
		this.states = {
			IDLE: 'idle',
			LISTENING: 'listening',
			THINKING: 'thinking',
			SPEAKING: 'speaking'
		};

		this.events = {
			CONNECTED: 'connected',
			DISCONNECTED: 'disconnected',
			STATE_CHANGE: 'stateChange',
			TRANSCRIPT: 'transcript',
			RESPONSE: 'response',
			ERROR: 'error',
			STATUS_UPDATE: 'statusUpdate'
		};

		// Internal state
		this.state = 'idle';
		this.isConnected = false;
		this.callbacks = {};
		this.ws = null;
		this.mediaRecorder = null;
		this.audioStream = null;

		// Mock conversation scenarios
		this.conversationScenarios = [
			{
				userInput: 'Hello, how are you?',
				aiResponse: "Hi there! I'm doing great, thank you for asking. How can I help you today?"
			},
			{
				userInput: "What's the weather like?",
				aiResponse:
					"I don't have access to real-time weather data, but I'd be happy to help you find a reliable weather service!"
			},
			{
				userInput: 'Tell me a joke',
				aiResponse: "Why don't scientists trust atoms? Because they make up everything! 😄"
			}
		];
		this.currentScenario = 0;
	}

	/**
	 * Register event listeners with fluent interface
	 */
	on(event, callback) {
		this.callbacks[event] = callback;
		return this; // Enable chaining
	}

	/**
	 * Connect to voice service and start conversation
	 */
	async connect() {
		try {
			// Step 1: Request microphone permissions
			this._emit('statusUpdate', 'Requesting microphone access...');
			await this._requestMicrophonePermission();

			// Step 2: Connect to WebSocket
			this._emit('statusUpdate', 'Connecting to voice service...');
			await this._connectWebSocket();

			// Step 3: Initialize audio recording
			this._emit('statusUpdate', 'Initializing audio processing...');
			await this._initializeAudioRecording();

			// Step 4: Ready to start
			this.isConnected = true;
			this._setState('listening');
			this._emit('connected');
			this._emit('statusUpdate', 'Connected! Start speaking...');

			// Start simulated conversation flow
			this._startMockConversationFlow();

			return this;
		} catch (error) {
			this._emit('error', error);
			throw error;
		}
	}

	/**
	 * Disconnect from voice service
	 */
	disconnect() {
		this.isConnected = false;

		// Clean up resources
		if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
			this.mediaRecorder.stop();
		}

		if (this.audioStream) {
			this.audioStream.getTracks().forEach((track) => track.stop());
		}

		if (this.ws) {
			this.ws.close();
		}

		this._setState('idle');
		this._emit('disconnected');
		this._emit('statusUpdate', 'Disconnected');

		return this;
	}

	/**
	 * Get current connection state
	 */
	getState() {
		return {
			isConnected: this.isConnected,
			currentState: this.state
		};
	}

	// Private methods for mock implementation

	async _requestMicrophonePermission() {
		return new Promise((resolve, reject) => {
			setTimeout(() => {
				// Mock permission request
				if (Math.random() > 0.1) {
					// 90% success rate
					resolve();
				} else {
					reject(new Error('Microphone permission denied'));
				}
			}, 800);
		});
	}

	async _connectWebSocket() {
		return new Promise((resolve, reject) => {
			setTimeout(() => {
				// Mock WebSocket connection
				this.ws = {
					readyState: 1, // OPEN
					close: () => {},
					send: (data) => console.log('📤 Sending to server:', data)
				};

				if (Math.random() > 0.05) {
					// 95% success rate
					resolve();
				} else {
					reject(new Error('Failed to connect to voice service'));
				}
			}, 500);
		});
	}

	async _initializeAudioRecording() {
		return new Promise((resolve) => {
			setTimeout(() => {
				// Mock audio stream
				this.audioStream = {
					getTracks: () => [{ stop: () => {} }]
				};

				this.mediaRecorder = {
					state: 'inactive',
					start: () => {},
					stop: () => {},
					ondataavailable: null
				};

				resolve();
			}, 300);
		});
	}

	_startMockConversationFlow() {
		// Simulate user speaking after a delay
		setTimeout(() => {
			this._simulateUserSpeech();
		}, 2000);
	}

	_simulateUserSpeech() {
		if (!this.isConnected) return;

		const scenario =
			this.conversationScenarios[this.currentScenario % this.conversationScenarios.length];

		// Simulate partial transcription
		this._setState('listening');
		this._simulatePartialTranscript(scenario.userInput, () => {
			// Final transcript
			this._emit('transcript', scenario.userInput, true);

			// AI thinking
			this._setState('thinking');

			setTimeout(() => {
				// AI responding
				this._setState('speaking');
				this._emit('response', scenario.aiResponse);

				// Back to listening after AI finishes
				setTimeout(() => {
					this._setState('listening');
					this.currentScenario++;

					// Next conversation turn after pause
					setTimeout(() => {
						if (this.isConnected) {
							this._simulateUserSpeech();
						}
					}, 4000);
				}, 2500);
			}, 1200);
		});
	}

	_simulatePartialTranscript(fullText, onComplete) {
		const words = fullText.split(' ');
		let currentText = '';
		let wordIndex = 0;

		const addWord = () => {
			if (wordIndex < words.length) {
				currentText += (wordIndex > 0 ? ' ' : '') + words[wordIndex];
				this._emit('transcript', currentText, false);
				wordIndex++;
				setTimeout(addWord, 150 + Math.random() * 200);
			} else {
				onComplete();
			}
		};

		addWord();
	}

	_setState(newState) {
		if (this.state !== newState) {
			this.state = newState;
			this._emit('stateChange', newState);
		}
	}

	_emit(event, ...args) {
		if (this.callbacks[event]) {
			this.callbacks[event](...args);
		}
	}
}
