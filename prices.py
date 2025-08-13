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
from soleRetreiver import getLivePriceImageSoleRetreiver
from googleShopping import getLivePriceGoogle
import math


def getLivePrice(name:str, style: str, colorway:str, save_dir="images"):
    # Get SoleRetriever price (and image path, ignored here)
    livePriceSoleRetriever, imagePath = getLivePriceImageSoleRetreiver(style)
    print('-----------------------------')
    print(f"SoleRetreiver Price: {livePriceSoleRetriever}")

    # Get Google Shopping price
    livePriceGoogle = getLivePriceGoogle(name, style, colorway)
    
    #PRINT STATEMENTS
    print(f"Google Shopping Price: {livePriceGoogle}")
    
    totalPrice = 0
    totalWeight = 0

    soleRetrieverWeight = 3
    googleShoppingWeight = 1

    # Add SoleRetriever price if not zero
    if livePriceSoleRetriever > 0:
        totalPrice += livePriceSoleRetriever * soleRetrieverWeight
        totalWeight += soleRetrieverWeight

    # Add Google Shopping price if not zero
    if livePriceGoogle > 0:
        totalPrice += livePriceGoogle * googleShoppingWeight
        totalWeight += googleShoppingWeight

    # If no valid prices were found, return 0
    if totalWeight == 0:
        return 0
    
    print(f'Total Live Price: {totalPrice / totalWeight}')

    return (totalPrice / totalWeight), imagePath




def resellPrediction(retail, livePrice):
    
    #Initializes variables
    retail = float(retail)
    livePrice = float(livePrice)
    hype=None
    dropFactor=0
    
    #if the live price is 75% more than the retail price, it is considered high hype
    if livePrice>= retail * 1.75:
        hype= "✅ High ✅"
        dropFactor= 0.7
    #if the live price is 40% more than the retail price, it is considered mid hype
    elif livePrice>= retail * 1.4:
        hype= "⚠️ Mid ⚠️"
        dropFactor= 0.6
    #if the live price is less than 40% more than the retail price, it is considered low hype
    else:
        hype= "❌ Low ❌"
        dropFactor=0.5
        
    midPoint= retail + ((livePrice-retail) * dropFactor) #drops the profit by a factor based on the level of hype
    
    if midPoint < retail:
        midPoint = retail
        
    # Round down to nearest 5
    def roundDown5(x):
        return 5 * math.floor(x / 5)
    
    lowPoint= roundDown5(int(midPoint-30)) #low point is 30 less than the mid point (rounded to 2 decimal places)
    highPoint= roundDown5(int(midPoint+30)) #high point is 30 more than the mid point (rounded to 2 decimal places)
    
    
    return hype, lowPoint, highPoint
    
    
    
    

         


