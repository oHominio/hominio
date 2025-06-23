"""
Message Router Service - Pure Communication Hub
Single source of truth for WebSocket communication with NO orchestration logic
Routes messages between services without any business logic
"""
import logging
import json
import asyncio
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class MessageRouter:
    def __init__(self):
        # Service references
        self.stt_service = None
        self.tts_service = None
        self.llm_service = None
        self.speech_pipeline = None  # The orchestrator
        
        # WebSocket state
        self.websocket_queue = None
        self.event_loop = None
        
    def initialize_services(self, stt_service, tts_service, llm_service, speech_pipeline):
        """Initialize service references - pure dependency injection"""
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.llm_service = llm_service
        self.speech_pipeline = speech_pipeline
        
        # Set message router references in services for communication
        if hasattr(self.stt_service, 'set_message_router'):
            self.stt_service.set_message_router(self)
        if hasattr(self.tts_service, 'set_message_router'):
            self.tts_service.set_message_router(self, self.send_websocket_message)
        if hasattr(self.speech_pipeline, 'set_message_router'):
            self.speech_pipeline.set_message_router(self)
            
        logger.info("✅ [Router] Services initialized - pure communication hub ready with TTS WebSocket callback")
    
    def set_websocket_queue(self, queue, loop):
        """Set WebSocket queue for outbound messages"""
        self.websocket_queue = queue
        self.event_loop = loop
        logger.info("✅ [Router] WebSocket queue configured")
    
    async def handle_websocket_message(self, message_data: Dict[str, Any]):
        """
        Pure message routing - NO business logic
        Routes incoming WebSocket messages to appropriate handlers
        """
        message_type = message_data.get("type")
        
        if not message_type:
            logger.warning("⚠️ [Router] Message missing type field")
            return
        
        logger.debug(f"🔄 [Router] Routing message type: {message_type}")
        
        # Route to speech pipeline (the orchestrator)
        if self.speech_pipeline and hasattr(self.speech_pipeline, 'handle_message'):
            try:
                await self.speech_pipeline.handle_message(message_data)
            except Exception as e:
                logger.error(f"❌ [Router] Error routing to speech pipeline: {e}")
        else:
            logger.warning("⚠️ [Router] No speech pipeline available for message routing")
    
    async def send_websocket_message(self, message: Dict[str, Any]):
        """
        Pure message sending - NO business logic
        Sends messages through WebSocket queue
        """
        if not self.websocket_queue or not self.event_loop:
            logger.error("❌ [Router] WebSocket queue not configured")
            return False
        
        try:
            await self.websocket_queue.put(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"❌ [Router] Error sending WebSocket message: {e}")
            return False
    
    def _send_websocket_message(self, message: Dict[str, Any]):
        """
        Synchronous wrapper for WebSocket sending
        Used by services that need sync interface
        """
        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                self.send_websocket_message(message),
                self.event_loop
            )
    
    def get_status(self):
        """Get router status - pure state reporting"""
        return {
            "services_connected": {
                "stt": self.stt_service is not None,
                "tts": self.tts_service is not None, 
                "llm": self.llm_service is not None,
                "speech_pipeline": self.speech_pipeline is not None
            },
            "websocket_configured": self.websocket_queue is not None,
            "role": "pure_communication_hub"
        } 