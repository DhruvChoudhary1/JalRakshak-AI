from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import threading
import time
import os

from ingres import update_state_groundwater_csv, scrape_city_groundwater_csv

app = Flask(__name__)
CORS(app)

CSV_PATH = './static/data/state_groundwater.csv'

# Example mapping: Add more states and their UUIDs as needed
STATE_UUIDS = {
    'RAJASTHAN': '785cc6f0-e9d0-4961-9578-08ed2f24377a',
    # Add other states here
}

def background_csv_updater():
    while True:
        try:
            update_state_groundwater_csv()
            print("CSV updated.")
        except Exception as e:
            print(f"CSV update error: {e}")
        time.sleep(60)  # Update every 60 seconds

threading.Thread(target=background_csv_updater, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/groundwater', methods=['POST'])
def groundwater_info():
    query = request.json.get('query', '').strip()
    state = None
    city = None

    # Check for city, state format
    if ',' in query:
        city, state = [x.strip().upper() for x in query.split(',', 1)]
        uuid = STATE_UUIDS.get(state)
        if not uuid:
            return jsonify({'status': 'error', 'message': 'State UUID not found. City-wise data unavailable.'})
        # Scrape city-wise data and save to a separate CSV
        scrape_city_groundwater_csv(state, uuid)
        csv_path = f'./static/data/{state}_city_groundwater.csv'
        try:
            df = pd.read_csv(csv_path)
            result = df[df['City'].str.upper() == city]
            if not result.empty:
                info = result.iloc[0].to_dict()
                return jsonify({'status': 'success', 'data': info})
            else:
                return jsonify({'status': 'error', 'message': 'City not found in selected state.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error loading city data: {e}'})
    else:
        state = query.upper()
        try:
            df = pd.read_csv(CSV_PATH)
            state_list = [s.upper() for s in df['State']]
            if state in state_list:
                result = df[df['State'].str.upper() == state]
                info = result.iloc[0].to_dict()
                return jsonify({'status': 'success', 'data': info})
            else:
                return jsonify({'status': 'error', 'message': 'State not found in latest data. If you are searching for a city, please use the format: City, State.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error loading state data: {e}'})

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    language = request.json.get('language', 'en')

    # City, State format
    if ',' in user_message:
        city, state = [x.strip().upper() for x in user_message.split(',', 1)]
        uuid = STATE_UUIDS.get(state)
        if uuid:
            csv_path = f'./static/data/{state}_city_groundwater.csv'
            if not os.path.exists(csv_path):
                scrape_city_groundwater_csv(state, uuid)
            try:
                city_df = pd.read_csv(csv_path)
                city_df['City'] = city_df['City'].astype(str).str.strip().str.upper()
                if city in city_df['City'].values:
                    city_data = city_df[city_df['City'] == city].iloc[0].to_dict()
                    response = (
                        f"Here is the groundwater data for {city}, {state}:\n"
                        f"Rainfall (mm): {city_data['Rainfall (mm)']}\n"
                        f"Annual Extractable Ground Water Resources (ham): {city_data['Annual Extractable Ground Water Resources (ham)']}\n"
                        f"Ground Water Extraction (ham): {city_data['Ground Water Extraction (ham)']}"
                    )
                else:
                    response = "I couldn't find groundwater data for that city in the selected state."
            except Exception as e:
                response = f"Error loading city data: {e}"
        else:
            response = "City-wise data is not available for this state."
        return jsonify({
            "response": response,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "language": language
        })
    else:
     state = user_message.strip().upper()
    try:
        df = pd.read_csv(CSV_PATH)
        # Normalize state names for comparison
        df['State'] = df['State'].astype(str).str.strip().str.upper()
        state = state.strip().upper()
        print("States in CSV:", df['State'].tolist())  # Debug print
        print("User state:", state)                    # Debug print
        # Use .loc for robust matching
        mask = df['State'] == state
        if mask.any():
            state_data = df.loc[mask].iloc[0].to_dict()
            response = (
                f"Here is the groundwater data for {state}:\n"
                f"Rainfall (mm): {state_data['Rainfall (mm)']}\n"
                f"Annual Extractable Ground Water Resources (ham): {state_data['Annual Extractable Ground Water Resources (ham)']}\n"
                f"Ground Water Extraction (ham): {state_data['Ground Water Extraction (ham)']}"
            )
        else:
            response = "I couldn't find groundwater data for that state."
    except Exception as e:
        response = f"Error loading state data: {e}"
    return jsonify({
        "response": response,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "language": language
    })
if __name__ == '__main__':
    app.run(debug=True, port=5000)