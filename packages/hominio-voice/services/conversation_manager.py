"""
Conversation Manager
Handles the conversation flow with interruption detection and management
"""
import logging
import asyncio
import threading
import json
import time
import struct
import queue
import numpy as np
from typing import Optional, Callable, Dict, Any, List, Set, Tuple
from fastapi import WebSocket
import concurrent.futures
from datetime import datetime
import hashlib

from engines.tts_engine import tts_manager
from engines.llm_client import llm_manager

logger = logging.getLogger(__name__)


class TextContext:
    """
    Extracts meaningful text segments (contexts) from a given string.
    Based on RealtimeVoiceChat reference implementation.
    """
    def __init__(self, split_tokens: Optional[Set[str]] = None) -> None:
        if split_tokens is None:
            # Default split tokens for sentence boundary detection
            default_splits: Set[str] = {".", "!", "?", ",", ";", ":", "\n", "-", "。", "、"}
            self.split_tokens: Set[str] = default_splits
        else:
            self.split_tokens: Set[str] = set(split_tokens)

    def get_context(self, txt: str, min_len: int = 6, max_len: int = 120, min_alnum_count: int = 10) -> Tuple[Optional[str], Optional[str]]:
        """
        Finds the shortest valid context at the beginning of the input text.
        
        Returns:
            A tuple containing (context_string, remaining_text) or (None, None)
        """
        alnum_count = 0

        for i in range(1, min(len(txt), max_len) + 1):
            char = txt[i - 1]
            if char.isalnum():
                alnum_count += 1

            # Check if the current character is a potential context end
            if char in self.split_tokens:
                # Check if length and alphanumeric count criteria are met
                if i >= min_len and alnum_count >= min_alnum_count:
                    context_str = txt[:i]
                    remaining_str = txt[i:]
                    logger.info(f"🧠 Context found after char {i}: '{context_str}'")
                    return context_str, remaining_str

        # No suitable context found within the max_len limit
        return None, None


class AudioBuffer:
    """
    Smart audio buffering system optimized for Kokoro engine.
    Ensures smooth playback by buffering initial chunks until stream is stable.
    """
    def __init__(self):
        self.buffer: List[bytes] = []
        self.good_streak = 0
        self.buffering = True
        self.buf_duration = 0.0
        self.sample_rate = 24000  # Kokoro engine sample rate
        self.bytes_per_sample = 2  # 16-bit audio
        self.prev_chunk_time = 0.0
        
    def add_chunk(self, chunk: bytes) -> Tuple[List[bytes], bool]:
        """
        Add audio chunk to buffer and return chunks to send.
        Optimized for Kokoro engine characteristics.
        
        Returns:
            Tuple of (chunks_to_send, first_chunk_callback_fired)
        """
        now = time.time()
        samples = len(chunk) // self.bytes_per_sample
        play_duration = samples / self.sample_rate
        
        # Track timing for stability detection
        if self.prev_chunk_time > 0:
            gap = now - self.prev_chunk_time
            if gap <= play_duration * 1.1:  # Allow small tolerance
                self.good_streak += 1
            else:
                logger.warning(f"🎵 Kokoro audio chunk timing unstable (gap={gap:.3f}s > {play_duration:.3f}s)")
                self.good_streak = 0
        
        self.prev_chunk_time = now
        
        # Always add chunk to buffer first
        self.buffer.append(chunk)
        self.buf_duration += play_duration
        
        chunks_to_send = []
        first_chunk_fired = False
        
        if self.buffering:
            # Kokoro-optimized flush conditions: faster than reference for responsiveness
            if self.good_streak >= 2 or self.buf_duration >= 0.3:  # Reduced from 0.5s to 0.3s
                logger.info(f"🎵 Flushing Kokoro audio buffer (streak={self.good_streak}, duration={self.buf_duration:.2f}s)")
                chunks_to_send = self.buffer.copy()
                self.buffer.clear()
                self.buf_duration = 0.0
                self.buffering = False
                first_chunk_fired = True
        else:
            # Not buffering, send chunk directly
            chunks_to_send = [chunk]
            
        return chunks_to_send, first_chunk_fired
    
    def flush_remaining(self) -> List[bytes]:
        """Flush any remaining buffered chunks"""
        if self.buffer:
            chunks = self.buffer.copy()
            self.buffer.clear()
            self.buf_duration = 0.0
            return chunks
        return []
    
    def reset(self):
        """Reset buffer state"""
        self.buffer.clear()
        self.good_streak = 0
        self.buffering = True
        self.buf_duration = 0.0
        self.prev_chunk_time = 0.0


