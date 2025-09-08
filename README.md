# AI INGRES Groundwater Chatbot - Prototype

## Overview
A chatbot prototype that integrates with INGRES (India-WRIS Geospatial Repository) for groundwater monitoring and Q&A with visualization capabilities.

## Features
- Interactive chatbot for groundwater queries
- District-wise groundwater status visualization
- INGRES dataset integration with inline citations
- Real-time groundwater level monitoring
- Water quality analysis and recommendations

## Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Data Visualization: Chart.js
- Mock INGRES API integration

## Setup

### Quick Start (Demo Mode)
```bash
pip install -r requirements.txt
python app.py
# Open browser to http://localhost:5000
```

### Production Setup (With API Keys)
1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```
2. **Add your API keys to `.env`:**
   ```bash
   # Required for full functionality
   INGRES_API_KEY=your_ingres_api_key
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run application:**
   ```bash
   python app.py
   ```

📖 **See `api_integration_guide.md` for detailed API setup instructions**

## Project Structure
```
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   ├── js/
│   │   └── script.js     # Frontend logic
│   └── data/
│       └── groundwater_data.json  # Mock INGRES data
└── templates/
    └── index.html        # Main interface
```
