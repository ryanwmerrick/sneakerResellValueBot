import tweepy
from pprint import pprint
#For hiding API keys
from dotenv import load_dotenv
import os
#For NICE KICKS PARSING
from releases import getReleases
#FOR LIVE PRICE PARSING FROM SOLERETRIEVER
from prices import getLivePrice, resellPrediction
from PIL import Image

#Loading API keys from .env file
load_dotenv()

#Creating a Tweepy client and API
def getClient():
    client = tweepy.Client(
        consumer_key=os.getenv("consumer_key"),
        consumer_secret=os.getenv("consumer_secret"),
        access_token=os.getenv("access_token"),
        access_token_secret=os.getenv("access_token_secret")
    )
    return client
def getAPI():
    auth = tweepy.OAuth1UserHandler(
        consumer_key=os.getenv("consumer_key"),
        consumer_secret=os.getenv("consumer_secret"),
        access_token=os.getenv("access_token"),
        access_token_secret=os.getenv("access_token_secret")
    )
    return tweepy.API(auth)

#Creates and Posts the Tweet
def createTweet(sneaker):
    # Gets the live price and image paths
    livePrice, imagePath = getLivePrice( sneaker['name'], sneaker["style"], sneaker['colorway'])
    hypeLevel, lowPoint, highPoint= resellPrediction(sneaker["retailPrice"], livePrice)
    
    # TWEET TEXT
    tweetTextWithPrediction = (
        f'{sneaker["name"]}\n'
        f'Colorway: {sneaker["colorway"]}\n'
        f'Retail Price: ${sneaker["retailPrice"]}\n'
        f'Current Average Live Price: ${int(livePrice)}\n'
        f'Resell: {hypeLevel}\n'
        f'Resell Prediction: ${lowPoint}-${highPoint}\n'
        f'Release Date: {sneaker["releaseDate"]}'
    )
    tweetTextWithoutPrediction = (
        f'{sneaker["name"]}\n'
        f'Colorway: {sneaker["colorway"]}\n'
        f'Retail Price: ${sneaker["retailPrice"]}\n'
        f'Release Date: {sneaker["releaseDate"]}'
    )
    # If Live Price or Resale Predictions is 0, we don't include the prediction
    tweetText = ""
    if(livePrice != 0 and lowPoint != 0 and highPoint != 0):
        tweetText=tweetTextWithPrediction
    else:
        tweetText=tweetTextWithoutPrediction
    

    # Upload the image if it exists
    api = getAPI()
    media_ids = []
    if imagePath:
        try:
            # Open the image and convert it to RGBA (to determine if transparent)
            img = Image.open(imagePath).convert("RGBA")
            # Create a white background and paste the image onto it
            white_bg = Image.new("RGB", img.size, (255, 255, 255))
            # Use White Background as mask if transparent, else paste without mask
            if img.mode == "RGBA":
                white_bg.paste(img, mask=img.split()[3])  # White Background with transparency
            else:
                white_bg.paste(img)
            # Save the image with a fixed name
            fixed_path = imagePath.replace('.jpg', '_fixed.jpg')
            white_bg.save(fixed_path, format='JPEG')
            media = api.media_upload(fixed_path)
            media_ids.append(media.media_id)
        except Exception as e:
            print(f"Failed to process/upload {imagePath}: {e}")


    # Post Tweet with media if we have any uploaded successfully
    client = getClient()
    try:
        if media_ids:
            client.create_tweet(text=tweetText, media_ids=media_ids)
            print("Tweet posted successfully!")
        else:
            print("No valid media to upload; posting tweet without media.")
            client.create_tweet(text=tweetText)
    except Exception as e:
        print(f"Failed to post tweet: {e}")
        
    print('-----------------------------')
    print('POSTED TWEET:')
    print(f'{tweetText}')
    

#MAIN EXECUTIONS
sneakers = getReleases()  # Gets the list of sneakers releasing tomorrow
if sneakers:
    for sneaker in sneakers:
        createTweet(sneaker)
else:
    print("No sneaker releases found for tomorrow.")