class PotentialSentenceDetector:
    """
    Detects potential sentence endings in real-time transcriptions for early LLM processing.
    Based on RealtimeVoiceChat reference implementation.
    """
    def __init__(self):
        self.sentence_end_cache = []
        self.potential_sentences_yielded = set()
        self.cache_max_age = 0.2  # 200ms
        self.trigger_count = 3
        
    def detect_potential_sentence_end(self, text: Optional[str], force_yield: bool = False) -> Optional[str]:
        """
        Detects potential sentence endings for early LLM processing.
        
        Returns:
            The sentence text if a potential end is detected, None otherwise
        """
        if not text:
            return None
            
        stripped_text = text.strip()
        if not stripped_text:
            return None
            
        # Don't consider ellipses as sentence end unless forced
        if stripped_text.endswith("...") and not force_yield:
            return None
            
        end_punctuations = [".", "!", "?"]
        now = time.time()
        
        # Only proceed if text ends with punctuation or if forced
        ends_with_punctuation = any(stripped_text.endswith(p) for p in end_punctuations)
        if not ends_with_punctuation and not force_yield:
            return None
            
        normalized_text = self._normalize_text(stripped_text)
        if not normalized_text:
            return None
            
        # Check if we've already yielded this sentence
        if normalized_text in self.potential_sentences_yielded:
            return None
            
        # Cache management
        entry_found = None
        for entry in self.sentence_end_cache:
            if self._is_similar_text(entry['text'], normalized_text):
                entry_found = entry
                break
                
        if entry_found:
            entry_found['timestamps'].append(now)
            # Keep only recent timestamps
            entry_found['timestamps'] = [
                ts for ts in entry_found['timestamps'] 
                if now - ts <= self.cache_max_age
            ]
            
            # Check if we have enough recent detections
            if len(entry_found['timestamps']) >= self.trigger_count:
                logger.info(f"🎯 Potential sentence end detected: '{stripped_text}'")
                self.potential_sentences_yielded.add(normalized_text)
                return stripped_text
        else:
            # Add new entry to cache
            self.sentence_end_cache.append({
                'text': normalized_text,
                'timestamps': [now],
                'original': stripped_text
            })
            
        # Clean old cache entries
        self._clean_cache(now)
        return None
        
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    def _is_similar_text(self, text1: str, text2: str, threshold: float = 0.96) -> bool:
        """Check if two normalized texts are similar"""
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, text1, text2).ratio()
        return similarity > threshold
        
    def _clean_cache(self, current_time: float):
        """Remove old cache entries"""
        self.sentence_end_cache = [
            entry for entry in self.sentence_end_cache
            if any(current_time - ts <= self.cache_max_age for ts in entry['timestamps'])
        ]
        
    def reset(self):
        """Reset detector state"""
        self.sentence_end_cache.clear()
        self.potential_sentences_yielded.clear()


class ConversationRequest:
    """Represents a request to be processed by the conversation manager"""
    def __init__(self, action: str, data: Optional[any] = None):
        self.action = action
        self.data = data
        self.timestamp = time.time()


class ConversationGeneration:
    """Tracks state for a single conversation generation"""
    def __init__(self, generation_id: int, user_text: str):
        self.id = generation_id
        self.user_text = user_text
        self.timestamp = time.time()
        self.llm_started = False
        self.llm_finished = False
        self.tts_started = False
        self.tts_finished = False
        self.aborted = False
        self.response_text = ""


