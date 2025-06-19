// This file centralizes the A2A-inspired protocol data structures.
// It is the single source of truth for the communication contract between services.

/**
 * The TaskState Enum, inspired by A2A.
 * We will start with a subset.
 */
export const TaskState = {
	RUNNING: 'running',
	COMPLETED: 'completed',
	NEEDS_HUMAN_INPUT: 'input_required',
	ERROR: 'error'
};

/**
 * Base JSON-RPC 2.0 Request Structure.
 */
export class JSONRPCRequest {
	jsonrpc = '2.0';
	id;
	method;
	params;

	constructor(id, method, params) {
		this.id = id;
		this.method = method;
		this.params = params;
	}
}

/**
 * Base JSON-RPC 2.0 Response Structure.
 */
export class JSONRPCResponse {
	jsonrpc = '2.0';
	id;
	result;
	error;

	constructor(id, { result, error }) {
		this.id = id;
		this.result = result;
		this.error = error;
	}
}
