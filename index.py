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
try:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    website_url = config('WEBSITE_URL')

    current_datetime = str(datetime.now())

    driver.get(website_url)

    properties_list = []

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'placardContainer'))
    )

    li_elements = driver.find_elements(By.XPATH, '//div[@id="placardContainer"]/ul/li')

    for li_element in li_elements:
        LISTING_NAME = extract_element_text(li_element, '.property-title')
        LISTING_LINK = extract_element_attribute(li_element, '.property-link', 'href')
        LISTING_ADDRESS = extract_element_attribute(li_element, '.property-address', 'title')
        LISTING_DESCRIPTION = extract_element_text(li_element, '.property-amenities')
        mediaLinksText = extract_element_text(li_element, '.mediaLinksList')
        HAS_VIDEOS = "Videos" in mediaLinksText
        HAS_VIRTUAL_TOUR = "Virtual Tour" in mediaLinksText
        HAS_EMAIL = has_email_button(li_element)
        PRICE = extract_element_text(li_element, '.property-pricing') # .price-range / .property-rents
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

    with open('properties_data.json', 'w') as json_file:
        json.dump(properties_list, json_file, indent=2)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