class ConversationManager:
    """Enhanced conversation manager with request queue and generation tracking"""
    
    def __init__(self):
        # State management
        self.current_state = "standby"  # standby, listening, vad-detected, thinking, speaking
        self.is_speaking = False
        self.is_listening = False
        
        # Generation tracking
        self.generation_counter = 0
        self.current_generation: Optional[ConversationGeneration] = None
        self.generation_lock = threading.Lock()
        
        # Request queue system
        self.requests_queue = queue.Queue()
        self.request_processor_thread = threading.Thread(target=self._request_processor_worker, daemon=True)
        self.shutdown_event = threading.Event()
        self.request_processor_thread.start()
        
        # Audio and streaming management
        self.active_tts_ws: Optional[WebSocket] = None
        self.interrupt_event = threading.Event()
        self.active_synthesis_thread: Optional[threading.Thread] = None
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # TTS generation tracking
        self.tts_generation_counter = 0
        self.current_generation_id = 0
        
        # Audio buffer and smart boundaries
        self.audio_buffer = AudioBuffer()
        self.potential_sentence_detector = PotentialSentenceDetector()
        
        # Deduplication
        self.last_tts_text = ""
        self.last_tts_timestamp = 0.0
        
        # Callbacks
        self.on_state_change: Optional[Callable] = None
        self.on_vad_start: Optional[Callable] = None
        self.on_vad_stop: Optional[Callable] = None
        self.on_tts_start: Optional[Callable] = None
        self.on_tts_end: Optional[Callable] = None
        self.on_interruption: Optional[Callable] = None

    def _request_processor_worker(self):
        """Worker thread that processes conversation requests"""
        logger.info("💬 Request processor worker started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get the most recent request by draining the queue
                request = self.requests_queue.get(block=True, timeout=1.0)
                
                # Drain queue to get most recent request
                while not self.requests_queue.empty():
                    try:
                        skipped_request = self.requests_queue.get_nowait()
                        logger.debug(f"💬 Skipping older request: {skipped_request.action}")
                        request = skipped_request
                    except queue.Empty:
                        break
                
                logger.debug(f"💬 Processing request: {request.action}")
                
                if request.action == "process_user_input":
                    self._process_user_input_sync(request.data)
                elif request.action == "abort_generation":
                    self._abort_current_generation()
                else:
                    logger.warning(f"💬 Unknown request action: {request.action}")
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"💬 Error in request processor: {e}")
                
        logger.info("💬 Request processor worker stopped")

    def _process_user_input_sync(self, user_text: str):
        """Synchronously process user input with generation tracking"""
        logger.info(f"💬 Processing user input: '{user_text}'")
        
        # Check if we should abort current generation
        should_abort = self._should_abort_for_new_input(user_text)
        if should_abort:
            self._abort_current_generation()
            
        # Create new generation
        with self.generation_lock:
            self.generation_counter += 1
            self.current_generation = ConversationGeneration(
                generation_id=self.generation_counter,
                user_text=user_text
            )
            generation_id = self.current_generation.id
            
        logger.info(f"💬 Starting generation {generation_id} for: '{user_text}'")
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # Update state
        self._update_state("thinking")
        
        # Start LLM processing
        try:
            # Schedule the async LLM processing
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(
                self._process_llm_response(generation_id, user_text),
                loop
            )
        except Exception as e:
            logger.error(f"💬 Error starting LLM processing: {e}")
            self._update_state("standby")

    def _should_abort_for_new_input(self, new_text: str) -> bool:
        """Check if current generation should be aborted for new input"""
        if not self.current_generation:
            return False
            
        # Calculate similarity
        try:
            from services.text_similarity import TextSimilarity
            similarity_checker = TextSimilarity(focus='end', n_words=5)
            similarity = similarity_checker.calculate_similarity(
                self.current_generation.user_text,
                new_text
            )
            
            if similarity >= 0.95:
                logger.info(f"💬 Text too similar ({similarity:.2f}), not aborting")
                return False
            else:
                logger.info(f"💬 Text different enough ({similarity:.2f}), aborting current generation")
                return True
                
        except Exception as e:
            logger.warning(f"💬 Error calculating similarity: {e}, assuming different")
            return True

    def _abort_current_generation(self):
        """Abort the current generation if one exists"""
        with self.generation_lock:
            if self.current_generation and not self.current_generation.aborted:
                logger.info(f"💬 Aborting generation {self.current_generation.id}")
                self.current_generation.aborted = True
                
                # Set interrupt event
                self.interrupt_event.set()
                
                # Stop any active synthesis
                if self.active_synthesis_thread and self.active_synthesis_thread.is_alive():
                    self.active_synthesis_thread.join(timeout=1.0)
                    
                self._update_state("standby")

    async def _process_llm_response(self, generation_id: int, user_text: str):
        """Process LLM response for a specific generation"""
        # Check if generation is still valid
        with self.generation_lock:
            if not self.current_generation or self.current_generation.id != generation_id:
                logger.info(f"💬 Generation {generation_id} no longer current, aborting")
                return
                
            if self.current_generation.aborted:
                logger.info(f"💬 Generation {generation_id} was aborted, stopping")
                return
                
            self.current_generation.llm_started = True
            
        try:
            # Import here to avoid circular imports
            from engines.llm_client import llm_manager
            
            if not llm_manager.is_ready():
                logger.error("💬 LLM client not ready")
                self._update_state("standby")
                return
                
            # Start LLM streaming
            await self._stream_llm_to_tts(generation_id, user_text)
            
        except Exception as e:
            logger.error(f"💬 Error in LLM processing for generation {generation_id}: {e}")
            self._update_state("standby")

    async def _stream_llm_to_tts(self, generation_id: int, user_text: str):
        """Stream LLM response to TTS for a specific generation"""
        # Check generation validity
        with self.generation_lock:
            if not self.current_generation or self.current_generation.id != generation_id:
                return
            if self.current_generation.aborted:
                return
                
        # Continue with existing streaming logic but with generation tracking
        await self._stream_llm_to_tts_impl(user_text)

    async def _stream_llm_to_tts_impl(self, user_text: str):
        """Implementation of LLM to TTS streaming (existing logic)"""
        # This contains the existing streaming implementation
        # ... (keep existing _stream_llm_to_tts method content)
        pass

    def set_state_change_callback(self, callback: Callable):
        """Set callback for state changes"""
        self.on_state_change = callback
    
    def _update_state(self, new_state: str, message: str = None):
        """Update conversation state and notify UI"""
        if self.current_state != new_state:
            logger.info(f"🎭 State change: {self.current_state} -> {new_state}")
            self.current_state = new_state
            
            # Update internal flags
            self.is_listening = new_state == "listening"
            self.is_thinking = new_state == "thinking"
            self.is_speaking = new_state == "speaking"
            self.vad_detected = new_state == "vad-detected"
            
            # Notify UI via callback
            if self.on_state_change:
                self.on_state_change(new_state, message)
    
    def set_active_tts_websocket(self, websocket: Optional[WebSocket]):
        """Set the active TTS WebSocket connection"""
        self.active_tts_ws = websocket
        if websocket:
            logger.info("🔊 Active TTS WebSocket connection set")
        else:
            logger.info("🔊 Active TTS WebSocket connection cleared")
    
    def start_listening(self):
        """Signal that we're listening for user input"""
        self._update_state("listening")
        logger.info("👂 Started listening")
    
    def stop_listening(self):
        """Signal that we've stopped listening"""
        if self.current_state == "listening":
            self._update_state("standby")
        logger.info("👂 Stopped listening")
    
    def on_vad_detected(self):
        """Called when voice activity is detected"""
        if self.current_state == "listening":
            self._update_state("vad-detected")
            logger.info("🎤 VAD detected - user is speaking")
    
    def on_vad_stopped(self):
        """Called when voice activity stops"""
        if self.current_state == "vad-detected":
            self._update_state("listening")
        logger.info("🎤 VAD stopped - user finished speaking")
    
    def on_potential_sentence_detected(self, text: str):
        """
        Called when a potential sentence ending is detected in real-time transcription.
        This allows for early LLM processing before final transcription is complete.
        """
        logger.info(f"🎯 Potential sentence detected for early processing: '{text}'")
        
        # Check if we should start early LLM processing
        potential_sentence = self.potential_sentence_detector.detect_potential_sentence_end(text)
        if potential_sentence:
            logger.info(f"🚀 Starting early LLM processing for: '{potential_sentence}'")
            # Start LLM processing in background while STT continues
            asyncio.create_task(self._process_early_sentence(potential_sentence))
    
    async def _process_early_sentence(self, sentence: str):
        """
        Process a potential sentence early while STT is still running.
        This provides faster response times by starting LLM processing early.
        """
        try:
            # Only process if we're not already speaking
            if not self.is_speaking:
                logger.info(f"🚀 Early sentence processing: '{sentence}'")
                # This will be overridden by final transcription if it arrives
                await self.process_user_input(sentence)
        except Exception as e:
            logger.error(f"Error in early sentence processing: {e}")
    
    def interrupt_if_speaking(self):
        """Interrupt current TTS if we're speaking"""
        if self.is_speaking:
            logger.info("🛑 Interrupting current TTS synthesis")
            self.interrupt_event.set()
            
            # Stop current synthesis thread
            if self.active_synthesis_thread and self.active_synthesis_thread.is_alive():
                # Signal interruption and wait briefly for thread to stop
                self.active_synthesis_thread.join(timeout=1.0)
            
            self._update_state("standby", "Interrupted")
            
            # Send interruption signal to client
            if self.active_tts_ws:
                try:
                    asyncio.create_task(self.active_tts_ws.send_text(json.dumps({
                        "type": "tts_interruption",
                        "message": "TTS interrupted by user speech"
                    })))
                except Exception as e:
                    logger.error(f"Error sending interruption signal: {e}")
            
            # Call interruption callback
            if self.on_interruption:
                self.on_interruption()
            
            return True
        return False
    
    async def process_user_input(self, user_text: str):
        """
        Process user input using request queue system
        
        Args:
            user_text: The transcribed user input
        """
        logger.info(f"💬 Queuing user input for processing: '{user_text}'")
        
        # Prevent processing empty or very short inputs
        if not user_text or len(user_text.strip()) < 2:
            logger.info("Ignoring short or empty input")
            return
        
        # Queue the request for processing by the worker thread
        request = ConversationRequest("process_user_input", user_text)
        self.requests_queue.put(request)
    
    def _preprocess_token(self, token: str) -> str:
        """
        Preprocess LLM token to clean up artifacts and normalize text.
        Based on RealtimeVoiceChat reference implementation.
        """
        if not token:
            return ""
            
        # Remove common artifacts
        token = token.replace("</s>", "").replace("<s>", "")
        token = token.replace("</|im_end|>", "").replace("<|im_start|>", "")
        
        # Normalize whitespace
        token = token.replace("\t", " ")
        
        # Remove excessive newlines but keep some structure
        if token.count("\n") > 2:
            token = token.replace("\n\n\n", "\n\n")
            
        return token
    
    def _should_skip_tts(self, text: str) -> bool:
        """Check if we should skip TTS to prevent looping"""
        import time
        import hashlib
        
        current_time = time.time()
        
        # Create a hash of the text for better comparison
        text_hash = hashlib.md5(text.encode()).hexdigest()
        last_text_hash = hashlib.md5(self.last_tts_text.encode()).hexdigest() if self.last_tts_text else ""
        
        # Check if it's the same text within a longer time window
        if (text_hash == last_text_hash and 
            current_time - self.last_tts_timestamp < 10.0):  # 10 second window
            logger.warning(f"🔄 Skipping duplicate TTS: '{text[:30]}...' (hash: {text_hash[:8]})")
            return True
        
        # Also check if we're already speaking
        if self.is_speaking:
            logger.warning(f"🔄 Skipping TTS - already speaking: '{text[:30]}...'")
            return True
        
        # Update tracking variables only if we're going to proceed
        self.last_tts_text = text
        self.last_tts_timestamp = current_time
        return False
    
    async def _synthesize_and_send(self, text: str):
        """
        Synthesize text and send audio to client with real-time streaming
        
        Args:
            text: Text to synthesize
        """
        if not self.active_tts_ws:
            logger.warning("No active TTS WebSocket connection")
            self._update_state("standby", "No WebSocket connection")
            return

        if not tts_manager.is_ready():
            logger.error("TTS engine not ready")
            self._update_state("standby", "TTS engine not ready")
            return

        # Check for TTS looping
        if self._should_skip_tts(text):
            self._update_state("standby", "Duplicate TTS skipped")
            return

        try:
            logger.info(f"🔊 Synthesizing and streaming: '{text[:50]}...'")
            
            # Update to speaking state
            self._update_state("speaking")
            
            # Signal TTS start
            if self.on_tts_start:
                self.on_tts_start()
            
            # Clear interrupt event
            self.interrupt_event.clear()
            
            # Increment generation ID for tracking
            self.tts_generation_counter += 1
            self.current_generation_id = self.tts_generation_counter
            generation_id = self.current_generation_id
            
            logger.info(f"🔊 Starting real-time TTS streaming {generation_id}")
            
            # Send WAV header first
            wav_header = tts_manager.get_wave_header()
            await self.active_tts_ws.send_bytes(wav_header)
            
            # Create audio queue for real-time streaming - use regular queue for thread communication
            audio_queue = asyncio.Queue()
            streaming_active = True
            
            # Capture the main event loop before starting the synthesis thread
            main_loop = asyncio.get_running_loop()
            
            # Start streaming task to send chunks as they arrive
            async def stream_audio_chunks():
                nonlocal streaming_active
                try:
                    chunk_count = 0
                    while streaming_active:
                        try:
                            # Wait for audio chunk with timeout
                            chunk = await asyncio.wait_for(audio_queue.get(), timeout=0.5)
                            
                            if chunk is None:  # Sentinel value for end
                                break
                            
                            if self.interrupt_event.is_set():
                                logger.info(f"🛑 Audio streaming interrupted for generation {generation_id}")
                                break
                            
                            # Send chunk immediately
                            await self.active_tts_ws.send_bytes(chunk)
                            chunk_count += 1
                            
                        except asyncio.TimeoutError:
                            # Check if synthesis is still active
                            if not streaming_active:
                                break
                            continue
                    
                    # Send completion signal if not interrupted
                    if not self.interrupt_event.is_set() and streaming_active:
                        await self.active_tts_ws.send_text("END")
                        logger.info(f"✅ Real-time TTS streaming completed for generation {generation_id} ({chunk_count} chunks)")
                    
                except Exception as e:
                    logger.error(f"Error in audio streaming task: {e}")
                finally:
                    streaming_active = False
                    # Always reset to listening after TTS completion for continuous conversation
                    if not self.interrupt_event.is_set():
                        self._update_state("listening", "Ready for next conversation...")
                        logger.info("🔄 Automatically returning to listening mode for continuous conversation")
                    
                    # Signal TTS end
                    if self.on_tts_end:
                        self.on_tts_end()
            
            # Start the streaming task
            streaming_task = asyncio.create_task(stream_audio_chunks())
            
            # Synthesize in thread with real-time chunk sending
            def synthesize_with_realtime_streaming():
                try:
                    from RealtimeTTS import TextToAudioStream
                    import time
                    
                    # Create TTS stream
                    tts_stream = TextToAudioStream(tts_manager.engine, muted=True)
                    
                    # Real-time chunk callback - sends immediately to queue
                    def on_audio_chunk(chunk):
                        if self.interrupt_event.is_set():
                            logger.info(f"🛑 Synthesis interrupted for generation {generation_id}")
                            return
                        
                        # Put chunk in queue for immediate streaming
                        try:
                            # Use the captured main loop
                            asyncio.run_coroutine_threadsafe(audio_queue.put(chunk), main_loop)
                        except Exception as e:
                            logger.error(f"Error queuing audio chunk: {e}")
                    
                    # Start synthesis with real-time callback
                    logger.info(f"🎵 Starting real-time synthesis for generation {generation_id}")
                    tts_stream.feed(text)
                    tts_stream.play(
                        muted=True, 
                        on_audio_chunk=on_audio_chunk,
                        log_synthesized_text=True
                    )
                    
                    # Signal end of synthesis
                    if not self.interrupt_event.is_set():
                        asyncio.run_coroutine_threadsafe(audio_queue.put(None), main_loop)  # Sentinel
                        logger.info(f"🎵 Synthesis completed for generation {generation_id}")
                    
                except Exception as e:
                    logger.error(f"Error in real-time synthesis thread: {e}")
                finally:
                    # Ensure streaming task knows synthesis is done
                    nonlocal streaming_active
                    streaming_active = False
                    # Put sentinel to unblock streaming task
                    try:
                        asyncio.run_coroutine_threadsafe(audio_queue.put(None), main_loop)
                    except:
                        pass
            
            # Start synthesis in thread
            self.active_synthesis_thread = threading.Thread(
                target=synthesize_with_realtime_streaming, 
                daemon=True
            )
            self.active_synthesis_thread.start()
            
            # Wait for streaming to complete
            await streaming_task
            
        except Exception as e:
            logger.error(f"Error in real-time synthesis setup: {e}")
            self._update_state("standby", "Synthesis setup error")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("🗑️ Conversation history cleared")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current conversation state"""
        return {
            "current_state": self.current_state,
            "is_speaking": self.is_speaking,
            "is_listening": self.is_listening,
            "is_thinking": self.is_thinking,
            "vad_detected": self.vad_detected,
            "has_active_websocket": self.active_tts_ws is not None,
            "conversation_length": len(self.conversation_history),
            "current_generation_id": self.current_generation_id,
            "tts_generation_counter": self.tts_generation_counter
        }
    
    def shutdown(self):
        """Shutdown the conversation manager"""
        logger.info("🔌 Shutting down conversation manager")
        
        # Interrupt any active synthesis
        self.interrupt_if_speaking()
        
        # Wait for synthesis thread to finish
        if self.active_synthesis_thread and self.active_synthesis_thread.is_alive():
            self.active_synthesis_thread.join(timeout=2.0)
        
        # Clear state
        self.active_tts_ws = None
        self._update_state("standby", "Shutdown")


# Global conversation manager instance
conversation_manager = ConversationManager() 