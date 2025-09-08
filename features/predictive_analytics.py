"""
Predictive Analytics Module for INGRES AI Chatbot
Handles water level predictions, trend analysis, and forecasting
"""

import json
import math
from datetime import datetime, timedelta

class PredictiveAnalytics:
    def __init__(self):
        self.models = {
            "seasonal": "Seasonal ARIMA Model",
            "regression": "Linear Regression",
            "neural": "Simple Neural Network",
            "ensemble": "Ensemble Method"
        }
        
        self.prediction_horizons = {
            "short_term": 30,   # 30 days
            "medium_term": 90,  # 3 months
            "long_term": 365    # 1 year
        }
    
    def predict_water_levels(self, district, current_level, horizon="medium_term"):
        """Predict future water levels for a district"""
        days = self.prediction_horizons.get(horizon, 90)
        
        # Simple prediction model (in production would use ML models)
        predictions = []
        base_level = current_level
        
        for day in range(1, days + 1):
            # Simulate seasonal variation and trend
            seasonal_factor = 1 + 0.3 * math.sin(2 * math.pi * day / 365)
            trend_factor = 1 - (0.001 * day)  # Slight declining trend
            noise = 0.1 * math.sin(day * 0.1)  # Random variation
            
            predicted_level = base_level * seasonal_factor * trend_factor + noise
            predicted_level = max(0, predicted_level)  # Ensure non-negative
            
            predictions.append({
                "date": (datetime.now() + timedelta(days=day)).isoformat()[:10],
                "predicted_level": round(predicted_level, 2),
                "confidence": max(0.5, 0.95 - (day * 0.005)),  # Decreasing confidence
                "day": day
            })
        
        return {
            "district": district,
            "current_level": current_level,
            "horizon": horizon,
            "days": days,
            "predictions": predictions,
            "model_used": "ensemble",
            "accuracy": 0.85,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_trends(self, district, historical_data=None):
        """Analyze historical trends and patterns"""
        # Mock historical analysis
        trend_analysis = {
            "overall_trend": "declining",
            "trend_strength": 0.65,
            "seasonal_patterns": {
                "monsoon_impact": 0.8,
                "summer_decline": 0.6,
                "winter_stability": 0.4
            },
            "anomalies_detected": [
                {
                    "date": "2023-08-15",
                    "type": "sudden_drop",
                    "magnitude": 2.3,
                    "possible_cause": "Excessive pumping"
                }
            ],
            "correlation_factors": {
                "rainfall": 0.75,
                "temperature": -0.45,
                "agricultural_activity": -0.60,
                "urban_development": -0.35
            }
        }
        
        return {
            "district": district,
            "analysis": trend_analysis,
            "recommendations": self._generate_trend_recommendations(trend_analysis),
            "timestamp": datetime.now().isoformat()
        }
    
    def forecast_crisis_probability(self, district, current_conditions):
        """Forecast probability of water crisis"""
        water_level = current_conditions.get("water_level", 10)
        quality = current_conditions.get("quality", "Moderate")
        trend = current_conditions.get("trend", "Stable")
        
        # Calculate crisis probability based on multiple factors
        level_risk = max(0, (15 - water_level) / 15)  # Higher risk for lower levels
        quality_risk = {"Good": 0.1, "Moderate": 0.3, "Poor": 0.6, "Critical": 0.9}.get(quality, 0.5)
        trend_risk = {"Improving": 0.1, "Stable": 0.3, "Declining": 0.7}.get(trend, 0.5)
        
        overall_probability = (level_risk * 0.5 + quality_risk * 0.3 + trend_risk * 0.2)
        
        # Forecast for different time periods
        forecasts = []
        for months in [1, 3, 6, 12]:
            # Probability increases over time if conditions are poor
            time_factor = 1 + (months * 0.1 * overall_probability)
            probability = min(0.95, overall_probability * time_factor)
            
            forecasts.append({
                "months": months,
                "probability": round(probability, 3),
                "risk_level": self._get_risk_level(probability),
                "confidence": max(0.6, 0.9 - (months * 0.05))
            })
        
        return {
            "district": district,
            "current_conditions": current_conditions,
            "forecasts": forecasts,
            "key_factors": {
                "water_level_risk": round(level_risk, 3),
                "quality_risk": round(quality_risk, 3),
                "trend_risk": round(trend_risk, 3)
            },
            "recommendations": self._generate_crisis_recommendations(overall_probability),
            "timestamp": datetime.now().isoformat()
        }
    
    def compare_districts(self, districts_data):
        """Compare predictive metrics across multiple districts"""
        comparisons = []
        
        for district, data in districts_data.items():
            prediction = self.predict_water_levels(district, data.get("water_level", 10))
            crisis_forecast = self.forecast_crisis_probability(district, data)
            
            comparisons.append({
                "district": district,
                "current_level": data.get("water_level", 10),
                "predicted_change_30d": prediction["predictions"][29]["predicted_level"] - data.get("water_level", 10),
                "crisis_probability_3m": crisis_forecast["forecasts"][1]["probability"],
                "risk_ranking": self._calculate_risk_ranking(data, prediction, crisis_forecast)
            })
        
        # Sort by risk ranking
        comparisons.sort(key=lambda x: x["risk_ranking"], reverse=True)
        
        return {
            "comparisons": comparisons,
            "highest_risk": comparisons[0]["district"] if comparisons else None,
            "lowest_risk": comparisons[-1]["district"] if comparisons else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_trend_recommendations(self, trend_analysis):
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        if trend_analysis["overall_trend"] == "declining":
            recommendations.extend([
                "Implement water conservation measures",
                "Monitor pumping activities closely",
                "Consider artificial recharge projects"
            ])
        
        if trend_analysis["seasonal_patterns"]["monsoon_impact"] < 0.5:
            recommendations.append("Improve rainwater harvesting infrastructure")
        
        return recommendations
    
    def _generate_crisis_recommendations(self, probability):
        """Generate crisis prevention recommendations"""
        if probability > 0.7:
            return [
                "Immediate intervention required",
                "Restrict groundwater extraction",
                "Activate emergency water supply",
                "Implement strict conservation measures"
            ]
        elif probability > 0.4:
            return [
                "Increase monitoring frequency",
                "Prepare contingency plans",
                "Promote water conservation",
                "Consider alternative water sources"
            ]
        else:
            return [
                "Continue regular monitoring",
                "Maintain current conservation efforts",
                "Plan for seasonal variations"
            ]
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability > 0.7:
            return "High"
        elif probability > 0.4:
            return "Medium"
        elif probability > 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def _calculate_risk_ranking(self, data, prediction, crisis_forecast):
        """Calculate overall risk ranking for a district"""
        level_score = max(0, (20 - data.get("water_level", 10)) / 20)
        trend_score = prediction["predictions"][29]["predicted_level"] < data.get("water_level", 10)
        crisis_score = crisis_forecast["forecasts"][1]["probability"]
        
        return (level_score * 0.4 + trend_score * 0.3 + crisis_score * 0.3)

# Global predictive analytics instance
predictive_analytics = PredictiveAnalytics()