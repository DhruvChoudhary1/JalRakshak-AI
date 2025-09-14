from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

def update_state_groundwater_csv():
    url = 'https://ingres.iith.ac.in/gecdataonline/gis/INDIA;parentLocName=INDIA;locname=INDIA;loctype=COUNTRY;view=ADMIN;locuuid=ffce954d-24e1-494b-ba7e-0931d8ad6085;year=2024-2025;computationType=normal;component=recharge;period=annual;category=safe;mapOnClickParams=false'
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(10)  # Increase if your internet is slow

    # Find the main state-wise table (update selector if needed)
    table = driver.find_element(By.CSS_SELECTOR, 'table.mat-table')
    rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')

    data = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(cells) == 4:
            data.append([cell.text.strip() for cell in cells])

    columns = ['State', 'Rainfall (mm)', 'Annual Extractable Ground Water Resources (ham)', 'Ground Water Extraction (ham)']
    df = pd.DataFrame(data, columns=columns)
    df.to_csv('./static/data/state_groundwater.csv', index=False)
    print("Saved to ./static/data/state_groundwater.csv")

    driver.quit() 