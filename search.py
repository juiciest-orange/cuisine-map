# Import necessary libraries
import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
import itertools
from selenium import webdriver  # For web scraping with Selenium
from selenium.webdriver.common.by import By  # For locating elements
from selenium.webdriver.common.action_chains import ActionChains  # For simulating keyboard actions
from selenium.webdriver.common.keys import Keys  # For simulating key presses
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup  # For parsing HTML content
import time  # For adding delays
import csv  # For working with CSV files

def sendQuery(query=""):
    """q : query to send to Google Maps search box"""
    # Find the search box using its HTML ID and enter the search term
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)

    # Wait for the results to load
    import time
    time.sleep(5)  # Adjust this delay based on your internet speed
    currentUrl = driver.current_url
    search_box.clear()
    return currentUrl
    print("Searching for restaurants...")

# Setting up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--window-position=-2400,-2400")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Choose Chrome Browser
driver = webdriver.Chrome(options=chrome_options)

# Open Google Maps
driver.get("https://www.google.com/maps")
print("Opened Google Maps")

def searchCuisine(filepath=""):
    # Open list of restaurants in a city
    buttonTexts = []
    with open(filepath, "r") as file:
        lines = file.read().splitlines()
        print("\nReading all restaurants into a list")
    # print(lines[0])
    for line in lines:
        driver.get("https://www.google.com/maps")
        # Open the URL
        currentUrl = sendQuery(line)
        driver.get(currentUrl)
        # Extract and print cuisine
        cuisine = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/span[1]/span/button')
        for button in cuisine:
            # print(button.text)
            buttonTexts.append(button.text)
            continue
    return buttonTexts

cuisineList = searchCuisine("restaurantListTest.txt")

print(len(cuisineList))

with open('restaurantCuisine.txt', 'w') as file:
    for i in cuisineList:
        print(i)
        file.writelines(i+"\n")
    file.close()
