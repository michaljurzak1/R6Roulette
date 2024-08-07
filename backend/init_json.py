import argparse
import sys
import json
import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class OperatorData:
    def __init__(self, location: str):
        self.location = location
        self.operator_website = "https://www.ubisoft.com/en-us/game/rainbow-six/siege/game-info/operators"
    
    def close_overlay(self, driver):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))
            ).click()
        except Exception as e:
            print("No overlay to close or unable to close overlay:", e)

    def get_operators(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.operator_website)

        self.close_overlay(driver)

        driver.find_element(by='css selector', value='[aria-label="Defender"]').click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.oplist__card'))
        )

        operators = driver.find_elements(By.CSS_SELECTOR, '.oplist__card')
        defenders = [op.find_element(By.TAG_NAME, "span").text.title() for op in operators]
        defenders_icons = [op.find_element(By.CLASS_NAME, "oplist__card__icon").get_attribute("src") for op in operators]

        driver.find_element(by='css selector', value='[aria-label="Attacker"]').click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.oplist__card'))
        )

        operators = driver.find_elements(By.CSS_SELECTOR, '.oplist__card')
        attackers = [op.find_element(By.TAG_NAME, "span").text.title() for op in operators]
        attackers_icons = [op.find_element(By.CLASS_NAME, "oplist__card__icon").get_attribute("src") for op in operators]

        driver.quit()
        
        if not defenders and not attackers:
            raise Exception("No operators found")
        
        return (defenders, defenders_icons), (attackers, attackers_icons)
        
    def save_to_json(self, defenders, defenders_icons, attackers, attackers_icons):
        defenders_data = {
            "defenders": [{"name": name, "icon": icon} for name, icon in zip(defenders, defenders_icons)]
        }
        attackers_data = {
            "attackers": [{"name": name, "icon": icon} for name, icon in zip(attackers, attackers_icons)]
        }
        
        with open(os.path.join(self.location, "defenders.json"), 'w') as defenders_file:
            json.dump(defenders_data, defenders_file, indent=4)
        print("Defenders data saved to defenders.json file successfully")
        
        with open(os.path.join(self.location, "attackers.json"), 'w') as attackers_file:
            json.dump(attackers_data, attackers_file, indent=4)
        print("Attackers data saved to attackers.json file successfully")

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--name', help='name of the JSON file')
    
    # args = parser.parse_args(sys.argv[1:])
    location = "../frontend/r6roulette/public"
    operator_data = OperatorData(location)
    defs, atks = operator_data.get_operators()
    operator_data.save_to_json(*defs, *atks)
