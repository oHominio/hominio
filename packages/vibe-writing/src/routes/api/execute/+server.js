import { createResearchAgent, createWriterAgent } from '$lib/team';
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
				// Send clean JSON object with event type included
				const eventData = {
					type: eventName,
					timestamp: new Date().toISOString(),
					...data
				};
				const message = `data: ${JSON.stringify(eventData)}\n\n`;
				console.log(`[WRITING] Sending JSON event: ${eventName}`);
				controller.enqueue(new TextEncoder().encode(message));
			};

			try {
				// 3. Create FRESH agent instances for this specific request
				const researchAgent = createResearchAgent();
				const writerAgent = createWriterAgent();

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

				// Create team with unique name to avoid conflicts
				const requestTeam = new Team({
					name: `RequestWritingVibeTeam_${id}`,
					agents: [researchAgent, writerAgent],
					tasks: [researchTask, writeTask],
					env: {
						OPENAI_API_KEY: SECRET_RED_PILL_API_KEY
					}
				});

				console.log(`[WRITING] Created isolated team ${requestTeam.name} for request ${id}`);

				// 4. Subscribe to the team's internal status updates
				const unsubscribe = requestTeam.store.subscribe((state) => {
					const lastLog = state.workflowLogs[state.workflowLogs.length - 1];
					if (lastLog) {
						console.log(`[WRITING] Team ${requestTeam.name} - ${lastLog.logDescription}`);
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
				console.log(`[WRITING] Starting workflow for team ${requestTeam.name}`);
				const teamResult = await requestTeam.start(taskDetails.inputs);

				// Fulfill the public contract for this Vibe.
				const structuredResult = {
					title: `Result for: ${taskDetails.task.description}`,
					body: ''
				};

				// Handle both successful and blocked/failed outcomes.
				if (teamResult && teamResult.status === 'FINISHED') {
					// Extract the final string from the potentially complex result object.
					let finalResultString;
					if (typeof teamResult.result === 'string') {
						finalResultString = teamResult.result;
					} else if (teamResult.result && typeof teamResult.result === 'object') {
						finalResultString =
							teamResult.result.output ||
							teamResult.result.result ||
							teamResult.result.content ||
							teamResult.result.finalResult ||
							(teamResult.result.tasks &&
								teamResult.result.tasks[teamResult.result.tasks.length - 1]?.output) ||
							JSON.stringify(teamResult.result, null, 2);
					} else {
						finalResultString = String(teamResult.result || 'No result generated');
					}
					structuredResult.body = finalResultString;
				} else {
					// The workflow was blocked or failed.
					structuredResult.body = `**Workflow Failed**

The agent team encountered an error and could not complete the task.

**Status:** ${teamResult.status}
**Details:** ${teamResult.result || 'No further details available.'}

This often happens if an agent gets stuck in a loop or cannot find a final answer within its iteration limit.`;
				}

				sendEvent('task_completed', {
					jsonrpc: '2.0',
					id: id,
					result: { status: 'FINISHED', result: structuredResult }
				});

				console.log(`[WRITING] Workflow completed successfully for team ${requestTeam.name}`);
				unsubscribe();
				controller.close();
			} catch (e) {
				console.error(`[WRITING] Error during Vibe execution for request ${id}:`, e.message);
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
			Connection: 'keep-alive',
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Headers': 'Cache-Control'
		}
	});
}
