<script>
	import { onMount } from 'svelte';
	import { marked } from 'marked';
	import { v4 as uuidv4 } from 'uuid';

	let taskDescription = 'The future of AI agents in software development';
	let expectedOutput = 'A 3-paragraph blog post about the topic.';
	let intents = [];
	let selectedIntentId = null;
	let logContentElement;
	let isNearBottom = true;

	marked.setOptions({
		gfm: true,
		breaks: true
	});

	function selectIntent(intentId) {
		selectedIntentId = intentId;
	}

	$: selectedIntent = intents.find((i) => i.id === selectedIntentId);

	// Smart auto-scroll: only scroll to bottom if user is already near the bottom
	$: if (
		selectedIntent &&
		logContentElement &&
		(selectedIntent.activityLog || selectedIntent.rawData) &&
		isNearBottom
	) {
		setTimeout(() => {
			if (logContentElement && isNearBottom) {
				logContentElement.scrollTop = logContentElement.scrollHeight;
			}
		}, 10);
	}

	// Check if user is near bottom when they scroll
	function handleLogScroll() {
		if (logContentElement) {
			const { scrollTop, scrollHeight, clientHeight } = logContentElement;
			const threshold = 100; // pixels from bottom
			isNearBottom = scrollTop + clientHeight >= scrollHeight - threshold;
		}
	}

	// When intents list changes, update selection
	$: {
		if (intents.length > 0 && !intents.find((i) => i.id === selectedIntentId)) {
			selectedIntentId = intents[0].id; // Select the newest one
		} else if (intents.length === 0) {
			selectedIntentId = null;
		}
	}

	async function startVibe() {
		const intentId = uuidv4();
		const abortController = new AbortController();

		const newIntent = {
			id: intentId,
			taskDescription,
			expectedOutput,
			tasks: [],
			activityLog: '',
			rawData: '', // For debugging
			finalResult: null,
			error: null,
			timer: 0,
			timerId: null,
			status: 'RUNNING', // RUNNING, DONE, ERROR, STOPPED
			abortController
		};

		intents = [newIntent, ...intents];
		selectIntent(intentId);

		newIntent.timerId = setInterval(() => {
			const intentIndex = intents.findIndex((i) => i.id === intentId);
			if (intentIndex !== -1) {
				// To trigger reactivity, we need to reassign the array
				intents[intentIndex].timer += 1;
				intents = [...intents];
			}
		}, 1000);

		try {
			const response = await fetch('/api/intentVibe/execute', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				signal: abortController.signal,
				body: JSON.stringify({
					vibe: 'writing',
					task: {
						details: {
							description: taskDescription,
							expectedOutput: expectedOutput
						},
						inputs: {}
					}
				})
			});

			if (!response.body) return;

			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) {
					break;
				}

				const chunk = decoder.decode(value, { stream: true });
				console.log('[OS Frontend] Raw Chunk Received:', chunk);
				buffer += chunk;

				// Add raw chunk to debug data
				const intentIndex = intents.findIndex((i) => i.id === intentId);
				if (intentIndex !== -1) {
					const updatedIntent = { ...intents[intentIndex] };
					updatedIntent.rawData += chunk;
					intents[intentIndex] = updatedIntent;
					intents = [...intents];
				}

				// Process complete SSE events
				const events = buffer.split('\n\n');
				buffer = events.pop() || ''; // Keep incomplete event in buffer

				console.log('[OS Frontend] Processing events:', events.length);
				console.log('[OS Frontend] Buffer after split:', buffer.length, 'chars');

				for (const event of events) {
					if (!event.trim()) continue;

					console.log('[OS Frontend] Processing event:', event.substring(0, 150) + '...');

					// Extract data line from SSE event
					const lines = event.split('\n');
					console.log('[OS Frontend] Event has', lines.length, 'lines');

					for (const line of lines) {
						if (line.startsWith('data: ')) {
							const dataContent = line.substring(6); // Remove 'data: ' prefix
							console.log('[OS Frontend] Found data line:', dataContent.substring(0, 100) + '...');
							if (!dataContent.trim()) continue;

							const intentIndex = intents.findIndex((i) => i.id === intentId);
							if (intentIndex === -1) {
								console.log('[OS Frontend] Intent not found for ID:', intentId);
								continue;
							}

							try {
								const data = JSON.parse(dataContent);
								console.log(`[OS Frontend] Received ${data.type} event for intent ${intentId}`);
								const updatedIntent = { ...intents[intentIndex] };

								// Handle clean JSON data from backend
								if (data.tasks) {
									updatedIntent.tasks = data.tasks;
									console.log(`[OS Frontend] Updated tasks: ${data.tasks.length} tasks`);
								}
								if (data.log) {
									updatedIntent.activityLog += data.log + '\n';
									console.log(`[OS Frontend] Added log entry`);
								}
								if (data.result) {
									updatedIntent.finalResult = data.result;
									updatedIntent.status = 'DONE';
									console.log(`[OS Frontend] Task completed with result`);
								}
								if (data.error) {
									updatedIntent.error = data.error;
									updatedIntent.status = 'ERROR';
									console.log(`[OS Frontend] Task failed with error`);
								}
								if (data.status === 'completed') {
									updatedIntent.status = 'DONE';
									console.log(`[OS Frontend] Task marked as completed`);
								}

								intents[intentIndex] = updatedIntent;
								intents = [...intents];
							} catch (e) {
								console.error('[OS Frontend] JSON Parse Error:', e.message);
								console.error('[OS Frontend] Raw data:', dataContent.substring(0, 200));
							}
						}
					}
				}
			}
		} catch (e) {
			if (e.name === 'AbortError') {
				console.log(`Intent ${intentId} aborted by user.`);
			} else {
				console.error('Fetch Error:', e);
				intents = intents.map((intent) => {
					if (intent.id === intentId) {
						intent.error = 'Connection failed. Check the console for details.';
						intent.status = 'ERROR';
					}
					return intent;
				});
			}
		} finally {
			stopVibe(intentId, false);
		}

		taskDescription = '';
		expectedOutput = '';
	}

	function stopVibe(intentId, fromUser = true) {
		const intent = intents.find((i) => i.id === intentId);
		if (intent) {
			if (fromUser && intent.abortController) {
				intent.abortController.abort();
			}
			if (intent.timerId) {
				clearInterval(intent.timerId);
				intent.timerId = null;
			}
			if (intent.status === 'RUNNING') {
				intent.status = fromUser ? 'STOPPED' : 'DONE';
			}
			intents = [...intents];
		}
	}

	onMount(() => {
		return () => {
			intents.forEach((intent) => {
				if (intent.abortController) {
					intent.abortController.abort();
				}
				if (intent.timerId) {
					clearInterval(intent.timerId);
				}
			});
		};
	});
