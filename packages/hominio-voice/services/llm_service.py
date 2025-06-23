"""
Large Language Model Service
Handles LLM client initialization and conversation management
"""
import logging
import os
import openai
from core.config import Config

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm_client = None
        self.conversation_history = []
        self.processed_sentences = set()
        self.system_prompt = self._load_system_prompt()
    
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
        """Get complete LLM response with conversation context"""
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
    
    def get_conversation_status(self):
        """Get current conversation status"""
        return {
            "conversation_length": len(self.conversation_history),
            "processed_sentences_count": len(self.processed_sentences),
            "conversation_history": self.conversation_history[-10:] if self.conversation_history else [],  # Last 10 messages for preview
            "system_prompt": self.system_prompt[:100] + "..." if len(self.system_prompt) > 100 else self.system_prompt
        }
    
    def reload_system_prompt(self):
        """Reload system prompt from file (useful for updates)"""
        self.system_prompt = self._load_system_prompt()
        logger.info("🔄 System prompt reloaded")
    
    def is_ready(self):
        """Check if LLM service is ready"""
        return self.llm_client is not None 