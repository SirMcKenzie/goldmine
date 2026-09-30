import os
import sys

from dotenv import load_dotenv

from scraper import GooglePlacesScraper

"""
create a super simple lead scraper and then improve.
start with the smallest, most achievable scraper.
"""

if __name__ == "__main__":
    # Load all environment variables
    load_dotenv()

    # Safely extract the secret key
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    if not api_key or "insert_" in api_key:
        print(
            "Error: Please check your .env file and insert a valid Google Places API Key."
        )
        sys.exit(1)

    # create the scraper tool instance
    google_places_scraper = GooglePlacesScraper(api_key=api_key)

    # run the scraper tool
    search_query = input("Search query: ")
    file_name = search_query.replace(" ", "-").lower() + ".csv"
    google_places_scraper.run(search_query, filename=file_name)
