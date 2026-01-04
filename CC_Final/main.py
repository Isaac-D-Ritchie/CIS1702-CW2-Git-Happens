"""Developer Notes:
    Hover Over Functions if you do not know what they do, The Docstrings included will help provide context

    There is still some todos (Not All Nessesary) that would be great to implement:

        !!Stability & Security!!
        API Key Security (Calling on .env using os.getenv)
        Date Validation Loop (Loops until valid input for Date)
        Location Validation (Checks API recognises City Name)

        !!Data Handling!!
        Allow for Saving Simple and Detailed Reporting, only Simple at the minute
        Allow txt to save exactly as is printed in terminal e.g Rain Chance Bar not saved to txt

        Reporting on Date Range One Location
            Trends over date range
        Reporting on Compare Cities
            Prints Side By Side metrics
            Maybe prints which is hottest, least chance of rain in a summary
        Reprint Saved Reports to terminal
        Select City from recent searches e.g "Recent Cities: Ormskirk, Liverpool, Manchester" Entering 2 would enter Liverpool as the Location rather than having to re-enter

        Testing edge cases and working on report"""

"""Git Happens API Scenario Main Program.

Program Information:
    Data Flow:

    Weather API -> Reporting(Data Analysis -> Printing) -> Saving

    Program Structure:

    Imported Modules
    Util Functions, Configs and Constants
    Classes
    Saving Function
    Reporting Function
    Main Function
"""

"""IMPORTED MODULES"""
import requests # Util for API requests
from requests.exceptions import HTTPError, JSONDecodeError # Exceptions for requests related errors
import logging as LOG # For Logging instead of Printing
from datetime import datetime as dt #formatting and timedelta
from typing import List, Dict, Optional, Any #Would've liked JSON import but issues with differing versions of python
import json # Read/Writing to JSON
import csv # Read/Writing to CSV
import statistics #Helps with analysis
import os #helper to find files


# --- LOG.CONFIG, UTILS & CONSTANTS ---
STATUS_CODES = {
            #success
            '200':'| JSON Recieved | Data Present and Formatted Correctly |',
            '204': '| JSON Recieved |  Data Not Present, Formatted Correctly |',
            #client error
            '400':'| Bad Request | Improper Query or Bad JSON Recieved |',
            '401':'| Bad API Key | Invalid or None API Key used |',
            '403':'| Forbidden | Fetch request is valid but no permission is given |',
            '404':'| Not Found | Requested resource does not exist |',
            '429':'| Rate-Limit Exceeded| Too Many Requests, Try again later! |',
            #server error
            '500':'| Internal Server Error | Unexpected Error with Server |',
            '502':'| Service Unavailable | Try again Later, Servers may be under maintenance |'
}

