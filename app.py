from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import threading
import time
import os
import spacy
from selenium import webdriver

from dotenv import load_dotenv 

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


from ingres import update_state_groundwater_csv, scrape_city_groundwater_csv
from features.crisis_predictor import crisis_predictor

app = Flask(__name__)
CORS(app)

CSV_PATH = './static/data/state_groundwater.csv'

# Example mapping: Add more states and their UUIDs as needed
STATE_UUIDS = {
    'RAJASTHAN': '785cc6f0-e9d0-4961-9578-08ed2f24377a',
    # Add other states here
}

# Load spaCy English model once
nlp = spacy.load("en_core_web_sm")

def extract_state_from_text(text, state_list):
    doc = nlp(text)
    text_upper = text.upper()
    # Direct substring match
    for state in state_list:
        if state in text_upper:
            return state
    # Use spaCy NER for location extraction
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            ent_text = ent.text.strip().upper()
            for state in state_list:
                if state == ent_text:
                    return state
    return None

def extract_city_from_text(text, city_list):
    doc = nlp(text)
    text_upper = text.upper()
    for city in city_list:
        if city in text_upper:
            return city
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            ent_text = ent.text.strip().upper()
            for city in city_list:
                if city == ent_text:
                    return city
    return None

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
    return render_template('index.html', GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY) 

@app.route('/api/groundwater', methods=['POST'])
def groundwater_info():
    query = request.json.get('query', '').strip()
    df = pd.read_csv(CSV_PATH)
    df['State'] = df['State'].astype(str).str.strip().str.upper()
    state_list = df['State'].tolist()

    # City, State format or free text
    if ',' in query:
        city, state = [x.strip().upper() for x in query.split(',', 1)]
    else:
        state = extract_state_from_text(query, state_list)
        city = None

    if city and state:
        uuid = STATE_UUIDS.get(state)
        if not uuid:
            return jsonify({'status': 'error', 'message': 'State UUID not found. City-wise data unavailable.'})
        scrape_city_groundwater_csv(state, uuid)
        csv_path = f'./static/data/{state}_city_groundwater.csv'
        try:
            city_df = pd.read_csv(csv_path)
            city_df['City'] = city_df['City'].astype(str).str.strip().str.upper()
            city_list = city_df['City'].tolist()
            found_city = extract_city_from_text(query, city_list)
            if found_city and found_city in city_df['City'].values:
                info = city_df[city_df['City'] == found_city].iloc[0].to_dict()
                return jsonify({'status': 'success', 'data': info})
            else:
                return jsonify({'status': 'error', 'message': 'City not found in selected state.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error loading city data: {e}'})
    elif state:
        if state in state_list:
            info = df[df['State'] == state].iloc[0].to_dict()
            return jsonify({'status': 'success', 'data': info})
        else:
            return jsonify({'status': 'error', 'message': 'State not found in latest data. If you are searching for a city, please use the format: City, State.'})
    else:
        return jsonify({'status': 'error', 'message': 'Could not extract a valid state or city from your query.'})

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    language = request.json.get('language', 'en')

    df = pd.read_csv(CSV_PATH)
    df['State'] = df['State'].astype(str).str.strip().str.upper()
    state_list = df['State'].tolist()

    # Try to extract city and state from free text
    if ',' in user_message:
        city, state = [x.strip().upper() for x in user_message.split(',', 1)]
    else:
        state = extract_state_from_text(user_message, state_list)
        city = None

    if city and state:
        uuid = STATE_UUIDS.get(state)
        if uuid:
            csv_path = f'./static/data/{state}_city_groundwater.csv'
            if not os.path.exists(csv_path):
                scrape_city_groundwater_csv(state, uuid)
            try:
                city_df = pd.read_csv(csv_path)
                city_df['City'] = city_df['City'].astype(str).str.strip().str.upper()
                city_list = city_df['City'].tolist()
                found_city = extract_city_from_text(user_message, city_list)
                if found_city and found_city in city_df['City'].values:
                    city_data = city_df[city_df['City'] == found_city].iloc[0].to_dict()
                    response = (
                        f"Here is the groundwater data for {found_city}, {state}:\n"
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
    elif state:
        if state in state_list:
            state_data = df[df['State'] == state].iloc[0].to_dict()
            response = (
                f"Here is the groundwater data for {state}:\n"
                f"Rainfall (mm): {state_data['Rainfall (mm)']}\n"
                f"Annual Extractable Ground Water Resources (ham): {state_data['Annual Extractable Ground Water Resources (ham)']}\n"
                f"Ground Water Extraction (ham): {state_data['Ground Water Extraction (ham)']}"
            )
        else:
            response = "I couldn't find groundwater data for that state."
        return jsonify({
            "response": response,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "language": language
        })
    else:
        response = "Could not extract a valid state or city from your query."
        return jsonify({
            "response": response,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "language": language
        })
    
@app.route('/api/crisis/state', methods=['POST'])
def crisis_state():
    state = request.json.get('state', '')
    result = crisis_predictor.predict_state_crisis(state)
    return jsonify(result)

@app.route('/api/crisis/city', methods=['POST'])
def crisis_city():
    state = request.json.get('state', '')
    city = request.json.get('city', '')
    result = crisis_predictor.predict_city_crisis(state, city)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)