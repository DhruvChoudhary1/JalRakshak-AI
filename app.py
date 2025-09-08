from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add services directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from config import Config
from services.ingres_service import INGRESService
from services.ai_service import AIService

# Import translation service
try:
    from services.translation_service import bhashini_service, fallback_translation
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    print("⚠️ Translation service not available")

# Import crisis predictor
try:
    from features.crisis_predictor import crisis_predictor
    CRISIS_PREDICTOR_AVAILABLE = True
except ImportError:
    CRISIS_PREDICTOR_AVAILABLE = False
    print("⚠️ Crisis predictor not available")

# Import additional features
try:
    from features.interactive_map import interactive_map
    from features.crowdsourced_reporting import crowdsourced_reporting
    from features.predictive_analytics import predictive_analytics
    from features.voice_interface import voice_interface
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    print("⚠️ Advanced features not available")

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Initialize services
ingres_service = INGRESService()
ai_service = AIService()

# Print API status on startup
print("\n" + "="*50)
print("🌊 AI INGRES Groundwater Chatbot Starting...")
print("="*50)

api_status = Config.get_api_status()
for api_name, status in api_status.items():
    print(f"{status} {api_name}")

print("\n📋 API Integration Status:")
Config.validate_required_keys()
print("="*50 + "\n")

# Mock INGRES groundwater data
GROUNDWATER_DATA = {
    "districts": {
        "Mumbai": {
            "water_level": 15.2,
            "quality": "Good",
            "trend": "Stable",
            "last_updated": "2024-01-15",
            "coordinates": [19.0760, 72.8777],
            "wells_monitored": 45,
            "citation": "INGRES-MH-001-2024"
        },
        "Pune": {
            "water_level": 12.8,
            "quality": "Moderate",
            "trend": "Declining",
            "last_updated": "2024-01-14",
            "coordinates": [18.5204, 73.8567],
            "wells_monitored": 38,
            "citation": "INGRES-MH-002-2024"
        },
        "Bangalore": {
            "water_level": 8.5,
            "quality": "Poor",
            "trend": "Critical",
            "last_updated": "2024-01-13",
            "coordinates": [12.9716, 77.5946],
            "wells_monitored": 52,
            "citation": "INGRES-KA-001-2024"
        },
        "Chennai": {
            "water_level": 6.2,
            "quality": "Critical",
            "trend": "Declining",
            "last_updated": "2024-01-12",
            "coordinates": [13.0827, 80.2707],
            "wells_monitored": 41,
            "citation": "INGRES-TN-001-2024"
        },
        "Delhi": {
            "water_level": 18.7,
            "quality": "Good",
            "trend": "Improving",
            "last_updated": "2024-01-16",
            "coordinates": [28.7041, 77.1025],
            "wells_monitored": 67,
            "citation": "INGRES-DL-001-2024"
        }
    }
}

# Chatbot responses with INGRES citations
CHATBOT_RESPONSES = {
    "water_level": [
        "Based on INGRES data, I can provide current groundwater levels for your district.",
        "Let me check the latest groundwater monitoring data from INGRES for you.",
        "I'll fetch the most recent water level measurements from our INGRES database."
    ],
    "quality": [
        "Water quality assessment is available through INGRES monitoring stations.",
        "I can provide water quality parameters based on recent INGRES analysis.",
        "Let me retrieve the latest water quality report from INGRES data."
    ],
    "trend": [
        "INGRES historical data shows interesting trends for groundwater levels.",
        "Based on multi-year INGRES data, I can analyze groundwater trends.",
        "Let me analyze the groundwater trend using INGRES time-series data."
    ],
    "general": [
        "I'm here to help with groundwater information using INGRES data.",
        "Ask me about water levels, quality, or trends in any district.",
        "I can provide INGRES-backed insights on groundwater status."
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test_chat():
    """Simple test page for chat functionality"""
    with open('test_chat.html', 'r') as f:
        return f.read()

@app.route('/api/districts')
def get_districts():
    return jsonify(list(GROUNDWATER_DATA["districts"].keys()))

@app.route('/api/groundwater/<district>')
def get_groundwater_data(district):
    if district in GROUNDWATER_DATA["districts"]:
        return jsonify(GROUNDWATER_DATA["districts"][district])
    return jsonify({"error": "District not found"}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    language = request.json.get('language', 'en')  # Default to English
    
    try:
        # Check if user mentioned a specific district or state
        mentioned_district = None
        mentioned_state = None
        
        # Enhanced district detection
        for district in GROUNDWATER_DATA["districts"].keys():
            if district.lower() in user_message.lower():
                mentioned_district = district
                break
        
        # Get live INGRES data if available
        district_data = None
        if mentioned_district:
            # Try to get live INGRES data first
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            live_data = loop.run_until_complete(
                ingres_service.get_groundwater_data(mentioned_district)
            )
            loop.close()
            
            district_data = live_data if live_data else {mentioned_district: GROUNDWATER_DATA["districts"][mentioned_district]}
        
        # Generate AI response with enhanced context
        if ai_service.is_available():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                ai_service.generate_ingres_response(user_message, district_data, language)
            )
            loop.close()
        else:
            response = generate_fallback_response(user_message, district_data)
        
        # Add visualization data if relevant
        viz_data = None
        if mentioned_district and district_data:
            viz_data = prepare_visualization_data(district_data)
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "district_data": district_data.get(mentioned_district) if mentioned_district and district_data else None,
            "visualization_data": viz_data,
            "language": language,
            "api_status": {
                "ai_enabled": ai_service.is_available(),
                "ingres_enabled": ingres_service.is_available(),
                "live_data": bool(district_data and mentioned_district)
            },
            "suggestions": get_query_suggestions(user_message)
        })
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "timestamp": datetime.now().isoformat(),
            "error": str(e) if app.debug else "Internal server error"
        }), 500

