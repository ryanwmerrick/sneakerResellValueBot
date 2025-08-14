from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import requests
from difflib import SequenceMatcher
import statistics
import shutil

def get_chromedriver_service():
    """
    Returns a Service object for ChromeDriver.
    In GitHub Actions, uses the pre-installed chromedriver in PATH.
    Locally, lets Selenium Manager download automatically if not found.
    """
    # Try to find chromedriver in PATH (GitHub Actions installs it here)
    chrome_driver_path = shutil.which("chromedriver")
    if chrome_driver_path:
        return Service(chrome_driver_path)
    # Fallback to Selenium Manager auto-download
    return Service()

def create_driver(headless=True):
    """
    Creates a Chrome WebDriver with options for automation.
    Set headless=False to see the browser (good for debugging).
    """
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    if headless:
        options.add_argument("--headless=new")  # use new headless mode
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

    service = get_chromedriver_service()
    return webdriver.Chrome(service=service, options=options)


def getLivePriceGoogle(name:str, style: str, colorway:str):
    
    
    driver = create_driver()

    try:
        #Searches Google Shopping for the sneaker
        driver.get("https://google.com/shopping")
        time.sleep(3) #waits for page to load
    
        # Wait for search input and enters the sneaker name, product ID, and colorway into search bar
        searchBar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.gLFyf"))
        )
        searchBar.clear()
        searchBar.send_keys(f"{name} {style} {colorway}" + Keys.RETURN)
        time.sleep(3
                   )  # Wait for search results to load
        
        #Gets all product containers
        product_containers = driver.find_elements(By.CSS_SELECTOR, "div.UC8ZCe.QS8Cxb")
    
        #Initializes Result Variables
        filtered_products = []
        #Ensures only one of each seller is added (stockx, goat, flight club, ebay)
        first_stockx_found = False
        first_goat_found = False
        first_fc_found = False
        first_ebay_found = False

        for container in product_containers:
            try:
                # Extracts the name, price, and seller from the product container
                nameElem = container.find_element(By.CSS_SELECTOR, "div.gkQHve.SsM98d.RmEs5b.gGeaLc")
                priceElem = container.find_element(By.CSS_SELECTOR, "span.lmQWe")
                sellerElem = container.find_element(By.CSS_SELECTOR, "span.WJMUdc.rw5ecc")
                # Gets the text from each element
                nameText = nameElem.text.strip()
                priceText = priceElem.text.strip()
                priceValue = float(priceText.replace('$', '').replace(',', ''))
                sellerText = sellerElem.text.strip()
                # Filters out products with no price or seller
                if not priceText.startswith('$'):
                    continue
                #Checks for first StockX Product
                if sellerText.lower() == "stockx" and not first_stockx_found:
                    for i in range(3):
                        filtered_products.append((nameText, priceValue, sellerText))
                    first_stockx_found = True
                #Checks for first Goat Product
                elif sellerText.lower() == "goat" and not first_goat_found:
                    for i in range(2):
                        filtered_products.append((nameText, priceValue, sellerText))
                    first_goat_found = True
                #Checks for first Flight Club Product
                elif sellerText.lower() == "flight club" and not first_fc_found:
                    for i in range(2):
                        filtered_products.append((nameText, priceValue, sellerText))
                    first_fc_found = True
                #Checks for first eBay Product
                elif sellerText.lower() == "ebay" and not first_ebay_found:
                    for i in range(2):
                        filtered_products.append((nameText, priceValue, sellerText))
                    first_ebay_found = True
            except Exception:
                continue
        #Filters the prices so that nothing outrageous is included
        allPrices= [price for title, price, seller in filtered_products]
        if allPrices:
            medianPrice= statistics.median(allPrices)
            allowedProducts= []
            for title, price, seller in filtered_products:
                if (medianPrice * 0.75 <= price) and (medianPrice * 1.6 >= price): #if the withing 75% and 160% of the median Price it is allowed
                    allowedProducts.append((title,price,seller))
        else:
            allowedProducts=[]
            

        #Gets the average price of the filtered products
        totalPrice = 0
        print("Filtered Google Shopping Products:") #TESTING
        for title, price, seller in allowedProducts:
            totalPrice += price
            print(f"{title} - ${price} ({seller})") #TESTING 
    #Closes Chrome Driver
    finally:
        driver.quit()
   
    #Returns the average price via Google Shopping
    return totalPrice / len(allowedProducts) if allowedProducts else 0

# getLivePriceGoogle('Nike Air Foamposite One "Cough Drop"','IB2219-001','Black/Varsity Red')