LOG.basicConfig(level=LOG.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def title_print(x: str) -> str:
    """
    Format and return a string as a stylized header for menus and reports.

    Parameters
    ----------
    x : str
        The text to be displayed within the header.

    Returns
    -------
    str
        The formatted header string with decorative borders and spacing.
    
    Example
    -------
        =========================
         WEATHER TOOL
        =========================
    """
    return '\n'*3 + '='*25 + f'\n {x.upper()}\n' + '='*25 + '\n'*2

def farenheit_to_celcius(x: float) -> float:
    """
    Convert a temperature value from Fahrenheit to Celsius.

    Parameters
    ----------
    x : float
        The temperature value in Fahrenheit.
    
    Returns
    -------
    float
        The temperature value converted to Celsius.
    """
    return (x - 32) / 1.8

# --- CORE CLASSES ---

class APIHandler:
    """
    Handles communication with the Visual Crossing Weather API.

    Attributes
    ----------
    location : str
        The city or region requested by the user.
    date : str
        The specific date for the weather report (optional).
    api_data : dict
        A dictionary containing the base URL and a list of API keys.
    """

    def __init__(self, location: str, date: str = ""):
        """Initializes the APIHandler with user query parameters."""
        LOG.info('API Handler Initialized.')

        self.location = location
        self.date = date
        self.api_data = {
            'url': 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
            'keys': ['247BUSAAULFLBGWM7NVZ49M4B', 'U4QN48S3UU3XJ2C3LAK6TC8MM']
        }
        
    def connect(self) -> Optional[Dict[str, Any]] | None: #Returns JSON
        """
        Attempt to fetch weather data by iterating through available API keys.

        Returns
        -------
        dict or None
            A dictionary containing the parsed JSON response if successful, 
            otherwise None.
        """
        url = self.api_data['url']
        for key in self.api_data['keys']:
            date_path = f"/{self.date}" if self.date else ""
            full_url = f'{url}{self.location}{date_path}?key={key}'

            try:
                LOG.info(f"Connecting to API for {self.location}...")
                with requests.get(full_url, timeout=10) as response:
                    response.raise_for_status()
                    LOG.info(STATUS_CODES.get(str(response.status_code), "| Status Code Received |"))

                    if response.status_code == 200:
                        LOG.info(f"Success with Key ending in ..{key[-4:]}")
                        return response.json() 
                    
            except (HTTPError, JSONDecodeError, Exception) as err:
                LOG.warning(f"Attempt with key ..{key[-4:]} failed: {err}")
        
        LOG.critical("All API keys failed. Returning to Main.")
        return None

class UserQuery:
    """
    Manages and caches a session history of user search queries.

    Attributes
    ----------
    querycache : dict
        A dictionary storing lists of 'cities' and 'dates' searched in this session.
    """

    def __init__(self) -> None:
        """Initializes an empty query cache."""
        self.querycache: Dict[str, List[str]] = {'cities': [], 'dates': []}

    def add_to_cache(self, location: str, date: str):
        """
        Add unique location and date entries to the session history.

        Parameters
        ----------
        location : str
            The name of the location to cache.
        date : str
            The date string to cache.
        """
        try:
            if location and location not in self.querycache['cities']:
                self.querycache['cities'].append(location)
                LOG.info(f'Cached Location: {location}')
            if date:
                dt.strptime(date, '%Y-%m-%d')
                if date not in self.querycache['dates']:
                    self.querycache['dates'].append(date)
                    LOG.info(f'Cached Date: {date}')
        except (TypeError, ValueError):
            LOG.warning(f'Skipping cache for invalid date/type: {date}')

    def fetch_history(self) -> str:
        """
        Retrieve a formatted string representing the session's search history.

        Returns
        -------
        str
            A human-readable summary of cached cities and dates.
        """
        cities = ", ".join(self.querycache['cities']) or "None"
        dates = ", ".join(self.querycache['dates']) or "None"
        return f"Recent Cities: {cities}\nRecent Dates:  {dates}"

# --- SAVING FUNCTION ---

def save_report(data: dict) -> None:
    """
    Write current weather metrics to CSV, JSON, and TXT files simultaneously.

    Parameters
    ----------
    data : dict
        The raw API data dictionary used to extract metrics.

    Notes
    -----
    * CSV: Includes a header if the file does not exist.
    * JSON: Appends using the JSON-Lines format.
    * TXT: Formats data as an aligned, human-readable list.
    """
    day = data['days'][0]
    location_name = data.get('address', 'Unknown').title()

    report_fields = {
        'timestamp': dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        'location': location_name,
        'date': day['datetime'],
        'avg_temp': round(farenheit_to_celcius(day['temp']), 1),
        'humidity': day.get('humidity'),
        'conditions': day.get('conditions')
    }
    
    try:
        # CSV SAVE
        csvpresent = os.path.isfile('reporting.csv')
        with open('reporting.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_fields.keys())
            if not csvpresent:
                writer.writeheader()
            writer.writerow(report_fields)
        LOG.info('Validated and saved to reporting.csv')

        # JSON SAVE
        with open('reporting.json', 'a') as f:
            f.write(json.dumps(report_fields) + '\n')
        LOG.info('Validated and saved to reporting.json')

        # TXT SAVE
        txtpresent = os.path.isfile('reporting.txt')
        with open('reporting.txt', 'a') as f:
            if not txtpresent:
                f.write("--- GIT HAPPENS WEATHER LOG START ---\n")
            
            f.write(f"\n[ENTRY: {report_fields['timestamp']}]\n")
            for key, value in report_fields.items():
                f.write(f"{key.upper():<12}: {value}\n")
            f.write("-" * 35 + "\n")
        LOG.info('Validated and saved to reporting.txt')

    except Exception as err:
        LOG.warning(f'Error with saving to files: {err}')

# --- REPORTING FUNCTIONS ---

def show_simple_report(data: dict, location: str, date_string: str) -> None:
    """
    Generate and print a concise high-level summary of daily weather.

    Parameters
    ----------
    data : dict
        The weather data dictionary.
    location : str
        The name of the location.
    date_string : str
        The date being reported.
    """
    day_data = data['days'][0]
    hours_data = day_data['hours']
    
    temp_list = [farenheit_to_celcius(h['temp']) for h in hours_data]
    condition_list = [h['conditions'] for h in hours_data]

    average_temp = statistics.mean(temp_list)
    most_common_weather = statistics.mode(condition_list)
    rain_percent = day_data.get('precipprob', 0)

    print(title_print(f"SUMMARY FOR: {location.upper()} | DATE: {date_string}"))
    print(f"Main Condition:  {most_common_weather}")
    print(f"Average Temp:    {average_temp:.1f}°C")
    print(f"High / Low:      {max(temp_list):.1f}°C / {min(temp_list):.1f}°C")
    
    stars = "*" * int(rain_percent // 5)
    print(f"Rain Chance:     [{stars:<20}] {rain_percent}%")
    print("="*30)
    LOG.info('Simple Analysis Report Generated')

def show_detailed_report(data: dict) -> None:
    """
    Generate and print an hourly table of temperature and conditions.

    Parameters
    ----------
    data : dict
        The weather data dictionary.
    """
    day_data = data['days'][0]
    print(f"\n{'TIME':<10} | {'TEMP (°C)':<10} | {'WEATHER'}")
    print("-" * 45)

    for hour in day_data['hours']:
        short_time = hour['datetime'][:5]
        celsius = farenheit_to_celcius(hour['temp'])
        print(f"{short_time:<10} | {celsius:<10.1f} | {hour['conditions']}")
    LOG.info('Detailed Table Report Generated')

def run_reports(data: dict, location: str, date_string: str):
    """
    Display a sub-menu for different viewing options for the current data.

    Parameters
    ----------
    data : dict
        The dictionary containing API response data.
    location : str
        The location name.
    date_string : str
        The date string.
    """
    LOG.info('Running Report Menu')
    formatted_date = date_string if date_string else "Today (Current)"

    while True:
        print(title_print('Report Menu'))
        print(f"Current View: {location.upper()} | {formatted_date}")
        print("1. Simple Summary")
        print("2. Detailed Hourly Breakdown")
        print("3. Save this report (CSV/JSON/TXT)")
        print("4. Back to Main Search")
        
        user_choice = input("\nEnter selection (1-4): ")

        if user_choice == "1":
            show_simple_report(data, location, formatted_date)
        elif user_choice == "2":
            show_detailed_report(data)
        elif user_choice == "3":
            save_report(data)
        elif user_choice == "4":
            break
        else:
            print("\nInvalid choice, please try again.\n")

# --- MAIN FUNCTION ---

def main():
    """
    Execute the primary application loop for the weather tool.
    """
    session_cache = UserQuery()
    while True:
        print(title_print('Weather Tool'))
        print(session_cache.fetch_history())
        
        loc = input("\nLocation (or 'Q' to quit): ").strip()
        if loc.lower() == 'q': 
            print("Ending session. Goodbye!")
            break
        if not loc: continue

        date = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
        session_cache.add_to_cache(loc, date)

        handler = APIHandler(loc, date)
        data = handler.connect()

        if data:
            run_reports(data, loc, date)
        else:
            print("\n!!! Data retrieval failed. Please check location/date and try again.\n")

if __name__ == "__main__":
    main()