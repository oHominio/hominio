"""
Message Router Service - Master Coordinator
Single source of truth for all WebSocket communication and service coordination
Handles routing messages between STT, TTS, and LLM services with streaming support
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
        
        # Streaming state - reference implementation pattern
        self.current_streaming_task = None
        self.is_processing_stream = False
        
    def initialize(self, stt_service, tts_service, llm_service, websocket_queue, event_loop):
        """Initialize the router as master coordinator with service references"""
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.llm_service = llm_service
        self.websocket_queue = websocket_queue
        self.event_loop = event_loop
        
        # Set up service coordination (single source of truth)
        self._setup_service_coordination()
        logger.info("✅ [Router] Message router initialized as master coordinator")
    
    def _setup_service_coordination(self):
        """Set up service coordination - router is the single source of truth"""
        # Set router references in all services
        if self.stt_service and hasattr(self.stt_service, 'set_message_router'):
            self.stt_service.set_message_router(self)
        
        if self.tts_service and hasattr(self.tts_service, 'set_message_router'):
            # Set TTS service router reference with WebSocket callback
            self.tts_service.set_message_router(self, self._send_websocket_message)
        
        # Set up STT callbacks - router handles all STT output
        if self.stt_service:
            self.stt_service.set_callbacks(
                on_full_sentence=self._handle_full_sentence,
                on_realtime_transcription=self._handle_realtime_transcription
            )
            
        logger.info("✅ [Router] Service coordination established - router is single source of truth")
    
    async def _send_websocket_message(self, message):
        """
        Router's WebSocket send method - single source of truth for all WebSocket communication
        
        Args:
            message: Message to send (dict or string)
        """
        if isinstance(message, dict):
            await self._send_to_websocket(message)
        else:
            # Handle text messages (like end markers)
            await self._send_to_websocket({"type": "text", "content": message})
    
    async def _handle_full_sentence(self, text: str):
        """Handle full sentence from STT -> coordinate LLM+TTS pipeline"""
        logger.info(f"🎤 [Router] Full sentence received: '{text}'")
        
        # Send to WebSocket for UI updates
        await self._send_to_websocket({
            'type': 'fullSentence',
            'text': text
        })
        
        # Check for duplicates (router coordinates duplicate detection)
        if self.llm_service and self.llm_service.is_sentence_processed(text):
            logger.info(f"🔄 [Router] Skipping duplicate sentence: '{text}'")
            return
            
        if self.llm_service:
            self.llm_service.mark_sentence_processed(text)
        
        # Stop any current streaming (router controls streaming state)
        if self.is_processing_stream:
            logger.info("🛑 [Router] Stopping current streaming for new request")
            await self._stop_current_streaming()
        
        # Start reference-style streaming pipeline (router coordinates the flow)
        await self._start_reference_streaming_pipeline(text)
    
    async def _start_reference_streaming_pipeline(self, text: str):
        """
        Router coordinates the complete pipeline:
        1. LLM streams tokens (router manages)
        2. Context detection finds boundaries (router handles)
        3. Quick TTS synthesis (router triggers)
        4. Final TTS synthesis (router manages)
        """
        if not self.llm_service or not self.llm_service.is_ready():
            logger.warning("[Router] LLM service not available")
            return
            
        self.is_processing_stream = True
        logger.info(f"🚀 [Router] Starting coordinated streaming pipeline for: '{text[:50]}...'")
        
        try:
            # Get active WebSocket (router manages all WebSocket communication)
            import __main__
            websocket = getattr(__main__, 'active_tts_ws', None)
            
            if not websocket:
                logger.warning("[Router] No active WebSocket for streaming")
                return
            
            # Pipeline state - router manages the complete flow
            quick_answer = ""
            quick_answer_provided = False
            quick_answer_overhang = ""
            accumulated_tokens = []
            
            async def on_quick_context(context: str, remaining: str):
                """Router handles quick context detection and triggers TTS"""
                nonlocal quick_answer, quick_answer_provided, quick_answer_overhang
                
                if quick_answer_provided:
                    return  # Already handled
                    
                logger.info(f"⚡ [Router] Quick context detected: '{context}', remaining: '{remaining}'")
                quick_answer = context
                quick_answer_overhang = remaining
                quick_answer_provided = True
                
                # Router sends quick context updates
                await self._send_to_websocket({
                    'type': 'quickContext',
                    'text': context,
                    'remaining': len(remaining) > 0
                })
                
                # Router triggers immediate TTS synthesis (routed through single source)
                if self.tts_service and self.tts_service.is_ready():
                    logger.info(f"🔊 [Router] Triggering quick TTS synthesis: '{context[:30]}...'")
                    await self.tts_service.synthesize_text(context, None, "QUICK_END")
                    
            async def on_token(token: str, full_text: str):
                """Router handles token streaming updates"""
                accumulated_tokens.append(token)
                
                # Router sends real-time updates
                await self._send_to_websocket({
                    'type': 'streamingToken',
                    'token': token,
                    'fullText': full_text[:100] + "..." if len(full_text) > 100 else full_text
                })
            
            # Router coordinates LLM streaming
            logger.info("🤖 [Router] Starting coordinated LLM token streaming...")
            full_response = ""
            token_count = 0
            
            async for token in self.llm_service.get_streaming_llm_response(
                text, 
                on_quick_context=on_quick_context,
                on_token=on_token
            ):
                if not self.is_processing_stream:
                    logger.info("🛑 [Router] Streaming stopped by coordinator")
                    break
                    
                full_response += token
                token_count += 1
                
                # Log timing metrics
                if token_count == 1:
                    logger.info(f"🤖 [Router] First token received (TTFT)")
            
            logger.info(f"🤖 [Router] LLM streaming completed. Generated {token_count} tokens")
            logger.info(f"🤖 [Router] Full response: '{full_response[:100]}...'")
            logger.info(f"🤖 [Router] Quick answer: '{quick_answer}'")
            logger.info(f"🤖 [Router] Quick answer provided: {quick_answer_provided}")
            
            # Router handles final TTS coordination - FIXED LOGIC
            if quick_answer_provided:
                # Calculate remaining text that wasn't in quick answer
                remaining_text = ""
                
                if quick_answer_overhang.strip():
                    # Use the overhang from context detection
                    remaining_text = quick_answer_overhang
                    logger.info(f"🔊 [Router] Using overhang: '{remaining_text[:50]}...'")
                
                # Check if there's additional text beyond quick_answer + overhang
                quick_plus_overhang = quick_answer + quick_answer_overhang
                if len(full_response) > len(quick_plus_overhang):
                    additional_text = full_response[len(quick_plus_overhang):]
                    remaining_text += additional_text
                    logger.info(f"🔊 [Router] Added additional text: '{additional_text[:50]}...'")
                
                if remaining_text.strip():
                    logger.info(f"🔊 [Router] Triggering final TTS synthesis: '{remaining_text[:50]}...'")
                    preprocessed_final = self.llm_service.preprocess_chunk(remaining_text)
                    await self.tts_service.synthesize_text_streaming(preprocessed_final, None)
                else:
                    logger.info("🔊 [Router] No remaining text for final TTS")
                    
            elif full_response.strip():
                # No quick context was found, synthesize the complete response
                logger.info(f"🔊 [Router] No quick context found, synthesizing complete response: '{full_response[:50]}...'")
                preprocessed_response = self.llm_service.preprocess_chunk(full_response)
                await self.tts_service.synthesize_text_streaming(preprocessed_response, None)
            else:
                logger.info("🔊 [Router] No response text to synthesize")
            
            # Router sends completion signal
            await self._send_to_websocket({
                'type': 'streamingComplete',
                'fullResponse': full_response,
                'quickAnswer': quick_answer,
                'finalAnswer': remaining_text if 'remaining_text' in locals() else ""
            })
            
            logger.info("✅ [Router] Coordinated streaming pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"❌ [Router] Error in coordinated streaming pipeline: {e}")
            await self._send_to_websocket({
                'type': 'error',
                'message': f"Streaming error: {str(e)}"
            })
            
            # Router handles error cleanup
            await self._send_websocket_message("ERROR")
        finally:
            self.is_processing_stream = False
    
    async def _stop_current_streaming(self):
        """Router stops all streaming operations"""
        if self.current_streaming_task and not self.current_streaming_task.done():
            self.current_streaming_task.cancel()
            try:
                await self.current_streaming_task
            except asyncio.CancelledError:
                pass
        
        if self.llm_service:
            self.llm_service.stop_streaming()
            
        self.is_processing_stream = False
        logger.info("🛑 [Router] All streaming operations stopped")
    
    def _handle_realtime_transcription(self, text: str):
        """Router handles realtime transcription coordination"""
        logger.debug(f"🔄 [Router] Realtime transcription: '{text}'")
        
        # Router manages text cleanup
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
        
        # Router sends to WebSocket
        asyncio.run_coroutine_threadsafe(
            self._send_to_websocket({
                'type': 'realtime',
                'text': text
            }),
            self.event_loop
        )
    
    async def _send_to_websocket(self, message: Dict[str, Any]):
        """Router manages all WebSocket communication"""
        if self.websocket_queue:
            try:
                await self.websocket_queue.put(json.dumps(message))
                logger.debug(f"📤 [Router] Queued message: {message['type']}")
            except Exception as e:
                logger.error(f"❌ [Router] Error queuing message: {e}")
    
    async def route_websocket_message(self, message_type: str, data: Dict[str, Any], websocket):
        """Router routes incoming WebSocket messages to appropriate services"""
        try:
            logger.info(f"📥 [Router] Routing message: {message_type}")
            
            if message_type == "stt-command":
                # Router handles STT commands
                command = data.get("command")
                logger.info(f"📥 [Router] STT command: {command}")
                # STT service handles its own commands through router coordination
                
            elif message_type == "tts-synthesize":
                # Router handles TTS requests (legacy endpoint)
                text = data.get("text", "")
                if text.strip() and self.tts_service and self.tts_service.is_ready():
                    logger.info(f"📥 [Router] TTS synthesis: {text[:50]}...")
                    await self.tts_service.synthesize_text(text, None)
                    
            elif message_type == "stop-streaming":
                # Router handles streaming control
                logger.info("📥 [Router] Stopping streaming operation")
                await self._stop_current_streaming()
                    
            elif message_type == "ping":
                # Router handles ping/pong
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }))
                
            else:
                logger.warning(f"⚠️ [Router] Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"❌ [Router] Error routing message {message_type}: {e}")
    
    def get_status(self):
        """Get router coordination status"""
        return {
            "role": "master_coordinator",
            "single_source_of_truth": True,
            "stt_connected": self.stt_service is not None,
            "tts_connected": self.tts_service is not None,
            "llm_connected": self.llm_service is not None,
            "websocket_connected": self.websocket_queue is not None,
            "is_streaming": self.is_processing_stream,
            "streaming_supported": True,
            "reference_style": True,
            "service_coordination": {
                "stt_router_ref": getattr(self.stt_service, 'message_router', None) is not None,
                "tts_router_ref": getattr(self.tts_service, 'message_router', None) is not None,
                "stt_callbacks_set": bool(getattr(self.stt_service, 'on_full_sentence_callback', None)),
                "tts_websocket_callback": getattr(self.tts_service, 'websocket_send_callback', None) is not None
            }
        } 