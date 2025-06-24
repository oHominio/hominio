# speech_pipeline.py - Adapted Complex Speech Pipeline Manager for Hominio Voice
from typing import Optional, Callable
import threading
import logging
import time
import asyncio
from queue import Queue, Empty
import sys

# Import our adapted services
from .tts_service import TTSService
from .llm_service import LLMService
from .text_context import TextContext
from .text_similarity import TextSimilarity
from core.config import Config

# (Logging setup)
logger = logging.getLogger(__name__)

class PipelineRequest:
    """
    Represents a request to be processed by the SpeechPipeline's request queue.
    Adapted for Hominio Voice architecture.
    """
    def __init__(self, action: str, data: Optional[any] = None):
        self.action = action
        self.data = data
        self.timestamp = time.time()

class RunningGeneration:
    """
    Holds the state and resources for a single, ongoing text-to-speech generation process.
    Adapted for Hominio Voice with WebSocket streaming.
    """
    def __init__(self, id: int):
        self.id: int = id
        self.text: Optional[str] = None
        self.timestamp = time.time()

        self.llm_generator = None
        self.llm_finished: bool = False
        self.llm_finished_event = threading.Event()
        self.llm_aborted: bool = False

        self.quick_answer: str = ""
        self.quick_answer_provided: bool = False
        self.quick_answer_first_chunk_ready: bool = False
        self.quick_answer_overhang: str = ""  # Text after the quick answer boundary
        self.tts_quick_started: bool = False

        self.tts_quick_allowed_event = threading.Event()
        self.audio_chunks = Queue()  # For WebSocket streaming
        self.audio_quick_finished: bool = False
        self.audio_quick_aborted: bool = False
        self.tts_quick_finished_event = threading.Event()

        self.abortion_started: bool = False

        self.tts_final_finished_event = threading.Event()
        self.tts_final_started: bool = False
        self.audio_final_aborted: bool = False
        self.audio_final_finished: bool = False
        self.final_answer: str = ""
        self.final_answer_chunks = Queue() # New queue for final answer text
        self.final_answer_llm_finished = threading.Event() # Event to signal LLM is done

        self.completed: bool = False

