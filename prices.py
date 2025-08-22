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
from googleTrends import getGoogleTrendsPrice
import math


def getLivePrice(name: str, style: str, colorway: str, retailPrice: int, save_dir="images"):

    # Get SoleRetriever price (and image path, ignored here)
    livePriceSoleRetriever, imagePath = getLivePriceImageSoleRetreiver(style)
    print('-----------------------------')
    print(f"SoleRetreiver Price: {livePriceSoleRetriever}")
    
    #GOOGLE TRENDS
    googleTrend = getGoogleTrendsPrice(name)
    print(f"Google Trends Score: {googleTrend:.2f}")
    
    # Adjust price based on trend
    if googleTrend == 0.0:
        trendFactor = -0.25 # Heavy penalty for dead shoes
    elif googleTrend <= 0.1:
        trendFactor = -0.15  # mid penalty for low interest
    else:
        trendFactor = min(0.05, math.log1p(googleTrend) / 100)  # Small reward, capped at +5%

    
    
    estimatedPrice = livePriceSoleRetriever * (1 + trendFactor)

    # Safeguard floor: not below 90% retail
    if estimatedPrice < (retailPrice * 0.9):
        estimatedPrice = int(retailPrice * 0.9)
        
    print(f"Adjusted Trend Factor: {trendFactor:.3f}")
    print(f"Total Estimate Live Price: {estimatedPrice:.2f}")

    return estimatedPrice, imagePath


def resellPrediction(retail, livePrice):
    #Initializes variables
    retail = float(retail)
    livePrice = float(livePrice)
    hype=None
    dropFactor=0
    
    #if the live price is 75% more than the retail price, it is considered high hype
    if livePrice>= retail * 2:
        hype= "✅ High ✅"
        dropFactor= 0.6
    #if the live price is 40% more than the retail price, it is considered mid hype
    elif livePrice>= retail * 1.6:
        hype= "⚠️ Mid ⚠️"
        dropFactor= 0.5
    #if the live price is less than 40% more than the retail price, it is considered low hype
    else:
        hype= "❌ Low ❌"
        dropFactor=0.4
        
    midPoint= retail + ((livePrice-retail) * dropFactor) #drops the profit by a factor based on the level of hype
    
    if midPoint < retail:
        midPoint = retail
        
    # Round down to nearest 5
    def roundDown5(x):
        return 5 * math.floor(x / 5)
    
    lowPoint= roundDown5(int(midPoint-30)) #low point is 30 less than the mid point (rounded to 2 decimal places)
    if lowPoint < retail * 0.9:  # Ensure low point is not less than 90% of retail price
        lowPoint = roundDown5(int(retail * 0.9)) # Ensure low point is not less than retail price
        
    highPoint= roundDown5(int(midPoint+30)) #high point is 30 more than the mid point (rounded to 2 decimal places)
    
    
    return hype, lowPoint, highPoint
    
    
    
    

         


