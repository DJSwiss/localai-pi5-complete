#!/usr/bin/env python3
"""
Test Image Generation with LocalAI
"""

import requests
import json
import base64
import os
from datetime import datetime

LOCALAI_URL = "http://localhost:8080"

def generate_image(prompt, size="512x512", steps=20):
    """Generate image using LocalAI"""
    
    url = f"{LOCALAI_URL}/v1/images/generations"
    
    payload = {
        "prompt": prompt,
        "size": size,
        "n": 1,
        "response_format": "b64_json"
    }
    
    print(f"🎨 Generating image: {prompt}")
    print(f"📐 Size: {size}, Steps: {steps}")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            # Save image
            image_data = result['data'][0]['b64_json']
            image_bytes = base64.b64decode(image_data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.png"
            filepath = f"./images/{filename}"
            
            os.makedirs("./images", exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            print(f"✅ Image saved: {filepath}")
            return filepath
        
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_image_generation():
    """Test various image prompts optimized for Pi 5"""
    
    prompts = [
        "A cute robot sitting on a Raspberry Pi 5, digital art",
        "A peaceful landscape with mountains and lakes, oil painting style",
        "A futuristic city skyline at sunset, cyberpunk style",
        "A friendly AI assistant helping a person, cartoon style"
    ]
    
    print("🎨 Testing Image Generation on Raspberry Pi 5")
    print("=" * 50)
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🖼️  Test {i}/4:")
        result = generate_image(prompt)
        
        if result:
            print(f"✅ Success! Check: {result}")
        else:
            print("❌ Failed to generate image")
        
        print("-" * 30)

if __name__ == "__main__":
    test_image_generation()