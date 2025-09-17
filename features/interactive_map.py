"""
Interactive Map Module for INGRES AI Chatbot
Handles map visualization and geospatial data processing
"""

import json
from datetime import datetime
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

class InteractiveMap:
    def __init__(self, state_csv='./static/data/state_groundwater.csv'):
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
        self.state_csv = state_csv
        self.n_clusters = 4  # For spatial clustering

    def get_map_data(self, bounds=None, zoom_level=5):
        """Get map data for visualization using latest CSV from ingres.py, with ML clustering and anomaly detection"""
        try:
            df = pd.read_csv(self.state_csv)
            # Prepare features for clustering and anomaly detection
            features = df[["Latitude", "Longitude", "Ground Water Extraction (ham)"]].dropna()
            # Clustering: group wells into zones
            if len(features) >= self.n_clusters:
                kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(features)
                df["cluster"] = -1
                df.loc[features.index, "cluster"] = clusters
            else:
                df["cluster"] = -1
            # Anomaly detection: flag abnormal wells
            if len(features) >= 10:
                iso = IsolationForest(contamination=0.1, random_state=42)
                anomalies = iso.fit_predict(features)
                df["anomaly"] = 0
                df.loc[features.index, "anomaly"] = anomalies
            else:
                df["anomaly"] = 0

            monitoring_points = []
            for idx, row in df.iterrows():
                monitoring_points.append({
                    "id": row.get("ID", ""),
                    "coordinates": [row.get("Latitude", 0), row.get("Longitude", 0)],
                    "district": row.get("District", row.get("State", "")),
                    "water_level": row.get("Ground Water Extraction (ham)", 0),
                    "quality": row.get("Quality", "Unknown"),
                    "status": self._get_status(row),
                    "last_updated": row.get("Last Updated", datetime.now().strftime("%Y-%m-%d")),
                    "cluster": int(row.get("cluster", -1)),
                    "anomaly": int(row.get("anomaly", 0))
                })
        except Exception:
            # fallback to sample data if CSV not available
            monitoring_points = [
                {
                    "id": "MH001",
                    "coordinates": [19.0760, 72.8777],
                    "district": "Mumbai",
                    "water_level": 15.2,
                    "quality": "Good",
                    "status": "Active",
                    "last_updated": "2024-01-15",
                    "cluster": 0,
                    "anomaly": 0
                },
                {
                    "id": "KA001", 
                    "coordinates": [12.9716, 77.5946],
                    "district": "Bangalore",
                    "water_level": 8.5,
                    "quality": "Poor",
                    "status": "Critical",
                    "last_updated": "2024-01-13",
                    "cluster": 1,
                    "anomaly": 1
                },
                {
                    "id": "TN001",
                    "coordinates": [13.0827, 80.2707],
                    "district": "Chennai",
                    "water_level": 6.2,
                    "quality": "Critical",
                    "status": "Alert",
                    "last_updated": "2024-01-12",
                    "cluster": 2,
                    "anomaly": 0
                },
                {
                    "id": "DL001",
                    "coordinates": [28.7041, 77.1025],
                    "district": "Delhi",
                    "water_level": 18.7,
                    "quality": "Good",
                    "status": "Active",
                    "last_updated": "2024-01-16",
                    "cluster": 3,
                    "anomaly": 0
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

    def _get_status(self, row):
        """Determine status based on extraction/resource ratio"""
        try:
            extraction = float(str(row.get("Ground Water Extraction (ham)", 0)).replace(',', ''))
            resource = float(str(row.get("Annual Extractable Ground Water Resources (ham)", 0)).replace(',', ''))
            ratio = extraction / resource if resource > 0 else 0
            if ratio > 1.0:
                return "Critical"
            elif ratio > 0.8:
                return "Alert"
            elif ratio > 0.6:
                return "Moderate"
            else:
                return "Active"
        except Exception:
            return "Unknown"

    def get_heatmap_data(self, data_type="water_level"):
        """Generate heatmap data for visualization using CSV"""
        try:
            df = pd.read_csv(self.state_csv)
            heatmap_points = []
            for _, row in df.iterrows():
                lat = row.get("Latitude", None)
                lon = row.get("Longitude", None)
                val = float(str(row.get("Ground Water Extraction (ham)", 0)).replace(',', ''))
                if lat and lon:
                    heatmap_points.append([lat, lon, val])
        except Exception:
            # fallback to sample data
            heatmap_points = [
                [19.0760, 72.8777, 0.8],
                [12.9716, 77.5946, 0.3],
                [13.0827, 80.2707, 0.2],
                [28.7041, 77.1025, 0.9],
                [18.5204, 73.8567, 0.6],
            ]
        return {
            "heatmap_data": heatmap_points,
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
        """Search for locations on the map (can be enhanced with ML/NLP)"""
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
        """Get statistics for a specific area using CSV data, with ML clustering info"""
        try:
            df = pd.read_csv(self.state_csv)
            wells = df[(df["Latitude"] >= coordinates[0] - 1) & (df["Latitude"] <= coordinates[0] + 1) &
                       (df["Longitude"] >= coordinates[1] - 1) & (df["Longitude"] <= coordinates[1] + 1)]
            avg_water_level = wells["Ground Water Extraction (ham)"].astype(float).mean() if not wells.empty else 0
            quality_dist = wells["Quality"].value_counts().to_dict() if "Quality" in wells else {}
            cluster_dist = wells["cluster"].value_counts().to_dict() if "cluster" in wells else {}
            anomaly_count = int(wells["anomaly"].sum()) if "anomaly" in wells else 0
            return {
                "center": coordinates,
                "radius_km": radius_km,
                "statistics": {
                    "monitoring_wells": len(wells),
                    "average_water_level": avg_water_level,
                    "quality_distribution": quality_dist,
                    "cluster_distribution": cluster_dist,
                    "anomaly_count": anomaly_count
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception:
            # fallback
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
                    "cluster_distribution": {0: 4, 1: 3, 2: 3, 3: 2},
                    "anomaly_count": 2
                },
                "timestamp": datetime.now().isoformat()
            }

# Global interactive map instance
interactive_map = InteractiveMap()