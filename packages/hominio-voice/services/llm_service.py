"""
Large Language Model Service
Handles LLM client initialization and conversation management with reference-style streaming support
"""
import logging
import os
import openai
import asyncio
from typing import AsyncGenerator, Dict, Any
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
        
        Reference implementation pattern:
        1. Stream tokens one by one
        2. Check for sentence boundary (quick context) 
        3. When found, trigger quick TTS immediately
        4. Continue streaming remaining tokens
        5. Final TTS handles remaining text
        
        Args:
            user_text: User input text
            on_quick_context: Callback when a quick context (sentence boundary) is found
            on_token: Callback for each token (for real-time updates)
        
        Yields:
            str: Individual tokens from the LLM response
        """
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        try:
            self.is_streaming = True
            
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_text})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Build messages with system prompt + conversation history
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history

            logger.info(f"🤖 Starting reference-style streaming LLM response for: '{user_text[:50]}...'")
            
            # Create streaming response
            stream = await self.llm_client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                stream=True,  # Enable streaming
                temperature=0.7,
                max_tokens=1000
            )
            
            # Reference-style streaming state
            accumulated_text = ""
            quick_context_found = False
            quick_context_text = ""
            quick_context_overhang = ""
            token_count = 0
            
            async for chunk in stream:
                if not self.is_streaming:
                    logger.info("🤖 Streaming stopped by external request")
                    break
                    
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    token_count += 1
                    accumulated_text += token
                    
                    # Log first token (TTFT - Time To First Token)
                    if token_count == 1:
                        logger.info(f"🤖 TTFT: First token received")
                    
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
                            logger.info(f"🧠 QUICK ANSWER FOUND: '{context}', overhang: '{overhang}'")
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
                logger.info(f"🧠 No quick context found, using full response as quick answer: '{accumulated_text[:50]}...'")
                if on_quick_context:
                    try:
                        await on_quick_context(accumulated_text, "")
                    except Exception as e:
                        logger.error(f"Error in final context callback: {e}")
            
            # Add assistant response to conversation history
            if accumulated_text.strip():
                self.conversation_history.append({"role": "assistant", "content": accumulated_text})
                logger.info(f"🤖 Reference-style streaming complete. Generated {token_count} tokens: '{accumulated_text[:100]}...'")
            
        except Exception as e:
            logger.error(f"Error in reference-style streaming LLM response: {e}")
            yield "I'm sorry, I encountered an error while processing your request."
        finally:
            self.is_streaming = False
    
    def stop_streaming(self):
        """Stop current streaming generation"""
        if self.is_streaming:
            logger.info("🤖 Stopping reference-style LLM streaming")
            self.is_streaming = False
    
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
            "reference_style": True
        }
    
    def reload_system_prompt(self):
        """Reload system prompt from file (useful for updates)"""
        self.system_prompt = self._load_system_prompt()
        logger.info("🔄 System prompt reloaded")
    
    def is_ready(self):
        """Check if LLM service is ready"""
        return self.llm_client is not None 