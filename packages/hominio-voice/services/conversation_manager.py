"""
Conversation Manager
Handles the conversation flow with interruption detection and management
"""
import logging
import asyncio
import threading
import json
from typing import Optional, Callable, Dict, Any, List
from fastapi import WebSocket

from engines.tts_engine import tts_manager
from engines.llm_client import llm_manager

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation flow with interruption handling"""
    
    def __init__(self):
        self.active_tts_ws: Optional[WebSocket] = None
        self.is_speaking = False
        self.is_listening = False
        self.current_generation_id = 0
        self.active_synthesis_thread: Optional[threading.Thread] = None
        self.interrupt_event = threading.Event()
        
        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        
        # Callbacks
        self.on_tts_start: Optional[Callable] = None
        self.on_tts_end: Optional[Callable] = None
        self.on_interruption: Optional[Callable] = None
    
    def set_active_tts_websocket(self, websocket: Optional[WebSocket]):
        """Set the active TTS WebSocket connection"""
        self.active_tts_ws = websocket
        if websocket:
            logger.info("🔊 Active TTS WebSocket connection set")
        else:
            logger.info("🔊 Active TTS WebSocket connection cleared")
    
    def start_listening(self):
        """Signal that we're listening for user input"""
        self.is_listening = True
        logger.info("👂 Started listening")
    
    def stop_listening(self):
        """Signal that we've stopped listening"""
        self.is_listening = False
        logger.info("👂 Stopped listening")
    
    def interrupt_if_speaking(self):
        """Interrupt current TTS if we're speaking"""
        if self.is_speaking:
            logger.info("🛑 Interrupting current TTS synthesis")
            self.interrupt_event.set()
            
            # Stop current synthesis thread
            if self.active_synthesis_thread and self.active_synthesis_thread.is_alive():
                # Signal interruption and wait briefly for thread to stop
                self.active_synthesis_thread.join(timeout=1.0)
            
            self.is_speaking = False
            
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
        Process user input and generate response
        
        Args:
            user_text: The transcribed user input
        """
        logger.info(f"💬 Processing user input: '{user_text}'")
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # Stop listening
        self.stop_listening()
        
        # Interrupt any current TTS
        self.interrupt_if_speaking()
        
        try:
            # Get LLM response
            if not llm_manager.is_ready():
                logger.error("LLM client not ready")
                return
            
            llm_response = await llm_manager.get_response(user_text)
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": llm_response})
            
            # Generate TTS audio
            await self._synthesize_and_send(llm_response)
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            # Send error response
            error_message = "I'm sorry, I encountered an error processing your request."
            await self._synthesize_and_send(error_message)
    
    async def _synthesize_and_send(self, text: str):
        """
        Synthesize text and send audio to client
        
        Args:
            text: Text to synthesize
        """
        if not self.active_tts_ws:
            logger.warning("No active TTS WebSocket connection")
            return
        
        if not tts_manager.is_ready():
            logger.error("TTS engine not ready")
            return
        
        try:
            logger.info(f"🔊 Synthesizing and sending: '{text[:50]}...'")
            
            # Signal TTS start
            self.is_speaking = True
            if self.on_tts_start:
                self.on_tts_start()
            
            # Clear interrupt event
            self.interrupt_event.clear()
            
            # Increment generation ID
            self.current_generation_id += 1
            generation_id = self.current_generation_id
            
            # Send WAV header first
            wav_header = tts_manager.get_wave_header()
            await self.active_tts_ws.send_bytes(wav_header)
            
            # Synthesize in thread with interruption support
            def synthesize_with_interruption():
                try:
                    audio_chunks = []
                    
                    def on_audio_chunk(chunk):
                        # Check for interruption
                        if self.interrupt_event.is_set():
                            logger.info(f"🛑 Synthesis interrupted for generation {generation_id}")
                            return
                        audio_chunks.append(chunk)
                    
                    # Use the synchronous synthesis method
                    import threading
                    from RealtimeTTS import TextToAudioStream
                    
                    tts_stream = TextToAudioStream(tts_manager.engine, muted=True)
                    
                    def sync_synthesis():
                        tts_stream.feed(text)
                        tts_stream.play(muted=True, on_audio_chunk=on_audio_chunk)
                    
                    sync_synthesis()
                    
                    # Send audio chunks if not interrupted
                    if not self.interrupt_event.is_set():
                        # Schedule sending chunks in the main event loop
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self._send_audio_chunks(audio_chunks, generation_id))
                        loop.close()
                    
                except Exception as e:
                    logger.error(f"Error in synthesis thread: {e}")
            
            # Start synthesis in thread
            self.active_synthesis_thread = threading.Thread(
                target=synthesize_with_interruption, 
                daemon=True
            )
            self.active_synthesis_thread.start()
            
        except Exception as e:
            logger.error(f"Error in synthesis setup: {e}")
            self.is_speaking = False
    
    async def _send_audio_chunks(self, audio_chunks: List[bytes], generation_id: int):
        """Send audio chunks to client"""
        try:
            if self.interrupt_event.is_set():
                logger.info(f"🛑 Skipping audio send for interrupted generation {generation_id}")
                return
            
            if not self.active_tts_ws:
                logger.warning("No active TTS WebSocket during audio send")
                return
            
            logger.info(f"📤 Sending {len(audio_chunks)} audio chunks for generation {generation_id}")
            
            for chunk in audio_chunks:
                if self.interrupt_event.is_set():
                    logger.info(f"🛑 Audio send interrupted for generation {generation_id}")
                    break
                
                await self.active_tts_ws.send_bytes(chunk)
            
            # Send completion signal if not interrupted
            if not self.interrupt_event.is_set():
                await self.active_tts_ws.send_text("END")
                logger.info(f"✅ TTS synthesis completed for generation {generation_id}")
            
        except Exception as e:
            logger.error(f"Error sending audio chunks: {e}")
        finally:
            # Signal TTS end
            self.is_speaking = False
            if self.on_tts_end:
                self.on_tts_end()
    
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
            "is_speaking": self.is_speaking,
            "is_listening": self.is_listening,
            "has_active_websocket": self.active_tts_ws is not None,
            "conversation_length": len(self.conversation_history),
            "current_generation_id": self.current_generation_id
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
        self.is_speaking = False
        self.is_listening = False


# Global conversation manager instance
conversation_manager = ConversationManager() 