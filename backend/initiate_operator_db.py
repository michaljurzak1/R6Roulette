import sqlite3
import argparse
import sys
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class Database:
    def __init__(self, name: str):
        self.name = name
        self.operator_website = "https://www.ubisoft.com/en-us/game/rainbow-six/siege/game-info/operators"
    
    def create_or_truncate_sqlite_db(self):
        """Create a sqlite3"""
        conn = None
        
        try:
            conn = sqlite3.connect(self.name)            
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS operators")

            conn.commit()
            
        except sqlite3.Error as e:
            print(e)
            
        finally:
            if conn:
                conn.close()

    def create_table(self, name: str):
        """Create a table in the sqlite3 database"""
        conn = None
        
        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE {name} (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    side TEXT NOT NULL,
                    icon TEXT NOT NULL
                )
            """)
            conn.commit()
            print("Table created successfully")
        except sqlite3.Error as e:
            print(e)
            
        finally:
            if conn:
                conn.close()
    
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
        
        if defenders is None and attackers is None:
            raise Exception("No operators found")
        
        return (defenders, defenders_icons ), (attackers, attackers_icons)
        
    def insert_operators(self, operators: list, operators_icons: list, side: str):
        conn = None
        
        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()
        
            data_to_insert = [(op, side, icon) for op, icon in zip(operators, operators_icons)]
            
            cursor.executemany("INSERT INTO operators (name, side, icon) VALUES (?, ?, ?)", data_to_insert)
            conn.commit()
            print("Operators inserted successfully")
        except sqlite3.Error as e:
            print(e)
            
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='name of the sqlite3 database file')
    
    db = Database(parser.parse_args(sys.argv[1:]).name)
    db.create_or_truncate_sqlite_db()
    db.create_table("operators")
    defs, atks = db.get_operators()
    db.insert_operators(*defs, "d")
    db.insert_operators(*atks, "a")