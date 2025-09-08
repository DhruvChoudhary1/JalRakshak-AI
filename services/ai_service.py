import requests
import json
from config import Config

# Optional imports - gracefully handle missing packages
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("ℹ️  Ollama not installed - will use other AI providers")

class AIService:
    """Service class for FREE AI APIs integration"""
    
    def __init__(self):
        # Check available AI services in order of preference
        self.huggingface_key = Config.HUGGINGFACE_API_KEY
        self.groq_key = Config.GROQ_API_KEY
        self.ollama_url = Config.OLLAMA_BASE_URL
        
        # Determine which AI service to use
        self.ai_provider = self._determine_provider()
        print(f"🤖 AI Provider: {self.ai_provider}")
    
    def _determine_provider(self):
        """Determine which AI provider to use based on availability"""
        # Check Groq (fastest free API)
        if self.groq_key:
            return "groq"
        
        # Check Hugging Face
        if self.huggingface_key:
            return "huggingface"
        
        # Check Ollama (local)
        if self._check_ollama():
            return "ollama"
        
        return "fallback"
    
    def _check_ollama(self):
        """Check if Ollama is running locally"""
        if not OLLAMA_AVAILABLE:
            return False
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def is_available(self):
        """Check if any AI API is available"""
        return self.ai_provider != "fallback"
    
    async def generate_response(self, user_message, groundwater_data=None):
        """
        Generate AI response using available FREE AI APIs
        
        Args:
            user_message (str): User's question
            groundwater_data (dict): Relevant groundwater data
            
        Returns:
            str: AI-generated response
        """
        return await self.generate_ingres_response(user_message, groundwater_data, 'en')
    
    async def generate_ingres_response(self, user_message, groundwater_data=None, language='en'):
        """
        Generate INGRES-specific AI response with multilingual support
        
        Args:
            user_message (str): User's question
            groundwater_data (dict): Relevant groundwater data
            language (str): Response language (en, hi, ta, etc.)
            
        Returns:
            str: AI-generated response
        """
        if not self.is_available():
            return self._get_fallback_response(user_message, groundwater_data)
        
        try:
            # Prepare enhanced context with groundwater data
            context = self._prepare_ingres_context(groundwater_data)
            
            # Create INGRES-specific system prompt
            system_prompt = self._create_ingres_prompt(context, language)
            
            # Generate response based on provider
            if self.ai_provider == "groq":
                response = await self._generate_groq_response(system_prompt, user_message)
            elif self.ai_provider == "huggingface":
                response = await self._generate_huggingface_response(system_prompt, user_message)
            elif self.ai_provider == "ollama":
                response = await self._generate_ollama_response(system_prompt, user_message)
            else:
                return self._get_fallback_response(user_message, groundwater_data)
            
            # Add INGRES-specific enhancements
            enhanced_response = self._enhance_ingres_response(response, groundwater_data)
            
            return enhanced_response
            
        except Exception as e:
            print(f"🤖 AI API error: {e}")
            return self._get_fallback_response(user_message, groundwater_data)
    
    async def _generate_groq_response(self, system_prompt, user_message):
        """Generate response using Groq API (FREE)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            
            # Ensure messages are properly formatted and not too long
            system_content = system_prompt[:1000] if len(system_prompt) > 1000 else system_prompt
            user_content = user_message[:500] if len(user_message) > 500 else user_message
            
            data = {
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                "model": Config.GROQ_MODEL,
                "max_tokens": 200,  # Reduced for better reliability
                "temperature": 0.7,
                "stream": False
            }
            
            print(f"🤖 Sending Groq request with model: {Config.GROQ_MODEL}")
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15
            )
            
            print(f"🤖 Groq response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                    print(f"✅ Groq response received: {len(content)} characters")
                    return content
                else:
                    print("❌ Groq response missing choices")
                    raise Exception("Invalid Groq API response format")
            elif response.status_code == 400:
                error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"❌ Groq 400 error: {error_detail}")
                raise Exception(f"Groq API request error: {error_detail}")
            elif response.status_code == 401:
                print("❌ Groq authentication failed - check API key")
                raise Exception("Groq API authentication failed - invalid API key")
            elif response.status_code == 429:
                print("❌ Groq rate limit exceeded")
                raise Exception("Groq API rate limit exceeded - try again later")
            else:
                print(f"❌ Groq API error {response.status_code}: {response.text}")
                raise Exception(f"Groq API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("❌ Groq API timeout")
            raise Exception("Groq API timeout - service may be slow")
        except requests.exceptions.ConnectionError:
            print("❌ Groq API connection error")
            raise Exception("Groq API connection failed - check internet connection")
        except Exception as e:
            print(f"❌ Groq API unexpected error: {e}")
            raise e
    
    async def _generate_huggingface_response(self, system_prompt, user_message):
        """Generate response using Hugging Face API (FREE)"""
        headers = {
            "Authorization": f"Bearer {self.huggingface_key}",
            "Content-Type": "application/json"
        }
        
        # Combine system prompt and user message for HF
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
        
        data = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{Config.HUGGINGFACE_MODEL}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            return "Response generated successfully."
        else:
            raise Exception(f"Hugging Face API error: {response.status_code}")
    
    async def _generate_ollama_response(self, system_prompt, user_message):
        """Generate response using Ollama (FREE, Local)"""
        if not OLLAMA_AVAILABLE:
            raise Exception("Ollama package not installed")
            
        try:
            response = ollama.chat(
                model=Config.OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response["message"]["content"].strip()
        except Exception as e:
            # Fallback to direct API call
            data = {
                "model": Config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"].strip()
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
    
    def _prepare_context(self, groundwater_data):
        """Prepare groundwater data context for AI"""
        return self._prepare_ingres_context(groundwater_data)
    
    def _prepare_ingres_context(self, groundwater_data):
        """Prepare enhanced INGRES groundwater data context for AI"""
        if not groundwater_data:
            return "No specific INGRES groundwater data available for this query."
        
        context_parts = []
        for district, data in groundwater_data.items():
            # Enhanced context with more details
            wells_info = f"({data.get('wells_monitored', 0)} monitoring wells)" if data.get('wells_monitored') else ""
            coordinates = f"Coordinates: {data.get('coordinates', ['N/A', 'N/A'])}" if data.get('coordinates') else ""
            
            context_parts.append(
                f"**{district} District INGRES Data:**\n"
                f"- Water Level: {data['water_level']} meters below ground level\n"
                f"- Quality Assessment: {data['quality']}\n"
                f"- Trend Analysis: {data['trend']}\n"
                f"- Monitoring Network: {wells_info}\n"
                f"- Last Updated: {data.get('last_updated', 'N/A')}\n"
                f"- {coordinates}\n"
                f"- Official Source: {data['citation']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_ingres_prompt(self, context, language='en'):
        """Create INGRES-specific system prompt"""
        language_instruction = ""
        if language == 'hi':
            language_instruction = "Respond in Hindi (Devanagari script) when appropriate."
        elif language == 'ta':
            language_instruction = "Respond in Tamil when appropriate."
        elif language != 'en':
            language_instruction = f"Respond in {language} when appropriate."
        
        return f"""You are an expert AI assistant for India's INGRES (India Groundwater Resource Estimation System) database.

