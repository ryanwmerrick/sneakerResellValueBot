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


def getLivePrice(name: str, style: str, colorway: str, retailPrice, save_dir="images"):
    """
    Get live sneaker price and adjust it using Google Trends.
    Handles None or invalid retailPrice safely.
    """

    # Ensure retailPrice is usable (convert to int or set to 0 if invalid)
    try:
        retailPrice = int(retailPrice)
    except (TypeError, ValueError):
        retailPrice = 0

    # Get SoleRetriever price (and image path, ignored here)
    livePriceSoleRetriever, imagePath = getLivePriceImageSoleRetreiver(style)
    print('-----------------------------')
    print(f"SoleRetreiver Price: {livePriceSoleRetriever}")

    # GOOGLE TRENDS
    googleTrend = getGoogleTrendsPrice(name)
    print(f"Google Trends Score: {googleTrend:.2f}")

    # Adjust price based on trend
    if googleTrend == 0.0:
        trendFactor = -0.25  # Heavy penalty for dead shoes
    elif googleTrend <= 0.1:
        trendFactor = -0.15  # mid penalty for low interest
    else:
        trendFactor = min(0.15, math.log1p(googleTrend) / 50)  # Small reward, capped at +15%

    estimatedPrice = livePriceSoleRetriever * (1 + trendFactor)

    print(f"Adjusted Trend Factor: {trendFactor:.3f}")
    print(f"Total Estimate Live Price: {estimatedPrice:.2f}")

    return estimatedPrice, imagePath


def resellPrediction(retail, livePrice):
    """
    Predict resell hype level and price range based on retail & live price.
    """
    try:
        retail = float(retail)
    except (TypeError, ValueError):
        retail = 0.0

    try:
        livePrice = float(livePrice)
    except (TypeError, ValueError):
        livePrice = 0.0

    hype = None
    dropFactor = 0

    # Hype levels
    if retail > 0:
        if livePrice >= retail * 2:
            hype = "✅ High ✅"
            dropFactor = 0.6
        elif livePrice >= retail * 1.6:
            hype = "⚠️ Mid ⚠️"
            dropFactor = 0.5
        else:
            hype = "❌ Low ❌"
            dropFactor = 0.4
    else:
        hype = "❓ Unknown ❓"
        dropFactor = 0.4

    # Midpoint calculation
    midPoint = retail + ((livePrice - retail) * dropFactor)
    if midPoint < retail:
        midPoint = retail

    # Round down helper
    def roundDown5(x):
        return 5 * math.floor(x / 5)

    # Low / High estimate
    lowPoint = roundDown5(int(midPoint - 30))
    if retail > 0 and lowPoint < retail * 0.9:  
        lowPoint = roundDown5(int(retail * 0.9))

    highPoint = roundDown5(int(midPoint + 30))

    return hype, lowPoint, highPoint
