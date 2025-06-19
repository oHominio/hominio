<script>
	import { onMount, afterUpdate } from 'svelte';
	import { Agent, Team, Task } from 'kaibanjs';
	import { PUBLIC_RED_PILL_API_KEY, PUBLIC_RED_PILL_BASE_URL } from '$env/static/public';
	import { marked } from 'marked';

	let status = 'Ready to test KaibanJS';
	let result = '';
	let agents = null;
	let team = null;
	let topic = 'The future of AI in web development';
	let isRunning = false;
	let taskResults = [];
	let workflowController = null;
	let taskProgress = [];
	let currentTask = null;
	let workflowLogs = [];
	let workflowStats = {
		totalTasks: 0,
		completedTasks: 0,
		errorCount: 0,
		totalTokensUsed: 0,
		totalCost: 0,
		startTime: null,
		endTime: null,
		duration: 0
	};
	let agentCosts = {}; // Track costs per agent
	let activeTab = 'activity'; // 'activity' or 'results'
	let activityLogsContainer; // Reference for auto-scroll

	let taskDescription = 'The future of AI agents in software development';
	let taskExpectedOutput = 'A 3-paragraph blog post about the topic.';

	let activityLog = [];
	let finalResult = '';
	let error = null;

	let eventSource;

	let tasks = [];

	// Custom Knowledge Base Tool
	class KnowledgeBaseTool {
		constructor() {
			this.name = 'knowledge_base_search';
			this.description = 'Search the knowledge base for information on various topics';
		}

		async invoke(query) {
			// Simulate knowledge base responses based on query content
			// Ensure query is a string before calling toLowerCase
			const queryStr = typeof query === 'string' ? query : String(query);
			const queryLower = queryStr.toLowerCase();

			if (queryLower.includes('ai') || queryLower.includes('artificial intelligence')) {
				return `AI Knowledge Base Results for "${queryStr}":
				
				• Current AI trends include large language models, multimodal AI, and edge computing
				• Key developments: GPT-4, Claude, Gemini showing improved reasoning capabilities
				• Challenges: AI safety, hallucinations, computational costs, ethical considerations
				• Opportunities: Automation, personalized experiences, scientific research acceleration
				• Future outlook: More efficient models, better human-AI collaboration, specialized AI agents`;
			}

			if (
				queryLower.includes('web development') ||
				queryLower.includes('frontend') ||
				queryLower.includes('backend')
			) {
				return `Web Development Knowledge Base Results for "${queryStr}":
				
				• Modern frameworks: React, Vue, Svelte for frontend; Node.js, Python, Go for backend
				• Key trends: JAMstack, serverless architecture, micro-frontends, WebAssembly
				• Challenges: Performance optimization, security, cross-browser compatibility
				• Opportunities: Progressive Web Apps, real-time applications, AI integration
				• Future outlook: Better developer experience, automated testing, AI-assisted coding`;
			}

			if (queryLower.includes('technology') || queryLower.includes('tech')) {
				return `Technology Knowledge Base Results for "${queryStr}":
				
				• Emerging technologies: Quantum computing, blockchain, IoT, 5G/6G networks
				• Industry trends: Digital transformation, remote work tools, cybersecurity focus
				• Challenges: Privacy concerns, digital divide, technology addiction
				• Opportunities: Innovation acceleration, global connectivity, efficiency gains
				• Future outlook: More integrated systems, sustainable technology, human-centric design`;
			}

			// Default response
			return `Knowledge Base Results for "${queryStr}":
			
			• General information available on various topics
			• Consider refining your search terms for more specific results
			• Topics covered include: technology, business, science, and current trends
			• For detailed analysis, try more specific queries`;
		}
	}

	const knowledgeBaseTool = new KnowledgeBaseTool();

	// Create Research Agent with Red Pill AI
	const researchAgent = new Agent({
		name: 'Research Agent',
		role: 'Information Researcher',
		goal: 'Conduct thorough research and provide comprehensive insights',
		background: 'Experienced researcher with expertise in analyzing trends and gathering insights',
		tools: [knowledgeBaseTool],
		llmConfig: {
			provider: 'openai',
			model: 'phala/qwen-2.5-7b-instruct',
			configuration: {
				apiKey: PUBLIC_RED_PILL_API_KEY,
				baseURL: PUBLIC_RED_PILL_BASE_URL,
				temperature: 0.7,
				maxTokens: 2000,
				maxRetries: 3
			}
		},
		maxIterations: 5,
		forceFinalAnswer: true
	});

	// Create Custom Storytelling Agent with Red Pill AI
	const writerAgent = new Agent({
		name: 'Storytelling Agent',
		role: 'Master Storyteller & Emotional Content Creator',
		goal: 'Transform research findings into captivating, emotionally resonant stories that inspire and engage readers on a deep human level',
		background: `You are a master storyteller with the soul of a poet and the mind of a strategist. Your superpower lies in weaving research data into compelling narratives that touch hearts, spark imagination, and drive action. 

		You understand that great storytelling is about:
		• Creating emotional connections through relatable human experiences
		• Using vivid imagery and sensory details that make readers FEEL the story
		• Building narrative tension that keeps readers engaged from start to finish
		• Incorporating universal themes that resonate across cultures and backgrounds
		• Using the power of metaphor, analogy, and symbolism to make complex ideas accessible
		• Crafting memorable moments that stick with readers long after they finish reading

		Your writing style combines:
		- The curiosity of a journalist uncovering hidden truths
		- The empathy of a counselor understanding human struggles
		- The vision of a futurist painting possibilities
		- The wisdom of a mentor guiding transformation
		- The passion of an advocate fighting for positive change`,
		tools: [knowledgeBaseTool],
		llmConfig: {
			provider: 'openai',
			model: 'phala/deepseek-r1-70b',
			configuration: {
				apiKey: PUBLIC_RED_PILL_API_KEY,
				baseURL: PUBLIC_RED_PILL_BASE_URL,
				temperature: 0.9, // Higher temperature for more creative storytelling
				maxTokens: 3500, // More tokens for detailed storytelling
				maxRetries: 3
			}
		},
		maxIterations: 4,
		forceFinalAnswer: true
	});

	// Dynamic agent configuration getter
	function getAgentConfig(agent) {
		return {
			name: agent.name,
			role: agent.role,
			goal: agent.goal,
			background: agent.background,
			model: agent.llmConfig?.model || 'Unknown',
			provider: agent.llmConfig?.provider || 'Unknown',
			temperature: agent.llmConfig?.configuration?.temperature || 'Not set',
			maxTokens: agent.llmConfig?.configuration?.maxTokens || 'Not set',
			maxRetries: agent.llmConfig?.configuration?.maxRetries || 'Not set',
			maxIterations: agent.maxIterations || 'Not set',
			forceFinalAnswer: agent.forceFinalAnswer || false,
			toolsCount: agent.tools?.length || 0
		};
	}

	// Get dynamic configurations
	$: researchConfig = getAgentConfig(researchAgent);
	$: writerConfig = getAgentConfig(writerAgent);

	// Define tasks
	let researchTask = new Task({
		title: 'Research Analysis',
		description: `Conduct comprehensive research on the topic: "${topic}".`,
		agent: researchAgent,
		expectedOutput: 'Detailed research findings with key insights and trends'
	});

	let writingTask = new Task({
		title: 'Storytelling & Content Creation',
		description: `Transform research findings into an emotionally engaging story about "${topic}".`,
		agent: writerAgent,
		expectedOutput: 'Captivating, emotionally resonant story that inspires and transforms readers'
	});

	onMount(async () => {
		try {
			// Create team with tasks
			team = new Team({
				name: 'Research & Writing Team',
				agents: [researchAgent, writerAgent],
				tasks: [researchTask, writingTask],
				inputs: { topic: topic },
				env: {
					OPENAI_API_KEY: PUBLIC_RED_PILL_API_KEY
				}
			});

			agents = [researchAgent, writerAgent];
			status = 'KaibanJS team initialized successfully!';
			console.log('Team created:', team);
		} catch (error) {
			status = `Team creation failed: ${error.message}`;
			console.error('Team creation error:', error);
		}
	});

	// Red Pill AI pricing (estimated based on your models)
	const modelPricing = {
		'phala/qwen-2.5-7b-instruct': {
			inputTokensPerM: 0.04, // $0.04 per 1M input tokens
			outputTokensPerM: 0.1, // $0.1 per 1M output tokens
			name: 'Qwen2.5 7B Instruct'
		},
		'phala/deepseek-r1-70b': {
			inputTokensPerM: 0.2, // $0.2 per 1M input tokens (estimated for 70B model)
			outputTokensPerM: 0.7, // $0.7 per 1M output tokens (estimated for 70B model)
			name: 'DeepSeek R1 70B'
		},
		'phala/meta-llama-3.3-70b-instruct': {
			inputTokensPerM: 0.12, // $0.12 per 1M input tokens (estimated)
			outputTokensPerM: 0.35, // $0.35 per 1M output tokens (estimated)
			name: 'Meta Llama 3.3 70B Instruct'
		}
	};

	// Calculate cost for specific token usage
	function calculateCost(inputTokens, outputTokens, modelName) {
		const pricing = modelPricing[modelName];
		if (!pricing) {
			return {
				inputCost: 0,
				outputCost: 0,
				totalCost: 0,
				note: 'Unknown pricing for model'
			};
		}

		const inputCost = (inputTokens / 1000000) * pricing.inputTokensPerM;
		const outputCost = (outputTokens / 1000000) * pricing.outputTokensPerM;
		const totalCost = inputCost + outputCost;

		return {
			inputCost: parseFloat(inputCost.toFixed(6)),
			outputCost: parseFloat(outputCost.toFixed(6)),
			totalCost: parseFloat(totalCost.toFixed(6)),
			modelDisplayName: pricing.name
		};
	}

	// Extract agent-specific costs from logs
	function extractAgentCosts(logs) {
		const costs = {};

		logs.forEach((log) => {
			if (log.agent && log.metadata && log.metadata.llmUsageStats) {
				const agentName = log.agent.name;
				const modelName = log.agent.llmConfig?.model || 'unknown';
				const inputTokens = log.metadata.llmUsageStats.inputTokens || 0;
				const outputTokens = log.metadata.llmUsageStats.outputTokens || 0;

				if (!costs[agentName]) {
					costs[agentName] = {
						name: agentName,
						model: modelName,
						totalInputTokens: 0,
						totalOutputTokens: 0,
						totalTokens: 0,
						totalCost: 0,
						inputCost: 0,
						outputCost: 0,
						callCount: 0,
						iterations: 0,
						tasks: new Set()
					};
				}

				costs[agentName].totalInputTokens += inputTokens;
				costs[agentName].totalOutputTokens += outputTokens;
				costs[agentName].totalTokens += inputTokens + outputTokens;
				costs[agentName].callCount++;

				if (log.task) {
					costs[agentName].tasks.add(log.task.title || log.task.id);
				}

				// Calculate costs
				const costCalc = calculateCost(inputTokens, outputTokens, modelName);
				costs[agentName].inputCost += costCalc.inputCost;
				costs[agentName].outputCost += costCalc.outputCost;
				costs[agentName].totalCost += costCalc.totalCost;
				costs[agentName].modelDisplayName = costCalc.modelDisplayName;
			}
		});

		// Convert tasks Set to Array for display
		Object.keys(costs).forEach((agentName) => {
			costs[agentName].tasksArray = Array.from(costs[agentName].tasks);
			delete costs[agentName].tasks;
		});

		return costs;
	}

	// Observability functions based on KaibanJS documentation
	function extractWorkflowStats(logs) {
		const stats = {
			totalTasks: 0,
			completedTasks: 0,
			errorCount: 0,
			totalTokensUsed: 0,
			totalCost: 0,
			startTime: null,
			endTime: null,
			duration: 0
		};

		logs.forEach((log) => {
			// Count tasks
			if (log.logType === 'TaskStatusUpdate') {
				if (log.taskStatus === 'DONE') {
					stats.completedTasks++;
				}
				// Count errors
				if (log.taskStatus === 'BLOCKED') {
					stats.errorCount++;
				}
			}

			// Count agent errors
			if (log.logType === 'AgentStatusUpdate' && log.agentStatus === 'THINKING_ERROR') {
				stats.errorCount++;
			}

			// Extract token usage and costs
			if (log.metadata) {
				if (log.metadata.llmUsageStats) {
					const inputTokens = log.metadata.llmUsageStats.inputTokens || 0;
					const outputTokens = log.metadata.llmUsageStats.outputTokens || 0;
					stats.totalTokensUsed += inputTokens + outputTokens;

					// Calculate cost if agent info is available
					if (log.agent && log.agent.llmConfig && log.agent.llmConfig.model) {
						const costCalc = calculateCost(inputTokens, outputTokens, log.agent.llmConfig.model);
						stats.totalCost += costCalc.totalCost;
					}
				}
				if (log.metadata.costDetails && log.metadata.costDetails.totalCost) {
					stats.totalCost += log.metadata.costDetails.totalCost;
				}
				if (log.metadata.startTime && !stats.startTime) {
					stats.startTime = log.metadata.startTime;
				}
				if (log.metadata.endTime) {
					stats.endTime = log.metadata.endTime;
				}
			}
		});

		// Calculate duration
		if (stats.startTime && stats.endTime) {
			stats.duration = (new Date(stats.endTime) - new Date(stats.startTime)) / 1000;
		}

		return stats;
	}

	function getTaskCompletionStats(taskId, logs) {
		const completedLog = logs.find(
			(log) =>
				log.task &&
				log.task.id === taskId &&
				log.logType === 'TaskStatusUpdate' &&
				log.task.status === 'DONE'
		);

		if (completedLog && completedLog.metadata) {
			return {
				taskId,
				duration: completedLog.metadata.duration || 0,
				iterations: completedLog.metadata.iterationCount || 0,
				tokenUsage: completedLog.metadata.llmUsageStats || {},
				cost: completedLog.metadata.costDetails || {}
			};
		}
		return null;
	}

	function countAgentErrors(agentName, logs) {
		return logs.filter(
			(log) =>
				log.agent &&
				log.agent.name === agentName &&
				log.logType === 'AgentStatusUpdate' &&
				log.agentStatus === 'THINKING_ERROR'
		).length;
	}

	// Monitor team state for progress updates
	function monitorTeamProgress() {
		if (!team || !team.store) return;

		// Subscribe to team state changes
		const unsubscribe = team.store.subscribe((state) => {
			if (state) {
				// Update task progress
				if (state.tasks) {
					taskProgress = state.tasks.map((task) => ({
						title: task.title,
						status: task.status,
						agent: task.agent?.name || 'Unknown',
						duration: task.duration || 0,
						iterations: task.iterations || 0,
						description: task.description || '',
						expectedOutput: task.expectedOutput || ''
					}));

					// Update current task
					currentTask = state.tasks.find((task) => task.status === 'DOING') || null;
				}

				// Update workflow logs and stats
				if (state.workflowLogs) {
					workflowLogs = state.workflowLogs;
					workflowStats = extractWorkflowStats(state.workflowLogs);
					agentCosts = extractAgentCosts(state.workflowLogs);

					// Log observability data to console
					console.log('📊 Workflow Stats Updated:', workflowStats);
					console.log('💰 Agent Costs Updated:', agentCosts);

					// Log recent activities
					const recentLogs = state.workflowLogs.slice(-5);
					recentLogs.forEach((log) => {
						console.log(`🔍 [${log.logType}] ${log.logDescription || 'No description'}`);
					});

					// Auto-scroll to bottom of activity logs
					if (activityLogsContainer && activeTab === 'activity') {
						setTimeout(() => {
							activityLogsContainer.scrollTop = activityLogsContainer.scrollHeight;
						}, 100);
					}
				}
			}
		});

		return unsubscribe;
	}

	// Execute workflow
	async function startWorkflow() {
		if (!team || isRunning) return;

		isRunning = true;
		status = 'Agents are working...';
		taskResults = [];
		result = '';
		workflowController = null;
		taskProgress = [];
		currentTask = null;
		workflowLogs = [];
		agentCosts = {}; // Reset agent costs
		workflowStats = {
			totalTasks: 0,
			completedTasks: 0,
			errorCount: 0,
			totalTokensUsed: 0,
			totalCost: 0,
			startTime: null,
			endTime: null,
			duration: 0
		};
		activeTab = 'activity'; // Switch to activity tab when starting

		// Start monitoring progress
		const unsubscribe = monitorTeamProgress();

		try {
			// Update task descriptions with current topic
			researchTask.description = `Conduct comprehensive research on the topic: "${topic}". 
			Analyze current trends, key developments, challenges, and opportunities. 
			Provide 5-7 key insights with supporting evidence.
			
			Use the knowledge_base_search tool to gather relevant information.`;

			writingTask.description = `Transform the research findings into a captivating, emotionally engaging story about "${topic}". 

			🎭 STORYTELLING MISSION:
			Create content that doesn't just inform—it INSPIRES, MOVES, and TRANSFORMS readers. Make them feel like they're part of an epic journey into the future.

			📖 EMOTIONAL STORYTELLING TACTICS TO USE:
			• Start with a HOOK that makes readers feel curiosity, wonder, or urgency
			• Use the "Hero's Journey" structure: Present challenges, show transformation, reveal the new world
			• Include HUMAN STORIES and relatable scenarios that readers can see themselves in
			• Paint VIVID PICTURES with sensory details that make abstract concepts tangible
			• Create EMOTIONAL PEAKS AND VALLEYS to keep readers engaged
			• Use METAPHORS and ANALOGIES that connect complex ideas to familiar experiences
			• Build toward a CLIMACTIC REVELATION that changes how readers see the world
			• End with a CALL TO ADVENTURE that empowers readers to take action

			🌟 STRUCTURE YOUR STORY:
			1. OPENING SCENE: Set the stage with a compelling scenario or question
			2. THE CURRENT WORLD: What exists today (with its limitations and frustrations)
			3. THE CATALYST: What's changing everything (the research findings)
			4. THE TRANSFORMATION: How this change will reshape our world
			5. THE NEW REALITY: Paint a vivid picture of the transformed future
			6. THE CALL TO ACTION: How readers can be part of this transformation

			Remember: You're not just writing an article—you're crafting an experience that will stay with readers long after they finish reading. Make them FEEL the excitement, possibility, and human impact of these developments.
			
			Use knowledge_base_search for additional context and human stories if needed.`;

			// Execute the team workflow and store controller
			const workflowPromise = team.start();
			workflowController = workflowPromise; // Store the promise as controller
			const teamResult = await workflowPromise;

			// Extract human-readable content from the result
			if (typeof teamResult === 'string') {
				result = teamResult;
			} else if (teamResult && typeof teamResult === 'object') {
				// Try to extract the final story content from the result object
				result =
					teamResult.output ||
					teamResult.result ||
					teamResult.content ||
					teamResult.finalResult ||
					(teamResult.tasks && teamResult.tasks[teamResult.tasks.length - 1]?.output) ||
					JSON.stringify(teamResult, null, 2);
			} else {
				result = String(teamResult || 'No result generated');
			}

			status = 'Workflow completed successfully!';
			activeTab = 'results'; // Switch to results tab when completed
			console.log('Team workflow result:', teamResult);
			console.log('Processed result for display:', result);
		} catch (error) {
			if (error.message?.includes('interrupted') || error.message?.includes('aborted')) {
				status = 'Workflow interrupted by user';
			} else {
				status = `Workflow failed: ${error.message}`;
				console.error('Workflow error:', error);
			}
		} finally {
			isRunning = false;
			workflowController = null;
			if (unsubscribe) unsubscribe();
		}
	}

	// Stop workflow
	async function stopWorkflow() {
		if (workflowController && isRunning) {
			try {
				// Check if the controller has an interrupt method
				if (typeof workflowController.interrupt === 'function') {
					await workflowController.interrupt();
				} else if (typeof workflowController.abort === 'function') {
					await workflowController.abort();
				} else {
					// If no interrupt method available, just set the status
					console.log('No interrupt method available on workflow controller');
				}
				status = 'Workflow stopped by user';
				isRunning = false;
			} catch (error) {
				console.error('Error stopping workflow:', error);
				status = 'Error stopping workflow';
				isRunning = false;
			}
		}
	}

	// Get status color for kanban cards
	function getStatusColor(status) {
		switch (status) {
			case 'PENDING':
				return 'bg-stone-400 text-white';
			case 'DOING':
				return 'bg-blue-600 text-white animate-pulse';
			case 'DONE':
				return 'bg-green-600 text-white';
			case 'BLOCKED':
				return 'bg-red-500 text-white';
			default:
				return 'bg-stone-500 text-white';
		}
	}

	// Get status icon
	function getStatusIcon(status) {
		switch (status) {
			case 'PENDING':
				return '•';
			case 'DOING':
				return '→';
			case 'DONE':
				return '✓';
			case 'BLOCKED':
				return '×';
			default:
				return '•';
		}
	}

	// afterUpdate is the robust way to handle DOM changes after the state updates.
	// This will ensure we scroll after the new log is rendered.
	afterUpdate(() => {
		if (activityLogsContainer) {
			activityLogsContainer.scrollTo({
				top: activityLogsContainer.scrollHeight,
				behavior: 'smooth'
			});
		}
	});

	async function startTask() {
		if (isRunning) return;

		isRunning = true;
		activityLog = [];
		finalResult = '';
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
				while (true) {
					const { done, value } = await reader.read();
					if (done) {
						if (!error) isRunning = false;
						break;
					}

					const chunk = decoder.decode(value, { stream: true });
					const events = chunk.split('\\n\\n').filter((e) => e.trim() !== '');

					for (const eventString of events) {
						if (!eventString.startsWith('event:')) continue;

						const eventNameLine = eventString.split('\\n')[0];
						const eventName = eventNameLine.substring('event: '.length).trim();
						const dataLine = eventString.substring(eventNameLine.length + 1);
						const dataString = dataLine.substring('data: '.length);

						try {
							const data = JSON.parse(dataString);
							if (eventName === 'task_status_update' && data.params?.status) {
								const logEntry = data.params.status;
								const logText = `[${new Date(logEntry.timestamp).toLocaleTimeString()}] ${logEntry.description}`;
								activityLog = [...activityLog, logText];

								// Update task board status
								const desc = logEntry.description;
								if (desc.startsWith('Task:') && desc.endsWith('started.')) {
									const taskTitle = desc.substring('Task: '.length, desc.indexOf(' started.'));
									const task = tasks.find((t) => t.title === taskTitle);
									if (task) task.status = 'DOING';
								} else if (desc.startsWith('Task completed:')) {
									const taskTitle = desc.substring('Task completed: '.length, desc.length - 1);
									const task = tasks.find((t) => t.title === taskTitle);
									if (task) task.status = 'DONE';
								}
								tasks = tasks; // Trigger reactivity
							} else if (eventName === 'task_completed' && data.result) {
								// The structure is result -> result -> result as discovered via debugging
								if (data.result?.result?.result) {
									finalResult = data.result.result.result;
								} else {
									error = `Task completed but the result format was unexpected.`;
								}
								isRunning = false;
							} else if (eventName === 'task_error' && data.error) {
								error = data.error.message;
								isRunning = false;
							}
						} catch (e) {
							console.error('Failed to parse event data:', e, 'Data string:', dataString);
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
		return () => {
			// Clean up the event source when the component is destroyed
			if (eventSource) {
				eventSource.close();
			}
		};
	});
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
												: 'text-gray-500'}">{task.status}</span
									>
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
						<h2 class="mb-4 text-2xl font-semibold text-cyan-300">Final Result</h2>
						<div class="prose prose-invert max-h-[60vh] max-w-none overflow-y-auto">
							{@html marked(finalResult)}
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
