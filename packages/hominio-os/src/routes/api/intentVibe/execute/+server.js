// In-memory store for task states. In a real app, this would be a database.
const taskStates = new Map();

// The URL for the vibe service we want to call.
// In a real app, this would be discovered from a service registry.
const VIBE_WRITING_URL = 'http://localhost:3001';

export async function POST({ request }) {
	// Abort controller to cancel the downstream request if the client disconnects.
	const vibeAbortController = new AbortController();
	request.signal.addEventListener('abort', () => {
		console.log('[OS IntentVibe] Client disconnected, aborting vibe request.');
		vibeAbortController.abort();
	});

	const incomingRequest = await request.json();
	const { vibe, task } = incomingRequest;

	const taskId = `task_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
	console.log(`[OS IntentVibe] Starting task ${taskId} for vibe: ${vibe}`);

	// Initialize task state
	const initialState = {
		id: taskId,
		vibe: vibe,
		status: 'PENDING',
		updates: [],
		result: null,
		error: null,
		createdAt: new Date().toISOString()
	};
	taskStates.set(taskId, initialState);

	// Prepare request to vibe service
	const vibeRequestParams = {
		id: taskId,
		jsonrpc: '2.0',
		method: 'executeVibe',
		params: { task: task.details, inputs: task.inputs }
	};

	const encodedParams = encodeURIComponent(JSON.stringify(vibeRequestParams));
	const vibeExecuteUrl = `${VIBE_WRITING_URL}/api/execute?params=${encodedParams}`;

	// Get stream from vibe service
	const vibeResponse = await fetch(vibeExecuteUrl, { signal: vibeAbortController.signal });

	// Create our response stream
	const stream = new ReadableStream({
		start(controller) {
			const decoder = new TextDecoder();
			const reader = vibeResponse.body.getReader();

			const processJSONEvent = (jsonString) => {
				if (!jsonString.trim()) return;

				try {
					const eventData = JSON.parse(jsonString);
					console.log(`[OS IntentVibe] Received event: ${eventData.type}`);

					// Store the raw event
					const currentState = taskStates.get(taskId);
					if (currentState) {
						currentState.updates.push({ ...eventData, processedAt: new Date().toISOString() });
					}

					// Create clean client update
					let clientUpdate = {
						type: 'update',
						timestamp: new Date().toISOString(),
						log: null,
						tasks: null,
						result: null,
						error: null,
						status: 'running'
					};

					if (eventData.type === 'task_status_update' && eventData.params?.status) {
						const status = eventData.params.status;
						clientUpdate.log = `[${new Date(status.timestamp).toLocaleTimeString()}] ${status.description}`;
						if (status.tasks) {
							clientUpdate.tasks = status.tasks.map((t) => ({ name: t.title, status: t.status }));
						}
						if (currentState) currentState.status = 'RUNNING';
					} else if (eventData.type === 'task_completed' && eventData.result) {
						clientUpdate.type = 'completed';
						clientUpdate.status = 'completed';
						clientUpdate.result = eventData.result.result;
						clientUpdate.log = `[${new Date().toLocaleTimeString()}] Task completed successfully`;
						if (currentState) {
							currentState.status = 'COMPLETED';
							currentState.result = eventData.result;
						}
					} else if (eventData.type === 'task_error' && eventData.error) {
						clientUpdate.type = 'error';
						clientUpdate.status = 'error';
						clientUpdate.error = eventData.error.message || JSON.stringify(eventData.error);
						clientUpdate.log = `[${new Date().toLocaleTimeString()}] Error: ${clientUpdate.error}`;
						if (currentState) {
							currentState.status = 'FAILED';
							currentState.error = eventData.error;
						}
					} else {
						console.log(`[OS IntentVibe] Unhandled event type: ${eventData.type}`);
						return; // Don't forward unhandled events
					}

					if (currentState) {
						taskStates.set(taskId, currentState);
					}

					// Forward clean JSON to client
					const outgoingEvent = `data: ${JSON.stringify(clientUpdate)}\n\n`;
					console.log(
						`[OS IntentVibe] Forwarding to client: ${clientUpdate.type} - ${clientUpdate.log || 'no log'}`
					);
					controller.enqueue(new TextEncoder().encode(outgoingEvent));
				} catch (e) {
					console.error(`[OS IntentVibe] JSON parse error:`, e.message);
					console.error(`[OS IntentVibe] Failed JSON:`, jsonString.substring(0, 200));
				}
			};

			const pump = async () => {
				try {
					let buffer = '';
					while (true) {
						const { done, value } = await reader.read();
						if (done) {
							if (buffer.trim()) {
								// Process any remaining data
								const lines = buffer.split('\n');
								for (const line of lines) {
									if (line.startsWith('data: ')) {
										const jsonData = line.substring('data: '.length);
										processJSONEvent(jsonData);
									}
								}
							}
							break;
						}

						buffer += decoder.decode(value, { stream: true });
						const parts = buffer.split('\n\n');
						buffer = parts.pop() || ''; // Keep incomplete part

						for (const part of parts) {
							if (part.trim()) {
								// Extract JSON from SSE format
								const lines = part.split('\n');
								for (const line of lines) {
									if (line.startsWith('data: ')) {
										const jsonData = line.substring('data: '.length);
										processJSONEvent(jsonData);
									}
								}
							}
						}
					}
				} catch (error) {
					if (error.name === 'AbortError') {
						console.log(`[OS IntentVibe] Request aborted for ${taskId}`);
					} else {
						console.error('[OS IntentVibe] Stream error:', error);
						controller.error(error);
					}
				} finally {
					console.log(
						`[OS IntentVibe] Stream finished for ${taskId}. Final state:`,
						taskStates.get(taskId)
					);
					if (controller.desiredSize !== null) {
						controller.close();
					}
				}
			};

			pump();
		}
	});

	return new Response(stream, {
		headers: {
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache',
			Connection: 'keep-alive'
		}
	});
}
