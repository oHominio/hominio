<script>
	import { onMount } from 'svelte';
	import { Agent, Team, Task } from 'kaibanjs';
	import { PUBLIC_RED_PILL_API_KEY, PUBLIC_RED_PILL_BASE_URL } from '$env/static/public';

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
</script>

<div class="min-h-screen bg-stone-50 text-slate-800">
	<!-- Header -->
	<div class="border-b border-stone-200 bg-white p-6 shadow-sm">
		<div class="mb-2 flex items-center justify-center gap-3">
			<div class="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800">
				<div class="h-3 w-3 rounded-full bg-white"></div>
			</div>
			<h1 class="text-center text-3xl font-bold text-slate-800">Hominio AI Agents</h1>
		</div>
		<p class="text-center text-slate-600">Research Agent + Storytelling Agent Collaboration</p>
	</div>

	<!-- Main Content - 50/50 Split -->
	<div class="flex h-screen">
		<!-- Left Panel - Agent Configuration & Controls -->
		<div class="w-1/2 overflow-y-auto border-r border-stone-200 bg-stone-50 p-6">
			<!-- Topic Input -->
			<div class="mb-6">
				<label for="topic" class="mb-2 block text-sm font-medium text-slate-700">
					Research Topic
				</label>
				<input
					id="topic"
					bind:value={topic}
					class="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-slate-800 placeholder-slate-400 shadow-sm focus:border-slate-800 focus:ring-2 focus:ring-slate-800 focus:outline-none"
					placeholder="Enter your research topic..."
					disabled={isRunning}
				/>
			</div>

			<!-- Control Buttons -->
			<div class="mb-6 flex gap-4">
				<button
					on:click={startWorkflow}
					disabled={!team || isRunning}
					class="flex-1 rounded-full bg-slate-800 px-6 py-3 font-semibold text-white shadow-sm transition-all duration-200 hover:bg-slate-700 hover:shadow-md disabled:cursor-not-allowed disabled:bg-stone-400"
				>
					{isRunning ? 'Running...' : 'Start Workflow'}
				</button>

				{#if isRunning}
					<button
						on:click={stopWorkflow}
						class="rounded-full bg-red-500 px-6 py-3 font-semibold text-white shadow-sm transition-all duration-200 hover:bg-red-600 hover:shadow-md"
					>
						Stop
					</button>
				{/if}
			</div>

			<!-- Status -->
			<div class="mb-6 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
				<h3 class="mb-2 text-lg font-semibold text-slate-800">Status</h3>
				<p class="text-slate-600">{status}</p>
			</div>

			<!-- Task Board - Moved above workflow statistics -->
			{#if isRunning || taskProgress.length > 0}
				<div class="mb-6">
					<h3 class="mb-4 text-xl font-semibold text-slate-800">Task Board</h3>

					{#if taskProgress.length > 0}
						<div class="grid grid-cols-1 gap-4">
							{#each taskProgress as task, index}
								<div
									class="rounded-xl border border-l-4 border-stone-200 bg-white shadow-sm {task.status ===
									'DOING'
										? 'border-l-blue-500'
										: task.status === 'DONE'
											? 'border-l-green-500'
											: task.status === 'BLOCKED'
												? 'border-l-red-500'
												: 'border-l-stone-400'} p-4"
								>
									<!-- Task Header -->
									<div class="mb-2 flex items-center justify-between">
										<h4 class="font-semibold text-slate-800">{task.title}</h4>
										<span class="rounded-full px-2 py-1 text-xs {getStatusColor(task.status)}">
											{getStatusIcon(task.status)}
											{task.status}
										</span>
									</div>

									<!-- Task Details -->
									<div class="mb-2 text-sm text-slate-600">
										Agent: <span class="font-medium text-slate-800">{task.agent}</span>
									</div>

									<!-- Task Description -->
									<div class="mb-2 line-clamp-2 text-xs text-slate-500">
										{task.description}
									</div>

									<!-- Progress Metrics -->
									<div class="flex justify-between text-xs text-slate-500">
										{#if task.duration > 0}
											<span>Duration: {task.duration.toFixed(1)}s</span>
										{/if}
										{#if task.iterations > 0}
											<span>Iterations: {task.iterations}</span>
										{/if}
									</div>

									<!-- Progress Bar -->
									{#if task.status === 'DOING'}
										<div class="mt-2">
											<div class="h-1 w-full rounded-full bg-stone-200">
												<div
													class="h-1 animate-pulse rounded-full bg-blue-500"
													style="width: 60%"
												></div>
											</div>
										</div>
									{:else if task.status === 'DONE'}
										<div class="mt-2">
											<div class="h-1 w-full rounded-full bg-stone-200">
												<div class="h-1 rounded-full bg-green-500" style="width: 100%"></div>
											</div>
										</div>
									{/if}
								</div>
							{/each}
						</div>
					{:else}
						<div class="py-8 text-center text-slate-500">
							<div
								class="mx-auto mb-2 h-8 w-8 animate-spin rounded-full border-4 border-slate-800 border-t-transparent"
							></div>
							<p>Initializing tasks...</p>
						</div>
					{/if}
				</div>
			{/if}

			<!-- Workflow Statistics -->
			{#if workflowLogs.length > 0}
				<div class="mb-6">
					<h3 class="mb-4 text-xl font-semibold text-slate-800">Workflow Statistics</h3>

					<!-- Workflow Statistics -->
					<div class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
						<div class="grid grid-cols-2 gap-3 text-sm">
							<div class="rounded-lg bg-stone-100 p-3">
								<div class="text-slate-600">Completed Tasks</div>
								<div class="font-bold text-green-600">{workflowStats.completedTasks}</div>
							</div>
							<div class="rounded-lg bg-stone-100 p-3">
								<div class="text-slate-600">Total Errors</div>
								<div class="font-bold text-red-500">{workflowStats.errorCount}</div>
							</div>
							<div class="rounded-lg bg-stone-100 p-3">
								<div class="text-slate-600">Tokens Used</div>
								<div class="font-bold text-blue-600">
									{workflowStats.totalTokensUsed.toLocaleString()}
								</div>
							</div>
							<div class="rounded-lg bg-stone-100 p-3">
								<div class="text-slate-600">Duration</div>
								<div class="font-bold text-slate-800">{workflowStats.duration.toFixed(1)}s</div>
							</div>
						</div>
						{#if workflowStats.totalCost > 0}
							<div class="mt-3 rounded-lg bg-stone-100 p-3 text-sm">
								<div class="text-slate-600">Estimated Total Cost</div>
								<div class="font-bold text-slate-800">${workflowStats.totalCost.toFixed(4)}</div>
							</div>
						{/if}
					</div>
				</div>
			{/if}

			<!-- Agent Cost Analysis -->
			{#if Object.keys(agentCosts).length > 0}
				<div class="mb-6">
					<h3 class="mb-4 text-xl font-semibold text-slate-800">Agent Cost Analysis</h3>

					<div class="space-y-4">
						{#each Object.values(agentCosts) as agentCost}
							<div class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
								<!-- Agent Header -->
								<div class="mb-3 flex items-center justify-between">
									<h4 class="font-semibold text-slate-800">{agentCost.name}</h4>
									<div
										class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600"
									>
										{agentCost.modelDisplayName || agentCost.model}
									</div>
								</div>

								<!-- Cost Summary -->
								<div class="mb-3 grid grid-cols-3 gap-3 text-sm">
									<div class="rounded-lg bg-green-50 p-3 text-center">
										<div class="text-xs text-green-600">Total Cost</div>
										<div class="font-bold text-green-700">${agentCost.totalCost.toFixed(4)}</div>
									</div>
									<div class="rounded-lg bg-blue-50 p-3 text-center">
										<div class="text-xs text-blue-600">Input Cost</div>
										<div class="font-bold text-blue-700">${agentCost.inputCost.toFixed(4)}</div>
									</div>
									<div class="rounded-lg bg-purple-50 p-3 text-center">
										<div class="text-xs text-purple-600">Output Cost</div>
										<div class="font-bold text-purple-700">${agentCost.outputCost.toFixed(4)}</div>
									</div>
								</div>

								<!-- Token Usage -->
								<div class="mb-3 grid grid-cols-3 gap-3 text-sm">
									<div class="rounded-lg bg-stone-100 p-3 text-center">
										<div class="text-xs text-slate-600">Total Tokens</div>
										<div class="font-bold text-slate-800">
											{agentCost.totalTokens.toLocaleString()}
										</div>
									</div>
									<div class="rounded-lg bg-stone-100 p-3 text-center">
										<div class="text-xs text-slate-600">Input Tokens</div>
										<div class="font-bold text-slate-800">
											{agentCost.totalInputTokens.toLocaleString()}
										</div>
									</div>
									<div class="rounded-lg bg-stone-100 p-3 text-center">
										<div class="text-xs text-slate-600">Output Tokens</div>
										<div class="font-bold text-slate-800">
											{agentCost.totalOutputTokens.toLocaleString()}
										</div>
									</div>
								</div>

								<!-- Additional Metrics -->
								<div class="grid grid-cols-2 gap-3 text-sm">
									<div class="rounded-lg bg-stone-50 p-2">
										<div class="text-xs text-slate-600">API Calls</div>
										<div class="font-medium text-slate-800">{agentCost.callCount}</div>
									</div>
									<div class="rounded-lg bg-stone-50 p-2">
										<div class="text-xs text-slate-600">Tasks Worked</div>
										<div class="font-medium text-slate-800">
											{agentCost.tasksArray?.length || 0}
										</div>
									</div>
								</div>

								<!-- Cost Efficiency Metrics -->
								{#if agentCost.totalCost > 0 && agentCost.tasksArray?.length > 0}
									<div class="mt-3 rounded-lg bg-amber-50 p-3 text-sm">
										<div class="mb-1 text-xs text-amber-600">Efficiency Metrics</div>
										<div class="grid grid-cols-2 gap-2">
											<div>
												<span class="text-amber-700">Cost per Task:</span>
												<span class="font-bold text-amber-800">
													${(agentCost.totalCost / agentCost.tasksArray.length).toFixed(4)}
												</span>
											</div>
											<div>
												<span class="text-amber-700">Cost per 1K Tokens:</span>
												<span class="font-bold text-amber-800">
													${((agentCost.totalCost / agentCost.totalTokens) * 1000).toFixed(4)}
												</span>
											</div>
										</div>
									</div>
								{/if}

								<!-- Tasks List -->
								{#if agentCost.tasksArray?.length > 0}
									<div class="mt-3 text-xs">
										<div class="mb-1 text-slate-600">Tasks:</div>
										<div class="flex flex-wrap gap-1">
											{#each agentCost.tasksArray as taskName}
												<span class="rounded-full bg-slate-100 px-2 py-0.5 text-slate-700">
													{taskName}
												</span>
											{/each}
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Agent Configuration Cards -->
			<div class="mb-6">
				<h3 class="mb-4 text-xl font-semibold text-slate-800">Agent Configuration</h3>
				<div class="space-y-4">
					<!-- Research Agent Config -->
					<div class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
						<h4 class="mb-3 text-lg font-semibold text-blue-600">{researchConfig.name}</h4>
						<div class="grid grid-cols-2 gap-2 text-sm">
							<div class="text-slate-600">Role:</div>
							<div class="text-slate-800">{researchConfig.role}</div>

							<div class="text-slate-600">Model:</div>
							<div class="text-slate-800">Qwen 2.5-7B Instruct</div>

							<div class="text-slate-600">Provider:</div>
							<div class="text-slate-800">Red Pill AI</div>

							<div class="text-slate-600">Temperature:</div>
							<div class="font-medium text-slate-800">{researchConfig.temperature}</div>

							<div class="text-slate-600">Max Tokens:</div>
							<div class="font-medium text-slate-800">{researchConfig.maxTokens}</div>

							<div class="text-slate-600">Max Iterations:</div>
							<div class="font-medium text-slate-800">{researchConfig.maxIterations}</div>

							<div class="text-slate-600">Max Retries:</div>
							<div class="font-medium text-slate-800">{researchConfig.maxRetries}</div>

							<div class="text-slate-600">Tools:</div>
							<div class="font-medium text-green-600">{researchConfig.toolsCount} tool(s)</div>
						</div>
						<div class="mt-3 rounded-lg bg-stone-50 p-2 text-xs text-slate-500">
							Goal: {researchConfig.goal}
						</div>
					</div>

					<!-- Storytelling Agent Config -->
					<div class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
						<h4 class="mb-3 text-lg font-semibold text-purple-600">{writerConfig.name}</h4>
						<div class="grid grid-cols-2 gap-2 text-sm">
							<div class="text-slate-600">Role:</div>
							<div class="text-slate-800">{writerConfig.role}</div>

							<div class="text-slate-600">Model:</div>
							<div class="text-slate-800">DeepSeek R1-70B</div>

							<div class="text-slate-600">Provider:</div>
							<div class="text-slate-800">Red Pill AI</div>

							<div class="text-slate-600">Temperature:</div>
							<div class="font-medium text-slate-800">{writerConfig.temperature}</div>

							<div class="text-slate-600">Max Tokens:</div>
							<div class="font-medium text-slate-800">{writerConfig.maxTokens}</div>

							<div class="text-slate-600">Max Iterations:</div>
							<div class="font-medium text-slate-800">{writerConfig.maxIterations}</div>

							<div class="text-slate-600">Max Retries:</div>
							<div class="font-medium text-slate-800">{writerConfig.maxRetries}</div>

							<div class="text-slate-600">Tools:</div>
							<div class="font-medium text-green-600">{writerConfig.toolsCount} tool(s)</div>
						</div>
						<div class="mt-3 rounded-lg bg-stone-50 p-2 text-xs text-slate-500">
							Goal: {writerConfig.goal}
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Right Panel - Results & Activity -->
		<div class="flex w-1/2 flex-col overflow-hidden bg-white p-6">
			<!-- Tab Header -->
			<div class="mb-4 flex rounded-full bg-stone-100 p-1">
				<button
					class="flex-1 rounded-full px-4 py-2 font-medium transition-all duration-200 {activeTab ===
					'activity'
						? 'bg-slate-800 text-white shadow-sm'
						: 'text-slate-600 hover:text-slate-800'}"
					on:click={() => (activeTab = 'activity')}
				>
					Activity Logs
				</button>
				<button
					class="flex-1 rounded-full px-4 py-2 font-medium transition-all duration-200 {activeTab ===
					'results'
						? 'bg-slate-800 text-white shadow-sm'
						: 'text-slate-600 hover:text-slate-800'}"
					on:click={() => (activeTab = 'results')}
					disabled={!result && !isRunning}
				>
					Results
				</button>
			</div>

			<!-- Tab Content -->
			<div class="flex-1 overflow-hidden">
				{#if activeTab === 'activity'}
					<!-- Activity Logs Tab -->
					<div class="flex h-full flex-col">
						<h3 class="mb-4 text-xl font-semibold text-slate-800">Real-time Activity</h3>

						{#if workflowLogs.length > 0 || isRunning}
							<div
								class="flex flex-1 flex-col overflow-hidden rounded-xl border border-stone-200 bg-white p-4"
							>
								<div
									class="flex-1 space-y-1 overflow-y-auto font-mono text-sm"
									bind:this={activityLogsContainer}
								>
									{#each workflowLogs as log, index}
										<div class="flex items-center gap-3 rounded px-2 py-1 hover:bg-stone-50">
											<!-- Timestamp -->
											<span class="w-16 text-xs text-slate-400">
												{new Date(log.timestamp || Date.now()).toLocaleTimeString('en-US', {
													hour12: false,
													hour: '2-digit',
													minute: '2-digit',
													second: '2-digit'
												})}
											</span>

											<!-- Log Type Badge -->
											<span
												class="rounded-full px-2 py-0.5 text-xs font-medium {log.logType ===
												'AgentStatusUpdate'
													? 'bg-blue-100 text-blue-700'
													: log.logType === 'TaskStatusUpdate'
														? 'bg-green-100 text-green-700'
														: 'bg-purple-100 text-purple-700'}"
											>
												{log.logType === 'AgentStatusUpdate'
													? 'AGENT'
													: log.logType === 'TaskStatusUpdate'
														? 'TASK'
														: 'SYSTEM'}
											</span>

											<!-- Status Badge -->
											{#if log.agentStatus}
												<span
													class="rounded-full px-2 py-0.5 text-xs font-medium {log.agentStatus ===
													'THINKING_ERROR'
														? 'bg-red-100 text-red-700'
														: log.agentStatus === 'THINKING'
															? 'bg-blue-100 text-blue-700'
															: 'bg-stone-100 text-stone-700'}"
												>
													{log.agentStatus}
												</span>
											{/if}
											{#if log.taskStatus}
												<span
													class="rounded-full px-2 py-0.5 text-xs font-medium {log.taskStatus ===
													'DONE'
														? 'bg-green-100 text-green-700'
														: log.taskStatus === 'DOING'
															? 'bg-blue-100 text-blue-700'
															: log.taskStatus === 'BLOCKED'
																? 'bg-red-100 text-red-700'
																: 'bg-stone-100 text-stone-700'}"
												>
													{log.taskStatus}
												</span>
											{/if}

											<!-- Log Description -->
											<span class="flex-1 truncate text-slate-700">
												{log.logDescription || 'No description available'}
											</span>

											<!-- Agent/Task Info -->
											{#if log.agent}
												<span class="text-xs text-slate-500">
													{log.agent.name}
												</span>
											{/if}
										</div>
									{/each}

									{#if isRunning && workflowLogs.length === 0}
										<div class="flex items-center justify-center py-8">
											<div
												class="mr-3 h-8 w-8 animate-spin rounded-full border-4 border-slate-800 border-t-transparent"
											></div>
											<span class="text-slate-500">Waiting for activity...</span>
										</div>
									{/if}
								</div>

								{#if workflowLogs.length > 10}
									<div class="mt-3 text-center text-xs text-slate-500">
										Showing all {workflowLogs.length} log entries
									</div>
								{/if}
							</div>
						{:else}
							<div
								class="flex flex-1 items-center justify-center rounded-xl border border-stone-200 bg-stone-50 p-6"
							>
								<div class="text-center">
									<div class="mb-4 text-4xl text-slate-400">Activity</div>
									<p class="text-slate-600">No activity yet</p>
									<p class="mt-2 text-sm text-slate-500">Start a workflow to see real-time logs</p>
								</div>
							</div>
						{/if}
					</div>
				{:else if activeTab === 'results'}
					<!-- Results Tab -->
					<div class="flex h-full flex-col">
						<h3 class="mb-4 text-xl font-semibold text-slate-800">Final Results</h3>

						{#if result}
							<div class="flex-1 overflow-y-auto rounded-xl border border-stone-200 bg-white p-6">
								<div
									class="prose prose-slate prose-headings:text-slate-800 prose-p:text-slate-700 prose-strong:text-slate-800 prose-em:text-slate-600 max-w-none"
								>
									<!-- Always display as formatted text, no JSON -->
									<div class="space-y-4">
										{#each String(result).split('\n\n') as paragraph}
											{#if paragraph.trim()}
												{#if paragraph.startsWith('#')}
													<!-- Handle markdown-style headers -->
													{@html paragraph.replace(
														/^#+\s*(.+)$/gm,
														'<h3 class="text-lg font-semibold text-slate-800 mb-2 mt-4">$1</h3>'
													)}
												{:else if paragraph.startsWith('**') && paragraph.endsWith('**')}
													<!-- Handle bold sections -->
													<h4 class="mb-2 font-semibold text-slate-800">
														{paragraph.replace(/\*\*/g, '')}
													</h4>
												{:else}
													<!-- Regular paragraphs -->
													<p class="mb-3 leading-relaxed text-slate-700">
														{@html paragraph
															.replace(
																/\*\*(.+?)\*\*/g,
																'<strong class="font-semibold text-slate-800">$1</strong>'
															)
															.replace(/\*(.+?)\*/g, '<em class="italic text-slate-600">$1</em>')}
													</p>
												{/if}
											{/if}
										{/each}
									</div>
								</div>
							</div>
						{:else if isRunning}
							<div
								class="flex flex-1 items-center justify-center rounded-xl border border-stone-200 bg-stone-50 p-6"
							>
								<div class="text-center">
									<div
										class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-slate-800 border-t-transparent"
									></div>
									<p class="text-slate-600">Agents are working on your request...</p>
									<p class="mt-2 text-sm text-slate-500">Results will appear here when ready</p>
									<p class="mt-3 text-xs text-slate-500">
										Switch to Activity Logs to see real-time progress
									</p>
								</div>
							</div>
						{:else}
							<div
								class="flex flex-1 items-center justify-center rounded-xl border border-stone-200 bg-stone-50 p-6"
							>
								<div class="text-center">
									<div class="mb-4 text-4xl text-slate-400">Results</div>
									<p class="text-slate-600">No results yet</p>
									<p class="mt-2 text-sm text-slate-500">
										Start a workflow to see the collaborative results
									</p>
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
