import asyncio
import logging
import threading
from typing import Optional, Callable, Dict, Any
import numpy as np
from scipy.signal import resample_poly
from transcribe import TranscriptionProcessor
from speech_pipeline_manager import SpeechPipelineManager

# Import memory management for async queues
from memory_manager import get_resource_tracker

logger = logging.getLogger(__name__)


class AudioInputProcessor:
    """
    Manages audio input, processes it for transcription, and handles related callbacks.

    This class receives raw audio chunks, resamples them to the required format (16kHz),
    feeds them to an underlying `TranscriptionProcessor`, and manages callbacks for
    real-time transcription updates, recording start events, and silence detection.
    It also runs the transcription process in a background task.
    """

    _RESAMPLE_RATIO = 3  # Resample ratio from 48kHz (assumed input) to 16kHz.

    def __init__(
            self,
            language: str = "en",
            silence_active_callback: Optional[Callable[[bool], None]] = None,
            pipeline_latency: float = 0.5,
        ) -> None:
        """
        Initializes the AudioInputProcessor with its own SpeechPipelineManager.

        Args:
            language: Target language code for transcription (e.g., "en").
            silence_active_callback: Optional callback function invoked when silence state changes.
                                     It receives a boolean argument (True if silence is active).
            pipeline_latency: Estimated latency of the processing pipeline in seconds.
        """
        self.last_partial_text: Optional[str] = None
        
        # Create per-user SpeechPipelineManager instance to prevent user interference
        self.speech_pipeline_manager = SpeechPipelineManager(
            tts_engine="kokoro",
            llm_provider="openai", 
            llm_model="phala/llama-3.3-70b-instruct",
            no_think=False,
        )
        
        self.transcriber = TranscriptionProcessor(
            language,
            on_recording_start_callback=self._on_recording_start,
            silence_active_callback=self._silence_active_callback,
            pipeline_latency=pipeline_latency,
        )
        # Flag to indicate if the transcription loop has failed fatally
        self._transcription_failed = False
        self.transcription_task = None  # Will be created when needed
        self._task_started = False

        self.realtime_callback: Optional[Callable[[str], None]] = None
        self.recording_start_callback: Optional[Callable[[None], None]] = None # Type adjusted
        self.silence_active_callback: Optional[Callable[[bool], None]] = silence_active_callback
        self.interrupted = False # TODO: Consider renaming or clarifying usage (interrupted by user speech?)
        
        # Initialize resource tracking and queue management
        self.resource_tracker = get_resource_tracker()
        self.resource_tracker.track_resource("global", "AudioInputProcessor", f"audio_input_{id(self)}")
        self.max_queue_size = 500  # Prevent memory overflow
        self.dropped_chunks = 0

        self._setup_callbacks()
        logger.debug(f"👂🚀 AudioInputProcessor initialized with dedicated SpeechPipelineManager")

    def start_transcription_task(self) -> None:
        """Start the transcription task if not already started."""
        if not self._task_started and self.transcription_task is None:
            try:
                self.transcription_task = asyncio.create_task(self._run_transcription_loop())
                self._task_started = True
                logger.debug("👂⚡ Transcription task started.")
            except RuntimeError as e:
                if "no running event loop" in str(e):
                    logger.warning("👂⚠️ No event loop available, transcription task will start when process_chunk_queue is called")
                else:
                    raise

    def _silence_active_callback(self, is_active: bool) -> None:
        """Internal callback relay for silence detection status."""
        if self.silence_active_callback:
            self.silence_active_callback(is_active)

    def _on_recording_start(self) -> None:
        """Internal callback relay triggered when the transcriber starts recording."""
        if self.recording_start_callback:
            self.recording_start_callback()

    def abort_generation(self) -> None:
        """Signals the underlying transcriber to abort any ongoing generation process."""
        logger.debug("👂🛑 Aborting generation requested.")
        self.transcriber.abort_generation()

    def _setup_callbacks(self) -> None:
        """Sets up internal callbacks for the TranscriptionProcessor instance."""
        def partial_transcript_callback(text: str) -> None:
            """Handles partial transcription results from the transcriber."""
            if text != self.last_partial_text:
                self.last_partial_text = text
                if self.realtime_callback:
                    self.realtime_callback(text)

        self.transcriber.realtime_transcription_callback = partial_transcript_callback

    async def _run_transcription_loop(self) -> None:
        """
        Continuously runs the transcription loop in a background asyncio task.

        It repeatedly calls the underlying `transcribe_loop`. If `transcribe_loop`
        finishes normally (completes one cycle), this loop calls it again.
        If `transcribe_loop` raises an Exception, it's treated as a fatal error,
        a flag is set, and this loop terminates. Handles CancelledError separately.
        """
        task_name = asyncio.current_task().get_name() if hasattr(asyncio.current_task(), 'get_name') else 'TranscriptionTask'
        logger.debug(f"👂▶️ Starting background transcription task ({task_name}).")
        while True: # Loop restored to continuously call transcribe_loop
            try:
                # Run one cycle of the underlying blocking loop
                await asyncio.to_thread(self.transcriber.transcribe_loop)
                # If transcribe_loop returns without error, it means one cycle is complete.
                # The `while True` ensures it will be called again.
                logger.debug("👂✅ TranscriptionProcessor.transcribe_loop completed one cycle.")
                # Add a small sleep to prevent potential tight loop if transcribe_loop returns instantly
                await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                logger.info(f"👂🚫 Transcription loop ({task_name}) cancelled.")
                # Do not set failure flag on cancellation
                break # Exit the while loop
            except Exception as e:
                # An actual error occurred within transcribe_loop
                logger.error(f"👂💥 Transcription loop ({task_name}) encountered a fatal error: {e}. Loop terminated.", exc_info=True)
                self._transcription_failed = True # Set failure flag
                break # Exit the while loop, stopping retries

        logger.info(f"👂⏹️ Background transcription task ({task_name}) finished.")

    def process_audio_chunk(self, raw_bytes: bytes) -> np.ndarray:
        """
        Converts raw audio bytes (int16) to a 16kHz 16-bit PCM numpy array.

        The audio is converted to float32 for accurate resampling and then
        converted back to int16, clipping values outside the valid range.

        Args:
            raw_bytes: Raw audio data assumed to be in int16 format.

        Returns:
            A numpy array containing the resampled audio in int16 format at 16kHz.
            Returns an array of zeros if the input is silent.
        """
        raw_audio = np.frombuffer(raw_bytes, dtype=np.int16)

        if np.max(np.abs(raw_audio)) == 0:
            # Calculate expected length after resampling for silence
            expected_len = int(np.ceil(len(raw_audio) / self._RESAMPLE_RATIO))
            return np.zeros(expected_len, dtype=np.int16)

        # Convert to float32 for resampling precision
        audio_float32 = raw_audio.astype(np.float32)

        # Resample using float32 data
        resampled_float = resample_poly(audio_float32, 1, self._RESAMPLE_RATIO)

        # Convert back to int16, clipping to ensure validity
        resampled_int16 = np.clip(resampled_float, -32768, 32767).astype(np.int16)

        return resampled_int16

    async def process_chunk_queue(self, audio_queue: asyncio.Queue) -> None:
        """
        Continuously processes audio chunks received from an asyncio Queue.

        Retrieves audio data, processes it using `process_audio_chunk`, and
        feeds the result to the transcriber unless interrupted or the transcription
        task has failed. Stops when `None` is received from the queue or upon error.

        Args:
            audio_queue: An asyncio queue expected to yield dictionaries containing
                         'pcm' (raw audio bytes) or None to terminate.
        """
        logger.debug("👂▶️ Starting audio chunk processing loop.")
        
        # Start transcription task if not already started
        if not self._task_started and self.transcription_task is None:
            try:
                self.transcription_task = asyncio.create_task(self._run_transcription_loop())
                self._task_started = True
                logger.debug("👂⚡ Transcription task started in process_chunk_queue.")
            except Exception as e:
                logger.error(f"👂💥 Failed to start transcription task: {e}")
                return
        while True:
            try:
                # Check if the transcription task has permanently failed *before* getting item
                if self._transcription_failed:
                    logger.error("👂🛑 Transcription task failed previously. Stopping audio processing.")
                    break # Stop processing if transcription backend is down

                # Check if the task finished unexpectedly (e.g., cancelled but not failed)
                # Needs to check self.transcription_task existence as it might be None during shutdown
                if self.transcription_task and self.transcription_task.done() and not self._transcription_failed:
                     # Attempt to check exception status if task is done
                     exception_result = self.transcription_task.exception()
                     if exception_result is not None:
                         logger.error(f"👂💥 Transcription task finished with exception: {exception_result}")
                         self._transcription_failed = True
                         break
                     else:
                         logger.warning("👂⚠️ Transcription task finished without exception. This is unexpected.")

                # Check queue size and apply backpressure
                queue_size = audio_queue.qsize()
                if queue_size > self.max_queue_size:
                    logger.warning(f"👂⚠️ Audio queue overflow ({queue_size}), dropping oldest chunks")
                    # Drop old chunks to prevent memory overflow
                    for _ in range(min(queue_size - self.max_queue_size + 50, queue_size)):
                        try:
                            audio_queue.get_nowait()
                            self.dropped_chunks += 1
                        except asyncio.QueueEmpty:
                            break

                # Get audio chunk with timeout to prevent infinite blocking
                try:
                    chunk_data = await asyncio.wait_for(audio_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    # Timeout occurred, check loop conditions again
                    continue

                # Check for termination signal
                if chunk_data is None:
                    logger.debug("👂🛑 Received termination signal (None). Stopping audio processing.")
                    break

                # Extract PCM data
                pcm_data = chunk_data.get('pcm')
                if pcm_data is None:
                    logger.warning("👂⚠️ Received chunk with no PCM data. Skipping.")
                    continue

                # Process audio chunk
                if not self.interrupted:
                    try:
                        processed_audio = self.process_audio_chunk(pcm_data)
                        self.transcriber.feed_audio(processed_audio.tobytes(), {})
                    except Exception as e:
                        logger.error(f"👂💥 Error processing audio chunk: {e}", exc_info=True)
                        # Continue processing despite error

                # Mark task as done for this chunk
                audio_queue.task_done()

            except asyncio.CancelledError:
                logger.info("👂🚫 Audio chunk processing cancelled.")
                break
            except Exception as e:
                logger.error(f"👂💥 Unexpected error in audio processing loop: {e}", exc_info=True)
                # Continue processing despite error
                await asyncio.sleep(0.1)  # Brief pause to prevent tight error loop

        logger.info("👂⏹️ Audio chunk processing loop finished.")

    def set_callbacks(
        self,
        realtime_callback: Optional[Callable[[str], None]] = None,
        recording_start_callback: Optional[Callable[[None], None]] = None,
    ) -> None:
        """
        Sets external callbacks for transcription events.

        Args:
            realtime_callback: Called with partial transcription text as it becomes available.
            recording_start_callback: Called when recording starts (e.g., when silence ends).
        """
        self.realtime_callback = realtime_callback
        self.recording_start_callback = recording_start_callback

    def shutdown(self) -> None:
        """
        Shuts down the AudioInputProcessor and cleans up resources.

        Cancels the background transcription task, shuts down internal components,
        and performs cleanup.
        """
        logger.info("👂🔌 Shutting down AudioInputProcessor...")

        # Cancel transcription task
        if self.transcription_task and not self.transcription_task.done():
            self.transcription_task.cancel()
            logger.debug("👂🚫 Transcription task cancelled.")

        # Shutdown transcriber
        if hasattr(self, 'transcriber') and self.transcriber:
            self.transcriber.shutdown()

        # Shutdown speech pipeline manager
        if hasattr(self, 'speech_pipeline_manager') and self.speech_pipeline_manager:
            self.speech_pipeline_manager.shutdown()

        # Untrack resource
        if hasattr(self, 'resource_tracker'):
            self.resource_tracker.untrack_resource("global", "AudioInputProcessor", f"audio_input_{id(self)}")

        if self.dropped_chunks > 0:
            logger.info(f"👂📊 Total dropped chunks during session: {self.dropped_chunks}")

        logger.info("👂🔌 AudioInputProcessor shutdown complete.")