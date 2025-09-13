#!/usr/bin/env python3
"""
Voice-Enabled Agent for LocalAI
Complete Speech-to-Text and Text-to-Speech integration
"""

import asyncio
import json
import logging
import requests
import openai
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Agent", version="1.0.0")

# Configure OpenAI client for LocalAI
LOCALAI_URL = "http://localhost:8080"
openai.api_base = f"{LOCALAI_URL}/v1"
openai.api_key = "not-needed-for-localai"

class VoiceAgent:
    def __init__(self):
        self.conversation_history = []
    
    async def speech_to_text(self, audio_file_path: str) -> str:
        """Convert speech to text"""
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'file': f}
                data = {'model': 'whisper-1'}
                
                response = requests.post(
                    f"{LOCALAI_URL}/v1/audio/transcriptions",
                    files=files,
                    data=data,
                    timeout=120
                )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '')
            else:
                raise Exception(f"STT failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Speech to text error: {e}")
            raise
    
    async def text_to_speech(self, text: str, voice: str = "alloy") -> str:
        """Convert text to speech"""
        try:
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": voice
            }
            
            response = requests.post(
                f"{LOCALAI_URL}/v1/audio/speech",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"response_{timestamp}.mp3"
                filepath = f"./audio/{filename}"
                
                os.makedirs("./audio", exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filepath
            else:
                raise Exception(f"TTS failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Text to speech error: {e}")
            raise
    
    async def process_with_ai(self, user_text: str) -> str:
        """Process user input with LocalAI"""
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Prepare messages for LocalAI
            messages = [
                {
                    "role": "system",
                    "content": """Du bist ein hilfsreicher AI-Assistent, der auf einem Raspberry Pi 5 läuft. 
Du kannst sprechen und hören. Antworte freundlich und informativ. 
Halte deine Antworten relativ kurz für die Sprachausgabe (max 2-3 Sätze)."""
                }
            ]
            
            # Add recent conversation history
            recent_messages = self.conversation_history[-5:]  # Last 5 exchanges
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Call LocalAI
            response = openai.ChatCompletion.create(
                model="phi-2",
                messages=messages,
                temperature=0.7,
                max_tokens=200  # Keep responses concise for speech
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.conversation_history.append({
                "role": "assistant", 
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return ai_response
        
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return "Entschuldigung, ich hatte ein Problem beim Verarbeiten Ihrer Anfrage."
    
    async def voice_chat(self, audio_file_path: str) -> dict:
        """Complete voice chat workflow"""
        try:
            # Step 1: Speech to Text
            logger.info("Converting speech to text...")
            user_text = await self.speech_to_text(audio_file_path)
            logger.info(f"User said: {user_text}")
            
            # Step 2: Process with AI
            logger.info("Processing with AI...")
            ai_response = await self.process_with_ai(user_text)
            logger.info(f"AI responded: {ai_response}")
            
            # Step 3: Text to Speech
            logger.info("Converting response to speech...")
            audio_response_path = await self.text_to_speech(ai_response)
            logger.info(f"Audio response saved: {audio_response_path}")
            
            return {
                "user_text": user_text,
                "ai_text": ai_response,
                "ai_audio": audio_response_path,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Voice chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Global voice agent instance
voice_agent = VoiceAgent()

@app.get("/")
async def root():
    return {
        "message": "Voice Agent for LocalAI",
        "features": ["speech-to-text", "text-to-speech", "voice-chat"],
        "status": "ready"
    }

@app.post("/voice-chat")
async def voice_chat_endpoint(audio: UploadFile = File(...)):
    """Upload audio and get voice response"""
    
    if not audio.filename.endswith(('.wav', '.mp3', '.m4a', '.flac')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    # Save uploaded audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_audio_path = f"./audio/temp_{timestamp}_{audio.filename}"
    
    with open(temp_audio_path, 'wb') as f:
        content = await audio.read()
        f.write(content)
    
    try:
        # Process voice chat
        result = await voice_agent.voice_chat(temp_audio_path)
        
        # Clean up temp file
        os.remove(temp_audio_path)
        
        return result
    
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        raise

@app.post("/text-to-speech")
async def tts_endpoint(text: str, voice: str = "alloy"):
    """Convert text to speech"""
    
    try:
        audio_path = await voice_agent.text_to_speech(text, voice)
        return {"audio_file": audio_path, "text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files"""
    
    audio_path = f"./audio/{filename}"
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(audio_path)

@app.get("/conversation-history")
async def get_history():
    """Get conversation history"""
    return {
        "history": voice_agent.conversation_history[-10:],  # Last 10 messages
        "total_messages": len(voice_agent.conversation_history)
    }

if __name__ == "__main__":
    import uvicorn
    os.makedirs("./audio", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8098)