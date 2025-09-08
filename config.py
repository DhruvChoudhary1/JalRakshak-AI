import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for API keys and settings"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # INGRES API Configuration
    INGRES_API_KEY = os.getenv('INGRES_API_KEY')
    INGRES_BASE_URL = os.getenv('INGRES_BASE_URL', 'https://indiawris.gov.in/api/v1')
    
    # FREE AI APIs Configuration
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    HUGGINGFACE_MODEL = os.getenv('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-medium')
    
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
    
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
    
    # Google Maps Configuration
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Weather API Configuration
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    # Mapbox Configuration
    MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')
    
    # Twilio Configuration (for SMS alerts)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # SendGrid Configuration (for email notifications)
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    
    # Bhashini API Configuration (Government of India Translation Service)
    BHASHINI_API_KEY = os.getenv('BHASHINI_API_KEY')
    BHASHINI_USER_ID = os.getenv('BHASHINI_USER_ID')
    
    # Database Configuration (SQLite by default - no setup required)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/groundwater.db')
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', 1000))
    
    @classmethod
    def validate_required_keys(cls):
        """Validate that required API keys are present"""
        required_keys = {
            'INGRES_API_KEY': cls.INGRES_API_KEY,
            'AI_API': cls.HUGGINGFACE_API_KEY or cls.GROQ_API_KEY or 'Local Ollama',
            'GOOGLE_MAPS_API_KEY': cls.GOOGLE_MAPS_API_KEY
        }
        
        missing_keys = [key for key, value in required_keys.items() if not value]
        
        if missing_keys:
            print(f"⚠️  Warning: Missing required API keys: {', '.join(missing_keys)}")
            print("📝 The application will run in demo mode with mock data.")
            print("🔑 Please add these keys to your .env file for full functionality.")
            return False
        
        print("✅ All required API keys are configured!")
        return True
    
    @classmethod
    def get_api_status(cls):
        """Get status of all API configurations"""
        apis = {
            'INGRES API': '✅' if cls.INGRES_API_KEY else '❌',
            'Hugging Face API': '✅' if cls.HUGGINGFACE_API_KEY else '⚠️',
            'Groq API': '✅' if cls.GROQ_API_KEY else '⚠️',
            'Ollama (Local)': '✅' if cls._check_ollama() else '⚠️',
            'Bhashini Translation': '✅' if cls.BHASHINI_API_KEY else '⚠️',
            'Google Maps API': '✅' if cls.GOOGLE_MAPS_API_KEY else '❌',
            'OpenWeather API': '✅' if cls.OPENWEATHER_API_KEY else '⚠️',
            'Mapbox API': '✅' if cls.MAPBOX_ACCESS_TOKEN else '⚠️',
            'Twilio API': '✅' if cls.TWILIO_ACCOUNT_SID else '⚠️',
            'SendGrid API': '✅' if cls.SENDGRID_API_KEY else '⚠️'
        }
        return apis
    
    @classmethod
    def _check_ollama(cls):
        """Check if Ollama is running locally"""
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
        return apis