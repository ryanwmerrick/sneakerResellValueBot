import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


# Function to get sneaker releases from Nice Kicks that release tomorrow
def getReleases():
    
    #Manually Scrape the Nice Kicks release calendar
    url = "http://www.nicekicks.com/sneaker-release-dates/"
    response = requests.get(url)
    soup= BeautifulSoup(response.content, 'html.parser')

    #gets tomorrow's date to compare against the release dates
    tomorrow = datetime.now() + timedelta(days=2)
    tomorrow_str = tomorrow.strftime('%B %-d, %Y')  # Ex: August 8, 2025

    releases = soup.find_all(class_="release-date__wrapper") #gathers all of the releases
    sneakers=[] #gatheres only the sneakers that release tomorrow

    for release in releases:
        #Get Name
        try:
            name = release.find('div', class_='release-date__title').text.strip()
        except AttributeError:
            name = None
        #Exctract all other information from <p> tag
        pTag= release.find('p')
        if pTag:
            strongs= pTag.find_all('strong') #divides pTag into all the Strong tags (which are how each of the sneaker attributes are labeled)
            #initializes variables to None
            colorway = None
            style = None
            releaseDate = None
            retailPrice = None
            livePrice=None
            
            #loops through each strong tag and extracts the label and value
            for strong in strongs:
                label= strong.text.strip().rstrip(':') #gets the label and removes everything after the colon
                value= strong.next_sibling #gets the value directly after the strong tag, which is always the value we want
                
                #Gets and cleans value text or None if it doesn't exist
                if value:
                    value = value.text.strip()
                else:
                    value = None
                #Assigns the value to the appropriate variable based on the label
                if label == 'Colorway':
                    colorway = value
                elif label == 'Style #':
                    style = value
                elif label == 'Release Date':
                    releaseDate = value
                elif label == 'Price':
                    retailPrice = value
            #Creates a sneaker dictionary with all the information we gathered
            sneaker= {
                "name": name,
                "colorway": colorway,
                "style": style,
                "releaseDate": releaseDate,
                "retailPrice": retailPrice.strip("$") if retailPrice else None # removes dollar sign
            }
            #Checks if the release date matches tomorrow's date
            if releaseDate == tomorrow_str:
                #If it does, append the sneaker to the sneakers list
                sneakers.append(sneaker)
    return sneakers
