<script>
	import { onMount } from 'svelte';
	import { HominioVoice } from '$lib/hominio-sdk.js';

	// Simple state management for the UI
	let voice;
	let isConnected = false;
	let conversationState = 'idle'; // Will be set after voice is initialized
	let lastTranscript = '';
	let lastResponse = '';
	let statusMessage = '';
	let error = null;

	onMount(() => {
		// Zero-config initialization - works out of the box!
		voice = new HominioVoice();

		// Set initial state now that voice is initialized
		conversationState = voice.states.IDLE;

		// Set up event listeners with clean, intuitive callbacks
		voice
			.on(voice.events.CONNECTED, () => {
				isConnected = true;
				error = null;
			})

			.on(voice.events.DISCONNECTED, () => {
				isConnected = false;
				conversationState = voice.states.IDLE;
				statusMessage = '';
			})

			.on(voice.events.STATE_CHANGE, (newState) => {
				conversationState = newState;
			})

			.on(voice.events.TRANSCRIPT, (text, isFinal) => {
				if (isFinal) {
					lastTranscript = text;
				}
			})

			.on(voice.events.RESPONSE, (text) => {
				lastResponse = text;
			})

			.on(voice.events.STATUS_UPDATE, (message) => {
				statusMessage = message;
			})

			.on(voice.events.ERROR, (err) => {
				error = err.message;
				console.error('Voice error:', err);
			});
	});

	async function startConversation() {
		try {
			error = null;
			await voice.connect();
		} catch (err) {
			error = err.message;
		}
	}

	function stopConversation() {
		voice.disconnect();
	}

	function getStateEmoji() {
		switch (conversationState) {
			case voice?.states.LISTENING:
				return '👂';
			case voice?.states.THINKING:
				return '🤔';
			case voice?.states.SPEAKING:
				return '🗣️';
			default:
				return '😴';
		}
	}

	function getStateLabel() {
		switch (conversationState) {
			case voice?.states.LISTENING:
				return 'Listening...';
			case voice?.states.THINKING:
				return 'AI is thinking...';
			case voice?.states.SPEAKING:
				return 'AI is speaking...';
			default:
				return 'Ready to talk';
		}
	}
</script>

