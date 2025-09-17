import pandas as pd
from datetime import datetime, timedelta

class WaterCrisisPredictor:
    """Predicts water crisis using groundwater CSV data"""

    def __init__(self, state_csv='./static/data/state_groundwater.csv'):
        self.state_csv = state_csv

    def predict_state_crisis(self, state):
        df = pd.read_csv(self.state_csv)
        df['State'] = df['State'].astype(str).str.strip().str.upper()
        state = state.strip().upper()
        row = df[df['State'] == state]
        if row.empty:
            return {"error": "State not found in groundwater data."}

        rainfall = float(str(row['Rainfall (mm)'].values[0]).replace(',', ''))
        resource = float(str(row['Annual Extractable Ground Water Resources (ham)'].values[0]).replace(',', ''))
        extraction = float(str(row['Ground Water Extraction (ham)'].values[0]).replace(',', ''))

        return self._predict_crisis(state, rainfall, resource, extraction, level_type="state")

    def predict_city_crisis(self, state, city):
        csv_path = f'./static/data/{state}_city_groundwater.csv'
        df = pd.read_csv(csv_path)
        df['City'] = df['City'].astype(str).str.strip().str.upper()
        city = city.strip().upper()
        row = df[df['City'] == city]
        if row.empty:
            return {"error": "City not found in groundwater data."}

        rainfall = float(str(row['Rainfall (mm)'].values[0]).replace(',', ''))
        resource = float(str(row['Annual Extractable Ground Water Resources (ham)'].values[0]).replace(',', ''))
        extraction = float(str(row['Ground Water Extraction (ham)'].values[0]).replace(',', ''))

        return self._predict_crisis(city, rainfall, resource, extraction, level_type="city")

    def _predict_crisis(self, location, rainfall, resource, extraction, level_type="state"):
        # Simple logic: If extraction > resource, crisis is likely
        ratio = extraction / resource if resource > 0 else 0
        if ratio > 1.0:
            severity = 'Critical'
            days_to_crisis = 15
        elif ratio > 0.8:
            severity = 'High'
            days_to_crisis = 30
        elif ratio > 0.6:
            severity = 'Moderate'
            days_to_crisis = 45
        else:
            severity = 'Low'
            days_to_crisis = 60

        crisis_date = datetime.now() + timedelta(days=days_to_crisis)
        recommendations = self._generate_recommendations(severity, days_to_crisis)

        return {
            'location': location,
            'level_type': level_type,
            'rainfall_mm': rainfall,
            'resource_ham': resource,
            'extraction_ham': extraction,
            'extraction_to_resource_ratio': round(ratio, 2),
            'severity': severity,
            'days_to_crisis': days_to_crisis,
            'crisis_date': crisis_date.strftime('%Y-%m-%d'),
            'recommendations': recommendations,
            'last_updated': datetime.now().isoformat(),
            'data_sources': ['INGRES Groundwater CSV']
        }

    def _generate_recommendations(self, severity, days):
        if severity == 'Critical':
            return [
                "IMMEDIATE ACTION REQUIRED",
                "Implement emergency water rationing",
                "Activate alternative water sources",
                f"Action needed within {days} days"
            ]
        elif severity == 'High':
            return [
                "Begin water conservation campaigns",
                "Prepare emergency water distribution plans",
                f"Action needed within {days} days"
            ]
        elif severity == 'Moderate':
            return [
                "Increase public awareness about water conservation",
                "Implement rainwater harvesting programs",
                f"Prepare over next {days} days"
            ]
        else:
            return [
                "Continue regular water monitoring",
                "Promote sustainable water usage",
                f"Monitor and prepare over next {days} days"
            ]

# Initialize predictor for import/use in app.py
crisis_predictor = WaterCrisisPredictor()

if __name__ == "__main__":
    # Demo run for state
    print(crisis_predictor.predict_state_crisis("RAJASTHAN"))
    # Demo run for city (requires city CSV)
    # print(crisis_predictor.predict_city_crisis("RAJASTHAN", "JAIPUR"))