class SpeechPipeline:
    """
    Complex Speech Pipeline Manager adapted for Hominio Voice.
    Orchestrates the full text-to-speech pipeline with sophisticated threading,
    worker management, and WebSocket integration.
    """
    def __init__(self):
        # Hominio Voice service references (injected by main)
        self.tts_service: Optional[TTSService] = None
        self.llm_service: Optional[LLMService] = None
        self.stt_service = None
        self.message_router = None
        
        # WebSocket callback for streaming audio chunks
        self.websocket_send_callback: Optional[Callable] = None
        
        # Pipeline components
        self.text_context = TextContext()
        self.text_similarity = TextSimilarity(focus='end', n_words=5)
        self.generation_counter: int = 0
        self.abort_lock = threading.Lock()

        # State
        self.history = []
        self.requests_queue = Queue()
        self.running_generation: Optional[RunningGeneration] = None

        # Threading Events
        self.shutdown_event = threading.Event()
        self.generator_ready_event = threading.Event()
        self.llm_answer_ready_event = threading.Event()
        self.stop_everything_event = threading.Event()
        self.stop_llm_request_event = threading.Event()
        self.stop_llm_finished_event = threading.Event()
        self.stop_tts_quick_request_event = threading.Event()
        self.stop_tts_quick_finished_event = threading.Event()
        self.stop_tts_final_request_event = threading.Event()
        self.stop_tts_final_finished_event = threading.Event()
        self.abort_completed_event = threading.Event()
        self.abort_block_event = threading.Event()
        self.abort_block_event.set()
        self.check_abort_lock = threading.Lock()

        # State Flags
        self.llm_generation_active = False
        self.tts_quick_generation_active = False
        self.tts_final_generation_active = False
        self.previous_request = None



        # Worker Threads
        self.request_processing_thread = threading.Thread(target=self._request_processing_worker, name="RequestProcessingThread", daemon=True)
        self.llm_inference_thread = threading.Thread(target=self._llm_inference_worker, name="LLMProcessingThread", daemon=True)
        self.tts_quick_inference_thread = threading.Thread(target=self._tts_quick_inference_worker, name="TTSQuickProcessingThread", daemon=True)
        self.tts_final_inference_thread = threading.Thread(target=self._tts_final_inference_worker, name="TTSFinalProcessingThread", daemon=True)

        # Start worker threads
        self.request_processing_thread.start()
        self.llm_inference_thread.start()
        self.tts_quick_inference_thread.start()
        self.tts_final_inference_thread.start()

        self.on_partial_assistant_text: Optional[Callable[[str], None]] = None

        logger.info("✅ [Pipeline] Complex Speech Pipeline Manager initialized with worker threads")

    def set_services(self, stt_service, tts_service, llm_service):
        """Set Hominio Voice service references"""
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.llm_service = llm_service
        
        # Set up STT callbacks for pipeline orchestration
        if self.stt_service:
            self.stt_service.set_callbacks(
                on_full_sentence=self._handle_full_sentence_from_stt,
                on_realtime_transcription=self._handle_realtime_transcription,
                on_vad_interruption=self._handle_vad_interruption  # NEW: VAD interruption
            )
        
        logger.info("✅ [Pipeline] Hominio Voice services connected to complex pipeline")

    def set_message_router(self, router):
        """Set message router reference for WebSocket communication"""
        self.message_router = router
        logger.info("✅ [Pipeline] Message router connected to complex pipeline")

    def set_websocket_callback(self, callback: Callable):
        """Set WebSocket send callback for audio streaming (called per connection)"""
        self.websocket_send_callback = callback
        logger.info("✅ [Pipeline] WebSocket callback set for audio streaming")

    async def _handle_full_sentence_from_stt(self, text: str):
        """Handle full sentence from STT -> trigger pipeline preparation"""
        logger.info(f"🎤 [Pipeline] Full sentence from STT: '{text}'")
        
        # Send to WebSocket via message router
        if self.message_router:
            await self.message_router.send_websocket_message({
                'type': 'fullSentence',
                'text': text
            })
        
        # Trigger pipeline preparation (this is the key integration point)
        self.prepare_generation(text)

    def _handle_realtime_transcription(self, text: str):
        """Handle realtime transcription from STT"""
        logger.debug(f"🔄 [Pipeline] Realtime transcription: '{text}'")
        
        # Send via message router
        if self.message_router:
            asyncio.run_coroutine_threadsafe(
                self.message_router.send_websocket_message({
                    'type': 'realtime',
                    'text': text
                }),
                self.message_router.event_loop
            )

    def _handle_vad_interruption(self, interruption_type: str):
        """Handle VAD interruption - CRITICAL: Immediately abort TTS synthesis and clear audio caches"""
        logger.info(f"🎤🛑 [Pipeline] VAD interruption received: {interruption_type}")
        
        if interruption_type == "vad_interruption_start":
            # IMMEDIATE abort with cache clearing
            logger.info("🎤🛑 [Pipeline] IMMEDIATE TTS abort triggered by VAD detection")
            
            # Clear ALL audio caches in running generation
            if self.running_generation:
                try:
                    # Clear audio chunk queues
                    while not self.running_generation.audio_chunks.empty():
                        try:
                            self.running_generation.audio_chunks.get_nowait()
                        except:
                            break
                    
                    # Clear final answer chunks
                    while not self.running_generation.final_answer_chunks.empty():
                        try:
                            self.running_generation.final_answer_chunks.get_nowait()
                        except:
                            break
                    
                    logger.info(f"🎤🧹 [Pipeline] [Gen {self.running_generation.id}] Audio caches cleared")
                except Exception as e:
                    logger.error(f"❌ [Pipeline] Error clearing audio caches: {e}")
            
            # Trigger immediate abort
            self.abort_generation(wait_for_completion=False, reason="VAD_interruption")
            
            # Clear TTS service audio caches
            if self.tts_service and hasattr(self.tts_service, 'clear_audio_caches'):
                try:
                    success = self.tts_service.clear_audio_caches()
                    if success:
                        logger.info("🔊🧹 [Pipeline] TTS service audio caches cleared")
                    else:
                        logger.warning("🔊⚠️ [Pipeline] TTS service cache clearing failed")
                except Exception as e:
                    logger.error(f"❌ [Pipeline] Error clearing TTS caches: {e}")
            
            # Send frontend clear signal through message router
            if self.message_router:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.message_router.send_websocket_message({
                            'type': 'clear_audio_buffers',
                            'reason': 'vad_interruption',
                            'timestamp': time.time()
                        }),
                        self.message_router.event_loop
                    )
                except Exception as e:
                    logger.error(f"❌ [Pipeline] Error sending clear audio signal: {e}")

    async def handle_message(self, message_data):
        """Handle messages routed from message router"""
        message_type = message_data.get("type")
        
        if message_type == "stt-command":
            command = message_data.get("command")
            if command == "stop":
                logger.info("🗣️🛑 [Pipeline] Received 'stop' command, initiating abort.")
                self.abort_generation(wait_for_completion=False, reason="stt-command stop")

        elif message_type == "vad_detect_start":
            # Handle basic VAD detection start through message router
            logger.info("🎤🔍 [Pipeline] VAD detection start received through message router")
            # Don't interrupt immediately - wait for intelligent analysis

        elif message_type == "intelligent_interrupt":
            # NEW: Handle intelligent TurnDetection-based interruption
            reason = message_data.get("reason", "unknown")
            confidence = message_data.get("confidence", 0.0)
            logger.info(f"🎤🧠 [Pipeline] INTELLIGENT INTERRUPT: {reason} (confidence: {confidence:.2f}s)")
            self._handle_vad_interruption(f"intelligent_interruption_{reason}")

        elif message_type == "stop-streaming":
            self.abort_generation(wait_for_completion=False, reason="stop-streaming message")
        elif message_type == "ping":
            if self.message_router:
                await self.message_router.send_websocket_message({
                    "type": "pong",
                    "timestamp": message_data.get("timestamp")
                })
        # Add other message handling as needed

    def is_valid_gen(self) -> bool:
        """Check if there is a currently running generation that has not started aborting"""
        return self.running_generation is not None and not self.running_generation.abortion_started

    def _request_processing_worker(self):
        """Worker thread that processes requests from the requests_queue"""
        logger.info("🗣️🚀 [Pipeline] Request Processor: Starting...")
        while not self.shutdown_event.is_set():
            try:
                request = self.requests_queue.get(block=True, timeout=1)

                if self.previous_request:
                    if self.previous_request.data == request.data and isinstance(request.data, str):
                        if request.timestamp - self.previous_request.timestamp < 2:
                            logger.info(f"🗣️🗑️ [Pipeline] Skipping duplicate request - {request.action}")
                            continue

                # Drain queue to get most recent request
                while not self.requests_queue.empty():
                    skipped_request = self.requests_queue.get(False)
                    logger.debug(f"🗣️🗑️ [Pipeline] Skipping older request - {skipped_request.action}")
                    request = skipped_request

                self.abort_block_event.wait()
                logger.debug(f"🗣️🔄 [Pipeline] Processing request - {request.action}")
                
                if request.action == "prepare":
                    self.process_prepare_generation(request.data)
                    self.previous_request = request
                elif request.action == "finish":
                    logger.info(f"🗣️🤷 [Pipeline] Received 'finish' action")
                    self.previous_request = request
                else:
                    logger.warning(f"🗣️❓ [Pipeline] Unknown action '{request.action}'")

            except Empty:
                continue
            except Exception as e:
                logger.exception(f"🗣️💥 [Pipeline] Request Processor Error: {e}")
        logger.info("🗣️🏁 [Pipeline] Request Processor: Shutting down.")

    def on_first_audio_chunk_synthesize(self):
        """Callback when first TTS audio chunk is ready"""
        logger.info("🗣️🎶 [Pipeline] First audio chunk synthesized")
        if self.running_generation:
            self.running_generation.quick_answer_first_chunk_ready = True

    def preprocess_chunk(self, chunk: str) -> str:
        """Preprocess text chunk before TTS"""
        return chunk.replace("—", "-").replace(""", '"').replace(""", '"').replace("'", "'").replace("'", "'").replace("…", "...")

    def _llm_inference_worker(self):
        """Worker thread that handles LLM inference for a generation."""
        logger.info("🗣️🧠 [Pipeline] LLM Worker: Starting...")
        while not self.shutdown_event.is_set():
            self.generator_ready_event.wait(timeout=1.0)
            if not self.generator_ready_event.is_set():
                continue

            current_gen = self.running_generation
            if not current_gen:
                self.generator_ready_event.clear()
                continue
            
            gen_id = current_gen.id
            logger.info(f"🗣️🧠🔄 [Pipeline] [Gen {gen_id}] LLM worker processing generation...")

            try:
                # This is an async generator, we need to run it in a sync context
                accumulated_text = ""  # Move this to outer scope
                
                async def process_generator():
                    nonlocal accumulated_text  # Access outer scope variable
                    # The LLM generator is async, so we iterate it asynchronously
                    async for chunk in current_gen.llm_generator:
                        if self.stop_llm_request_event.is_set():
                            logger.info(f"🗣️🧠❌ [Pipeline] [Gen {gen_id}] LLM worker stop request detected.")
                            current_gen.llm_aborted = True
                            break

                        if not current_gen.quick_answer_provided:
                            # Phase 1: We are still looking for the end of the first sentence.
                            accumulated_text += chunk
                            context, overhang = self.text_context.get_context(accumulated_text)
                            if context:
                                # First sentence found!
                                logger.info(f"🗣️🧠✔️ [Pipeline] [Gen {gen_id}] Quick answer found. Context: '{context}', Overhang: '{overhang}'")
                                current_gen.quick_answer = context
                                current_gen.quick_answer_provided = True
                                self.llm_answer_ready_event.set() # Signal the quick TTS worker

                                # If there was text after the sentence end, store it as overhang for final TTS
                                if overhang:
                                    logger.info(f"🗣️🧠📬 [Pipeline] [Gen {gen_id}] Storing overhang '{overhang}' for final TTS.")
                                    current_gen.quick_answer_overhang = overhang
                        else:
                            # Phase 2: Quick answer is now found, all subsequent chunks go to the final answer queue.
                            logger.info(f"🗣️🧠📬 [Pipeline] [Gen {gen_id}] Putting final chunk '{chunk}' into queue.")
                            current_gen.final_answer_chunks.put(chunk)

                # We need an event loop to run our async `process_generator` function
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(process_generator())
                
                # This code runs after the generator is fully consumed
                if not current_gen.llm_aborted:
                    if not current_gen.quick_answer_provided:
                        # This handles cases where the entire LLM response is very short and has no sentence break.
                        # We treat the whole thing as the "quick answer".
                        logger.info(f"🗣️🧠✔️ [Pipeline] [Gen {gen_id}] No context boundary found, using full response as quick answer.")
                        current_gen.quick_answer = accumulated_text
                        current_gen.quick_answer_provided = True
                        self.llm_answer_ready_event.set()
                    
                    # Signal that LLM is completely finished
                    logger.info(f"🗣️🧠🏁 [Pipeline] [Gen {gen_id}] LLM generation completed, signaling final answer finished.")
                    current_gen.final_answer_llm_finished.set()

            except Exception as e:
                logger.exception(f"🗣️🧠💥 [Pipeline] [Gen {gen_id}] LLM worker error: {e}")
                current_gen.llm_aborted = True
            finally:
                # This block runs whether the try succeeded or failed
                if current_gen:
                    logger.info(f"🗣️🧠🏁 [Pipeline] [Gen {gen_id}] LLM worker finished processing.")
                    current_gen.llm_finished_event.set() # Signal that the LLM is done
                    # Always signal final answer queue processing to stop
                    current_gen.final_answer_llm_finished.set()
                
                # Clear the event so we wait for the next generation
                self.generator_ready_event.clear()

    def check_abort(self, txt: str, wait_for_finish: bool = True, abort_reason: str = "unknown") -> bool:
        """Check if current generation should be aborted based on new input text"""
        with self.check_abort_lock:
            if self.running_generation:
                current_gen_id_str = f"Gen {self.running_generation.id}"
                logger.info(f"🗣️🛑❓ [Pipeline] {current_gen_id_str} Abort check (reason: {abort_reason})")

                if self.running_generation.abortion_started:
                    logger.info(f"🗣️🛑⏳ [Pipeline] {current_gen_id_str} Already aborting")
                    if wait_for_finish:
                        completed = self.abort_completed_event.wait(timeout=5.0)
                        if not completed:
                            logger.error(f"🗣️🛑💥 [Pipeline] {current_gen_id_str} Timeout waiting for abort")
                            self.running_generation = None
                        else:
                            logger.info(f"🗣️🛑✅ [Pipeline] {current_gen_id_str} Abort completed")
                    return True
                else:
                    # Check similarity
                    try:
                        if self.running_generation.text is None:
                            similarity = 0.0
                        else:
                            similarity = self.text_similarity.calculate_similarity(self.running_generation.text, txt)
                    except Exception as e:
                        logger.warning(f"🗣️🛑💥 [Pipeline] {current_gen_id_str} Similarity error: {e}")
                        similarity = 0.0

                    if similarity >= 0.95:
                        logger.info(f"🗣️🛑🙅 [Pipeline] {current_gen_id_str} Too similar ({similarity:.2f}), ignoring")
                        return False

                    # Different enough, initiate abort
                    logger.info(f"🗣️🛑🚀 [Pipeline] {current_gen_id_str} Different enough ({similarity:.2f}), aborting")
                    self.abort_generation(wait_for_completion=wait_for_finish, timeout=7.0, reason=f"check_abort ({abort_reason})")
                    return True
            else:
                logger.info("🗣️🛑🤷 [Pipeline] No active generation to abort")
                return False

    def _tts_quick_inference_worker(self):
        """Worker thread that handles TTS synthesis for quick answer using Hominio Voice TTSService"""
        logger.info("🗣️👄🚀 [Pipeline] Quick TTS Worker: Starting...")
        while not self.shutdown_event.is_set():
            ready = self.llm_answer_ready_event.wait(timeout=1.0)
            if not ready:
                continue

            if self.stop_tts_quick_request_event.is_set():
                logger.info("🗣️👄❌ [Pipeline] Quick TTS Worker: Abort detected")
                self.stop_tts_quick_request_event.clear()
                self.stop_tts_quick_finished_event.set()
                self.tts_quick_generation_active = False
                continue

            self.llm_answer_ready_event.clear()
            current_gen = self.running_generation

            if not current_gen or not current_gen.quick_answer:
                logger.warning("🗣️👄❓ [Pipeline] Quick TTS Worker: No valid generation")
                self.tts_quick_generation_active = False
                continue

            if current_gen.audio_quick_aborted or current_gen.abortion_started:
                logger.info(f"🗣️👄❌ [Pipeline] [Gen {current_gen.id}] Already aborted")
                continue

            gen_id = current_gen.id
            logger.info(f"🗣️👄🔄 [Pipeline] [Gen {gen_id}] Processing quick TTS...")

            self.tts_quick_generation_active = True
            self.stop_tts_quick_finished_event.clear()
            current_gen.tts_quick_finished_event.clear()
            current_gen.tts_quick_started = True

            try:
                if self.stop_tts_quick_request_event.is_set() or current_gen.abortion_started:
                    logger.info(f"🗣️👄❌ [Pipeline] [Gen {gen_id}] Aborting TTS synthesis")
                    current_gen.audio_quick_aborted = True
                else:
                    logger.info(f"🗣️👄🎶 [Pipeline] [Gen {gen_id}] Synthesizing: '{current_gen.quick_answer[:50]}...'")
                    
                    # Use Hominio Voice TTS service for synthesis
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    try:
                        loop.run_until_complete(
                            self.tts_service.synthesize_text_streaming(current_gen.quick_answer, None)
                        )
                        logger.info(f"🗣️👄✅ [Pipeline] [Gen {gen_id}] Quick TTS completed")
                    except Exception as tts_e:
                        logger.error(f"🗣️👄💥 [Pipeline] [Gen {gen_id}] TTS error: {tts_e}")
                        current_gen.audio_quick_aborted = True

            except Exception as e:
                logger.exception(f"🗣️👄💥 [Pipeline] [Gen {gen_id}] Quick TTS Worker Error: {e}")
                current_gen.audio_quick_aborted = True
            finally:
                self.tts_quick_generation_active = False
                self.stop_tts_quick_finished_event.set()
                logger.info(f"🗣️👄🏁 [Pipeline] [Gen {gen_id}] Quick TTS Worker finished")

                if current_gen.audio_quick_aborted or self.stop_tts_quick_request_event.is_set():
                    logger.info(f"🗣️👄❌ [Pipeline] [Gen {gen_id}] Quick TTS Aborted")
                    self.stop_tts_quick_request_event.clear()
                    current_gen.audio_quick_aborted = True
                else:
                    logger.info(f"🗣️👄✅ [Pipeline] [Gen {gen_id}] Quick TTS Success")
                    current_gen.tts_quick_finished_event.set()

                current_gen.audio_quick_finished = True

    def _tts_final_inference_worker(self):
        """Worker thread that handles TTS synthesis for final answer - STREAMING FIX"""
        logger.info("🗣️👄🚀 [Pipeline] Final TTS Worker: Starting...")
        while not self.shutdown_event.is_set():
            current_gen = self.running_generation
            time.sleep(0.01)  # Prevent tight spinning when idle

            # --- Wait for prerequisites - FIXED: Don't wait for quick TTS to finish! ---
            if not current_gen: continue  # No active generation
            if current_gen.tts_final_started: continue  # Final TTS already running for this gen
            if not current_gen.quick_answer_provided: continue  # Wait for quick answer to be found
            # REMOVED: if not current_gen.audio_quick_finished: continue  # Don't wait for quick TTS to finish!

            gen_id = current_gen.id

            # --- Check conditions to *start* final TTS ---
            if current_gen.audio_quick_aborted:
                continue
            if not current_gen.quick_answer_provided:
                logger.debug(f"🗣️👄🙅 [Pipeline] [Gen {gen_id}] Quick answer boundary was not found, skipping final TTS")
                continue
            if current_gen.abortion_started:
                logger.debug(f"🗣️👄🙅 [Pipeline] [Gen {gen_id}] Generation is aborting, skipping final TTS")
                continue

            # --- Conditions met, start final TTS - STREAMING MODE ---
            logger.info(f"🗣️👄🔄 [Pipeline] [Gen {gen_id}] Final TTS Worker: Starting STREAMING final TTS...")

            # Set state for active generation
            self.tts_final_generation_active = True
            self.stop_tts_final_finished_event.clear()
            current_gen.tts_final_started = True
            current_gen.tts_final_finished_event.clear()

            try:
                # STREAMING APPROACH: Synthesize chunks as they come in, don't wait for all text
                logger.info(f"🗣️👄🎶 [Pipeline] [Gen {gen_id}] Starting STREAMING final TTS synthesis...")
                
                # Create async synthesis function that processes chunks in real-time
                async def stream_final_synthesis():
                    """Stream TTS synthesis as chunks become available"""
                    
                    # First, handle overhang if any
                    if current_gen.quick_answer_overhang:
                        preprocessed_overhang = self.preprocess_chunk(current_gen.quick_answer_overhang)
                        logger.info(f"🗣️👄🎶 [Pipeline] [Gen {gen_id}] Synthesizing overhang: '{preprocessed_overhang[:30]}...'")
                        current_gen.final_answer += preprocessed_overhang
                        
                        # Synthesize overhang immediately
                        await self.tts_service.synthesize_text_streaming(preprocessed_overhang, None)
                    
                    # Then, process chunks as they arrive from LLM
                    accumulated_chunk = ""
                    chunk_count = 0
                    
                    while not current_gen.final_answer_llm_finished.is_set() or not current_gen.final_answer_chunks.empty():
                        # Check for stop request
                        if self.stop_tts_final_request_event.is_set():
                            logger.info(f"🗣️👄❌ [Pipeline] [Gen {gen_id}] Final TTS streaming stopped by request.")
                            current_gen.audio_final_aborted = True
                            break
                        
                        try:
                            # Get next chunk with short timeout
                            chunk = current_gen.final_answer_chunks.get(timeout=0.1)
                            preprocessed_chunk = self.preprocess_chunk(chunk)
                            accumulated_chunk += preprocessed_chunk
                            current_gen.final_answer += preprocessed_chunk
                            chunk_count += 1
                            
                            # Stream synthesis every few chunks or on sentence boundaries
                            should_synthesize = (
                                len(accumulated_chunk) > 50 or  # Every ~50 characters
                                any(punct in preprocessed_chunk for punct in ['.', '!', '?', ',']) or  # Sentence boundaries
                                current_gen.final_answer_llm_finished.is_set()  # LLM finished
                            )
                            
                            if should_synthesize and accumulated_chunk.strip():
                                logger.info(f"🗣️👄🎶 [Pipeline] [Gen {gen_id}] Streaming chunk {chunk_count}: '{accumulated_chunk[:30]}...'")
                                await self.tts_service.synthesize_text_streaming(accumulated_chunk, None)
                                accumulated_chunk = ""  # Reset for next batch
                                
                        except Empty:
                            # No chunk available, continue waiting
                            continue
                        except Exception as e:
                            logger.error(f"🗣️👄💥 [Pipeline] [Gen {gen_id}] Error in streaming synthesis: {e}")
                            break
                    
                    # Synthesize any remaining accumulated text
                    if accumulated_chunk.strip():
                        logger.info(f"🗣️👄🎶 [Pipeline] [Gen {gen_id}] Final streaming chunk: '{accumulated_chunk[:30]}...'")
                        await self.tts_service.synthesize_text_streaming(accumulated_chunk, None)
                    
                    logger.info(f"🗣️👄✅ [Pipeline] [Gen {gen_id}] Streaming final TTS completed - processed {chunk_count} chunks")

                # Run streaming synthesis
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(stream_final_synthesis())
                
                logger.info(f"🗣️👄✅ [Pipeline] [Gen {gen_id}] Final TTS completed")
            except Exception as e:
                logger.exception(f"🗣️👄💥 [Pipeline] [Gen {gen_id}] Final TTS Worker Error: {e}")
                current_gen.audio_final_aborted = True
            finally:
                # Clean up state regardless of how the try block exited
                self.tts_final_generation_active = False
                self.stop_tts_final_finished_event.set()
                logger.info(f"🗣️👄🏁 [Pipeline] [Gen {gen_id}] Final TTS Worker finished processing cycle")

                # Check if synthesis completed naturally or was stopped
                if current_gen.audio_final_aborted or self.stop_tts_final_request_event.is_set():
                    logger.info(f"🗣️👄❌ [Pipeline] [Gen {gen_id}] Final TTS Marked as Aborted/Incomplete")
                    self.stop_tts_final_request_event.clear()
                    current_gen.audio_final_aborted = True
                else:
                    logger.info(f"🗣️👄✅ [Pipeline] [Gen {gen_id}] Final TTS Finished Successfully")
                    current_gen.tts_final_finished_event.set()

                current_gen.audio_final_finished = True

    def process_prepare_generation(self, txt: str):
        """Handle 'prepare' action: initiate new text-to-speech generation"""
        id_in_spec = self.generation_counter + 1
        aborted = self.check_abort(txt, wait_for_finish=True, abort_reason=f"process_prepare_generation for new id {id_in_spec}")

        self.generation_counter += 1
        new_gen_id = self.generation_counter
        logger.info(f"🗣️✨🔄 [Pipeline] [Gen {new_gen_id}] Preparing generation for: '{txt[:50]}...'")

        # Reset flags and events
        logger.debug(f"🗣️✨🧹 [Pipeline] [Gen {new_gen_id}] Resetting pipeline events and flags.")
        self.llm_generation_active = False
        self.tts_quick_generation_active = False
        self.tts_final_generation_active = False
        self.llm_answer_ready_event.clear()
        self.generator_ready_event.clear()
        self.stop_llm_request_event.clear()
        self.stop_llm_finished_event.clear()
        self.stop_tts_quick_request_event.clear()
        self.stop_tts_quick_finished_event.clear()
        self.stop_tts_final_request_event.clear()
        self.stop_tts_final_finished_event.clear()
        self.abort_completed_event.clear()
        self.abort_block_event.set()

        # Create new generation object
        self.running_generation = RunningGeneration(id=new_gen_id)
        self.running_generation.text = txt

        try:
            logger.info(f"🗣️🧠🚀 [Pipeline] [Gen {new_gen_id}] Creating LLM generator...")
            
            # Create async generator for streaming LLM response using Hominio Voice LLMService
            async def create_llm_generator():
                async for token in self.llm_service.get_streaming_llm_response(txt):
                    yield token
            
            self.running_generation.llm_generator = create_llm_generator()
            logger.info(f"🗣️🧠✔️ [Pipeline] [Gen {new_gen_id}] LLM generator created")
            self.generator_ready_event.set()
        except Exception as e:
            logger.exception(f"🗣️🧠💥 [Pipeline] [Gen {new_gen_id}] Failed to create LLM generator: {e}")
            self.running_generation = None

    def process_abort_generation(self):
        """Handle core logic of aborting current generation"""
        with self.abort_lock:
            current_gen_obj = self.running_generation
            current_gen_id_str = f"Gen {current_gen_obj.id}" if current_gen_obj else "Gen None"

            if current_gen_obj is None or current_gen_obj.abortion_started:
                logger.info(f"🗣️🛑🤷 [Pipeline] {current_gen_id_str} Abort requested but no active generation or already aborting.")
                self.abort_completed_event.set()
                self.abort_block_event.set()
                return

            logger.info(f"🗣️🛑🚀 [Pipeline] {current_gen_id_str} Abortion process starting...")
            current_gen_obj.abortion_started = True
            self.abort_block_event.clear()
            self.abort_completed_event.clear()
            self.stop_everything_event.set()
            aborted_something = False

            # Abort LLM
            is_llm_potentially_active = self.llm_generation_active or self.generator_ready_event.is_set()
            if is_llm_potentially_active:
                logger.info(f"🗣️🛑🧠❌ [Pipeline] {current_gen_id_str} - Stopping LLM...")
                self.stop_llm_request_event.set()
                self.generator_ready_event.set()
                stopped = self.stop_llm_finished_event.wait(timeout=5.0)
                if stopped:
                    logger.info(f"🗣️🛑🧠👍 [Pipeline] {current_gen_id_str} LLM stopped")
                    self.stop_llm_finished_event.clear()
                else:
                    logger.warning(f"🗣️🛑🧠⏱️ [Pipeline] {current_gen_id_str} LLM stop timeout")
                
                # Stop LLM streaming if available
                if self.llm_service:
                    self.llm_service.stop_streaming()
                    # Also cancel any active generation requests
                    if hasattr(self.llm_service, 'cancel_generation'):
                        self.llm_service.cancel_generation()
                
                self.llm_generation_active = False
                aborted_something = True
            self.stop_llm_request_event.clear()

            # Abort Quick TTS
            is_tts_quick_potentially_active = self.tts_quick_generation_active or self.llm_answer_ready_event.is_set()
            if is_tts_quick_potentially_active:
                logger.info(f"🗣️🛑👄❌ [Pipeline] {current_gen_id_str} Stopping Quick TTS...")
                self.stop_tts_quick_request_event.set()
                self.llm_answer_ready_event.set()
                stopped = self.stop_tts_quick_finished_event.wait(timeout=5.0)
                if stopped:
                    logger.info(f"🗣️🛑👄👍 [Pipeline] {current_gen_id_str} Quick TTS stopped")
                    self.stop_tts_quick_finished_event.clear()
                else:
                    logger.warning(f"🗣️🛑👄⏱️ [Pipeline] {current_gen_id_str} Quick TTS stop timeout")
                self.tts_quick_generation_active = False
                aborted_something = True
            self.stop_tts_quick_request_event.clear()

            # Abort Final TTS
            is_tts_final_potentially_active = self.tts_final_generation_active
            if is_tts_final_potentially_active:
                logger.info(f"🗣️🛑👄❌ [Pipeline] {current_gen_id_str} Stopping Final TTS...")
                self.stop_tts_final_request_event.set()
                stopped = self.stop_tts_final_finished_event.wait(timeout=5.0)
                if stopped:
                    logger.info(f"🗣️🛑👄👍 [Pipeline] {current_gen_id_str} Final TTS stopped")
                    self.stop_tts_final_finished_event.clear()
                else:
                    logger.warning(f"🗣️🛑👄⏱️ [Pipeline] {current_gen_id_str} Final TTS stop timeout")
                self.tts_final_generation_active = False
                aborted_something = True
            self.stop_tts_final_request_event.clear()



            # Clear running generation
            if self.running_generation is not None and self.running_generation.id == current_gen_obj.id:
                logger.info(f"🗣️🛑🧹 [Pipeline] {current_gen_id_str} Clearing generation object")
                if current_gen_obj.llm_generator and hasattr(current_gen_obj.llm_generator, 'close'):
                    try:
                        current_gen_obj.llm_generator.close()
                    except Exception as e:
                        logger.warning(f"🗣️🛑🧠💥 [Pipeline] {current_gen_id_str} Error closing generator: {e}")
                self.running_generation = None

            # Final cleanup
            self.generator_ready_event.clear()
            self.llm_answer_ready_event.clear()

            logger.info(f"🗣️🛑✅ [Pipeline] {current_gen_id_str} Abort complete. Running generation object cleared.")
            self.abort_completed_event.set()
            self.abort_block_event.set()

    # Public Methods

    def prepare_generation(self, txt: str):
        """Public method to request preparation of new speech generation"""
        logger.info(f"🗣️📥 [Pipeline] Queueing 'prepare' request for: '{txt[:50]}...'")
        self.requests_queue.put(PipelineRequest("prepare", txt))

    def finish_generation(self):
        """Public method to signal end of user input"""
        logger.info(f"🗣️📥 [Pipeline] Queueing 'finish' request")
        self.requests_queue.put(PipelineRequest("finish"))

    def abort_generation(self, wait_for_completion: bool = False, timeout: float = 7.0, reason: str = ""):
        """Public method to initiate abortion of current speech generation"""
        if self.shutdown_event.is_set():
            logger.warning("🗣️🔌 [Pipeline] Shutdown in progress, ignoring abort")
            return

        gen_id_str = f"Gen {self.running_generation.id}" if self.running_generation else "Gen None"
        logger.info(f"🗣️🛑🚀 [Pipeline] Requesting abort (wait={wait_for_completion}, reason='{reason}') for {gen_id_str}")

        self.process_abort_generation()

        if wait_for_completion:
            logger.info(f"🗣️🛑⏳ [Pipeline] Waiting for abort completion...")
            completed = self.abort_completed_event.wait(timeout=timeout)
            if completed:
                logger.info(f"🗣️🛑✅ [Pipeline] Abort completion confirmed")
            else:
                logger.warning(f"🗣️🛑⏱️ [Pipeline] Abort completion timeout")
            self.abort_block_event.set()

    def reset(self):
        """Reset pipeline state completely"""
        logger.info("🗣️🔄 [Pipeline] Resetting pipeline state...")
        self.abort_generation(wait_for_completion=True, timeout=7.0, reason="reset")
        self.history = []

        logger.info("🗣️🧹 [Pipeline] Reset complete")

    def shutdown(self):
        """Graceful shutdown of pipeline and worker threads"""
        logger.info("🗣️🔌 [Pipeline] Initiating shutdown...")
        self.shutdown_event.set()

        logger.info("🗣️🔌🛑 [Pipeline] Final abort before shutdown...")
        self.abort_generation(wait_for_completion=True, timeout=3.0, reason="shutdown")

        # Wake up threads
        logger.info("🗣️🔌🔔 [Pipeline] Signaling events to wake threads...")
        self.generator_ready_event.set()
        self.llm_answer_ready_event.set()
        self.stop_llm_finished_event.set()
        self.stop_tts_quick_finished_event.set()
        self.stop_tts_final_finished_event.set()
        self.abort_completed_event.set()
        self.abort_block_event.set()


        # Join threads
        threads_to_join = [
            (self.request_processing_thread, "Request Processor"),
            (self.llm_inference_thread, "LLM Worker"),
            (self.tts_quick_inference_thread, "Quick TTS Worker"),
            (self.tts_final_inference_thread, "Final TTS Worker"),
        ]

        for thread, name in threads_to_join:
            if thread.is_alive():
                logger.info(f"🗣️🔌⏳ [Pipeline] Joining {name}...")
                thread.join(timeout=5.0)
                if thread.is_alive():
                    logger.warning(f"🗣️🔌⏱️ [Pipeline] {name} thread did not join cleanly")
            else:
                logger.info(f"🗣️🔌👍 [Pipeline] {name} thread already finished")

        logger.info("🗣️🔌✅ [Pipeline] Shutdown complete")

    def get_status(self):
        """Get complex pipeline status"""
        return {
            "role": "complex_speech_pipeline_orchestrator",
            "generation_counter": self.generation_counter,
            "running_generation_id": self.running_generation.id if self.running_generation else None,
            "running_generation_aborted": self.running_generation.abortion_started if self.running_generation else None,
            "worker_states": {
                "llm_active": self.llm_generation_active,
                "tts_quick_active": self.tts_quick_generation_active,
                "tts_final_active": self.tts_final_generation_active
            },
            "event_states": {
                "generator_ready": self.generator_ready_event.is_set(),
                "llm_answer_ready": self.llm_answer_ready_event.is_set(),
                "abort_block": self.abort_block_event.is_set(),
            },
            "queue_sizes": {
                "requests": self.requests_queue.qsize(),
            },
            "services_connected": {
                "stt": self.stt_service is not None,
                "tts": self.tts_service is not None,
                "llm": self.llm_service is not None,
                "message_router": self.message_router is not None
            },
            "thread_states": {
                "request_processor": self.request_processing_thread.is_alive(),
                "llm_worker": self.llm_inference_thread.is_alive(),
                "tts_quick_worker": self.tts_quick_inference_thread.is_alive(),
                "tts_final_worker": self.tts_final_inference_thread.is_alive()
            },
            "pipeline_pattern": "complex_reference_style_with_threading"
        }