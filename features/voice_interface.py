"""
Voice Interface Module for INGRES AI Chatbot
Handles voice input/output and speech recognition with ML/NLP
"""

import json
import asyncio
from datetime import datetime
import speech_recognition as sr
from transformers import pipeline

class VoiceInterface:
    def __init__(self):
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
        # ML/NLP pipeline for intent recognition (English only for demo)
        self.intent_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

    def get_supported_languages(self):
        """Get list of supported languages for voice interface"""
        return self.supported_languages

    def process_voice_query(self, audio_data, language='en'):
        """Process voice query and return text + ML intent classification"""
        # Speech recognition (English only for demo)
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_data) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language=language)
        except Exception:
            text = "Could not process audio"

        # ML intent classification (English only for demo)
        if language == 'en' and text and text != "Could not process audio":
            intent_result = self.intent_classifier(text)
            intent = intent_result[0]['label']
            confidence = intent_result[0]['score']
        else:
            intent = "unknown"
            confidence = 0.0

        return {
            "success": True,
            "text": text,
            "language": language,
            "intent": intent,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

    def generate_voice_response(self, text, language='en'):
        """Generate voice response configuration"""
        # Optionally, use ML/NLP for response generation or translation
        return {
            "text": text,
            "language": language,
            "voice_config": {
                "rate": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            },
            "supported": language in self.supported_languages
        }

# Global voice interface instance
voice_interface = VoiceInterface()