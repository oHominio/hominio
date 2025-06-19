import { researchAgent, writerAgent } from '$lib/team';
import { Team, Task } from 'kaibanjs';
import { SECRET_RED_PILL_API_KEY } from '$env/static/private';

export async function GET({ url }) {
	// 1. Decode the initial task from the URL query parameters
	const encodedParams = url.searchParams.get('params');
	if (!encodedParams) {
		return new Response('Missing params', { status: 400 });
	}
	const params = JSON.parse(decodeURIComponent(encodedParams));
	const { id, params: taskDetails } = params;

	// 2. Create a ReadableStream to send events
	const stream = new ReadableStream({
		async start(controller) {
			const sendEvent = (eventName, data) => {
				const jsonData = JSON.stringify(data);
				// SSE spec requires newlines to be sent as separate `data:` lines.
				const dataString = jsonData
					.split('\\n')
					.map((line) => `data: ${line}`)
					.join('\\n');
				const message = `event: ${eventName}\\n${dataString}\\n\\n`;
				controller.enqueue(new TextEncoder().encode(message));
			};

			try {
				// 3. Create a NEW, stateless team for this specific request.
				const researchTask = new Task({
					title: 'Research Analysis',
					description: `Conduct comprehensive research on the topic: "${taskDetails.task.description}"`,
					agent: researchAgent,
					expectedOutput: 'Detailed research findings with key insights and trends'
				});

				const writeTask = new Task({
					title: 'Storytelling & Content Creation',
					description: `Transform the research findings into an engaging story. The final output should be: ${taskDetails.task.expectedOutput}`,
					agent: writerAgent,
					expectedOutput: taskDetails.task.expectedOutput
				});

				const requestTeam = new Team({
					name: 'RequestWritingVibeTeam',
					agents: [researchAgent, writerAgent],
					tasks: [researchTask, writeTask],
					env: {
						OPENAI_API_KEY: SECRET_RED_PILL_API_KEY
					}
				});

				// 4. Subscribe to the team's internal status updates
				const unsubscribe = requestTeam.store.subscribe((state) => {
					const lastLog = state.workflowLogs[state.workflowLogs.length - 1];
					if (lastLog) {
						sendEvent('task_status_update', {
							jsonrpc: '2.0',
							method: 'taskStatusUpdate',
							params: {
								id: id,
								status: {
									state: state.workflowStatus,
									description: lastLog.logDescription,
									timestamp: new Date().toISOString(),
									tasks: state.tasks.map((task) => ({
										title: task.title,
										status: task.status
									}))
								}
							}
						});
					}
				});

				// 5. Start the workflow and handle the final result
				const finalResult = await requestTeam.start(taskDetails.inputs);

				sendEvent('task_completed', {
					jsonrpc: '2.0',
					id: id,
					result: { status: 'FINISHED', result: finalResult }
				});

				unsubscribe();
				controller.close();
			} catch (e) {
				console.error('Error during Vibe execution:', e);
				sendEvent('task_error', {
					jsonrpc: '2.0',
					id: id,
					error: { code: -32000, message: e.message }
				});
				controller.close();
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
