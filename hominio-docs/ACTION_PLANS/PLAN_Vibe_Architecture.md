# ACTION PLAN: Vibe Microservice Architecture

This document outlines the execution plan to refactor the current monolithic KaibanJS application into a distributed, microservice-based architecture centered around a master orchestrator (`hominio-voice`) and specialized, installable teams ("Vibes").

## 1. Deconstruction of the Current State

*   **Problem:** The current application is a monolith. All agents, UI components, and state management are in a single SvelteKit application.
*   **Weak Points:**
    *   **Not Scalable:** Adding new agents or complex logic increases the complexity of the single codebase.
    *   **Not Modular:** Agent logic is tightly coupled with the UI. Reusing agents in other contexts is impossible without significant refactoring.
    *   **Difficult to Maintain:** Changes to one part of the system can have unintended consequences on others.
    *   **Not Extensible:** There is no clear pattern for adding new, independent capabilities. The "marketplace" concept is impossible.

## 2. Engineered Solution: The "Vibe" Architecture

*   **Goal:** A distributed system where specialized AI teams (`Vibes`) operate as standalone microservices, and a central orchestrator (`hominio-voice`) delegates complex tasks to them. The main application (`hominio-os`) serves as the user-facing UI, completely decoupled from the AI business logic.
*   **Core Components:**
    1.  **`hominio-os`:** The primary user interface. Hosts the SvelteKit frontend. It communicates with `hominio-voice`.
    2.  **`hominio-voice`:** The orchestration server. Hosts a master KaibanJS team whose purpose is to understand user intent and delegate tasks to the appropriate `Vibes` using custom tools.
    3.  **`vibe-writing` (and other Vibes):** Standalone SvelteKit applications, each exposing a specific KaibanJS team's functionality via an API. They are the "workers".
    4.  **`hominio-sdk`:** A shared library (package) containing reusable code: UI components, KaibanJS custom tools (`RemoteVibeTool`), type definitions, and utility functions.
*   **Key Principles:**
    *   **Monorepo:** Use `bun` workspaces to manage the four separate packages (`os`, `voice`, `sdk`, `vibe-writing`).
    *   **Service-Oriented Architecture:** Each `Vibe` is a service with a well-defined API.
    *   **Dynamic Installation:** Vibes will be "installable" via a manifest file (`vibe.json`), allowing the orchestrator to discover and use them dynamically.
    *   **SCOPE DEFERRAL:** All functionality related to token counting, cost calculation, and monitoring dashboards is explicitly out of scope for this initial architectural implementation. The focus is solely on establishing the distributed workflow.

## 3. Execution Plan

**STRATEGIC NOTE:** This plan is now inspired by the **Agent2Agent (A2A) protocol**. We are not using the A2A SDK directly, but we are adopting its core principles (SSE streaming, Agent Card discovery) to ensure our architecture is robust, standard, and interoperable.

### Milestone 0: Interface Definition (A2A-Compliant)

*   **1. Vibe Manifest / "Agent Card" (`vibe.json`)**
    *   **Purpose:** To allow a Vibe to be discoverable and "installable" by the orchestrator, inspired by A2A Agent Cards.
    *   **Structure:**
        ```json
        {
          "a2a_version": "0.2.3",
          "name": "vibe-writing",
          "displayName": "Creative Writing & Research Vibe",
          "description": "A specialized AI team for conducting research and writing compelling content, stories, and articles.",
          "transport": {
            "type": "http:sse",
            "endpoint": "/api/execute"
          },
          "version": "1.0.0"
        }
        ```

*   **2. Vibe Execution Interface (A2A-inspired SSE Streaming)**
    *   **Purpose:** A real-time, non-blocking contract for delegating tasks and receiving status updates, using Server-Sent Events (SSE).
    *   **Endpoint:** `GET /api/execute` (The client connects to this endpoint to initiate the SSE stream).
    *   **Initial Request:** The client passes the initial task parameters as query parameters on the GET request.
        *   `GET /api/execute?params={encoded_json_rpc_request}`
    *   **Server Stream Events:** The Vibe will send a stream of JSON objects, each representing an event.
        *   **`event: task_status_update`**
            ```json
            {
              "jsonrpc": "2.0",
              "method": "taskStatusUpdate",
              "params": {
                "id": "xyz-123",
                "status": {
                  "state": "running", 
                  "description": "Research agent has started the investigation.",
                  "timestamp": "2024-03-15T12:01:00Z"
                }
              }
            }
            ```
        *   **`event: task_completed`**
            ```json
            {
              "jsonrpc": "2.0",
              "id": "xyz-123",
              "result": { "status": "COMPLETED", "result": "The A2A protocol is..." }
            }
            ```

### Milestone 1: Foundation - The Bun Monorepo

**Testable Goal:** A fully configured `bun` monorepo where all packages install correctly and can import shared code from the SDK.

*   [x] **Task 1.1: Initialize `bun` Workspace.**
*   [x] **Task 1.2: Define Dependency Catalogs.**
*   [x] **Task 1.3: Populate `hominio-sdk`.**
*   [x] **Task 1.4: Configure Package Dependencies.**
*   [x] **Task 1.5: Test Milestone 1.**

