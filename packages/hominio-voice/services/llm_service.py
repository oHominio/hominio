"""
Large Language Model Service
Handles LLM client initialization and conversation management with reference-style streaming support
"""
import logging
import os
import openai
import asyncio
import uuid
import time
import threading
from typing import AsyncGenerator, Dict, Any, Optional
from core.config import Config
from .text_context import TextContext

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm_client = None
        self.conversation_history = []
        self.processed_sentences = set()
        self.system_prompt = self._load_system_prompt()
        self.text_context = TextContext()
        
        # Reference-style streaming state
        self.current_generation = None
        self.is_streaming = False
        self.was_interrupted = False
        
        # Request tracking for cancellation (like reference implementation)
        self._active_requests: Dict[str, Dict[str, Any]] = {}
        self._requests_lock = threading.Lock()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'system_prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()
            logger.info("✅ System prompt loaded successfully")
            return prompt
        except Exception as e:
            logger.warning(f"⚠️ Failed to load system prompt: {e}")
            # Fallback system prompt
            return "You are Hominio, a helpful and friendly AI voice assistant. Keep responses concise and conversational since they will be spoken aloud."
    
    async def initialize_llm_client(self):
        """Initialize LLM Client"""
        try:
            api_key = os.getenv("REDPILL_API_KEY")
            if not api_key:
                raise ValueError("REDPILL_API_KEY environment variable not set.")
            
            self.llm_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=Config.LLM_BASE_URL,
            )
            logger.info("✅ OpenAI client for RedPill initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM Client: {e}")
            raise
    
    def clear_conversation(self):
        """Clear conversation history and processed sentences"""
        self.conversation_history.clear()
        self.processed_sentences.clear()
        logger.info("🧹 Conversation history and processed sentences cleared")
    
    def is_sentence_processed(self, text: str) -> bool:
        """Check if sentence has already been processed"""
        return text in self.processed_sentences
    
    def mark_sentence_processed(self, text: str):
        """Mark sentence as processed to avoid duplicates"""
        self.processed_sentences.add(text)
    
    def _register_request(self, request_id: str, stream_obj: Any):
        """Register an active generation stream for cancellation tracking"""
        with self._requests_lock:
            if request_id in self._active_requests:
                logger.warning(f"🤖⚠️ Request ID {request_id} already registered. Overwriting.")
            self._active_requests[request_id] = {
                "stream": stream_obj,
                "start_time": time.time()
            }
            logger.debug(f"🤖ℹ️ Registered active request: {request_id} (Stream: {type(stream_obj)}, Count: {len(self._active_requests)})")
    
    def _unregister_request(self, request_id: str):
        """Remove request from tracking"""
        with self._requests_lock:
            request_data = self._active_requests.pop(request_id, None)
            if request_data:
                logger.debug(f"🤖🗑️ Unregistered request: {request_id}")
                return request_data
            return None
    
    def cancel_generation(self, request_id: Optional[str] = None) -> bool:
        """
        Cancel active generation streams with proper resource cleanup
        
        Args:
            request_id: Specific request to cancel, or None to cancel all
            
        Returns:
            True if at least one request was cancelled
        """
        cancelled_any = False
        with self._requests_lock:
            ids_to_cancel = []
            if request_id is None:
                if not self._active_requests:
                    logger.debug("🤖🗑️ Cancel all requested, but no active requests found.")
                    return False
                logger.info(f"🤖🗑️ Attempting to cancel ALL active generation requests ({len(self._active_requests)}).")
                ids_to_cancel = list(self._active_requests.keys())
            else:
                if request_id not in self._active_requests:
                    logger.warning(f"🤖🗑️ Cancel requested for ID '{request_id}', but it's not an active request.")
                    return False
                logger.info(f"🤖🗑️ Attempting to cancel generation request: {request_id}")
                ids_to_cancel.append(request_id)
            
            # Perform the cancellation
            for req_id in ids_to_cancel:
                if self._cancel_single_request_unsafe(req_id):
                    cancelled_any = True
        return cancelled_any
    
    def _cancel_single_request_unsafe(self, request_id: str) -> bool:
        """Internal helper to cancel a single request (thread-unsafe)"""
        request_data = self._active_requests.pop(request_id, None)
        if not request_data:
            logger.debug(f"🤖🗑️ Request {request_id} already removed before cancellation attempt.")
            return False
        
        stream_obj = request_data.get("stream")
        logger.debug(f"🤖🗑️ Cancelling request {request_id}. Stream object: {type(stream_obj)}")
        
        # Attempt to close the underlying stream
        if stream_obj:
            try:
                if hasattr(stream_obj, 'close') and callable(stream_obj.close):
                    logger.debug(f"🤖🗑️ [{request_id}] Attempting to close stream object...")
                    stream_obj.close()
                    logger.info(f"🤖🗑️ Closed stream for cancelled request {request_id}.")
                else:
                    logger.warning(f"🤖⚠️ [{request_id}] Stream object of type {type(stream_obj)} does not have a callable 'close' method.")
            except Exception as e:
                logger.error(f"🤖💥 Error closing stream for request {request_id}: {e}", exc_info=False)
        else:
            logger.warning(f"🤖⚠️ [{request_id}] No stream object found in request data to close.")
        
        logger.info(f"🤖🗑️ Removed generation request {request_id} from tracking (close attempted).")
        return True
    
    async def get_llm_response(self, user_text: str) -> str:
        """Get complete LLM response with conversation context (legacy method)"""
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_text})
            
            # Keep conversation history manageable (last 10 exchanges = 20 messages)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Build messages with system prompt + conversation history
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history

            # Use the full conversation history for context
            response = await self.llm_client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,  # Send system prompt + conversation context
                stream=False  # Get complete response
            )
            content = response.choices[0].message.content
            logger.info(f"🤖 LLM response: '{content}'")
            
            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": content})
            
            return content
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return "I'm sorry, I encountered an error."
    
    async def get_streaming_llm_response(self, user_text: str, on_quick_context=None, on_token=None) -> AsyncGenerator[str, None]:
        """
        Get streaming LLM response with reference-style context detection for TTS
        Enhanced with proper cancellation support and request tracking
        
        Args:
            user_text: User input text
            on_quick_context: Callback when a quick context (sentence boundary) is found
            on_token: Callback for each token (for real-time updates)
        
        Yields:
            str: Individual tokens from the LLM response
        """
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        # Generate unique request ID for tracking
        request_id = f"llm-stream-{uuid.uuid4()}"
        stream = None
        
        try:
            self.is_streaming = True
            self.was_interrupted = False
            
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_text})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Build messages with system prompt + conversation history
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history

            logger.info(f"🤖 [{request_id}] Starting reference-style streaming LLM response for: '{user_text[:50]}...'")
            
            # Create streaming response
            stream = await self.llm_client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                stream=True,  # Enable streaming
                temperature=0.7,
                max_tokens=1000
            )
            
            # Register stream for cancellation tracking
            self._register_request(request_id, stream)
            
            # Reference-style streaming state
            accumulated_text = ""
            quick_context_found = False
            quick_context_text = ""
            quick_context_overhang = ""
            token_count = 0
            
            async for chunk in stream:
                # Check for cancellation before processing each chunk
                with self._requests_lock:
                    if request_id not in self._active_requests:
                        logger.info(f"🤖🗑️ Stream {request_id} cancelled externally during iteration.")
                        break
                
                if not self.is_streaming:
                    logger.info(f"🤖🛑 [{request_id}] Streaming stopped by external request")
                    break
                    
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    token_count += 1
                    accumulated_text += token
                    
                    # Log first token (TTFT - Time To First Token)
                    if token_count == 1:
                        logger.info(f"🤖 [{request_id}] TTFT: First token received")
                    
                    # Preprocess token for TTS compatibility
                    preprocessed_token = self.preprocess_chunk(token)
                    
                    # Call token callback for real-time updates
                    if on_token:
                        try:
                            await on_token(preprocessed_token, accumulated_text)
                        except Exception as e:
                            logger.error(f"Error in token callback: {e}")
                    
                    # Check for quick context (sentence boundary) - reference pattern
                    if not quick_context_found and len(accumulated_text) > 20:
                        context, overhang = self.text_context.get_context(accumulated_text)
                        if context:
                            logger.info(f"🧠 [{request_id}] QUICK ANSWER FOUND: '{context}', overhang: '{overhang}'")
                            quick_context_found = True
                            quick_context_text = context
                            quick_context_overhang = overhang
                            
                            # Call quick context callback for immediate TTS (reference pattern)
                            if on_quick_context:
                                try:
                                    await on_quick_context(context, overhang)
                                except Exception as e:
                                    logger.error(f"Error in quick context callback: {e}")
                            
                            # Continue streaming - don't break here (reference pattern)
                            # The remaining tokens will be handled by final TTS
                    
                    yield preprocessed_token
            
            # Handle case where no quick context was found (reference pattern)
            if not quick_context_found and accumulated_text.strip():
                logger.info(f"🧠 [{request_id}] No quick context found, using full response as quick answer: '{accumulated_text[:50]}...'")
                if on_quick_context:
                    try:
                        await on_quick_context(accumulated_text, "")
                    except Exception as e:
                        logger.error(f"Error in final context callback: {e}")
            
            # Add assistant response to conversation history ONLY if not interrupted
            if accumulated_text.strip() and not self.was_interrupted:
                self.conversation_history.append({"role": "assistant", "content": accumulated_text})
                logger.info(f"🤖 [{request_id}] Reference-style streaming complete. Generated {token_count} tokens: '{accumulated_text[:100]}...'")
            elif self.was_interrupted:
                logger.info(f"🤖🛑 [{request_id}] Response was interrupted - NOT adding to conversation history: '{accumulated_text[:100]}...'")
            
        except Exception as e:
            # Check if this was due to cancellation
            is_cancelled = False
            with self._requests_lock:
                is_cancelled = request_id not in self._active_requests
            
            if is_cancelled:
                logger.warning(f"🤖⚠️ [{request_id}] Stream error likely due to cancellation: {e}")
            else:
                logger.error(f"🤖💥 [{request_id}] Error in reference-style streaming LLM response: {e}")
                yield "I'm sorry, I encountered an error while processing your request."
        finally:
            self.is_streaming = False
            
            # Ensure stream is closed and unregistered
            if stream and hasattr(stream, 'close'):
                try:
                    logger.debug(f"🤖🗑️ [{request_id}] Closing stream in finally block.")
                    stream.close()
                except Exception as close_err:
                    logger.warning(f"🤖⚠️ [{request_id}] Error closing stream in finally: {close_err}", exc_info=False)
            
            # Unregister request
            self._unregister_request(request_id)
    
    def stop_streaming(self):
        """Stop current streaming generation with enhanced cancellation"""
        if self.is_streaming:
            logger.info("🤖🛑 Stopping reference-style LLM streaming - marking as interrupted")
            self.is_streaming = False
            self.was_interrupted = True
            
            # Cancel all active requests
            self.cancel_generation()
    
    def preprocess_chunk(self, chunk: str) -> str:
        """
        Preprocess a text chunk before TTS synthesis (reference pattern)
        
        Args:
            chunk: The input text chunk
            
        Returns:
            The preprocessed text chunk
        """
        return chunk.replace("—", "-").replace(""", '"').replace(""", '"').replace("'", "'").replace("'", "'").replace("…", "...")
    
    def get_conversation_status(self):
        """Get current conversation status"""
        return {
            "conversation_length": len(self.conversation_history),
            "processed_sentences_count": len(self.processed_sentences),
            "conversation_history": self.conversation_history[-10:] if self.conversation_history else [],  # Last 10 messages for preview
            "system_prompt": self.system_prompt[:100] + "..." if len(self.system_prompt) > 100 else self.system_prompt,
            "is_streaming": self.is_streaming,
            "active_requests": len(self._active_requests),
            "reference_style": True
        }
    
    def reload_system_prompt(self):
        """Reload system prompt from file (useful for updates)"""
        self.system_prompt = self._load_system_prompt()
        logger.info("🔄 System prompt reloaded")
    
    def is_ready(self):
        """Check if LLM service is ready"""
        return self.llm_client is not None 
    
    def cleanup_stale_requests(self, timeout_seconds: int = 300):
        """Clean up requests older than the specified timeout"""
        stale_ids = []
        now = time.time()
        
        with self._requests_lock:
            stale_ids = [
                req_id for req_id, req_data in self._active_requests.items()
                if (now - req_data.get("start_time", 0)) > timeout_seconds
            ]
        
        if stale_ids:
            logger.info(f"🤖🧹 Found {len(stale_ids)} potentially stale requests (>{timeout_seconds}s). Cleaning up...")
            cleaned_count = 0
            for req_id in stale_ids:
                if self.cancel_generation(req_id):
                    cleaned_count += 1
            logger.info(f"🤖🧹 Cleaned up {cleaned_count}/{len(stale_ids)} stale requests.")
            return cleaned_count
        return 0 