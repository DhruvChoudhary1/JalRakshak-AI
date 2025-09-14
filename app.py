from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import threading
import time

# Import your INGRES scraping function from iingres.py
from iingres import update_state_groundwater_csv

app = Flask(__name__)
CORS(app)

CSV_PATH = './static/data/state_groundwater.csv'

def background_csv_updater():
    while True:
        try:
            update_state_groundwater_csv()
            print("CSV updated.")
        except Exception as e:
            print(f"CSV update error: {e}")
        time.sleep(1)  # Update every second

# Start background thread to keep CSV updated
threading.Thread(target=background_csv_updater, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state-groundwater', methods=['POST'])
def get_state_groundwater():
    state = request.json.get('state', '').strip().upper()
    df = pd.read_csv(CSV_PATH)
    result = df[df['State'].str.upper() == state]
    if not result.empty:
        info = result.iloc[0].to_dict()
        return jsonify({'status': 'success', 'data': info})
    else:
        return jsonify({'status': 'error', 'message': 'State not found.'})

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    language = request.json.get('language', 'en')
    mentioned_state = None
    state_data = None

    df = pd.read_csv(CSV_PATH)
    for state in df['State']:
        if state.lower() in user_message.lower():
            mentioned_state = state
            break

    if mentioned_state:
        result = df[df['State'] == mentioned_state]
        if not result.empty:
            state_data = result.iloc[0].to_dict()
            response = (
                f"Here is the groundwater data for {mentioned_state}:\n"
                f"Rainfall (mm): {state_data['Rainfall (mm)']}\n"
                f"Annual Extractable Ground Water Resources (ham): {state_data['Annual Extractable Ground Water Resources (ham)']}\n"
                f"Ground Water Extraction (ham): {state_data['Ground Water Extraction (ham)']}"
            )
        else:
            response = "I couldn't find groundwater data for that state."
    else:
        response = "Please specify a state to get groundwater data."

    return jsonify({
        "response": response,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "state_data": state_data,
        "language": language
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)