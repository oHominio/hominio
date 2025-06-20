import { Agent } from 'kaibanjs';
import { SECRET_RED_PILL_API_KEY, SECRET_RED_PILL_BASE_URL } from '$env/static/private';

// A simple placeholder tool to match the reference implementation
class KnowledgeBaseTool {
	constructor() {
		this.name = 'knowledge_base_search';
		this.description = 'Search the knowledge base for information on various topics';
	}
	async invoke(query) {
		return `Placeholder knowledge for "${query}"`;
	}
}

export function createResearchAgent() {
	const knowledgeBaseTool = new KnowledgeBaseTool();

	return new Agent({
		name: 'Research Agent',
		role: 'Information Researcher',
		goal: 'Conduct thorough research and provide comprehensive insights',
		background: `Experienced researcher with expertise in analyzing trends and gathering insights. 
You must formulate your final answer based *only* on the information you've gathered with your available tools. 
Do not attempt to use any other tools.`,
		tools: [knowledgeBaseTool],
		llmConfig: {
			provider: 'openai',
			model: 'phala/qwen-2.5-7b-instruct',
			configuration: {
				apiKey: SECRET_RED_PILL_API_KEY,
				baseURL: SECRET_RED_PILL_BASE_URL,
				temperature: 0.7,
				maxTokens: 2000,
				maxRetries: 2
			}
		},
		maxIterations: 3,
		forceFinalAnswer: true
	});
}

export function createWriterAgent() {
	const knowledgeBaseTool = new KnowledgeBaseTool();

	return new Agent({
		name: 'Storytelling Agent',
		role: 'Master Storyteller & Emotional Content Creator',
		goal: 'Transform research findings into captivating, emotionally resonant stories',
		background: 'A master storyteller who weaves data into compelling narratives.',
		tools: [knowledgeBaseTool],
		llmConfig: {
			provider: 'openai',
			model: 'phala/deepseek-r1-70b',
			configuration: {
				apiKey: SECRET_RED_PILL_API_KEY,
				baseURL: SECRET_RED_PILL_BASE_URL,
				temperature: 0.9,
				maxTokens: 3500,
				maxRetries: 2
			}
		},
		maxIterations: 2,
		forceFinalAnswer: true
	});
}

// Deprecated: Keep for backward compatibility, but these should not be used for concurrent requests
const knowledgeBaseTool = new KnowledgeBaseTool();

export const researchAgent = new Agent({
	name: 'Research Agent',
	role: 'Information Researcher',
	goal: 'Conduct thorough research and provide comprehensive insights',
	background: `Experienced researcher with expertise in analyzing trends and gathering insights. 
You must formulate your final answer based *only* on the information you've gathered with your available tools. 
Do not attempt to use any other tools.`,
	tools: [knowledgeBaseTool],
	llmConfig: {
		provider: 'openai',
		model: 'phala/qwen-2.5-7b-instruct',
		configuration: {
			apiKey: SECRET_RED_PILL_API_KEY,
			baseURL: SECRET_RED_PILL_BASE_URL,
			temperature: 0.7,
			maxTokens: 2000,
			maxRetries: 2
		}
	},
	maxIterations: 3,
	forceFinalAnswer: true
});

export const writerAgent = new Agent({
	name: 'Storytelling Agent',
	role: 'Master Storyteller & Emotional Content Creator',
	goal: 'Transform research findings into captivating, emotionally resonant stories',
	background: 'A master storyteller who weaves data into compelling narratives.',
	tools: [knowledgeBaseTool],
	llmConfig: {
		provider: 'openai',
		model: 'phala/deepseek-r1-70b',
		configuration: {
			apiKey: SECRET_RED_PILL_API_KEY,
			baseURL: SECRET_RED_PILL_BASE_URL,
			temperature: 0.9,
			maxTokens: 3500,
			maxRetries: 2
		}
	},
	maxIterations: 2,
	forceFinalAnswer: true
});
