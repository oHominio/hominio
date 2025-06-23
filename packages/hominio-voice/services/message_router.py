"""
Message Router Service
Handles routing messages between STT, TTS, and LLM services
"""
import logging
import json
import asyncio
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class MessageRouter:
    def __init__(self):
        self.stt_service = None
        self.tts_service = None
        self.llm_service = None
        self.websocket_queue = None
        self.event_loop = None
        
    def initialize(self, stt_service, tts_service, llm_service, websocket_queue, event_loop):
        """Initialize the router with service references"""
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.llm_service = llm_service
        self.websocket_queue = websocket_queue
        self.event_loop = event_loop
        
        # Set up service callbacks
        self._setup_service_callbacks()
        logger.info("✅ Message router initialized")
    
    def _setup_service_callbacks(self):
        """Set up callbacks between services"""
        # STT callbacks
        if self.stt_service:
            self.stt_service.set_callbacks(
                on_full_sentence=self._handle_full_sentence,
                on_realtime_transcription=self._handle_realtime_transcription
            )
    
    async def _handle_full_sentence(self, text: str):
        """Handle full sentence from STT -> trigger LLM -> TTS"""
        logger.info(f"🎤 Full sentence: '{text}'")
        
        # Send to WebSocket
        await self._send_to_websocket({
            'type': 'fullSentence',
            'text': text
        })
        
        # Check for duplicates
        if self.llm_service and self.llm_service.is_sentence_processed(text):
            logger.info(f"🔄 Skipping duplicate sentence: '{text}'")
            return
            
        if self.llm_service:
            self.llm_service.mark_sentence_processed(text)
        
        # Process with LLM
        if self.llm_service and self.llm_service.is_ready():
            try:
                llm_response = await self.llm_service.get_llm_response(text)
                # Trigger TTS synthesis
                await self._handle_tts_request(llm_response)
            except Exception as e:
                logger.error(f"Error in LLM processing: {e}")
        else:
            logger.warning("LLM service not available")
    
    def _handle_realtime_transcription(self, text: str):
        """Handle realtime transcription from STT"""
        logger.debug(f"🔄 Realtime: '{text}'")
        
        # Clean up text
        text = text.lstrip()
        if text.startswith("..."):
            text = text[3:]
        if text.endswith("...'."):
            text = text[:-1]
        if text.endswith("...'"):
            text = text[:-1]
        text = text.lstrip()
        if text:
            text = text[0].upper() + text[1:]
        
        # Send to WebSocket
        asyncio.run_coroutine_threadsafe(
            self._send_to_websocket({
                'type': 'realtime',
                'text': text
            }),
            self.event_loop
        )
    
    async def _handle_tts_request(self, text: str, websocket=None):
        """Handle TTS synthesis request"""
        if self.tts_service and self.tts_service.is_ready():
            # Get the active WebSocket from main.py globals if not provided
            if not websocket:
                # Import here to avoid circular imports
                import __main__
                websocket = getattr(__main__, 'active_tts_ws', None)
            
            if websocket:
                logger.info(f"🔊 Synthesizing: '{text[:50]}...'")
                await self.tts_service.synthesize_text(text, websocket)
            else:
                logger.warning("No active WebSocket for TTS")
        else:
            logger.warning("TTS service not available")
    
    async def _send_to_websocket(self, message: Dict[str, Any]):
        """Send message to WebSocket queue"""
        if self.websocket_queue:
            try:
                await self.websocket_queue.put(json.dumps(message))
                logger.debug(f"📤 Queued message: {message['type']}")
            except Exception as e:
                logger.error(f"Error queuing message: {e}")
    
    async def route_websocket_message(self, message_type: str, data: Dict[str, Any], websocket):
        """Route incoming WebSocket messages to appropriate services"""
        try:
            if message_type == "stt-command":
                # Route to STT service
                command = data.get("command")
                logger.info(f"📥 Routing STT command: {command}")
                # STT service handles its own commands
                
            elif message_type == "tts-synthesize":
                # Route to TTS service
                text = data.get("text", "")
                if text.strip() and self.tts_service and self.tts_service.is_ready():
                    logger.info(f"📥 Routing TTS synthesis: {text[:50]}...")
                    await self.tts_service.synthesize_text(text, websocket)
                    
            elif message_type == "ping":
                # Handle ping/pong
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }))
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error routing message {message_type}: {e}")
    
    def get_status(self):
        """Get router status"""
        return {
            "stt_connected": self.stt_service is not None,
            "tts_connected": self.tts_service is not None,
            "llm_connected": self.llm_service is not None,
            "websocket_connected": self.websocket_queue is not None
        } 