def generate_fallback_response(user_message, district_data):
    """Generate enhanced responses when AI service is unavailable"""
    message_lower = user_message.lower()
    
    # Determine query type
    if any(word in message_lower for word in ['level', 'depth', 'meter', 'mbgl']):
        response_type = "water_level"
    elif any(word in message_lower for word in ['quality', 'contamination', 'pollution', 'tds', 'ph']):
        response_type = "quality"
    elif any(word in message_lower for word in ['trend', 'change', 'history', 'declining', 'improving']):
        response_type = "trend"
    elif any(word in message_lower for word in ['alert', 'warning', 'critical', 'emergency']):
        response_type = "alert"
    else:
        response_type = "general"
    
    response = random.choice(CHATBOT_RESPONSES[response_type])
    
    # Add specific INGRES data if district mentioned
    if district_data and response_type != "general":
        district = list(district_data.keys())[0]
        data = district_data[district]
        
        if response_type == "water_level":
            level_status = "Critical" if data['water_level'] < 10 else "Moderate" if data['water_level'] < 20 else "Good"
            response += f"\n\n📊 **INGRES Data for {district}:**"
            response += f"\n• Water Level: {data['water_level']} meters below ground level"
            response += f"\n• Status: {level_status}"
            response += f"\n• Wells Monitored: {data['wells_monitored']}"
            response += f"\n• Last Updated: {data['last_updated']}"
            response += f"\n• Source: {data['citation']}"
            
        elif response_type == "quality":
            response += f"\n\n🔬 **Water Quality Assessment for {district}:**"
            response += f"\n• Quality Rating: {data['quality']}"
            response += f"\n• Monitoring Status: Active ({data['wells_monitored']} wells)"
            response += f"\n• Last Assessment: {data['last_updated']}"
            response += f"\n• INGRES Source: {data['citation']}"
            
        elif response_type == "trend":
            trend_emoji = "📈" if data['trend'] == "Improving" else "📉" if data['trend'] == "Declining" else "➡️"
            response += f"\n\n{trend_emoji} **Groundwater Trend Analysis for {district}:**"
            response += f"\n• Current Trend: {data['trend']}"
            response += f"\n• Water Level: {data['water_level']} mbgl"
            response += f"\n• Quality Status: {data['quality']}"
            response += f"\n• Data Source: {data['citation']}"
            
        elif response_type == "alert":
            if data['water_level'] < 10 or data['quality'] in ['Poor', 'Critical']:
                response += f"\n\n⚠️ **ALERT: {district} requires attention!**"
                response += f"\n• Water Level: {data['water_level']} mbgl (Critical threshold: <10m)"
                response += f"\n• Quality: {data['quality']}"
                response += f"\n• Trend: {data['trend']}"
                response += f"\n• Immediate monitoring recommended"
            else:
                response += f"\n\n✅ **Status Update for {district}:**"
                response += f"\n• No critical alerts currently"
                response += f"\n• Water Level: {data['water_level']} mbgl (Acceptable)"
                response += f"\n• Quality: {data['quality']}"
    
    response += "\n\n💡 **Tip:** Configure FREE AI APIs (Groq/Hugging Face) for detailed analysis and recommendations."
    return response

