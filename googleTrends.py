from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
import warnings
import math
import time

warnings.simplefilter(action="ignore", category=FutureWarning)

# Initialize once
pytrends = TrendReq(hl="en-US", tz=360)

def getGoogleTrendsPrice(name: str, max_retries: int = 5, sleep_time: int = 10) -> float:
    """
    Get the average Google Trends interest for a keyword over the last 7 days.
    Retries automatically if Google returns a 429 Too Many Requests error.
    """
    retries = 0
    while retries < max_retries:
        try:
            # Build payload with one keyword
            pytrends.build_payload([name], timeframe="now 7-d")

            # Get interest over time
            data = pytrends.interest_over_time()
            if data.empty or data is None:
                return 0.0  # if no data is found

            # Drop the isPartial column if it exists
            if "isPartial" in data.columns:
                data = data.drop(columns=["isPartial"])

            # Calculate the mean for the keyword
            weekly_avg = data[name].mean()
            return weekly_avg

        except TooManyRequestsError:
            print(f"⚠️ Too many requests for '{name}'. Sleeping {sleep_time}s and retrying...")
            time.sleep(sleep_time)
            retries += 1
        except Exception as e:
            print(f"❌ Unexpected error for '{name}': {e}")
            return 0.0

    print(f"❌ Max retries reached for '{name}'. Returning 0.")
    return 0.0


# Example usage
# print(getGoogleTrendsPrice('Nike Air Max 1000 "Oatmeal"'))
# print(getGoogleTrendsPrice('adidas Adimule Slides WMNS "Magic Beige"'))
