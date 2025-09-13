#!/usr/bin/env python3
"""
Test Audio Features with LocalAI
Speech-to-Text and Text-to-Speech
"""

import requests
import json
import os
import wave
import time
from datetime import datetime

LOCALAI_URL = "http://localhost:8080"

def text_to_speech(text, voice="alloy", model="tts-1"):
    """Convert text to speech using LocalAI"""
    
    url = f"{LOCALAI_URL}/v1/audio/speech"
    
    payload = {
        "model": model,
        "input": text,
        "voice": voice
    }
    
    print(f"🔊 Converting to speech: {text[:50]}...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}.mp3"
            filepath = f"./audio/{filename}"
            
            os.makedirs("./audio", exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Audio saved: {filepath}")
            return filepath
        
        else:
            print(f"❌ TTS Error: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"❌ TTS Exception: {e}")
        return None

def speech_to_text(audio_file, model="whisper-1"):
    """Convert speech to text using LocalAI"""
    
    url = f"{LOCALAI_URL}/v1/audio/transcriptions"
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return None
    
    print(f"🎤 Transcribing: {audio_file}")
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            data = {'model': model}
            
            response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '')
            print(f"✅ Transcription: {text}")
            return text
        
        else:
            print(f"❌ STT Error: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"❌ STT Exception: {e}")
        return None

def create_voice_chat_demo():
    """Demo voice chat functionality"""
    
    print("🎤🔊 Voice Chat Demo with LocalAI on Raspberry Pi 5")
    print("=" * 60)
    
    # Demo texts for TTS
    demo_texts = [
        "Hallo! Ich bin LocalAI und laufe auf einem Raspberry Pi 5.",
        "Ich kann Sprache verstehen und auch sprechen.",
        "Mit mir können Sie vollständige Sprachunterhaltungen führen.",
        "Fragen Sie mich etwas, und ich antworte Ihnen mit Sprache!"
    ]
    
    print("\n🔊 Testing Text-to-Speech:")
    print("-" * 30)
    
    for i, text in enumerate(demo_texts, 1):
        print(f"\n🎯 Demo {i}/4:")
        result = text_to_speech(text)
        
        if result:
            print(f"✅ Audio generated: {result}")
            print(f"💡 Play with: mpv {result}")
        else:
            print("❌ Failed to generate audio")
    
    print("\n🎤 Testing Speech-to-Text:")
    print("-" * 30)
    print("📝 Note: You need to provide an audio file for STT testing")
    print("💡 Record audio with: arecord -f cd test.wav")
    print("💡 Then test with: speech_to_text('test.wav')")

def create_voice_agent_integration():
    """Show how to integrate voice with agents"""
    
    integration_code = '''
# Voice-enabled Agent Integration Example

async def voice_chat(audio_file):
    """Complete voice chat workflow"""
    
    # 1. Speech to Text
    user_text = speech_to_text(audio_file)
    
    # 2. Process with AI Agent  
    agent_response = await call_agent(user_text)
    
    # 3. Text to Speech
    audio_response = text_to_speech(agent_response)
    
    return {
        "user_speech": user_text,
        "agent_text": agent_response, 
        "agent_speech": audio_response
    }

# Usage:
result = await voice_chat("user_question.wav")
# Play: mpv result["agent_speech"]
'''
    
    print("\n🤖 Voice Agent Integration:")
    print("-" * 30)
    print(integration_code)

def test_multilingual_support():
    """Test multilingual TTS support"""
    
    multilingual_texts = {
        "Deutsch": "Guten Tag! Wie kann ich Ihnen helfen?",
        "English": "Hello! How can I assist you today?",
        "Español": "¡Hola! ¿Cómo puedo ayudarte?",
        "Français": "Bonjour! Comment puis-je vous aider?"
    }
    
    print("\n🌍 Testing Multilingual TTS:")
    print("-" * 30)
    
    for language, text in multilingual_texts.items():
        print(f"\n🗣️  {language}:")
        result = text_to_speech(text)
        if result:
            print(f"✅ Generated: {result}")

if __name__ == "__main__":
    create_voice_chat_demo()
    create_voice_agent_integration()
    test_multilingual_support()
    
    print("\n" + "=" * 60)
    print("🎉 Audio Features Test Complete!")
    print("\n📋 Quick Commands:")
    print("   • Record audio: arecord -f cd -t wav test.wav")
    print("   • Play audio: mpv audio/speech_*.mp3")
    print("   • Test STT: python -c 'import test_audio_features; test_audio_features.speech_to_text(\"test.wav\")'")
    print("\n🤖 Voice chat is ready on your Pi 5! 🍓🎤")