def prepare_visualization_data(district_data):
    """Prepare data for charts and maps"""
    if not district_data:
        return None
    
    district = list(district_data.keys())[0]
    data = district_data[district]
    
    return {
        "district": district,
        "coordinates": data.get('coordinates', [0, 0]),
        "water_level": data.get('water_level', 0),
        "quality_score": {"Good": 4, "Moderate": 3, "Poor": 2, "Critical": 1}.get(data.get('quality', 'Unknown'), 2),
        "trend_direction": {"Improving": 1, "Stable": 0, "Declining": -1}.get(data.get('trend', 'Unknown'), 0),
        "wells_count": data.get('wells_monitored', 0),
        "last_updated": data.get('last_updated', ''),
        "citation": data.get('citation', '')
    }

def get_query_suggestions(user_message):
    """Generate relevant query suggestions based on user input"""
    message_lower = user_message.lower()
    
    base_suggestions = [
        "Show water levels in Mumbai",
        "What is the water quality in Bangalore?",
        "Compare groundwater trends across states",
        "Show critical water zones in India"
    ]
    
    # Context-aware suggestions
    if any(word in message_lower for word in ['level', 'depth']):
        return [
            "Compare water levels with last year",
            "Show districts with critical water levels",
            "What causes water level changes?",
            "Predict future water availability"
        ]
    elif any(word in message_lower for word in ['quality', 'contamination']):
        return [
            "Show water quality parameters",
            "Which areas have safe drinking water?",
            "What affects groundwater quality?",
            "Water treatment recommendations"
        ]
    else:
        return base_suggestions

@app.route('/api/visualization')
def get_visualization_data():
    # Prepare data for charts
    districts = list(GROUNDWATER_DATA["districts"].keys())
    water_levels = [GROUNDWATER_DATA["districts"][d]["water_level"] for d in districts]
    quality_scores = []
    
    # Convert quality to numeric scores for visualization
    quality_map = {"Excellent": 5, "Good": 4, "Moderate": 3, "Poor": 2, "Critical": 1}
    for district in districts:
        quality = GROUNDWATER_DATA["districts"][district]["quality"]
        quality_scores.append(quality_map.get(quality, 2))
    
    return jsonify({
        "districts": districts,
        "water_levels": water_levels,
        "quality_scores": quality_scores,
        "citations": [GROUNDWATER_DATA["districts"][d]["citation"] for d in districts],
        "coordinates": [GROUNDWATER_DATA["districts"][d]["coordinates"] for d in districts],
        "trends": [GROUNDWATER_DATA["districts"][d]["trend"] for d in districts],
        "last_updated": max([GROUNDWATER_DATA["districts"][d]["last_updated"] for d in districts])
    })

@app.route('/api/ingres/live/<district>')
async def get_live_ingres_data(district):
    """Get live INGRES data for a specific district"""
    try:
        live_data = await ingres_service.get_groundwater_data(district)
        
        if live_data and district in live_data:
            return jsonify({
                "success": True,
                "data": live_data[district],
                "source": "INGRES Live API",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Fallback to mock data
            if district in GROUNDWATER_DATA["districts"]:
                return jsonify({
                    "success": True,
                    "data": GROUNDWATER_DATA["districts"][district],
                    "source": "Mock Data (INGRES API unavailable)",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "District not found",
                    "available_districts": list(GROUNDWATER_DATA["districts"].keys())
                }), 404
                
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "fallback_available": district in GROUNDWATER_DATA["districts"]
        }), 500

@app.route('/api/languages')
def get_supported_languages():
    """Get list of supported languages"""
    return jsonify({
        "supported_languages": {
            'en': 'English',
            'hi': 'हिंदी (Hindi)', 
            'ta': 'தமிழ் (Tamil)',
            'te': 'తెలుగు (Telugu)',
            'bn': 'বাংলা (Bengali)',
            'gu': 'ગુજરાતી (Gujarati)',
            'kn': 'ಕನ್ನಡ (Kannada)',
            'ml': 'മലയാളം (Malayalam)',
            'mr': 'मराठी (Marathi)',
            'or': 'ଓଡ଼ିଆ (Odia)',
            'pa': 'ਪੰਜਾਬੀ (Punjabi)',
            'ur': 'اردو (Urdu)'
        },
        "default_language": "en",
        "translation_service": "Bhashini (Government of India)" if Config.BHASHINI_API_KEY else "Fallback Dictionary"
    })

