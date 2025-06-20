<script>
	import { onMount } from 'svelte';
	import { marked } from 'marked';
	import { v4 as uuidv4 } from 'uuid';

	let taskDescription = 'The future of AI agents in software development';
	let expectedOutput = 'A 3-paragraph blog post about the topic.';
	let intents = [];
	let selectedIntentId = null;

	marked.setOptions({
		gfm: true,
		breaks: true
	});

	function selectIntent(intentId) {
		selectedIntentId = intentId;
	}

	$: selectedIntent = intents.find((i) => i.id === selectedIntentId);

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

<div class="flex h-screen bg-gray-900 font-sans text-gray-100">
	<!-- Left Sidebar for Controls & Intent List -->
	<div class="w-1/4 flex-shrink-0 space-y-6 overflow-y-auto bg-gray-800 p-6">
		<header>
			<h1 class="text-3xl font-bold text-cyan-400">Hominio OS</h1>
			<p class="mt-1 text-gray-400">The orchestrator for your AI agent teams.</p>
		</header>

		<div>
			<h2 class="mb-4 text-xl font-semibold text-cyan-300">Start New Intent</h2>
			<div class="space-y-4">
				<div>
					<label for="description" class="mb-1 block text-sm text-gray-400">Task Description</label>
					<textarea
						id="description"
						bind:value={taskDescription}
						rows="4"
						class="w-full rounded-md border border-gray-600 bg-gray-700 p-2 text-sm focus:ring-2 focus:ring-cyan-500 focus:outline-none"
					></textarea>
				</div>
				<div>
					<label for="expectedOutput" class="mb-1 block text-sm text-gray-400"
						>Expected Output</label
					>
					<textarea
						id="expectedOutput"
						bind:value={expectedOutput}
						rows="3"
						class="w-full rounded-md border border-gray-600 bg-gray-700 p-2 text-sm focus:ring-2 focus:ring-cyan-500 focus:outline-none"
					></textarea>
				</div>
				<button
					on:click={startVibe}
					class="w-full rounded-md bg-cyan-600 px-4 py-2 font-bold text-white transition-colors hover:bg-cyan-700 disabled:bg-gray-600"
				>
					Execute Writing Vibe
				</button>
			</div>
		</div>

		<div class="border-t border-gray-700 pt-4">
			<h3 class="mb-2 font-semibold text-cyan-300">Intents</h3>
			<div class="flex-grow space-y-2 overflow-y-auto">
				{#if intents.length === 0}
					<div class="pt-4 text-center text-sm text-gray-500">No intents yet.</div>
				{/if}
				{#each intents as intent (intent.id)}
					<div
						role="button"
						tabindex="0"
						class="cursor-pointer rounded-md border-l-4 p-3 {selectedIntentId === intent.id
							? 'border-cyan-500 bg-cyan-900/50'
							: 'border-gray-600 bg-gray-700/50 hover:bg-gray-700'}"
						on:click={() => selectIntent(intent.id)}
						on:keypress={() => selectIntent(intent.id)}
					>
						<div class="flex items-center justify-between">
							<p class="flex-1 truncate text-sm font-semibold">{intent.taskDescription}</p>

							{#if intent.status === 'RUNNING'}
								<button
									on:click|stopPropagation={() => stopVibe(intent.id)}
									class="btn btn-xs btn-ghost btn-circle"
									title="Stop Intent"
									aria-label="Stop Intent"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 20 20"
										fill="currentColor"
									>
										<path
											fill-rule="evenodd"
											d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"
											clip-rule="evenodd"
										/>
									</svg>
								</button>
							{/if}
						</div>
						<div class="mt-1 flex items-center justify-between">
							{#if intent.status === 'RUNNING'}
								<div class="badge badge-info badge-outline badge-xs">Running</div>
							{:else if intent.status === 'DONE'}
								<div class="badge badge-success badge-outline badge-xs">Done</div>
							{:else if intent.status === 'ERROR'}
								<div class="badge badge-error badge-outline badge-xs">Error</div>
							{:else if intent.status === 'STOPPED'}
								<div class="badge badge-warning badge-outline badge-xs">Stopped</div>
							{/if}
							<div class="text-right text-xs text-gray-400">
								{Math.floor(intent.timer / 60)}m {intent.timer % 60}s
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>

	<!-- Main Content: Task Board & Results -->
	<main class="w-1/2 flex-grow space-y-4 overflow-y-auto p-6">
		{#if selectedIntent}
			<div class="flex items-center justify-between">
				<h2 class="truncate text-2xl font-bold text-cyan-400">
					Intent: {selectedIntent.taskDescription}
				</h2>
			</div>

			<div class="h-full rounded-lg bg-gray-800 p-6 shadow-lg">
				{#if selectedIntent.finalResult}
					<div>
						<h3 class="text-xl font-bold text-cyan-300">{selectedIntent.finalResult.title}</h3>
						<div class="prose prose-invert mt-4 max-w-none">
							{@html marked(selectedIntent.finalResult.body || '')}
						</div>
					</div>
				{:else if selectedIntent.error}
					<div class="rounded-lg border border-red-700 bg-red-900/50 p-4">
						<h4 class="mb-1 font-semibold text-red-300">Error</h4>
						<p class="text-sm text-red-200">{@html marked(selectedIntent.error || '')}</p>
					</div>
				{:else if selectedIntent.tasks.length > 0}
					<div>
						<h3 class="mb-4 text-lg font-semibold text-cyan-300">Task Board</h3>
						<div class="grid h-96 grid-cols-4 gap-4">
							<!-- TODO Column -->
							<div class="rounded-lg border-t-4 border-yellow-500 bg-gray-700/50 p-4">
								<h4 class="mb-3 text-center font-semibold text-yellow-400">📋 To Do</h4>
								<div class="space-y-2">
									{#each selectedIntent.tasks.filter((t) => t.status === 'TODO') as task}
										<div class="rounded-md border-l-2 border-yellow-500 bg-gray-800 p-3 shadow-sm">
											<p class="text-sm font-medium text-gray-200">{task.name}</p>
											<div class="mt-1 flex items-center justify-between">
												<span
													class="inline-block rounded bg-yellow-500/20 px-2 py-1 text-xs text-yellow-400"
												>
													TODO
												</span>
											</div>
										</div>
									{/each}
								</div>
							</div>

							<!-- DOING Column -->
							<div class="rounded-lg border-t-4 border-blue-500 bg-gray-700/50 p-4">
								<h4 class="mb-3 text-center font-semibold text-blue-400">⚡ In Progress</h4>
								<div class="space-y-2">
									{#each selectedIntent.tasks.filter((t) => t.status === 'DOING') as task}
										<div class="rounded-md border-l-2 border-blue-500 bg-gray-800 p-3 shadow-sm">
											<p class="text-sm font-medium text-gray-200">{task.name}</p>
											<div class="mt-1 flex items-center justify-between">
												<span
													class="inline-block rounded bg-blue-500/20 px-2 py-1 text-xs text-blue-400"
												>
													DOING
												</span>
												<div class="loading loading-dots loading-xs text-blue-400"></div>
											</div>
										</div>
									{/each}
								</div>
							</div>

							<!-- DONE Column -->
							<div class="rounded-lg border-t-4 border-green-500 bg-gray-700/50 p-4">
								<h4 class="mb-3 text-center font-semibold text-green-400">✅ Done</h4>
								<div class="space-y-2">
									{#each selectedIntent.tasks.filter((t) => t.status === 'DONE') as task}
										<div class="rounded-md border-l-2 border-green-500 bg-gray-800 p-3 shadow-sm">
											<p class="text-sm font-medium text-gray-200">{task.name}</p>
											<div class="mt-1">
												<span
													class="inline-block rounded bg-green-500/20 px-2 py-1 text-xs text-green-400"
												>
													DONE
												</span>
											</div>
										</div>
									{/each}
								</div>
							</div>

							<!-- BLOCKED Column -->
							<div class="rounded-lg border-t-4 border-red-500 bg-gray-700/50 p-4">
								<h4 class="mb-3 text-center font-semibold text-red-400">🚫 Blocked</h4>
								<div class="space-y-2">
									{#each selectedIntent.tasks.filter((t) => t.status === 'BLOCKED' || t.status === 'ERROR') as task}
										<div class="rounded-md border-l-2 border-red-500 bg-gray-800 p-3 shadow-sm">
											<p class="text-sm font-medium text-gray-200">{task.name}</p>
											<div class="mt-1">
												<span
													class="inline-block rounded bg-red-500/20 px-2 py-1 text-xs text-red-400"
												>
													{task.status}
												</span>
											</div>
										</div>
									{/each}
								</div>
							</div>
						</div>
					</div>
				{:else}
					<div class="flex h-full flex-col items-center justify-center p-8 text-center">
						<span class="loading loading-dots loading-lg text-cyan-500"></span>
						<p class="mt-4 text-gray-400">Awaiting first update from agent...</p>
					</div>
				{/if}
			</div>
		{:else}
			<div class="flex h-full items-center justify-center rounded-lg bg-gray-800/50">
				<div class="text-center">
					<h2 class="text-2xl font-bold text-cyan-400">Welcome to Hominio OS</h2>
					<p class="mt-2 text-gray-400">
						Start a new intent from the control panel on the left to begin.
					</p>
				</div>
			</div>
		{/if}
	</main>

	<!-- Right Sidebar for Activity Log -->
	<aside class="flex h-screen w-1/3 flex-col bg-gray-800/50 p-6">
		<h2 class="mb-4 flex-shrink-0 text-xl font-bold text-cyan-300">Activity Log</h2>
		<div class="flex-grow overflow-y-auto rounded-lg bg-gray-900 p-4">
			{#if selectedIntent}
				{#if selectedIntent.activityLog.trim()}
					<div class="space-y-2">
						<h4 class="text-sm font-semibold text-cyan-400">Activity Log:</h4>
						<pre
							class="font-mono text-xs whitespace-pre-wrap text-gray-300">{selectedIntent.activityLog}</pre>
					</div>
				{:else if selectedIntent.rawData}
					<div class="space-y-2">
						<h4 class="text-sm font-semibold text-yellow-400">Raw SSE Data (Debug Mode):</h4>
						<pre
							class="rounded bg-gray-800 p-2 font-mono text-xs whitespace-pre-wrap text-gray-300">{selectedIntent.rawData}</pre>
					</div>
				{:else}
					<div class="flex h-full items-center justify-center">
						<p class="text-sm text-gray-500">No activity log yet. Waiting for updates...</p>
					</div>
				{/if}
			{:else}
				<div class="flex h-full items-center justify-center">
					<p class="text-sm text-gray-500">Select an intent to view its log.</p>
				</div>
			{/if}
		</div>
	</aside>
</div>
