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
from bs4 import BeautifulSoup

def getLivePriceImageSoleRetreiver(productID: str, save_dir="images"):
    service = Service()

    #Makes Chrome Undetectable and Not Visible
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=service, options=options)
    
    #header for beautiful soup image download
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
    }

    try:
        driver.get("https://soleretriever.com")
        time.sleep(1) #waits for page to load
    
        # Wait for search input and enter Product ID
        searchBar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.form-input"))
        )
        searchBar.clear()
        searchBar.send_keys(f"{productID}" + Keys.RETURN)
        time.sleep(1)  # Wait for search results to load

        # Try to locate product container
        try:
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, '{productID.lower()}')]/ancestor::div[contains(@class, 'full-grid-item')]"))
            )
            link = container.find_element(By.CSS_SELECTOR, f'a[href*="{productID.lower()}"]')
            driver.execute_script("arguments[0].click();", link)
        except Exception:
            print(f"Product ID: {productID} not found in search results, SKIPPING")
            return 0.0, []

        

        #scroll to bottom to load all images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
        time.sleep(4) # give some time for images to load
        #USES BEATIFULSOUP TO SCRAPE THE PAGE
        
        html= driver.page_source
        soup= BeautifulSoup(html, 'html.parser')
        
        mainImages = []  # initializes mainImages to avoid reference before assignment error
        
        imageSection = soup.find('section', class_="grid")

        
        if imageSection:
            print("FOUND IMAGE SECTION")
            mainImages= imageSection.find_all('img')[:4] #gets the first 4 images (main images)
            print(f"FOUND {len(mainImages)} IMAGES")
        
        img_paths = []
        os.makedirs(save_dir, exist_ok=True)  # ensure the folder exists
        #Creates images directory if it doesn't exist (copied code for this part to avoid issues with image saving)
        for idx, img in enumerate(mainImages, start=1):
            srcset = img.get("srcset")
            if srcset:
                image_url = srcset.split(",")[-1].strip().split(" ")[0]
            else:
                image_url = img.get("src")

            img_path = os.path.join(save_dir, f"{productID}_{idx}.jpg")
            response = requests.get(image_url, headers=headers)
            if response.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(response.content)
                img_paths.append(img_path)
                print(f"Downloaded high-res image: {img_path}")
            else:
                print(f"Failed to download image {image_url} - Status code: {response.status_code}")

        
        #Get Live Price
        livePriceElement= soup.find("span", class_="flex items-center justify-center text-turquoise-500 cursor-pointer bg-turquoise-50 rounded font-medium h-6 px-1 -mx-1")
        if(livePriceElement):
            livePrice = livePriceElement.text.strip("$")
        else:
            livePrice = 0.0
        print(f"FOUND LIVE PRICE: {livePrice}")

        
    #Closes Chrome Driver
    finally:
        driver.quit()
    #Returns the live price and image path from Sole Retreiver 
    return float(livePrice), img_paths

# getLivePriceImageSoleRetreiver("DV4982-004") #TESTING