@app.route('/api/search/districts')
def search_districts():
    """Search districts by name or state"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify(list(GROUNDWATER_DATA["districts"].keys()))
    
    # Simple search in district names
    matching_districts = [
        district for district in GROUNDWATER_DATA["districts"].keys()
        if query in district.lower()
    ]
    
    return jsonify({
        "query": query,
        "matches": matching_districts,
        "total_available": len(GROUNDWATER_DATA["districts"])
    })

@app.route('/api/alerts')
def get_water_alerts():
    """Get critical water alerts based on INGRES data"""
    alerts = []
    
    for district, data in GROUNDWATER_DATA["districts"].items():
        alert_level = "none"
        message = ""
        
        # Check water level alerts
        if data["water_level"] < 5:
            alert_level = "critical"
            message = f"Extremely low groundwater level: {data['water_level']}m"
        elif data["water_level"] < 10:
            alert_level = "high"
            message = f"Low groundwater level: {data['water_level']}m"
        elif data["quality"] in ["Poor", "Critical"]:
            alert_level = "medium"
            message = f"Water quality concern: {data['quality']}"
        elif data["trend"] == "Declining":
            alert_level = "low"
            message = f"Declining groundwater trend"
        
        if alert_level != "none":
            alerts.append({
                "district": district,
                "alert_level": alert_level,
                "message": message,
                "water_level": data["water_level"],
                "quality": data["quality"],
                "trend": data["trend"],
                "last_updated": data["last_updated"],
                "citation": data["citation"]
            })
    
    # Sort by alert level priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda x: priority_order.get(x["alert_level"], 4))
    
    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts),
        "critical_count": len([a for a in alerts if a["alert_level"] == "critical"]),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/crisis/predict/<district>')
def predict_water_crisis(district):
    """Predict water crisis for a specific district"""
    try:
        if not CRISIS_PREDICTOR_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Crisis predictor not available",
                "fallback": "Basic seasonal analysis available"
            }), 503
        
        # Get current water level if available
        current_water_level = None
        if district in GROUNDWATER_DATA["districts"]:
            current_water_level = GROUNDWATER_DATA["districts"][district]["water_level"]
        
        # Generate crisis prediction
        prediction = crisis_predictor.predict_crisis(district, current_water_level)
        
        return jsonify({
            "success": True,
            "prediction": prediction,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "district": district
        }), 500

@app.route('/api/crisis/alerts')
def get_crisis_alerts():
    """Get crisis alerts for all monitored districts"""
    try:
        alerts = []
        
        for district, data in GROUNDWATER_DATA["districts"].items():
            if CRISIS_PREDICTOR_AVAILABLE:
                prediction = crisis_predictor.predict_crisis(district, data["water_level"])
                
                if prediction["prediction"]["severity"] in ["Critical", "High"]:
                    alerts.append({
                        "district": district,
                        "severity": prediction["prediction"]["severity"],
                        "days_to_crisis": prediction["prediction"]["days_to_crisis"],
                        "probability": prediction["prediction"]["probability"],
                        "current_water_level": data["water_level"],
                        "recommendations": prediction["recommendations"][:3]  # Top 3 recommendations
                    })
        
        # Sort by severity and timeline
        severity_order = {"Critical": 0, "High": 1, "Moderate": 2, "Low": 3}
        alerts.sort(key=lambda x: (severity_order.get(x["severity"], 4), x["days_to_crisis"]))
        
        return jsonify({
            "success": True,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_count": len([a for a in alerts if a["severity"] == "Critical"]),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Interactive Map API Endpoints
@app.route('/api/map/data')
def get_map_data():
    """Get interactive map data"""
    try:
        bounds = request.args.get('bounds')
        zoom_level = int(request.args.get('zoom', 5))
        
        if ADVANCED_FEATURES_AVAILABLE:
            map_data = interactive_map.get_map_data(bounds, zoom_level)
            return jsonify({
                "success": True,
                "data": map_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "Interactive map not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/map/heatmap')
def get_heatmap_data():
    """Get heatmap data for visualization"""
    try:
        data_type = request.args.get('type', 'water_level')
        
        if ADVANCED_FEATURES_AVAILABLE:
            heatmap_data = interactive_map.get_heatmap_data(data_type)
            return jsonify({
                "success": True,
                "data": heatmap_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "Heatmap feature not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/map/search')
def search_map_location():
    """Search for locations on the map"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Search query required"
            }), 400
        
        if ADVANCED_FEATURES_AVAILABLE:
            results = interactive_map.search_location(query)
            return jsonify({
                "success": True,
                "results": results
            })
        else:
            return jsonify({
                "success": False,
                "error": "Map search not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/map/layers', methods=['POST'])
def toggle_map_layer():
    """Toggle map layer visibility"""
    try:
        data = request.get_json()
        layer_name = data.get('layer')
        enabled = data.get('enabled', True)
        
        if ADVANCED_FEATURES_AVAILABLE:
            result = interactive_map.toggle_layer(layer_name, enabled)
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "error": "Layer toggle not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Crowdsourced Reporting API Endpoints
@app.route('/api/reports', methods=['POST'])
def submit_report():
    """Submit a new crowdsourced report"""
    try:
        report_data = request.get_json()
        
        if ADVANCED_FEATURES_AVAILABLE:
            result = crowdsourced_reporting.submit_report(report_data)
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "error": "Reporting feature not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/reports/location/<location>')
def get_reports_by_location(location):
    """Get reports for a specific location"""
    try:
        radius = int(request.args.get('radius', 10))
        
        if ADVANCED_FEATURES_AVAILABLE:
            reports = crowdsourced_reporting.get_reports_by_location(location, radius)
            return jsonify({
                "success": True,
                "data": reports
            })
        else:
            return jsonify({
                "success": False,
                "error": "Reports feature not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/reports/categories')
def get_report_categories():
    """Get available report categories"""
    try:
        if ADVANCED_FEATURES_AVAILABLE:
            categories = crowdsourced_reporting.get_report_categories()
            return jsonify({
                "success": True,
                "categories": categories
            })
        else:
            return jsonify({
                "success": False,
                "error": "Categories feature not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/reports/stats')
def get_community_stats():
    """Get community reporting statistics"""
    try:
        if ADVANCED_FEATURES_AVAILABLE:
            stats = crowdsourced_reporting.get_community_stats()
            return jsonify({
                "success": True,
                "data": stats
            })
        else:
            return jsonify({
                "success": False,
                "error": "Stats feature not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Predictive Analytics API Endpoints
@app.route('/api/predict/water-levels/<district>')
def predict_water_levels(district):
    """Predict future water levels for a district"""
    try:
        horizon = request.args.get('horizon', 'medium_term')
        current_level = float(request.args.get('current_level', 10))
        
        if ADVANCED_FEATURES_AVAILABLE:
            prediction = predictive_analytics.predict_water_levels(district, current_level, horizon)
            return jsonify({
                "success": True,
                "prediction": prediction
            })
        else:
            return jsonify({
                "success": False,
                "error": "Prediction feature not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/predict/trends/<district>')
def analyze_trends(district):
    """Analyze historical trends for a district"""
    try:
        if ADVANCED_FEATURES_AVAILABLE:
            analysis = predictive_analytics.analyze_trends(district)
            return jsonify({
                "success": True,
                "analysis": analysis
            })
        else:
            return jsonify({
                "success": False,
                "error": "Trend analysis not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/predict/crisis-probability/<district>')
def forecast_crisis_probability(district):
    """Forecast water crisis probability"""
    try:
        # Get current conditions from request or use defaults
        conditions = {
            "water_level": float(request.args.get('water_level', 10)),
            "quality": request.args.get('quality', 'Moderate'),
            "trend": request.args.get('trend', 'Stable')
        }
        
        if ADVANCED_FEATURES_AVAILABLE:
            forecast = predictive_analytics.forecast_crisis_probability(district, conditions)
            return jsonify({
                "success": True,
                "forecast": forecast
            })
        else:
            return jsonify({
                "success": False,
                "error": "Crisis forecasting not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/predict/compare')
def compare_districts():
    """Compare predictive metrics across districts"""
    try:
        if ADVANCED_FEATURES_AVAILABLE:
            comparison = predictive_analytics.compare_districts(GROUNDWATER_DATA["districts"])
            return jsonify({
                "success": True,
                "comparison": comparison
            })
        else:
            return jsonify({
                "success": False,
                "error": "Comparison feature not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Voice Interface API Endpoints
@app.route('/api/voice/languages')
def get_voice_languages():
    """Get supported languages for voice interface"""
    try:
        if ADVANCED_FEATURES_AVAILABLE:
            languages = voice_interface.get_supported_languages()
            return jsonify({
                "success": True,
                "languages": languages
            })
        else:
            return jsonify({
                "success": False,
                "error": "Voice interface not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/voice/config', methods=['POST'])
def get_voice_config():
    """Get voice response configuration"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        if ADVANCED_FEATURES_AVAILABLE:
            config = voice_interface.generate_voice_response(text, language)
            return jsonify({
                "success": True,
                "config": config
            })
        else:
            return jsonify({
                "success": False,
                "error": "Voice config not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("\n🚀 Starting INGRES Chatbot Live Model...")
    print("🌐 Access at: http://localhost:5000")
    print("🧪 Test APIs: python test_live_apis.py")
    print("📚 Setup Guide: See LIVE_API_SETUP_GUIDE.md")
    print("-" * 50)
    
    app.run(debug=Config.DEBUG, port=5000, host='0.0.0.0')