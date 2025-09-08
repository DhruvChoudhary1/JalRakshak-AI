import requests
import json
from config import Config

class BhashiniService:
    """Service for Bhashini API integration (Government of India's language translation)"""
    
    def __init__(self):
        self.api_key = Config.BHASHINI_API_KEY
        self.user_id = Config.BHASHINI_USER_ID
        self.base_url = "https://meity-auth.ulcacontrib.org"
        self.pipeline_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
        
        # Language codes supported by Bhashini
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi', 
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'or': 'Odia',
            'pa': 'Punjabi',
            'ur': 'Urdu'
        }
    
    def is_available(self):
        """Check if Bhashini API is configured"""
        return bool(self.api_key and self.user_id)
    
    async def translate_text(self, text, source_lang='en', target_lang='hi'):
        """
        Translate text using Bhashini API
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code
            target_lang (str): Target language code
            
        Returns:
            str: Translated text or original if translation fails
        """
        if not self.is_available():
            print("🌐 Bhashini API not configured, returning original text")
            return text
        
        if source_lang == target_lang:
            return text
        
        try:
            # Get authorization token
            auth_token = await self._get_auth_token()
            if not auth_token:
                return text
            
            # Prepare translation request
            translation_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_lang,
                                "targetLanguage": target_lang
                            }
                        }
                    }
                ],
                "inputData": {
                    "input": [{"source": text}]
                }
            }
            
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.pipeline_url,
                headers=headers,
                json=translation_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('pipelineResponse', [{}])[0].get('output', [{}])[0].get('target', text)
                return translated_text
            else:
                print(f"❌ Bhashini translation error: {response.status_code}")
                return text
                
        except Exception as e:
            print(f"🌐 Bhashini translation error: {e}")
            return text
    
    async def _get_auth_token(self):
        """Get authorization token from Bhashini"""
        try:
            auth_payload = {
                "userId": self.user_id,
                "ulcaApiKey": self.api_key
            }
            
            response = requests.post(
                f"{self.base_url}/ulca/apis/v0/model/getModelsPipeline",
                json=auth_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('pipelineResponseConfig', [{}])[0].get('config', {}).get('serviceId')
            
            return None
            
        except Exception as e:
            print(f"🔑 Bhashini auth error: {e}")
            return None
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return self.supported_languages
    
    def detect_language(self, text):
        """
        Simple language detection based on script
        
        Args:
            text (str): Input text
            
        Returns:
            str: Detected language code
        """
        # Simple script-based detection
        if any('\u0900' <= char <= '\u097F' for char in text):  # Devanagari
            return 'hi'
        elif any('\u0B80' <= char <= '\u0BFF' for char in text):  # Tamil
            return 'ta'
        elif any('\u0C00' <= char <= '\u0C7F' for char in text):  # Telugu
            return 'te'
        elif any('\u0980' <= char <= '\u09FF' for char in text):  # Bengali
            return 'bn'
        elif any('\u0A80' <= char <= '\u0AFF' for char in text):  # Gujarati
            return 'gu'
        elif any('\u0C80' <= char <= '\u0CFF' for char in text):  # Kannada
            return 'kn'
        elif any('\u0D00' <= char <= '\u0D7F' for char in text):  # Malayalam
            return 'ml'
        elif any('\u0900' <= char <= '\u097F' for char in text):  # Marathi (Devanagari)
            return 'mr'
        else:
            return 'en'  # Default to English

class FallbackTranslationService:
    """Fallback translation service using simple dictionary mapping"""
    
    def __init__(self):
        # Basic groundwater terms in major Indian languages
        self.translations = {
            'hi': {
                'water level': 'जल स्तर',
                'groundwater': 'भूजल',
                'quality': 'गुणवत्ता',
                'good': 'अच्छा',
                'poor': 'खराब',
                'critical': 'गंभीर',
                'district': 'जिला',
                'meters': 'मीटर',
                'trend': 'प्रवृत्ति',
                'declining': 'घटता हुआ',
                'improving': 'सुधरता हुआ',
                'stable': 'स्थिर'
            },
            'ta': {
                'water level': 'நீர் மட்டம்',
                'groundwater': 'நிலத்தடி நீர்',
                'quality': 'தரம்',
                'good': 'நல்ல',
                'poor': 'மோசமான',
                'critical': 'முக்கியமான',
                'district': 'மாவட்டம்',
                'meters': 'மீட்டர்',
                'trend': 'போக்கு',
                'declining': 'குறைந்து வரும்',
                'improving': 'மேம்படுத்தும்',
                'stable': 'நிலையான'
            }
        }
    
    def translate_key_terms(self, text, target_lang):
        """Translate key groundwater terms"""
        if target_lang not in self.translations:
            return text
        
        translated_text = text
        for english_term, translated_term in self.translations[target_lang].items():
            translated_text = translated_text.replace(english_term, f"{translated_term} ({english_term})")
        
        return translated_text

# Initialize services
bhashini_service = BhashiniService()
fallback_translation = FallbackTranslationService()