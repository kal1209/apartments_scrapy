import os
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from decouple import config

def extract_element_text(element, selector):
    try:
        return element.find_element(By.CSS_SELECTOR, selector).text
    except NoSuchElementException:
        return ""

def extract_element_attribute(element, selector, attribute):
    try:
        return element.find_element(By.CSS_SELECTOR, selector).get_attribute(attribute)
    except NoSuchElementException:
        return ""
    
def has_email_button(li_element):
    try:
        li_element.find_element(By.CSS_SELECTOR, '.checkAvailability')
        return True
    except NoSuchElementException:
        return False

def get_page_number(driver):
    try:
        page_text = driver.find_element(By.CSS_SELECTOR, '#placardContainer .pageRange').text
        return int(page_text.split(' ')[-1])
    except NoSuchElementException:
        return 1

def get_apart_data(website_url):
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(website_url)

        properties_list = []
        current_datetime = str(datetime.now())

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'placardContainer'))
        )

        li_elements = driver.find_elements(By.CSS_SELECTOR, '#placardContainer li.mortar-wrapper')

        for li_element in li_elements:
            LISTING_NAME = extract_element_text(li_element, '.property-title')
            LISTING_LINK = extract_element_attribute(li_element, '.property-link', 'href')
            LISTING_ADDRESS = extract_element_attribute(li_element, '.property-address', 'title')
            LISTING_DESCRIPTION = extract_element_text(li_element, '.property-amenities')
            mediaLinksText = extract_element_text(li_element, '.mediaLinksList')
            HAS_VIDEOS = "Videos" in mediaLinksText
            HAS_VIRTUAL_TOUR = "Virtual Tour" in mediaLinksText
            HAS_EMAIL = has_email_button(li_element)
            PRICE = extract_element_text(li_element, '.property-pricing') or extract_element_text(li_element, '.price-range') or extract_element_text(li_element, '.property-rents')
            PHONE_NUMBER = extract_element_text(li_element, '.phone-link')
            SPECIALS_TEXT = extract_element_text(li_element, '.property-specials')

            property_info = {
                "SCRAPE_TIME": current_datetime,
                "REQUEST_TIME": str(datetime.now()),
                "LISTING_NAME": LISTING_NAME,
                "LISTING_LINK": LISTING_LINK,
                "LISTING_ADDRESS": LISTING_ADDRESS,
                "LISTING_DESCRIPTION": LISTING_DESCRIPTION,
                "HAS_VIDEOS": HAS_VIDEOS,
                "HAS_VIRTUAL_TOUR": HAS_VIRTUAL_TOUR,
                "HAS_EMAIL": HAS_EMAIL,
                "PRICE": PRICE,
                "PHONE_NUMBER": PHONE_NUMBER,
                "SPECIALS_TEXT": SPECIALS_TEXT,
            }
            properties_list.append(property_info)
        
        return {
            "properties_list": properties_list,
            "page": get_page_number(driver)
        }

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

if not os.path.exists("arpart_list"):
    os.makedirs("arpart_list")

with open("states.json", "r", encoding="utf-8") as f:
    short_states = json.load(f)

with open("states_cities.json", "r", encoding="utf-8") as f:
    states_cities = json.load(f)

for state_name, cities in states_cities.items():
    short_state = short_states[state_name]

    if not os.path.exists(f"arpart_list/{state_name}"):
        os.makedirs(f"arpart_list/{state_name}")

    for city in cities:
        apart_list = []

        for page in range(1, 19):
            url = f"{config('WEBSITE_URL')}{city.replace(' ', '-')}-{short_state}/{page}/"
            data = get_apart_data(url)
            apart_list += data["properties_list"]

            if page >= data["page"]:
                break
        
        with open(f"arpart_list/{state_name}/{city}.csv", 'w', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=apart_list[0].keys())
            csv_writer.writeheader()
            for row in apart_list:
                csv_writer.writerow(row)
