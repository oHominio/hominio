<script>
	import { onMount } from 'svelte';
	import { marked } from 'marked';

	let isRunning = false;
	let activityLogsContainer;

	let taskDescription = 'The future of AI agents in software development';
	let taskExpectedOutput = 'A 3-paragraph blog post about the topic.';

	let activityLog = [];
	let finalResult = null;
	let error = null;

	let tasks = [];

	async function startTask() {
		if (isRunning) return;

		isRunning = true;
		activityLog = [];
		finalResult = null;
		error = null;
		tasks = [
			{ title: 'Research Analysis', status: 'PENDING' },
			{ title: 'Storytelling & Content Creation', status: 'PENDING' }
		];

		try {
			const response = await fetch('/api/orchestrator/execute', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					vibe: 'writing',
					task: {
						details: { description: taskDescription, expectedOutput: taskExpectedOutput },
						inputs: {}
					}
				})
			});

			if (!response.ok) {
				const errorText = await response.text();
				throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();

			const processStream = async () => {
				let buffer = '';
				while (true) {
					const { done, value } = await reader.read();
					if (done) {
						if (!error) isRunning = false;
						break;
					}

					buffer += decoder.decode(value, { stream: true });
					const eventStrings = buffer.split('\\n\\n');
					buffer = eventStrings.pop() || ''; // Keep the incomplete part

					for (const eventString of eventStrings) {
						if (!eventString.trim()) continue;

						const lines = eventString.split('\\n');
						let eventName = 'message';
						let dataContent = '';

						for (const line of lines) {
							if (line.startsWith('event:')) {
								eventName = line.substring('event:'.length).trim();
							} else if (line.startsWith('data:')) {
								dataContent += line.substring('data:'.length).trim();
							}
						}

						if (!dataContent) continue;

						try {
							const data = JSON.parse(dataContent);
							if (eventName === 'task_status_update' && data.params?.status) {
								const logEntry = data.params.status;
								const logText = `[${new Date(
									logEntry.timestamp
								).toLocaleTimeString()}] ${logEntry.description}`;
								activityLog = [...activityLog, logText];

								if (logEntry.tasks) {
									tasks = logEntry.tasks;
								}
							} else if (eventName === 'task_completed' && data.result) {
								const finalOutput = data.result?.result;
								if (finalOutput && typeof finalOutput === 'object' && finalOutput.body) {
									finalResult = finalOutput;
								} else {
									error = `Task completed but the result format was unexpected.`;
									console.log('Unexpected result format:', finalOutput);
								}
								tasks = tasks.map((t) => ({ ...t, status: 'DONE' }));
								isRunning = false;
							} else if (eventName === 'task_error' && data.error) {
								error = data.error.message;
								tasks = tasks.map((t) => ({ ...t, status: 'BLOCKED' }));
								isRunning = false;
							}
						} catch (e) {
							console.error('Failed to parse event data:', e, 'Data string:', dataContent);
							error = `Failed to process an event from the server: ${e.message}`;
							isRunning = false;
						}
					}
				}
			};
			await processStream();
		} catch (e) {
			error = e.message;
			isRunning = false;
		}
	}

	onMount(() => {
		// Auto-scroll logic
		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				if (mutation.type === 'childList') {
					activityLogsContainer.scrollTop = activityLogsContainer.scrollHeight;
				}
			}
		});

		if (activityLogsContainer) {
			observer.observe(activityLogsContainer, { childList: true });
		}

		return () => {
			observer.disconnect();
		};
	});

	function getStatusColor(status) {
		switch (status) {
			case 'PENDING':
				return 'border-l-gray-500 bg-gray-800';
			case 'DOING':
				return 'border-l-blue-500 bg-blue-900/50 animate-pulse';
			case 'DONE':
				return 'border-l-green-500 bg-green-900/50';
			case 'BLOCKED':
				return 'border-l-red-500 bg-red-900/50';
			default:
				return 'border-l-gray-700 bg-gray-800';
		}
	}
</script>

<svelte:head>
	<title>Hominio Brain</title>
</svelte:head>

