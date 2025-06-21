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
import numpy as np
from typing import Optional, Callable, Dict, Any, List, Set, Tuple
from fastapi import WebSocket

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


class ConversationManager:
    """Manages conversation flow with interruption handling and visual state management"""
    
    def __init__(self):
        self.active_tts_ws: Optional[WebSocket] = None
        self.is_speaking = False
        self.is_listening = False
        self.is_thinking = False
        self.vad_detected = False
        self.current_generation_id = 0
        self.active_synthesis_thread: Optional[threading.Thread] = None
        self.interrupt_event = threading.Event()
        
        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.current_state = "standby"  # standby, listening, vad-detected, thinking, speaking
        
        # TTS looping prevention
        self.last_tts_text = ""
        self.last_tts_timestamp = 0
        self.tts_generation_counter = 0
        
        # Performance improvements
        self.text_context = TextContext()  # Smart sentence boundary detection
        self.audio_buffer = AudioBuffer()  # Smart audio buffering
        self.potential_sentence_detector = PotentialSentenceDetector()  # Early sentence detection
        
        # Callbacks for UI state updates
        self.on_state_change: Optional[Callable] = None
        self.on_tts_start: Optional[Callable] = None
        self.on_tts_end: Optional[Callable] = None
        self.on_interruption: Optional[Callable] = None
    
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
        Process user input with real-time LLM streaming into TTS
        
        Args:
            user_text: The transcribed user input
        """
        logger.info(f"💬 Processing user input with streaming: '{user_text}'")
        
        # Prevent processing empty or very short inputs
        if not user_text or len(user_text.strip()) < 2:
            logger.info("Ignoring short or empty input")
            self._update_state("standby")
            return
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # Update to thinking state
        self._update_state("thinking")
        
        # Interrupt any current TTS
        self.interrupt_if_speaking()
        
        try:
            # Get streaming LLM response and feed directly into TTS
            if not llm_manager.is_ready():
                logger.error("LLM client not ready")
                self._update_state("standby", "LLM not ready")
                return
            
            await self._stream_llm_to_tts(user_text)
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            # Send error response
            error_message = "I'm sorry, I encountered an error processing your request."
            await self._synthesize_and_send(error_message)
    
    async def _stream_llm_to_tts(self, user_text: str):
        """
        Stream LLM response directly into TTS synthesis with smart sentence boundary detection
        
        Args:
            user_text: User input text
        """
        if not self.active_tts_ws:
            logger.warning("No active TTS WebSocket connection")
            self._update_state("standby", "No WebSocket connection")
            return

        if not tts_manager.is_ready():
            logger.error("TTS engine not ready")
            self._update_state("standby", "TTS engine not ready")
            return

        try:
            logger.info(f"🔄 Starting LLM-to-TTS streaming pipeline with smart boundaries")
            
            # Update to speaking state early
            self._update_state("speaking")
            
            # Signal TTS start
            if self.on_tts_start:
                self.on_tts_start()
            
            # Clear interrupt event
            self.interrupt_event.clear()
            
            # Reset audio buffer for new generation
            self.audio_buffer.reset()
            
            # Increment generation ID for tracking
            self.tts_generation_counter += 1
            self.current_generation_id = self.tts_generation_counter
            generation_id = self.current_generation_id
            
            logger.info(f"🔄 Starting smart streaming pipeline {generation_id}")
            
            # Send WAV header first
            wav_header = tts_manager.get_wave_header()
            await self.active_tts_ws.send_bytes(wav_header)
            
            # Create queues for the streaming pipeline
            llm_text_queue = asyncio.Queue()
            audio_queue = asyncio.Queue()
            
            # Pipeline control flags
            llm_complete = False
            tts_complete = False
            streaming_active = True
            quick_answer_sent = False
            
            # Accumulated response for conversation history and sentence detection
            full_llm_response = ""
            accumulated_text = ""
            
            # Task 1: Stream LLM tokens with smart sentence boundary detection
            async def stream_llm_tokens():
                nonlocal llm_complete, full_llm_response, accumulated_text, quick_answer_sent
                try:
                    logger.info(f"🤖 Starting smart LLM streaming for generation {generation_id}")
                    
                    async for token in llm_manager.get_streaming_response(user_text):
                        if self.interrupt_event.is_set():
                            logger.info(f"🛑 LLM streaming interrupted for generation {generation_id}")
                            break
                        
                        # Preprocess token (clean up artifacts)
                        clean_token = self._preprocess_token(token)
                        if not clean_token:
                            continue
                            
                        full_llm_response += clean_token
                        accumulated_text += clean_token
                        
                        # Check for sentence boundary for quick answer
                        if not quick_answer_sent:
                            context, remaining = self.text_context.get_context(accumulated_text)
                            if context:
                                logger.info(f"🎯 Quick answer found: '{context}'")
                                await llm_text_queue.put(("quick_answer", context))
                                accumulated_text = remaining or ""
                                quick_answer_sent = True
                                continue
                        
                        # Send token for continuous synthesis
                        await llm_text_queue.put(("token", clean_token))
                    
                    # Send any remaining text as final chunk
                    if accumulated_text.strip():
                        await llm_text_queue.put(("final_chunk", accumulated_text.strip()))
                    
                    # Signal end of LLM stream
                    await llm_text_queue.put(None)  # Sentinel
                    llm_complete = True
                    logger.info(f"🤖 Smart LLM streaming completed for generation {generation_id}")
                    
                except Exception as e:
                    logger.error(f"Error in smart LLM streaming: {e}")
                    await llm_text_queue.put(None)  # Ensure TTS knows to stop
                    llm_complete = True
            
            # Task 2: Process LLM tokens with smart TTS synthesis
            def synthesize_streaming_text():
                nonlocal tts_complete, streaming_active
                try:
                    from RealtimeTTS import TextToAudioStream
                    import asyncio
                    import threading
                    
                    # Create TTS stream
                    tts_stream = TextToAudioStream(tts_manager.engine, muted=True)
                    first_chunk_sent = False
                    
                    # Smart audio chunk callback with buffering
                    def on_audio_chunk(chunk):
                        nonlocal first_chunk_sent
                        if self.interrupt_event.is_set():
                            return
                        
                        try:
                            # Use smart buffering system optimized for Kokoro
                            chunks_to_send, first_chunk_fired = self.audio_buffer.add_chunk(chunk)
                            
                            # Send buffered chunks
                            loop = asyncio.get_event_loop()
                            for buffered_chunk in chunks_to_send:
                                asyncio.run_coroutine_threadsafe(audio_queue.put(buffered_chunk), loop)
                            
                            # Fire first chunk callback if needed
                            if first_chunk_fired and not first_chunk_sent:
                                first_chunk_sent = True
                                logger.info(f"🎵 First Kokoro audio chunk sent for generation {generation_id}")
                                
                        except Exception as e:
                            logger.error(f"Error in Kokoro audio buffering: {e}")
                    
                    # Create a smart text generator that handles different message types
                    def smart_text_generator():
                        sentence_buffer = ""
                        quick_answer_processed = False
                        
                        while True:
                            try:
                                # Get next message from LLM stream
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                
                                try:
                                    message = loop.run_until_complete(
                                        asyncio.wait_for(llm_text_queue.get(), timeout=1.0)
                                    )
                                except asyncio.TimeoutError:
                                    if llm_complete:
                                        break
                                    continue
                                finally:
                                    loop.close()
                                
                                if message is None:  # End of LLM stream
                                    # Yield any remaining text
                                    if sentence_buffer.strip():
                                        yield sentence_buffer.strip()
                                    break
                                
                                if self.interrupt_event.is_set():
                                    break
                                
                                # Handle different message types
                                if isinstance(message, tuple):
                                    msg_type, content = message
                                    
                                    if msg_type == "quick_answer" and not quick_answer_processed:
                                        # Prioritize quick answer for immediate synthesis
                                        logger.info(f"🚀 Processing quick answer: '{content[:50]}...'")
                                        yield content
                                        quick_answer_processed = True
                                        
                                    elif msg_type == "token":
                                        sentence_buffer += content
                                        
                                        # Check for sentence completion with more sophisticated logic
                                        if (len(sentence_buffer) > 30 and 
                                            any(punct in content for punct in ['.', '!', '?']) and
                                            len(sentence_buffer.split()) > 5):
                                            
                                            sentence_text = sentence_buffer.strip()
                                            if sentence_text:
                                                logger.debug(f"🎵 Yielding sentence: '{sentence_text[:50]}...'")
                                                yield sentence_text
                                                sentence_buffer = ""
                                        
                                        # Prevent overly long buffers
                                        elif len(sentence_buffer) > 300:
                                            sentence_text = sentence_buffer.strip()
                                            if sentence_text:
                                                logger.debug(f"🎵 Yielding long buffer: '{sentence_text[:50]}...'")
                                                yield sentence_text
                                                sentence_buffer = ""
                                                
                                    elif msg_type == "final_chunk":
                                        # Process final remaining text
                                        if content.strip():
                                            yield content.strip()
                                else:
                                    # Fallback for simple string messages
                                    sentence_buffer += str(message)
                                
                            except Exception as e:
                                logger.error(f"Error in smart text generator: {e}")
                                break
                    
                    # Start TTS synthesis with the smart text generator
                    logger.info(f"🎵 Starting smart TTS synthesis for generation {generation_id}")
                    tts_stream.feed(smart_text_generator())
                    tts_stream.play(
                        muted=True, 
                        on_audio_chunk=on_audio_chunk,
                        log_synthesized_text=True
                    )
                    
                    # Flush any remaining buffered chunks
                    remaining_chunks = self.audio_buffer.flush_remaining()
                    if remaining_chunks and not self.interrupt_event.is_set():
                        loop = asyncio.get_event_loop()
                        for chunk in remaining_chunks:
                            asyncio.run_coroutine_threadsafe(audio_queue.put(chunk), loop)
                    
                    # Signal end of TTS synthesis
                    if not self.interrupt_event.is_set():
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)  # Sentinel
                        logger.info(f"🎵 Smart TTS synthesis completed for generation {generation_id}")
                    
                except Exception as e:
                    logger.error(f"Error in smart TTS synthesis: {e}")
                finally:
                    tts_complete = True
                    streaming_active = False
                    # Ensure audio queue gets sentinel
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
                    except:
                        pass
            
            # Task 3: Stream audio chunks to client
            async def stream_audio_to_client():
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
                            # Check if both LLM and TTS are complete
                            if llm_complete and tts_complete:
                                break
                            continue
                    
                    # Send completion signal if not interrupted
                    if not self.interrupt_event.is_set():
                        await self.active_tts_ws.send_text("END")
                        logger.info(f"✅ Streaming pipeline completed for generation {generation_id} ({chunk_count} chunks)")
                    
                except Exception as e:
                    logger.error(f"Error in audio streaming to client: {e}")
                finally:
                    streaming_active = False
                    # Always reset to standby after completion
                    if not self.interrupt_event.is_set():
                        self._update_state("standby", "Ready to listen...")
                    
                    # Signal TTS end
                    if self.on_tts_end:
                        self.on_tts_end()
            
            # Start all pipeline tasks
            llm_task = asyncio.create_task(stream_llm_tokens())
            
            # Start TTS synthesis in thread
            self.active_synthesis_thread = threading.Thread(
                target=synthesize_streaming_text, 
                daemon=True
            )
            self.active_synthesis_thread.start()
            
            # Start audio streaming task
            audio_task = asyncio.create_task(stream_audio_to_client())
            
            # Wait for all tasks to complete
            await asyncio.gather(llm_task, audio_task, return_exceptions=True)
            
            # Add complete response to conversation history
            if full_llm_response.strip():
                self.conversation_history.append({"role": "assistant", "content": full_llm_response.strip()})
                logger.info(f"💬 Added complete response to history: '{full_llm_response[:50]}...'")
            
        except Exception as e:
            logger.error(f"Error in streaming pipeline: {e}")
            self._update_state("standby", "Pipeline error")
    
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
            
            # Create audio queue for real-time streaming
            audio_queue = asyncio.Queue()
            streaming_active = True
            
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
                    # Always reset to standby after TTS completion
                    if not self.interrupt_event.is_set():
                        self._update_state("standby", "Ready to listen...")
                    
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
                            # Use thread-safe method to put in asyncio queue
                            loop = asyncio.get_event_loop()
                            asyncio.run_coroutine_threadsafe(audio_queue.put(chunk), loop)
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
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)  # Sentinel
                        logger.info(f"🎵 Synthesis completed for generation {generation_id}")
                    
                except Exception as e:
                    logger.error(f"Error in real-time synthesis thread: {e}")
                finally:
                    # Ensure streaming task knows synthesis is done
                    nonlocal streaming_active
                    streaming_active = False
                    # Put sentinel to unblock streaming task
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(audio_queue.put(None), loop)
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