</script>

<div class="app-container">
	<!-- Header -->
	<header class="app-header">
		<div class="logo-section">
			<div class="logo-icon"></div>
			<div class="logo-text">
				<h1>Hominio OS</h1>
				<p>Your AI agent orchestration platform</p>
			</div>
		</div>
	</header>

	<div class="main-layout">
		<!-- Left Sidebar for Controls & Intent List -->
		<aside class="control-panel">
			<div class="panel-section">
				<h2 class="section-title">Start New Intent</h2>
				<div class="form-group">
					<label for="description">Task Description</label>
					<textarea
						id="description"
						bind:value={taskDescription}
						rows="4"
						class="form-textarea"
						placeholder="Describe what you want to accomplish..."
					></textarea>
				</div>
				<div class="form-group">
					<label for="expectedOutput">Expected Output</label>
					<textarea
						id="expectedOutput"
						bind:value={expectedOutput}
						rows="3"
						class="form-textarea"
						placeholder="What format or type of result do you expect?"
					></textarea>
				</div>
				<button on:click={startVibe} class="btn btn-primary"> Execute Writing Vibe </button>
			</div>

			<div class="panel-section">
				<h3 class="section-title">Active Intents</h3>
				<div class="intents-list">
					{#if intents.length === 0}
						<div class="empty-state">
							<p>No intents yet. Start one above!</p>
						</div>
					{/if}
					{#each intents as intent (intent.id)}
						<div
							class="intent-card {selectedIntentId === intent.id ? 'selected' : ''}"
							role="button"
							tabindex="0"
							on:click={() => selectIntent(intent.id)}
							on:keypress={() => selectIntent(intent.id)}
						>
							<div class="intent-header">
								<p class="intent-title">{intent.taskDescription}</p>

								{#if intent.status === 'RUNNING'}
									<button
										on:click|stopPropagation={() => stopVibe(intent.id)}
										class="stop-btn"
										title="Stop Intent"
										aria-label="Stop Intent"
									>
										Stop
									</button>
								{/if}
							</div>

							<div class="intent-footer">
								<div class="status-badge status-{intent.status.toLowerCase()}">
									{#if intent.status === 'RUNNING'}
										<span class="loading-dot"></span> Running
									{:else if intent.status === 'DONE'}
										Complete
									{:else if intent.status === 'ERROR'}
										Error
									{:else if intent.status === 'STOPPED'}
										Stopped
									{/if}
								</div>
								<div class="timer">
									{Math.floor(intent.timer / 60)}:{(intent.timer % 60).toString().padStart(2, '0')}
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</aside>

		<!-- Main Content: Task Board & Results -->
		<main class="main-content">
			{#if selectedIntent}
				<div class="content-header">
					<h2 class="intent-name">{selectedIntent.taskDescription}</h2>
				</div>

				<div class="content-body">
					{#if selectedIntent.finalResult}
						<div class="result-section">
							<h3 class="result-title">{selectedIntent.finalResult.title}</h3>
							<div class="result-content">
								{@html marked(selectedIntent.finalResult.body || '')}
							</div>
						</div>
					{:else if selectedIntent.error}
						<div class="error-section">
							<h4>Error Occurred</h4>
							<div class="error-content">
								{@html marked(selectedIntent.error || '')}
							</div>
						</div>
					{:else if selectedIntent.tasks.length > 0}
						<div class="task-board">
							<h3 class="board-title">Task Progress Board</h3>
							<div class="board-columns">
								<!-- TODO Column -->
								<div class="board-column todo-column">
									<div class="column-header">
										<h4>To Do</h4>
									</div>
									<div class="tasks-container">
										{#each selectedIntent.tasks.filter((t) => t.status === 'TODO') as task}
											<div class="task-card todo-task">
												<p class="task-name">{task.name}</p>
												<div class="task-status">TODO</div>
											</div>
										{/each}
									</div>
								</div>

								<!-- DOING Column -->
								<div class="board-column doing-column">
									<div class="column-header">
										<h4>In Progress</h4>
									</div>
									<div class="tasks-container">
										{#each selectedIntent.tasks.filter((t) => t.status === 'DOING') as task}
											<div class="task-card doing-task">
												<p class="task-name">{task.name}</p>
												<div class="task-status">
													<span class="loading-dot"></span> DOING
												</div>
											</div>
										{/each}
									</div>
								</div>

								<!-- DONE Column -->
								<div class="board-column done-column">
									<div class="column-header">
										<h4>Complete</h4>
									</div>
									<div class="tasks-container">
										{#each selectedIntent.tasks.filter((t) => t.status === 'DONE') as task}
											<div class="task-card done-task">
												<p class="task-name">{task.name}</p>
												<div class="task-status">DONE</div>
											</div>
										{/each}
									</div>
								</div>

								<!-- BLOCKED Column -->
								<div class="board-column blocked-column">
									<div class="column-header">
										<h4>Blocked</h4>
									</div>
									<div class="tasks-container">
										{#each selectedIntent.tasks.filter((t) => t.status === 'BLOCKED' || t.status === 'ERROR') as task}
											<div class="task-card blocked-task">
												<p class="task-name">{task.name}</p>
												<div class="task-status">{task.status}</div>
											</div>
										{/each}
									</div>
								</div>
							</div>
						</div>
					{:else}
						<div class="loading-section">
							<div class="loading-animation">
								<div class="loading-dot"></div>
								<div class="loading-dot"></div>
								<div class="loading-dot"></div>
							</div>
							<p>Initializing AI agents...</p>
						</div>
					{/if}
				</div>
			{:else}
				<div class="welcome-section">
					<div class="welcome-content">
						<h2>Welcome to Hominio OS</h2>
						<p>Your AI-powered orchestration platform for complex workflows</p>
						<p class="welcome-subtitle">Start a new intent from the control panel to begin</p>
					</div>
				</div>
			{/if}
		</main>

		<!-- Right Sidebar for Activity Log -->
		<aside class="activity-panel">
			<h2 class="panel-title">Activity Log</h2>
			{#if selectedIntent}
				{#if selectedIntent.activityLog.trim()}
					<h4 class="log-title">System Activity</h4>
					<pre
						class="log-content"
						bind:this={logContentElement}
						on:scroll={handleLogScroll}>{selectedIntent.activityLog}</pre>
				{:else if selectedIntent.rawData}
					<h4 class="debug-title">Debug Data</h4>
					<pre
						class="debug-content"
						bind:this={logContentElement}
						on:scroll={handleLogScroll}>{selectedIntent.rawData}</pre>
				{:else}
					<div class="empty-log">
						<p>Waiting for activity...</p>
					</div>
				{/if}
			{:else}
				<div class="empty-log">
					<p>Select an intent to view its activity log</p>
				</div>
			{/if}
		</aside>
	</div>
</div>

<style>
	.app-container {
		height: 100vh;
		max-height: 100vh;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		font-family:
			-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
		overflow: hidden;
	}

	.app-header {
		background: rgba(255, 255, 255, 0.7);
		backdrop-filter: blur(10px);
		border-bottom: 1px solid rgba(30, 58, 95, 0.1);
		padding: 1rem 2rem;
	}

	.logo-section {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.logo-icon {
		width: 40px;
		height: 40px;
		background: #1e3a5f;
		border-radius: 10px;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}

	.logo-icon::before {
		content: '';
		width: 12px;
		height: 12px;
		background: #f5f1e8;
		border-radius: 50%;
		position: absolute;
		top: 8px;
	}

	.logo-icon::after {
		content: '';
		width: 20px;
		height: 12px;
		background: #f5f1e8;
		border-radius: 10px 10px 0 0;
		position: absolute;
		bottom: 5px;
	}

	.logo-text h1 {
		margin: 0;
		font-size: 1.75rem;
		font-weight: 700;
		color: #1e3a5f;
		letter-spacing: -0.02em;
	}

	.logo-text p {
		margin: 0;
		color: #6b7280;
		font-size: 0.9rem;
	}

	.main-layout {
		flex: 1;
		display: grid;
		grid-template-columns: 320px 1fr 300px;
		gap: 0;
		height: calc(100vh - 90px);
		overflow: hidden;
		min-width: 0;
		width: 100vw;
	}

	.control-panel,
	.activity-panel {
		background: rgba(255, 255, 255, 0.6);
		backdrop-filter: blur(20px);
		border-right: 1px solid rgba(30, 58, 95, 0.1);
		padding: 1.5rem;
		overflow-y: auto;
		overflow-x: hidden;
		display: flex;
		flex-direction: column;
		height: 100%;
		min-width: 0;
		max-width: 100%;
	}

	.activity-panel {
		border-right: none;
		border-left: 1px solid rgba(30, 58, 95, 0.1);
		padding: 1rem;
		width: 300px;
		max-width: 300px;
		min-width: 300px;
		height: 100%;
		max-height: 100%;
		min-height: 0;
	}

	.panel-section {
		margin-bottom: 2rem;
	}

	.section-title,
	.panel-title {
		color: #1e3a5f;
		font-size: 1.1rem;
		font-weight: 600;
		margin-bottom: 1rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		color: #6b7280;
		font-size: 0.9rem;
		font-weight: 500;
	}

	.form-textarea {
		width: 100%;
		padding: 0.75rem;
		border: 2px solid rgba(30, 58, 95, 0.1);
		border-radius: 12px;
		background: rgba(255, 255, 255, 0.9);
		color: #1e3a5f;
		font-size: 0.9rem;
		resize: vertical;
		transition: all 0.3s ease;
		font-family: inherit;
	}

	.form-textarea:focus {
		outline: none;
		border-color: #7ed4ad;
		box-shadow: 0 0 0 3px rgba(126, 212, 173, 0.2);
	}

	.btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.875rem 1.5rem;
		border: none;
		border-radius: 50px;
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-family: inherit;
		width: 100%;
	}

	.btn-primary {
		background: #1e3a5f;
		color: white;
	}

	.btn-primary:hover {
		background: #2a4a6b;
		transform: translateY(-2px);
		box-shadow: 0 10px 20px rgba(30, 58, 95, 0.2);
	}

	.intents-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.empty-state {
		text-align: center;
		padding: 2rem 0;
		color: #6b7280;
		font-size: 0.9rem;
	}

	.intent-card {
		background: rgba(255, 255, 255, 0.8);
		border: 2px solid rgba(30, 58, 95, 0.1);
		border-radius: 16px;
		padding: 1rem;
		cursor: pointer;
		transition: all 0.3s ease;
	}

	.intent-card:hover {
		border-color: #7ed4ad;
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(30, 58, 95, 0.1);
	}

	.intent-card.selected {
		border-color: #7ed4ad;
		background: rgba(126, 212, 173, 0.1);
		box-shadow: 0 8px 16px rgba(126, 212, 173, 0.2);
	}

	.intent-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 0.75rem;
	}

	.intent-title {
		margin: 0;
		font-size: 0.9rem;
		font-weight: 600;
		color: #1e3a5f;
		line-height: 1.3;
		flex: 1;
	}

	.stop-btn {
		background: none;
		border: none;
		font-size: 1.2rem;
		cursor: pointer;
		padding: 0;
		margin-left: 0.5rem;
		opacity: 0.7;
		transition: opacity 0.3s ease;
	}

	.stop-btn:hover {
		opacity: 1;
	}

	.intent-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.status-badge {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.status-running {
		background: rgba(59, 130, 246, 0.2);
		color: #1e40af;
	}

	.status-done {
		background: rgba(34, 197, 94, 0.2);
		color: #15803d;
	}

	.status-error {
		background: rgba(239, 68, 68, 0.2);
		color: #dc2626;
	}

	.status-stopped {
		background: rgba(156, 163, 175, 0.2);
		color: #6b7280;
	}

	.timer {
		font-size: 0.75rem;
		color: #6b7280;
		font-mono: true;
	}

	.main-content {
		background: rgba(255, 255, 255, 0.4);
		padding: 2rem;
		overflow-y: auto;
		overflow-x: hidden;
		display: flex;
		flex-direction: column;
		height: 100%;
		max-height: 100%;
		min-height: 0;
	}

	.content-header {
		margin-bottom: 2rem;
	}

	.intent-name {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 700;
		color: #1e3a5f;
	}

	.content-body {
		flex: 1;
		background: rgba(255, 255, 255, 0.8);
		backdrop-filter: blur(20px);
		border-radius: 24px;
		padding: 2rem;
		box-shadow: 0 20px 40px rgba(30, 58, 95, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.5);
	}

	.result-section {
		max-width: none;
	}

	.result-title {
		color: #1e3a5f;
		font-size: 1.5rem;
		font-weight: 600;
		margin-bottom: 1.5rem;
	}

	.result-content {
		color: #1e3a5f;
		line-height: 1.6;
	}

	.result-content :global(h1),
	.result-content :global(h2),
	.result-content :global(h3) {
		color: #1e3a5f;
		margin-top: 1.5rem;
		margin-bottom: 0.75rem;
	}

	.result-content :global(p) {
		margin-bottom: 1rem;
	}

	.error-section {
		background: rgba(239, 68, 68, 0.1);
		border: 2px solid rgba(239, 68, 68, 0.2);
		border-radius: 16px;
		padding: 1.5rem;
	}

	.error-section h4 {
		color: #dc2626;
		margin-bottom: 1rem;
	}

	.error-content {
		color: #7f1d1d;
		line-height: 1.5;
	}

	.task-board {
		height: 100%;
	}

	.board-title {
		color: #1e3a5f;
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 1.5rem;
	}

	.board-columns {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1.5rem;
		height: calc(100% - 4rem);
	}

	.board-column {
		background: rgba(255, 255, 255, 0.6);
		border-radius: 16px;
		padding: 1rem;
		display: flex;
		flex-direction: column;
	}

	.column-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 1rem;
		padding-bottom: 0.75rem;
		border-bottom: 2px solid rgba(30, 58, 95, 0.1);
	}

	.column-icon {
		font-size: 1.2rem;
	}

	.column-header h4 {
		margin: 0;
		font-size: 0.9rem;
		font-weight: 600;
		color: #1e3a5f;
	}

	.tasks-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		overflow-y: auto;
	}

	.task-card {
		background: rgba(255, 255, 255, 0.9);
		border-radius: 12px;
		padding: 1rem;
		border-left: 4px solid;
		box-shadow: 0 4px 8px rgba(30, 58, 95, 0.1);
	}

	.todo-task {
		border-left-color: #f59e0b;
	}

	.doing-task {
		border-left-color: #3b82f6;
	}

	.done-task {
		border-left-color: #10b981;
	}

	.blocked-task {
		border-left-color: #ef4444;
	}

	.task-name {
		margin: 0 0 0.75rem 0;
		font-size: 0.85rem;
		font-weight: 500;
		color: #1e3a5f;
		line-height: 1.3;
	}

	.task-status {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.75rem;
		font-weight: 600;
		color: #6b7280;
	}

	.loading-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: #6b7280;
	}

	.loading-animation {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}

	.loading-dot {
		width: 8px;
		height: 8px;
		background: #7ed4ad;
		border-radius: 50%;
		animation: loading-pulse 1.5s ease-in-out infinite;
	}

	.loading-dot:nth-child(2) {
		animation-delay: 0.2s;
	}

	.loading-dot:nth-child(3) {
		animation-delay: 0.4s;
	}

	@keyframes loading-pulse {
		0%,
		80%,
		100% {
			transform: scale(0.8);
			opacity: 0.5;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}

	.welcome-section {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
	}

	.welcome-content h2 {
		margin: 0 0 0.5rem 0;
		font-size: 2rem;
		font-weight: 700;
		color: #1e3a5f;
	}

	.welcome-content p {
		margin: 0;
		color: #6b7280;
		font-size: 1.1rem;
	}

	.welcome-icon {
		font-size: 4rem;
		margin: 2rem 0;
	}

	.welcome-subtitle {
		font-size: 0.9rem !important;
		color: #9ca3af !important;
	}

	.log-title,
	.debug-title {
		color: #1e3a5f;
		font-size: 0.9rem;
		font-weight: 600;
		margin-bottom: 1rem;
	}

	.debug-title {
		color: #f59e0b;
	}

	.log-content,
	.debug-content {
		font-family:
			'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
		font-size: 0.75rem;
		line-height: 1.4;
		color: #1e3a5f;
		white-space: pre-wrap;
		word-wrap: break-word;
		word-break: break-all;
		background: rgba(30, 58, 95, 0.02);
		padding: 0.5rem;
		border-radius: 6px;
		margin: 0;
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		max-height: 100%;
		min-height: 0;
	}

	.debug-content {
		background: rgba(245, 158, 11, 0.02);
		color: #92400e;
	}

	.empty-log {
		display: flex;
		align-items: center;
		justify-content: center;
		flex: 1;
		color: #9ca3af;
		font-size: 0.9rem;
		text-align: center;
		padding: 2rem 0;
	}

	@media (max-width: 1200px) {
		.main-layout {
			grid-template-columns: 280px 1fr 280px;
		}

		.control-panel,
		.activity-panel {
			padding: 1.5rem;
		}
	}

	@media (max-width: 768px) {
		.main-layout {
			grid-template-columns: 1fr;
			grid-template-rows: auto 1fr auto;
		}

		.control-panel,
		.activity-panel {
			height: auto;
			max-height: 300px;
		}

		.board-columns {
			grid-template-columns: 1fr 1fr;
			gap: 1rem;
		}
	}
</style>
