from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

def update_state_groundwater_csv():
    """Scrape and update state-wise groundwater CSV."""
    url = 'https://ingres.iith.ac.in/gecdataonline/gis/INDIA;parentLocName=INDIA;locname=INDIA;loctype=COUNTRY;view=ADMIN;locuuid=ffce954d-24e1-494b-ba7e-0931d8ad6085;year=2024-2025;computationType=normal;component=recharge;period=annual;category=safe;mapOnClickParams=false'
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(10)

    table = driver.find_element(By.CSS_SELECTOR, 'table.mat-table')
    rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')

    data = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(cells) == 4:
            data.append([cell.text.strip() for cell in cells])

    columns = ['State', 'Rainfall (mm)', 'Annual Extractable Ground Water Resources (ham)', 'Ground Water Extraction (ham)']
    os.makedirs('./static/data', exist_ok=True)
    df = pd.DataFrame(data, columns=columns)
    df.to_csv('./static/data/state_groundwater.csv', index=False)
    print("Saved to ./static/data/state_groundwater.csv")
    driver.quit()

def scrape_city_groundwater_csv(state_name, state_uuid):
    """
    Scrape and save city-wise groundwater data for a given state.
    Args:
        state_name (str): Name of the state (e.g., 'RAJASTHAN')
        state_uuid (str): UUID of the state (from URL)
    """
    url = (
        f"https://ingres.iith.ac.in/gecdataonline/gis/INDIA;"
        f"locname={state_name};loctype=STATE;view=ADMIN;"
        f"locuuid={state_uuid};year=2024-2025;computationType=normal;"
        f"component=recharge;period=annual;category=safe;"
        f"mapOnClickParams=true;stateuuid={state_uuid}"
    )
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(10)

    table = driver.find_element(By.CSS_SELECTOR, 'table.mat-table')
    rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')

    data = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(cells) == 4:
            data.append([cell.text.strip() for cell in cells])

    columns = ['City', 'Rainfall (mm)', 'Annual Extractable Ground Water Resources (ham)', 'Ground Water Extraction (ham)']
    os.makedirs('./static/data', exist_ok=True)
    csv_path = f'./static/data/{state_name}_city_groundwater.csv'
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(csv_path, index=False)
    print(f"Saved to {csv_path}")
    driver.quit()