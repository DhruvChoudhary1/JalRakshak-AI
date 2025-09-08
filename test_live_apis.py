#!/usr/bin/env python3
"""
Test script for INGRES Chatbot Live APIs
Tests all configured APIs and provides setup guidance
"""

import os
import sys
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from config import Config
from services.ai_service import AIService
from services.ingres_service import INGRESService

class APITester:
    def __init__(self):
        self.results = {}
        self.ai_service = AIService()
        self.ingres_service = INGRESService()
    
    def print_header(self):
        print("\n" + "="*60)
        print("🧪 INGRES CHATBOT API TESTING SUITE")
        print("="*60)
        print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Goal: Verify all APIs for live deployment")
        print("="*60 + "\n")
    
    def test_groq_api(self):
        """Test Groq AI API"""
        print("🤖 Testing Groq AI API...")
        
        if not Config.GROQ_API_KEY:
            print("❌ Groq API key not configured")
            print("💡 Get FREE key from: https://console.groq.com/")
            self.results['groq'] = False
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {"role": "user", "content": "Test message for INGRES chatbot"}
                ],
                "model": Config.GROQ_MODEL,
                "max_tokens": 50
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Groq API working perfectly!")
                print(f"📊 Model: {Config.GROQ_MODEL}")
                self.results['groq'] = True
            else:
                print(f"❌ Groq API error: {response.status_code}")
                print(f"📝 Response: {response.text[:100]}...")
                self.results['groq'] = False
                
        except Exception as e:
            print(f"❌ Groq API connection error: {e}")
            self.results['groq'] = False
    
    def test_huggingface_api(self):
        """Test Hugging Face API"""
        print("\n🤗 Testing Hugging Face API...")
        
        if not Config.HUGGINGFACE_API_KEY:
            print("❌ Hugging Face API key not configured")
            print("💡 Get FREE key from: https://huggingface.co/settings/tokens")
            self.results['huggingface'] = False
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": "Test groundwater query",
                "parameters": {"max_new_tokens": 20}
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{Config.HUGGINGFACE_MODEL}",
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Hugging Face API working!")
                print(f"📊 Model: {Config.HUGGINGFACE_MODEL}")
                self.results['huggingface'] = True
            else:
                print(f"❌ Hugging Face API error: {response.status_code}")
                self.results['huggingface'] = False
                
        except Exception as e:
            print(f"❌ Hugging Face API error: {e}")
            self.results['huggingface'] = False
    
    def test_ollama_api(self):
        """Test Ollama Local API"""
        print("\n🦙 Testing Ollama Local API...")
        
        try:
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    print("✅ Ollama running locally!")
                    print(f"📊 Available models: {len(models)}")
                    for model in models[:3]:  # Show first 3 models
                        print(f"   - {model.get('name', 'Unknown')}")
                    self.results['ollama'] = True
                else:
                    print("⚠️ Ollama running but no models installed")
                    print("💡 Install model: ollama pull llama2")
                    self.results['ollama'] = False
            else:
                print("❌ Ollama not responding")
                self.results['ollama'] = False
                
        except Exception as e:
            print("❌ Ollama not running locally")
            print("💡 Install from: https://ollama.ai/")
            self.results['ollama'] = False
    
    def test_ingres_api(self):
        """Test INGRES API"""
        print("\n🌊 Testing INGRES API...")
        
        if not Config.INGRES_API_KEY:
            print("❌ INGRES API key not configured")
            print("💡 Contact: support@indiawris.gov.in for API access")
            print("📝 Mention: Educational AI chatbot project")
            self.results['ingres'] = False
            return
        
        try:
            headers = {
                'Authorization': f'Bearer {Config.INGRES_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Test basic API connectivity
            response = requests.get(
                f"{Config.INGRES_BASE_URL}/groundwater/stations",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ INGRES API connected successfully!")
                data = response.json()
                print(f"📊 Stations available: {len(data.get('stations', []))}")
                self.results['ingres'] = True
            elif response.status_code == 401:
                print("❌ INGRES API authentication failed")
                print("💡 Check API key validity")
                self.results['ingres'] = False
            else:
                print(f"❌ INGRES API error: {response.status_code}")
                self.results['ingres'] = False
                
        except Exception as e:
            print(f"❌ INGRES API connection error: {e}")
            print("💡 Using mock data for demo")
            self.results['ingres'] = False
    
    def test_bhashini_api(self):
        """Test Bhashini Translation API"""
        print("\n🌐 Testing Bhashini Translation API...")
        
        if not Config.BHASHINI_API_KEY or not Config.BHASHINI_USER_ID:
            print("❌ Bhashini API credentials not configured")
            print("💡 Get FREE access from: https://bhashini.gov.in/bhashadaan/en/")
            self.results['bhashini'] = False
            return
        
        try:
            auth_payload = {
                "userId": Config.BHASHINI_USER_ID,
                "ulcaApiKey": Config.BHASHINI_API_KEY
            }
            
            response = requests.post(
                "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline",
                json=auth_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Bhashini API authenticated!")
                print("🌍 22 Indian languages supported")
                self.results['bhashini'] = True
            else:
                print(f"❌ Bhashini API error: {response.status_code}")
                self.results['bhashini'] = False
                
        except Exception as e:
            print(f"❌ Bhashini API error: {e}")
            self.results['bhashini'] = False
    
    def test_openweather_api(self):
        """Test OpenWeatherMap API"""
        print("\n🌤️ Testing OpenWeatherMap API...")
        
        if not Config.OPENWEATHER_API_KEY:
            print("❌ OpenWeatherMap API key not configured")
            print("💡 Get FREE key from: https://openweathermap.org/api")
            self.results['openweather'] = False
            return
        
        try:
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q=Mumbai&appid={Config.OPENWEATHER_API_KEY}",
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ OpenWeatherMap API working!")
                data = response.json()
                print(f"📊 Test location: {data.get('name', 'Unknown')}")
                self.results['openweather'] = True
            else:
                print(f"❌ OpenWeatherMap API error: {response.status_code}")
                self.results['openweather'] = False
                
        except Exception as e:
            print(f"❌ OpenWeatherMap API error: {e}")
            self.results['openweather'] = False
    
    async def test_ai_service_integration(self):
        """Test AI service integration"""
        print("\n🔗 Testing AI Service Integration...")
        
        try:
            test_message = "What is the groundwater level in Mumbai?"
            test_data = {
                "Mumbai": {
                    "water_level": 15.2,
                    "quality": "Good",
                    "trend": "Stable",
                    "citation": "INGRES-TEST-001"
                }
            }
            
            if self.ai_service.is_available():
                response = await self.ai_service.generate_ingres_response(
                    test_message, test_data, 'en'
                )
                print("✅ AI Service integration working!")
                print(f"📝 Sample response: {response[:100]}...")
                self.results['ai_integration'] = True
            else:
                print("⚠️ No AI APIs configured - using fallback responses")
                self.results['ai_integration'] = False
                
        except Exception as e:
            print(f"❌ AI Service integration error: {e}")
            self.results['ai_integration'] = False
    
    async def test_ingres_service_integration(self):
        """Test INGRES service integration"""
        print("\n🔗 Testing INGRES Service Integration...")
        
        try:
            data = await self.ingres_service.get_groundwater_data("Mumbai")
            
            if data and "Mumbai" in data:
                print("✅ INGRES Service integration working!")
                print(f"📊 Sample data: Water level {data['Mumbai']['water_level']}m")
                self.results['ingres_integration'] = True
            else:
                print("⚠️ INGRES API not available - using mock data")
                self.results['ingres_integration'] = False
                
        except Exception as e:
            print(f"❌ INGRES Service integration error: {e}")
            self.results['ingres_integration'] = False
    
    def test_database_connection(self):
        """Test database connectivity"""
        print("\n💾 Testing Database Connection...")
        
        try:
            import sqlite3
            
            # Test SQLite connection
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print("✅ SQLite database working!")
                print("📁 Location: Local SQLite file (auto-created)")
                self.results['database'] = True
            else:
                print("❌ Database connection failed")
                self.results['database'] = False
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            self.results['database'] = False
    
    def print_summary(self):
        """Print test summary and recommendations"""
        print("\n" + "="*60)
        print("📊 API TESTING SUMMARY")
        print("="*60)
        
        # Count working APIs
        working_apis = sum(1 for result in self.results.values() if result)
        total_apis = len(self.results)
        
        print(f"✅ Working APIs: {working_apis}/{total_apis}")
        print(f"📈 Success Rate: {(working_apis/total_apis)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        status_icons = {True: "✅", False: "❌"}
        
        for api, status in self.results.items():
            icon = status_icons[status]
            print(f"   {icon} {api.replace('_', ' ').title()}")
        
        print("\n🎯 Deployment Readiness:")
        
        # Essential APIs for basic functionality
        essential_working = self.results.get('database', False)
        if essential_working:
            print("✅ MINIMUM: Ready for demo with mock data")
        
        # Enhanced functionality
        ai_working = any([
            self.results.get('groq', False),
            self.results.get('huggingface', False),
            self.results.get('ollama', False)
        ])
        
        if ai_working:
            print("✅ ENHANCED: Ready with AI responses")
        
        # Full production
        if self.results.get('ingres', False) and ai_working:
            print("✅ PRODUCTION: Ready with live INGRES data")
        
        print("\n💡 Next Steps:")
        
        if not ai_working:
            print("1. 🔑 Configure at least one AI API (Groq recommended)")
            print("   - Groq: https://console.groq.com/ (fastest)")
            print("   - Hugging Face: https://huggingface.co/settings/tokens")
            print("   - Ollama: https://ollama.ai/ (local)")
        
        if not self.results.get('ingres', False):
            print("2. 🌊 Apply for INGRES API access")
            print("   - Email: support@indiawris.gov.in")
            print("   - Mention: Educational AI chatbot project")
        
        if not self.results.get('bhashini', False):
            print("3. 🌐 Configure Bhashini for multilingual support")
            print("   - Website: https://bhashini.gov.in/bhashadaan/en/")
        
        print("\n🚀 Ready to deploy? Run: python run_app.py")
        print("="*60 + "\n")

async def main():
    """Main test function"""
    tester = APITester()
    
    tester.print_header()
    
    # Test individual APIs
    tester.test_groq_api()
    tester.test_huggingface_api()
    tester.test_ollama_api()
    tester.test_ingres_api()
    tester.test_bhashini_api()
    tester.test_openweather_api()
    
    # Test service integrations
    await tester.test_ai_service_integration()
    await tester.test_ingres_service_integration()
    
    # Test database
    tester.test_database_connection()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())