### Milestone 2: The First Vibe - `vibe-writing` Service

This milestone focuses on creating the first standalone, specialized AI service.

*   [ ] **Task 2.1: Define the Vibe's Kaiban Team.**
    *   [ ] Move the existing `researchAgent` and `writerAgent` definitions into `packages/vibe-writing/src/lib/team.js`.
    *   [ ] Create a KaibanJS `Team` instance in that file that uses these agents. The task list will be populated dynamically.

*   [ ] **Task 2.2: Create the API Endpoint.**
    *   [ ] In `packages/vibe-writing`, create a SvelteKit API route: `src/routes/api/execute/+server.js`.
    *   [ ] This endpoint will receive a request with a `task` description and `inputs`.
    *   [ ] It will dynamically create a new `Task` instance, add it to the `vibe-writing` team, execute the team with `team.start()`, and return the final result as a JSON response.

*   [ ] **Task 2.3: Create the Vibe Manifest.**
    *   [ ] Create a `packages/vibe-writing/static/vibe.json` file.
    *   [ ] This manifest will describe the Vibe: `{ "name": "vibe-writing", "displayName": "Creative Writing & Research", "endpoint": "/api/execute", "capabilities": ["research", "storytelling", "content creation"] }`.
    *   [ ] Create a `/api/manifest` endpoint to serve this file.

*   [ ] **Task 2.4: Test the Vibe Service.**
    *   [ ] Run the `vibe-writing` app on its own port.
    *   [ ] Use a tool like `curl` or Postman to send a request to its `/api/execute` endpoint and verify that it correctly runs the agents and returns a result.

### Milestone 3: The Orchestrator - `hominio-voice`

This milestone implements the "brain" of the operation.

*   [ ] **Task 3.1: Define the Orchestration Team.**
    *   [ ] In `packages/hominio-voice/src/lib/team.js`, define the `MasterCoordinatorAgent`.
    *   [ ] This agent's primary tool will be an instance of the `RemoteVibeTool` imported from `hominio-sdk`.

*   [ ] **Task 3.2: Implement Dynamic Tool Loading.**
    *   [ ] The `hominio-voice` server will have a configuration of available Vibes (e.g., in a `.env` file or a config file).
    *   [ ] On startup, it will fetch the `vibe.json` from each configured Vibe URL.
    *   [ ] It will dynamically create an instance of `RemoteVibeTool` for each available Vibe and add it to the `MasterCoordinatorAgent`.

*   [ ] **Task 3.3: Create the Orchestration Endpoint.**
    *   [ ] Create an API endpoint `packages/hominio-voice/src/routes/api/orchestrate/+server.js`.
    *   [ ] This endpoint receives a high-level user prompt.
    *   [ ] It runs the `hominio-voice` team, which uses the `MasterCoordinatorAgent` to analyze the prompt and delegate to the appropriate `RemoteVibeTool` (e.g., `vibe-writing`).
    *   [ ] It will stream progress back to the caller and return the final result.

### Milestone 4: The UI Host - `hominio-os`

This milestone focuses on creating the user-facing application, which is now decoupled from the core logic.

*   [ ] **Task 4.1: Refactor the UI.**
    *   [ ] The main page of `hominio-os` will be the user interface.
    *   [ ] It should be a clean Svelte component that takes a user prompt.
    *   [ ] Remove all KaibanJS agent/team definitions from this application.

*   [ ] **Task 4.2: Connect UI to Orchestrator.**
    *   [ ] When the user submits a prompt, the `hominio-os` frontend will make an API call to the `hominio-voice` server's `/api/orchestrate` endpoint.
    *   [ ] It will receive and display the streamed progress and final results.

*   [ ] **Task 4.3: Integrate SDK Components.**
    *   [ ] Import and use the reusable UI components (e.g., `VibeCard.svelte`) from `hominio-sdk` to display information about the available Vibes.

### Milestone 5: Integration & End-to-End Test

*   [ ] **Task 5.1: Configure Environment.**
    *   [ ] Use `.env` files in each package to manage ports and URLs for communication between services.
    *   **NOTE:** Service-to-service authentication is deferred for this initial implementation to focus on core data flow.

*   [ ] **Task 5.2: Full Workflow Test.**
    *   [ ] Run all three applications (`hominio-os`, `hominio-voice`, `vibe-writing`) concurrently on different ports.
    *   [ ] Perform an end-to-end test: Type a prompt into the `hominio-os` UI and verify that the request flows through `hominio-voice` to `vibe-writing` and the final result is displayed correctly.
    *   [ ] Verify that logs in each service show the correct flow of information, including a shared `intentId`.

*   **3. UI to Orchestrator Communication**
    *   **NOTE:** To relay the real-time updates from the Vibe to the end-user, the connection between `hominio-os` and `hominio-voice` must also be real-time (e.g., using WebSockets). This will be implemented in a later milestone. 