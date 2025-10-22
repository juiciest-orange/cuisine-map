# Import necessary libraries
import os
import re
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
    return currentUrl
    print("Searching for restaurants...")

# Hard code in a city
city = 'Mountain View, CA'
currentUrl = sendQuery("""restaurants in {cityName}""".format(cityName=city))

# Open the URL
driver.get(currentUrl)

def scroll_panel_with_page_down(driver, panel_xpath, presses, pause_time):
    """
    Scrolls within a specific panel by simulating Page Down key presses.

    :param driver: The Selenium WebDriver instance.
    :param panel_xpath: The XPath to the panel element.
    :param presses: The number of times to press the Page Down key.
    :param pause_time: Time to pause between key presses, in seconds.
    """
    # Find the panel element
    panel_element = driver.find_element(By.XPATH, panel_xpath)
    
    # Ensure the panel is in focus by clicking on it
    # Note: Some elements may not need or allow clicking to focus. Adjust as needed.
    actions = ActionChains(driver)
    actions.move_to_element(panel_element).click().perform()

    # Send the Page Down key to the panel element
    for _ in range(presses):
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(pause_time)
        actions.move_to_element(panel_element).click().perform()
        # Get all window handles
        window_handles = driver.window_handles
        # Switch to the first tab (index 0)
        driver.switch_to.window(window_handles[0])

# XPath to the main panel where addresses are displayed
panel_xpath = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div"

# Scroll down within the main panel
# scroll_panel_with_page_down(driver, panel_xpath, presses=20, pause_time=1)
scroll_panel_with_page_down(driver, panel_xpath, presses=20, pause_time=5)

# Extract and print all addresses visible on the page after scrolling
addresses = driver.find_elements(By.CLASS_NAME, 'hfpxzc')

page_source = driver.page_source
# Parse with BeautifulSoup
soup = BeautifulSoup(page_source, "html.parser")

# For addresses and restaurant info
data_containers = soup.find_all("a", class_="hfpxzc")
cuisine = soup.find_all("div", class_="W4Efsd")

# Close the Selenium WebDriver
driver.quit()

restuarantNames = []
for address in data_containers:
    restuarantName = re.findall(r'\<a\saria\-label\=\"(.+)\"\sclass', str(address))
    restuarantNames.append(restuarantName[0].replace("'",''))
print("""Found {n} restaurants in {c}""".format(n = len(restuarantNames), c = city))

cuisine = soup.find_all("div", class_="W4Efsd")
restaurantInfo = []
for address in cuisine:
    cuisineType = re.findall(r'\<span\>([\w\s\#\-]+)\<', str(address))
    if len(cuisineType) <=  1:
        continue
    elif len(cuisineType) == 4:
        restaurantInfo.append(cuisineType)

# Dedupe restaurant info
restaurantInfo.sort()
restaurantInfo= list(k for k,_ in itertools.groupby(restaurantInfo))

restaurantCuisine = []
restaurantAddress = []
for r in restaurantInfo:
    # print(r)
    restaurantCuisine.append(r[0])
    restaurantAddress.append(r[3])


with open('restaurantNames.txt', 'w') as file:
    for i in restuarantNames:
        i + ", " + city
        file.write(i + ", " + city + "\n")
    file.close()
print("Wrote %s restaurant names to restaurantNames.txt" %len(restuarantNames))