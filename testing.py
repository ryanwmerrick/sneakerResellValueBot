import time
import os
import requests
from releases import getReleases
from prices import getLivePrice
from soleRetreiver import getLivePriceImageSoleRetreiver
from googleShopping import getLivePriceGoogle
import math


#TEST DAILY RELEASE
releases= getReleases()

if releases:
    for release in releases:
        getLivePrice(release['name'], release['style'], release['colorway'])
        
        
#TEST CUSTOM RELEASE

sneaker={
    'name': 'Air Jordan 14 Golf "Hyper Royal"',
    'style':'HJ7710-101',
    'colorway':'White/Black/Hyper Royal'
}

getLivePrice(sneaker['name'], sneaker['style'], sneaker['colorway'])



        


        


