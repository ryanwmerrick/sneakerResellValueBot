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

        # Wait for the clickable <a> link that includes the Product ID
        container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, '{productID.lower()}')]/ancestor::div[contains(@class, 'full-grid-item block group transition-opacity h-full place-self-stretch relative')]"))
        )
        link = container.find_element(By.CSS_SELECTOR, f'a[href*="{productID.lower()}"]')
        driver.execute_script("arguments[0].click();", link)

    
        # Wait for the live price span to be visible
        livePrice = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.text-turquoise-500"))
        ).text.strip("$") #removes dollar sign
        
        # Scroll to the bottom of the page to load all lazy images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # give some time for images to load

        
        
        # Find the main large image
         # Grab the first image in the main grid
        mainImages = driver.find_elements(By.CSS_SELECTOR, "img.w-full.cursor-pointer.rounded-md")[:4]
        print(f"FOUND{len(mainImages)} IMAGES")
        
        os.makedirs(save_dir, exist_ok=True)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36"
        }

        img_paths = []
        for idx, img in enumerate(mainImages, start=1):
            srcset = img.get_attribute("srcset")
            if srcset:
                image_url = srcset.split(",")[-1].strip().split(" ")[0]
            else:
                image_url = img.get_attribute("src")

            img_path = os.path.join(save_dir, f"{productID}_{idx}.jpg")
            response = requests.get(image_url, headers=headers)
            if response.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(response.content)
                img_paths.append(img_path)
                print(f"Downloaded high-res image: {img_path}")
            else:
                print(f"Failed to download image {image_url} - Status code: {response.status_code}")

    #Closes Chrome Driver
    finally:
        driver.quit()
    #Returns the live price and image path from Sole Retreiver 
    return float(livePrice), img_paths

# getLivePriceImageSoleRetreiver("U204LMMC") #TESTING