**Your Role:**
- Provide accurate, scientific groundwater analysis using INGRES data
- Explain technical terms in simple language for all users (farmers, policymakers, researchers)
- Always cite INGRES sources and mention data limitations
- Provide actionable recommendations based on data

**INGRES Data Context:**
{context}

**Response Guidelines:**
- Start with key findings, then provide details
- Use emojis appropriately (💧 🔬 📊 ⚠️ ✅)
- Include specific numbers and citations
- Suggest next steps or monitoring recommendations
- Mention if data is limited or needs verification
- {language_instruction}

**Technical Standards:**
- Water levels <10m: Critical concern
- Water levels 10-20m: Moderate concern  
- Water levels >20m: Generally acceptable
- Quality ratings: Excellent > Good > Moderate > Poor > Critical

Be concise but comprehensive. Focus on practical insights."""
    
    def _enhance_ingres_response(self, response, groundwater_data):
        """Add INGRES-specific enhancements to AI response"""
        if not groundwater_data:
            return response
        
        # Add data summary footer
        district_count = len(groundwater_data)
        total_wells = sum(data.get('wells_monitored', 0) for data in groundwater_data.values())
        
        footer = f"\n\n📋 **Data Summary:** {district_count} district(s), {total_wells} monitoring wells"
        footer += f"\n🔗 **Source:** India Groundwater Resource Estimation System (INGRES)"
        footer += f"\n⏰ **Real-time Updates:** Data refreshed from CGWB monitoring network"
        
        return response + footer
    
    def _get_fallback_response(self, user_message, groundwater_data):
        """Generate fallback response when OpenAI is unavailable"""
        message_lower = user_message.lower()
        
        # Simple keyword-based responses
        if any(word in message_lower for word in ['level', 'depth', 'meter']):
            if groundwater_data:
                district = list(groundwater_data.keys())[0]
                data = groundwater_data[district]
                return f"The current groundwater level in {district} is {data['water_level']} meters below ground level. This data is from INGRES source: {data['citation']}. Note: Enhanced AI responses require OpenAI API configuration."
            return "I can provide groundwater level information. Please specify a district or configure OpenAI API for enhanced responses."
        
        elif any(word in message_lower for word in ['quality', 'contamination', 'pollution']):
            if groundwater_data:
                district = list(groundwater_data.keys())[0]
                data = groundwater_data[district]
                return f"The water quality in {district} is rated as '{data['quality']}' based on INGRES monitoring. Source: {data['citation']}. For detailed analysis, please configure OpenAI API."
            return "I can provide water quality assessments. Please specify a district or configure a FREE AI API (Groq/Hugging Face/Ollama) for enhanced responses."
        
        elif any(word in message_lower for word in ['trend', 'change', 'history']):
            if groundwater_data:
                district = list(groundwater_data.keys())[0]
                data = groundwater_data[district]
                return f"The groundwater trend in {district} is '{data['trend']}' according to INGRES data. Source: {data['citation']}. Configure a FREE AI API for detailed trend analysis."
            return "I can analyze groundwater trends. Please specify a district or configure a FREE AI API for enhanced responses."
        
        else:
            return "I'm here to help with groundwater information from INGRES data. Ask me about water levels, quality, or trends in any district. Note: Configure FREE AI APIs (Groq/Hugging Face/Ollama) for enhanced responses."

class PromptTemplates:
    """Templates for different types of groundwater queries"""
    
    WATER_LEVEL_ANALYSIS = """
    Analyze the groundwater level data and provide:
    1. Current status assessment
    2. Comparison with safe levels
    3. Potential concerns or recommendations
    4. Seasonal considerations if applicable
    """
    
    QUALITY_ASSESSMENT = """
    Assess the water quality data and explain:
    1. What the quality rating means
    2. Potential health implications
    3. Treatment recommendations if needed
    4. Monitoring suggestions
    """
    
    TREND_ANALYSIS = """
    Analyze the groundwater trend and discuss:
    1. What the trend indicates
    2. Potential causes
    3. Future projections
    4. Mitigation strategies
    """