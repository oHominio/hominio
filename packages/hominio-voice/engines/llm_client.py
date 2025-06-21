"""
LLM Client Management
Handles OpenAI-compatible API client initialization and management
"""
import logging
import openai
from typing import Optional, AsyncGenerator, Dict, Any

from core.config import Config

logger = logging.getLogger(__name__)


class LLMClientManager:
    """Manages LLM client initialization and operations"""
    
    def __init__(self):
        self.client: Optional[openai.AsyncOpenAI] = None
        self._is_ready = False
    
    async def initialize(self) -> bool:
        """Initialize the LLM client"""
        try:
            logger.info("🤖 Initializing LLM client...")
            
            if not Config.LLM_API_KEY:
                raise ValueError("REDPILL_API_KEY environment variable not set")
            
            # Initialize OpenAI-compatible client
            self.client = openai.AsyncOpenAI(
                api_key=Config.LLM_API_KEY,
                base_url=Config.LLM_BASE_URL
            )
            
            # Test the client with a simple request
            if await self._test_client():
                self._is_ready = True
                logger.info("✅ LLM client initialized successfully")
                return True
            else:
                raise Exception("Client test failed")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            return False
    
    async def _test_client(self) -> bool:
        """Test the LLM client with a simple request"""
        try:
            response = await self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": "Say 'OK' if you can hear me."}],
                max_tokens=10,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            logger.info(f"✅ LLM client test successful - response: '{content}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ LLM client test error: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if the client is ready"""
        return self._is_ready and self.client is not None
    
    async def get_response(self, user_text: str, stream: bool = False) -> str:
        """
        Get response from LLM
        
        Args:
            user_text: User input text
            stream: Whether to stream the response
            
        Returns:
            Complete response text
        """
        if not self.is_ready():
            raise RuntimeError("LLM client not ready")
        
        try:
            logger.info(f"🤖 Getting LLM response for: '{user_text[:50]}...'")
            
            response = await self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": user_text}],
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                full_response = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                # Handle non-streaming response
                content = response.choices[0].message.content
                logger.info(f"🤖 LLM response: '{content[:100]}...'")
                return content
                
        except Exception as e:
            logger.error(f"❌ Error getting LLM response: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    async def get_streaming_response(self, user_text: str) -> AsyncGenerator[str, None]:
        """
        Get streaming response from LLM
        
        Args:
            user_text: User input text
            
        Yields:
            Response chunks as they arrive
        """
        if not self.is_ready():
            raise RuntimeError("LLM client not ready")
        
        try:
            logger.info(f"🤖 Getting streaming LLM response for: '{user_text[:50]}...'")
            
            response = await self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": user_text}],
                stream=True
            )
            
            async for chunk in response:
                # Add safety checks for chunk structure
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content') and choice.delta.content:
                        yield choice.delta.content
                    
        except Exception as e:
            logger.error(f"❌ Error getting streaming LLM response: {e}")
            yield "I'm sorry, I encountered an error processing your request."
    
    def shutdown(self):
        """Shutdown the LLM client"""
        try:
            if self.client:
                # AsyncOpenAI doesn't have explicit shutdown, just clear reference
                self.client = None
                logger.info("🤖 LLM client shutdown")
        except Exception as e:
            logger.error(f"Error shutting down LLM client: {e}")
        finally:
            self._is_ready = False


# Global LLM client manager instance
llm_manager = LLMClientManager() 