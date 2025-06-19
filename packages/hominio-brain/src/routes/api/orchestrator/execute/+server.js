// In-memory store for task states. In a real app, this would be a database.
const taskStates = new Map();

// The URL for the vibe service we want to call.
// In a real app, this would be discovered from a service registry.
const VIBE_WRITING_URL = 'http://localhost:3001';

export async function POST({ request }) {
	const incomingRequest = await request.json();
	const { vibe, task } = incomingRequest; // e.g., vibe: 'writing', task: { ... }

	const taskId = `task_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

	// The initial state we'll store for our task
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

	const vibeRequestParams = {
		id: taskId, // We use our orchestrator's task ID
		jsonrpc: '2.0',
		method: 'executeVibe',
		params: { task: task.details, inputs: task.inputs }
	};

	const encodedParams = encodeURIComponent(JSON.stringify(vibeRequestParams));
	const vibeExecuteUrl = `${VIBE_WRITING_URL}/api/execute?params=${encodedParams}`;

	// Here is the core of the proxy logic.
	// We make a request to the Vibe and get its stream.
	const vibeResponse = await fetch(vibeExecuteUrl);

	// We create a NEW stream that our UI will listen to.
	const stream = new ReadableStream({
		async start(controller) {
			const decoder = new TextDecoder();
			const reader = vibeResponse.body.getReader();

			const processEvent = (eventString) => {
				if (!eventString) return;

				const lines = eventString.split('\\n');
				let eventName = 'message';
				let dataContent = '';

				for (const line of lines) {
					if (line.startsWith('event:')) {
						eventName = line.substring('event:'.length).trim();
					} else if (line.startsWith('data:')) {
						// Concatenate multi-line data.
						dataContent += line.substring('data:'.length).trim();
					}
				}

				if (!dataContent) return;

				try {
					const data = JSON.parse(dataContent);

					// 1. Persist State
					const currentState = taskStates.get(taskId);
					if (currentState) {
						currentState.updates.push({ eventName, data, timestamp: new Date().toISOString() });
						if (eventName === 'task_completed') {
							currentState.status = data.result?.status || 'COMPLETED';

							// PARSE THE RESULT OBJECT HERE
							const teamResult = data.result?.result;
							let finalResultString;
							if (typeof teamResult === 'string') {
								finalResultString = teamResult;
							} else if (teamResult && typeof teamResult === 'object') {
								finalResultString =
									teamResult.output ||
									teamResult.result ||
									teamResult.content ||
									teamResult.finalResult ||
									(teamResult.tasks && teamResult.tasks[teamResult.tasks.length - 1]?.output) ||
									JSON.stringify(teamResult, null, 2);
							} else {
								finalResultString = String(teamResult || 'No result generated');
							}
							// Store the raw result but prepare to send the parsed string
							currentState.result = teamResult;
							data.result.result = finalResultString;
						} else if (eventName === 'task_error') {
							currentState.status = 'FAILED';
							currentState.error = data.error;
						} else if (data.params?.status?.state) {
							currentState.status = data.params.status.state;
						}
						taskStates.set(taskId, currentState);
					}

					// 2. Forward the (now modified) event string to our client
					const outgoingEvent = `event: ${eventName}\\ndata: ${JSON.stringify(data)}\\n\\n`;
					controller.enqueue(new TextEncoder().encode(outgoingEvent));
				} catch (e) {
					console.error(
						'Orchestrator: Error processing event JSON:',
						e,
						'Data String:',
						dataContent
					);
				}
			};

			try {
				let buffer = '';
				while (true) {
					const { done, value } = await reader.read();
					if (done) {
						if (buffer.trim()) processEvent(buffer);
						break;
					}

					buffer += decoder.decode(value, { stream: true });
					const parts = buffer.split('\\n\\n');
					buffer = parts.pop() || ''; // Keep the incomplete part

					for (const part of parts) {
						if (part.trim()) {
							processEvent(part);
						}
					}
				}
			} catch (error) {
				console.error('Error reading from vibe stream:', error);
				controller.error(error);
			} finally {
				console.log(`Stream closed for ${taskId}. Final state:`, taskStates.get(taskId));
				if (controller.desiredSize !== null) {
					controller.close();
				}
			}
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