<div class="flex h-screen bg-gray-900 font-sans text-gray-100">
	<!-- Main Content Area -->
	<div class="flex w-3/4 flex-col overflow-y-auto p-4 sm:p-6 md:p-8">
		<header class="mb-4 flex-shrink-0">
			<h1 class="text-4xl font-bold text-cyan-400">Hominio Brain</h1>
			<p class="mt-2 text-gray-400">The orchestrator for your AI agent teams.</p>
		</header>

		<main class="grid flex-grow grid-cols-1 gap-8 lg:grid-cols-2">
			<!-- Left side of main -->
			<div class="flex-shrink-0 rounded-lg bg-gray-800 p-6 shadow-lg">
				<h2 class="mb-4 text-2xl font-semibold text-cyan-300">Start New Task</h2>
				<form on:submit|preventDefault={startTask}>
					<div class="mb-4">
						<label for="description" class="mb-2 block text-gray-400">Task Description</label>
						<textarea
							id="description"
							bind:value={taskDescription}
							rows="4"
							class="w-full rounded-md border border-gray-600 bg-gray-700 p-2 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
						></textarea>
					</div>
					<div class="mb-6">
						<label for="expectedOutput" class="mb-2 block text-gray-400">Expected Output</label>
						<textarea
							id="expectedOutput"
							bind:value={taskExpectedOutput}
							rows="3"
							class="w-full rounded-md border border-gray-600 bg-gray-700 p-2 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
						></textarea>
					</div>
					<button
						type="submit"
						disabled={isRunning}
						class="w-full rounded-md bg-cyan-600 px-4 py-2 font-bold text-white transition-colors hover:bg-cyan-700 disabled:bg-gray-600"
					>
						{#if isRunning}Running...{:else}Execute Writing Vibe{/if}
					</button>
				</form>
			</div>

			<!-- Right side of main: Task Board & Results -->
			<div class="flex flex-col space-y-4">
				<div>
					<h2 class="mb-4 text-2xl font-semibold text-cyan-300">Task Board</h2>
					{#if tasks.length > 0}
						<div class="space-y-4">
							{#each tasks as task (task.title)}
								<div class="rounded-lg border-l-4 p-4 transition-all {getStatusColor(task.status)}">
									<h3 class="text-lg font-bold">{task.title}</h3>
									<span
										class="font-mono text-sm uppercase {task.status === 'DONE'
											? 'text-green-400'
											: task.status === 'DOING'
												? 'text-blue-400'
												: 'text-gray-500'}"
									>
										{task.status}
									</span>
								</div>
							{/each}
						</div>
					{:else}
						<div class="rounded-lg bg-gray-800 p-4 text-gray-500">
							<p>Start a workflow to see tasks.</p>
						</div>
					{/if}
				</div>

				{#if finalResult}
					<div class="animate-fade-in flex-grow rounded-lg bg-gray-800 p-6 shadow-lg">
						<h2 class="mb-4 text-2xl font-semibold text-cyan-300">{finalResult.title}</h2>
						<div class="prose prose-invert max-h-[60vh] max-w-none overflow-y-auto">
							{@html marked(finalResult.body)}
						</div>
					</div>
				{/if}
			</div>
		</main>

		<!-- Errors below the main grid -->
		{#if error}
			<div
				class="bg-opacity-50 animate-fade-in mt-8 rounded-lg border border-red-700 bg-red-900 p-4 text-red-200 shadow-lg"
			>
				<h2 class="mb-2 text-xl font-semibold text-white">Error</h2>
				<p>{error}</p>
			</div>
		{/if}
	</div>

	<!-- Activity Log Aside -->
	<aside class="flex h-screen w-1/4 flex-col bg-black p-4">
		<h2 class="mb-4 flex-shrink-0 text-2xl font-semibold text-cyan-300">Activity Log</h2>
		<div class="flex-grow overflow-y-auto font-mono text-sm" bind:this={activityLogsContainer}>
			{#each activityLog as log, i (i)}
				<p class="animate-fade-in whitespace-pre-wrap">{log}</p>
			{/each}
		</div>
	</aside>
</div>

<style>
	@keyframes fade-in {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	.animate-fade-in {
		animation: fade-in 0.5s ease-out forwards;
	}
</style>
