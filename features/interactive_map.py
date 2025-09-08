"""
Interactive Map Module for INGRES AI Chatbot
Handles map visualization and geospatial data processing
"""

import json
from datetime import datetime

class InteractiveMap:
    def __init__(self):
        self.map_layers = {
            "groundwater_levels": True,
            "quality_zones": True,
            "monitoring_wells": True,
            "crisis_alerts": True,
            "user_reports": False
        }
        
        self.map_config = {
            "default_center": [20.5937, 78.9629],  # India center
            "default_zoom": 5,
            "max_zoom": 18,
            "min_zoom": 4
        }
    
    def get_map_data(self, bounds=None, zoom_level=5):
        """Get map data for visualization"""
        # Sample groundwater monitoring points
        monitoring_points = [
            {
                "id": "MH001",
                "coordinates": [19.0760, 72.8777],
                "district": "Mumbai",
                "water_level": 15.2,
                "quality": "Good",
                "status": "Active",
                "last_updated": "2024-01-15"
            },
            {
                "id": "KA001", 
                "coordinates": [12.9716, 77.5946],
                "district": "Bangalore",
                "water_level": 8.5,
                "quality": "Poor",
                "status": "Critical",
                "last_updated": "2024-01-13"
            },
            {
                "id": "TN001",
                "coordinates": [13.0827, 80.2707],
                "district": "Chennai",
                "water_level": 6.2,
                "quality": "Critical",
                "status": "Alert",
                "last_updated": "2024-01-12"
            },
            {
                "id": "DL001",
                "coordinates": [28.7041, 77.1025],
                "district": "Delhi",
                "water_level": 18.7,
                "quality": "Good",
                "status": "Active",
                "last_updated": "2024-01-16"
            }
        ]
        
        return {
            "monitoring_points": monitoring_points,
            "layers": self.map_layers,
            "config": self.map_config,
            "bounds": bounds,
            "zoom_level": zoom_level,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_heatmap_data(self, data_type="water_level"):
        """Generate heatmap data for visualization"""
        heatmap_points = []
        
        # Sample data for heatmap
        base_points = [
            [19.0760, 72.8777, 0.8],  # Mumbai - Good
            [12.9716, 77.5946, 0.3],  # Bangalore - Poor
            [13.0827, 80.2707, 0.2],  # Chennai - Critical
            [28.7041, 77.1025, 0.9],  # Delhi - Good
            [18.5204, 73.8567, 0.6],  # Pune - Moderate
        ]
        
        return {
            "heatmap_data": base_points,
            "data_type": data_type,
            "legend": {
                "water_level": {
                    "high": {"value": 0.8, "color": "#00ff00", "label": "High (>15m)"},
                    "medium": {"value": 0.6, "color": "#ffff00", "label": "Medium (10-15m)"},
                    "low": {"value": 0.3, "color": "#ff8800", "label": "Low (5-10m)"},
                    "critical": {"value": 0.1, "color": "#ff0000", "label": "Critical (<5m)"}
                }
            }
        }
    
    def search_location(self, query):
        """Search for locations on the map"""
        # Simple location search - in production would use geocoding API
        locations = {
            "mumbai": {"coordinates": [19.0760, 72.8777], "name": "Mumbai, Maharashtra"},
            "bangalore": {"coordinates": [12.9716, 77.5946], "name": "Bangalore, Karnataka"},
            "chennai": {"coordinates": [13.0827, 80.2707], "name": "Chennai, Tamil Nadu"},
            "delhi": {"coordinates": [28.7041, 77.1025], "name": "Delhi"},
            "pune": {"coordinates": [18.5204, 73.8567], "name": "Pune, Maharashtra"}
        }
        
        query_lower = query.lower()
        matches = []
        
        for key, location in locations.items():
            if query_lower in key or query_lower in location["name"].lower():
                matches.append({
                    "name": location["name"],
                    "coordinates": location["coordinates"],
                    "relevance": 1.0 if query_lower == key else 0.8
                })
        
        return {
            "query": query,
            "matches": matches,
            "total": len(matches)
        }
    
    def toggle_layer(self, layer_name, enabled):
        """Toggle map layer visibility"""
        if layer_name in self.map_layers:
            self.map_layers[layer_name] = enabled
            return {
                "success": True,
                "layer": layer_name,
                "enabled": enabled,
                "layers": self.map_layers
            }
        
        return {
            "success": False,
            "error": f"Layer '{layer_name}' not found",
            "available_layers": list(self.map_layers.keys())
        }
    
    def get_area_statistics(self, coordinates, radius_km=50):
        """Get statistics for a specific area"""
        return {
            "center": coordinates,
            "radius_km": radius_km,
            "statistics": {
                "monitoring_wells": 12,
                "average_water_level": 11.8,
                "quality_distribution": {
                    "Good": 4,
                    "Moderate": 3,
                    "Poor": 3,
                    "Critical": 2
                },
                "trend_analysis": {
                    "improving": 2,
                    "stable": 6,
                    "declining": 4
                }
            },
            "timestamp": datetime.now().isoformat()
        }

# Global interactive map instance
interactive_map = InteractiveMap()