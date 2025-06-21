# Action Plan: Conversational AI Integration

This document outlines the plan to integrate a streaming Large Language Model (LLM) between the existing Speech-to-Text (STT) and Text-to-Speech (TTS) services, creating a complete, low-latency conversational AI loop.

## Milestone 1: Backend LLM Foundation

The first step is to establish the technical foundation for communicating with the external LLM provider.

- [ ] **Task 1.1: Add OpenAI Dependency**
  - `file`: `packages/hominio-voice/requirements.txt`
  - `action`: Add the `openai` library to the list of dependencies. This allows us to use the OpenAI-compatible client for the RedPill API.

- [ ] **Task 1.2: Initialize LLM Client**
  - `file`: `packages/hominio-voice/main.py`
  - `action`: In the `lifespan` context manager, initialize the `openai.AsyncOpenAI` client.
  - `details`:
    - The client must be configured with `api_key=os.getenv("REDPILL_API_KEY")`.
    - The `base_url` must be set to `https://api.redpill.ai/v1`.
    - Store the client instance in a global variable, e.g., `llm_client`.

## Milestone 2: Backend Orchestration & Logic

This is the core of the integration, where we chain all the services together.

- [ ] **Task 2.1: Refactor TTS WebSocket Endpoint**
  - `file`: `packages/hominio-voice/main.py`
  - `action`: Modify the `/ws/tts` endpoint. It should no longer expect to receive text from the client.
  - `details`:
    - Create a global variable `active_tts_ws: WebSocket = None`.
    - When a client connects to `/ws/tts`, store the `websocket` object in `active_tts_ws`.
    - When the client disconnects, set `active_tts_ws` back to `None`.
    - This turns the endpoint into a simple, stateful push channel for the server to send audio.

- [ ] **Task 2.2: Implement the Conversational Chain**
  - `file`: `packages/hominio-voice/main.py`
  - `action`: The logic will be implemented inside the `process_full_sentence` function, which is the callback for a completed STT transcription.
  - `details`:
    1.  When `process_full_sentence` is called with the user's transcribed text, it will invoke a new async generator function `get_llm_response(text)`.
    2.  `get_llm_response` will use the `llm_client` to call `chat.completions.create(model="phala/qwen-2.5-7b-instruct", messages=[...], stream=True)`. It will `yield` the text content from each chunk of the response.
    3.  A new `TextToAudioStream` will be instantiated using the existing `kokoro_engine`.
    4.  The stream will be configured with an `on_audio_chunk` callback. This callback's sole purpose is to send the received `chunk` over the `active_tts_ws` WebSocket, if it's connected.
    5.  The text generator from the LLM will be fed into the TTS stream: `tts_stream.feed(get_llm_response(text))`.
    6.  The stream will be started non-blockingly and muted: `tts_stream.play_async(muted=True)`. This is critical, as we only want to get the audio chunks, not play them on the server.

## Milestone 3: Deployment and Validation

Once the backend logic is in place, we will deploy and test the end-to-end functionality.

- [ ] **Task 3.1: Deploy the Application**
  - `action`: Run `fly deploy` to push the new container with the updated code and dependencies.
  - `verification`: Ensure the application starts without errors and that the `REDPILL_API_KEY` is correctly picked up.

- [ ] **Task 3.2: End-to-End Test**
  - `action`: Open the web interface. Hold to record and speak a sentence.
  - `expected result`:
    1.  Your speech is transcribed in real-time (gray text).
    2.  The final transcription appears (black text).
    3.  After a short pause (for LLM processing), you should hear the synthesized voice of the AI's response playing back automatically.
    4.  The process should feel fluid and conversational. 