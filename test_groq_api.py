#!/usr/bin/env python3
"""
Quick test script for Groq API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_groq_api():
    api_key = os.getenv('GROQ_API_KEY')
    model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        return False
    
    print(f"🤖 Testing Groq API with model: {model}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [
            {"role": "user", "content": "Hello, respond with just 'API working'"}
        ],
        "model": model,
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ Groq API Working! Response: {content}")
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Groq API Test")
    print("=" * 30)
    success = test_groq_api()
    print("=" * 30)
    if success:
        print("🎉 Groq API is ready for INGRES chatbot!")
    else:
        print("🔧 Fix the issues above and try again")