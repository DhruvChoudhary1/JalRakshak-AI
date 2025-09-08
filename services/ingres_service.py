import requests
import json
from datetime import datetime
from config import Config

class INGRESService:
    """Service class for INGRES API integration"""
    
    def __init__(self):
        self.api_key = Config.INGRES_API_KEY
        self.base_url = Config.INGRES_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        } if self.api_key else {}
    
    def is_available(self):
        """Check if INGRES API is available"""
        return bool(self.api_key)
    
    async def get_groundwater_data(self, district=None, state=None):
        """
        Fetch groundwater data from INGRES API
        
        Args:
            district (str): District name
            state (str): State name
            
        Returns:
            dict: Groundwater data or mock data if API unavailable
        """
        if not self.is_available():
            print("📡 INGRES API not configured, using mock data")
            return self._get_mock_data(district)
        
        try:
            # Construct API endpoint
            endpoint = f"{self.base_url}/groundwater"
            params = {}
            
            if district:
                params['district'] = district
            if state:
                params['state'] = state
            
            # Make API request
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_ingres_data(data)
            else:
                print(f"❌ INGRES API error: {response.status_code}")
                return self._get_mock_data(district)
                
        except requests.exceptions.RequestException as e:
            print(f"🔌 INGRES API connection error: {e}")
            return self._get_mock_data(district)
    
    def _format_ingres_data(self, raw_data):
        """Format raw INGRES data to our standard format"""
        formatted_data = {}
        
        for station in raw_data.get('stations', []):
            district = station.get('district')
            if district:
                formatted_data[district] = {
                    'water_level': station.get('water_level_mbgl', 0),
                    'quality': self._determine_quality(station.get('water_quality_index', 0)),
                    'trend': station.get('trend', 'Unknown'),
                    'last_updated': station.get('last_measurement', datetime.now().isoformat()),
                    'coordinates': [
                        station.get('latitude', 0),
                        station.get('longitude', 0)
                    ],
                    'wells_monitored': station.get('wells_count', 0),
                    'citation': station.get('station_id', 'INGRES-UNKNOWN')
                }
        
        return formatted_data
    
    def _determine_quality(self, wqi):
        """Convert Water Quality Index to quality category"""
        if wqi >= 90:
            return "Excellent"
        elif wqi >= 70:
            return "Good"
        elif wqi >= 50:
            return "Moderate"
        elif wqi >= 25:
            return "Poor"
        else:
            return "Critical"
    
    def _get_mock_data(self, district=None):
        """Return mock data when INGRES API is unavailable"""
        mock_data = {
            "Mumbai": {
                "water_level": 15.2,
                "quality": "Good",
                "trend": "Stable",
                "last_updated": "2024-01-15",
                "coordinates": [19.0760, 72.8777],
                "wells_monitored": 45,
                "citation": "INGRES-MH-001-2024 (Mock Data)"
            },
            "Pune": {
                "water_level": 12.8,
                "quality": "Moderate",
                "trend": "Declining",
                "last_updated": "2024-01-14",
                "coordinates": [18.5204, 73.8567],
                "wells_monitored": 38,
                "citation": "INGRES-MH-002-2024 (Mock Data)"
            },
            "Bangalore": {
                "water_level": 8.5,
                "quality": "Poor",
                "trend": "Critical",
                "last_updated": "2024-01-13",
                "coordinates": [12.9716, 77.5946],
                "wells_monitored": 52,
                "citation": "INGRES-KA-001-2024 (Mock Data)"
            }
        }
        
        if district and district in mock_data:
            return {district: mock_data[district]}
        
        return mock_data

# Example INGRES API endpoints (based on typical government API structure)
INGRES_ENDPOINTS = {
    'groundwater_stations': '/groundwater/stations',
    'water_levels': '/groundwater/levels',
    'water_quality': '/groundwater/quality',
    'monitoring_wells': '/groundwater/wells',
    'historical_data': '/groundwater/historical',
    'alerts': '/groundwater/alerts'
}