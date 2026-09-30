import csv
import datetime
import json
import os
import time

import requests

from config import MAX_QUERIES_PER_DAY

"""
Requests business data from Google.
Scans the returned website URLs for basic text mentioning an email. ADD LATER
Appends rows into CSV file.
"""

# use a virtualenv then install with pip:
# python-dotenv to handle .env
# requests to get the email address from extracted URL
# later check if i can use a cloudflare worker to run Python
# so i can have this tool hosted and use a clean UI

LOG_FILE = "api_usage_log.json"


class GooglePlacesScraper:
    SAST = datetime.timezone(datetime.timedelta(hours=2))
    today = str(datetime.datetime.now(tz=SAST).date())

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.nationalPhoneNumber,places.websiteUri",
        }

    def _get_daily_usage(self) -> int:
        """
        Reads the log file to get today's current API call count.
        """

        # If the log file does not exist yet, today's count is 0
        if not os.path.exists(LOG_FILE):
            return 0

        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
                # If the log file matches today's date, return its count.
                # Otherwise count starts at 0.
                if data.get("date") == GooglePlacesScraper.today:
                    return data.get("count", 0)
        except (json.JSONDecodeError, KeyError):
            pass

        return 165  # safety net to disable API calls if log cannot be read

    def _increment_daily_usage(self, current_count: int) -> None:
        """
        Increments and saves today's API call count to the log file.
        """
        new_count = current_count + 1

        with open(LOG_FILE, "w") as f:
            json.dump({"date": GooglePlacesScraper.today, "count": new_count}, f)

    def fetch_places(self, query: str) -> list:
        url = "https://places.googleapis.com/v1/places:searchText"
        payload = {"textQuery": query}
        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            return []

        return response.json().get("places", [])

    def extract_email(self, url):
        # to be implemented
        return "N/A"

    def run(self, query: str, filename: str = "leads.csv") -> None:
        """
        Executes fetch_places() method.
        Structures the returned data (list of dictionaries).
        Creates a CSV file and writes rows of data into it.
        """
        try:
            # Check current usage from the LOG_FILE
            current_api_usage = self._get_daily_usage()

            if current_api_usage >= MAX_QUERIES_PER_DAY:
                print(
                    f"Request query limit reached for today: {current_api_usage} of {MAX_QUERIES_PER_DAY}"
                )
                return

            query = query.strip()
            # mini regex check for special chars
            if "!" in query:
                print("Invalid search parameters.")
                return

            print(f"Fetching leads for query: '{query}'...")

            places = []
            start_perf = time.perf_counter()
            places = self.fetch_places(query)
            end_perf = time.perf_counter()

            print(f"Took {end_perf - start_perf:.3f} seconds")

            if places == []:
                print("No searches matched your query.")
                return

            # Structure the returned data using list of dicts
            structured_leads = []

            for place in places:
                # Navigate nested keys using .get() fallbacks - get() second argument is a default fallback
                name = place.get("displayName", {}).get("text", "Unknown Business")
                phone = place.get("nationalPhoneNumber", "N/A")
                website = place.get("websiteUri", "N/A")

                # Placeholder call for email extraction logic
                email = self.extract_email(website)

                structured_leads.append(
                    {"name": name, "phone": phone, "website": website, "email": email}
                )

            # Define target diretory as 'leads' folder
            target_dir = "leads"

            # Create dir if it does not yet exist
            os.makedirs(target_dir, exist_ok=True)

            # Join the dir path and filename path
            full_path = os.path.join(target_dir, filename)

            # Open the file and write rows into the CSV
            fields = ["name", "phone", "website", "email"]

            print(f"Writing to file at {full_path} now...")
            with open(full_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)

                # Write the column headers first (Fields list)
                writer.writeheader()

                # Append all list rows
                writer.writerows(structured_leads)

            self._increment_daily_usage(current_api_usage)
            updated_usage = current_api_usage + 1

            print(
                f"Done! Successfully wrote {len(structured_leads)} leads to {full_path}"
            )
            print(
                f"Requests remaining: {MAX_QUERIES_PER_DAY - updated_usage} of {MAX_QUERIES_PER_DAY} total"
            )

        except requests.exceptions.ConnectionError:
            print("Connection error. Check internet connection and try again.")
            return

        except TypeError as error:
            print(f"String input only!\nError: {error}")
            return