<main>
	<h1>🎤 Hominio Voice SDK Demo</h1>
	<p>Zero-config voice conversation integration - works instantly out of the box!</p>

	<div class="voice-controls">
		<div class="status-card">
			<div class="status-icon">{getStateEmoji()}</div>
			<div class="status-text">
				<strong>{getStateLabel()}</strong>
				<div class="connection-status">
					{isConnected ? '🟢 Connected' : '🔴 Disconnected'}
				</div>
				{#if statusMessage}
					<div class="status-message">{statusMessage}</div>
				{/if}
			</div>
		</div>

		<div class="controls">
			{#if !isConnected}
				<button class="start-btn" on:click={startConversation}> 🎤 Start Conversation </button>
			{:else}
				<button class="stop-btn" on:click={stopConversation}> 🛑 Stop Conversation </button>
			{/if}
		</div>

		{#if error}
			<div class="error">❌ {error}</div>
		{/if}
	</div>

	<div class="conversation-display">
		{#if lastTranscript}
			<div class="transcript">
				<strong>👤 You said:</strong>
				<p>"{lastTranscript}"</p>
			</div>
		{/if}

		{#if lastResponse}
			<div class="response">
				<strong>🤖 AI responded:</strong>
				<p>"{lastResponse}"</p>
			</div>
		{/if}

		{#if !lastTranscript && !lastResponse}
			<div class="empty-state">
				<p>💬 Your conversation will appear here</p>
			</div>
		{/if}
	</div>

	<div class="code-example">
		<h2>📝 Developer Experience - Complete Implementation</h2>
		<div class="code-tabs">
			<div class="tab active">JavaScript</div>
		</div>
		<pre><code
				>{`// 1. Install the SDK
npm install @hominio/voice-sdk

// 2. Import and initialize (ZERO CONFIG!)
import { HominioVoice } from '@hominio/voice-sdk';

const voice = new HominioVoice(); // That's it! Works out of the box

// 3. Set up event listeners (chainable, clean)
voice
	.on(voice.events.STATE_CHANGE, (state) => {
		console.log('State changed:', state);
		// Update your UI: idle → listening → thinking → speaking
	})
	.on(voice.events.TRANSCRIPT, (text, isFinal) => {
		if (isFinal) {
			console.log('User said:', text);
		}
	})
	.on(voice.events.RESPONSE, (text) => {
		console.log('AI responded:', text);
	});

// 4. Start/stop conversation (2 methods)
await voice.connect();    // Auto-handles everything!
voice.disconnect();       // Clean shutdown

// 💡 Check states easily
if (voice.getState().currentState === voice.states.LISTENING) {
	console.log('User is speaking!');
}

// ✨ OPTIONAL: Custom configuration
const customVoice = new HominioVoice({
	apiKey: 'your-production-key',      // Optional override
	serverUrl: 'wss://your-server.com', // Optional override  
	systemPrompt: 'You are a helpful assistant specialized in...'
});

// That's it! 🎉 Voice chat in ~10 lines`}</code
			></pre>
	</div>

	<div class="features-grid">
		<h2>✨ What You Get Out of the Box</h2>
		<div class="features">
			<div class="feature">
				<div class="feature-icon">⚡</div>
				<h3>Zero Configuration</h3>
				<p>Works instantly - no API keys or setup required</p>
			</div>
			<div class="feature">
				<div class="feature-icon">🎤</div>
				<h3>Auto Mic Permissions</h3>
				<p>SDK handles browser permissions automatically</p>
			</div>
			<div class="feature">
				<div class="feature-icon">🔄</div>
				<h3>Real-time States</h3>
				<p>listening → thinking → speaking transitions</p>
			</div>
			<div class="feature">
				<div class="feature-icon">💬</div>
				<h3>Live Transcription</h3>
				<p>Partial + final speech-to-text results</p>
			</div>
			<div class="feature">
				<div class="feature-icon">🤖</div>
				<h3>AI Responses</h3>
				<p>Intelligent conversation with TTS playback</p>
			</div>
			<div class="feature">
				<div class="feature-icon">🌐</div>
				<h3>Framework Agnostic</h3>
				<p>Works with React, Vue, Svelte, vanilla JS</p>
			</div>
		</div>
	</div>
</main>

<style>
	main {
		max-width: 900px;
		margin: 0 auto;
		padding: 2rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	h1 {
		text-align: center;
		color: #2c3e50;
		margin-bottom: 0.5rem;
	}

	p {
		text-align: center;
		color: #7f8c8d;
		margin-bottom: 2rem;
	}

	.voice-controls {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		padding: 2rem;
		border-radius: 16px;
		margin-bottom: 2rem;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
	}

	.status-card {
		display: flex;
		align-items: center;
		gap: 1rem;
		background: rgba(255, 255, 255, 0.9);
		padding: 1.5rem;
		border-radius: 12px;
		margin-bottom: 1.5rem;
	}

	.status-icon {
		font-size: 2rem;
	}

	.status-text strong {
		display: block;
		color: #2c3e50;
		font-size: 1.1rem;
		margin-bottom: 0.25rem;
	}

	.connection-status {
		font-size: 0.9rem;
		color: #7f8c8d;
		margin-bottom: 0.25rem;
	}

	.status-message {
		font-size: 0.85rem;
		color: #3498db;
		font-style: italic;
	}

	.controls {
		text-align: center;
	}

	.start-btn,
	.stop-btn {
		background: linear-gradient(135deg, #7ed4ad 0%, #6bc49a 100%);
		border: none;
		padding: 1rem 2rem;
		border-radius: 50px;
		color: white;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 5px 15px rgba(126, 212, 173, 0.3);
	}

	.stop-btn {
		background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
		box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
	}

	.start-btn:hover,
	.stop-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
	}

	.error {
		background: rgba(231, 76, 60, 0.1);
		border: 1px solid #e74c3c;
		color: #e74c3c;
		padding: 1rem;
		border-radius: 8px;
		margin-top: 1rem;
		text-align: center;
	}

	.conversation-display {
		background: #f8f9fa;
		padding: 2rem;
		border-radius: 12px;
		margin-bottom: 2rem;
		min-height: 120px;
	}

	.transcript,
	.response {
		margin-bottom: 1.5rem;
		padding: 1rem;
		border-radius: 8px;
	}

	.transcript {
		background: #e3f2fd;
		border-left: 4px solid #2196f3;
	}

	.response {
		background: #f1f8e9;
		border-left: 4px solid #4caf50;
	}

	.transcript p,
	.response p {
		margin: 0.5rem 0 0 0;
		font-style: italic;
	}

	.empty-state {
		text-align: center;
		color: #6c757d;
		padding: 2rem;
	}

	.code-example {
		background: #2d3748;
		color: #e2e8f0;
		padding: 2rem;
		border-radius: 12px;
		overflow-x: auto;
		margin-bottom: 2rem;
	}

	.code-example h2 {
		color: #7ed4ad;
		margin-top: 0;
		margin-bottom: 1rem;
	}

	.code-tabs {
		display: flex;
		margin-bottom: 1rem;
	}

	.tab {
		background: rgba(255, 255, 255, 0.1);
		padding: 0.5rem 1rem;
		border-radius: 6px 6px 0 0;
		font-size: 0.85rem;
		color: #a0aec0;
	}

	.tab.active {
		background: rgba(255, 255, 255, 0.2);
		color: #e2e8f0;
	}

	pre {
		margin: 0;
		font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
		font-size: 0.85rem;
		line-height: 1.6;
	}

	code {
		color: #e2e8f0;
	}

	.features-grid {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
		padding: 2rem;
		border-radius: 16px;
		color: white;
	}

	.features-grid h2 {
		text-align: center;
		margin-bottom: 2rem;
		color: white;
	}

	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 1.5rem;
	}

	.feature {
		background: rgba(255, 255, 255, 0.2);
		padding: 1.5rem;
		border-radius: 12px;
		text-align: center;
		backdrop-filter: blur(10px);
	}

	.feature-icon {
		font-size: 2rem;
		margin-bottom: 1rem;
	}

	.feature h3 {
		margin: 0 0 0.5rem 0;
		font-size: 1rem;
	}

	.feature p {
		margin: 0;
		font-size: 0.85rem;
		opacity: 0.9;
		text-align: center;
	}
</style>
