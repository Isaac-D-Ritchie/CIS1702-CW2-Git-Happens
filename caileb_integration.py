"""MAIN INFO
Git Happens API Scenario Main Program.

Data Flow:

Weather API -> Data Analysis -> Reporting -> Saving


Program Structure:

Imported Modules
Classes and Background Functions
Reporting Functions
Front-end Functions
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

#Title formatting for Reporting and Menu Functions
def title_print(x: str) -> str:
    return '\n'*3 + '='*25 + f'\n {x}\n' + '='*25 + '\n'*2
#Farenheit conversion
def farenheit_to_celcius(x: int):
    return (x - 32) / 1.8


# --- CORE CLASSES ---

class APIHandler:
    """
    Handles API Communication
        Contains:
        Connect Function
        Location & Date Variables
    """

    def __init__(self, location, date=""):
        LOG.info('API Handler Initialized.')
        #assigning variables to instance 'self'
        self.location = location
        self.date = date
        #API BASIC INFO
        self.api_data = {
            'url':'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
            'keys':['247BUSAAULFLBGWM7NVZ49M4B','U4QN48S3UU3XJ2C3LAK6TC8MM']
        }
        
        #FETCH REQUEST FUNCTION
    def connect(self) -> Optional[Any] | None: # Optional[Any] -> JSON in future
        """
        Connect to the Visual Crossing Weather API and return the first
        successful ``requests.Response``.

        The method iterates over the API keys stored in
        ``self.api_data['keys']``.  For each key it constructs the request
        URL (optionally including ``self.userquery[0]``) and attempts a GET
        request with a 10‑second timeout.  If the HTTP status code is
        200 (OK) or 204 (No Content) the response is returned immediately.
        Any other successful status code or an exception triggers a retry
        with the next key.

        Errors are caught and logged:

        * ``HTTPError`` – non‑successful HTTP responses
        * ``JSONDecodeError`` – problems parsing the JSON payload
        * Generic ``Exception`` – any other unexpected error

        If all keys fail the method logs a critical message and returns
        ``None``.

        Parameters
        ----------
        None – all required values are taken from the instance attributes.

        Returns
        -------
        requests.Response | None
            The first successful response, or ``None`` if the request fails.
        """
        
        url = self.api_data['url']
        for i in self.api_data['keys']:
            date_path = f"/{self.date}" if self.date else ""
            full_url = f'{url}{self.location}{date_path}?key={i}'

            try:
                LOG.info(f"Connecting to {url} with location:{self.location} and date:{self.date}")
                with requests.get(full_url, timeout=10) as response:
                    response.raise_for_status()
                    LOG.info(STATUS_CODES.get(str(response.status_code)))

                    if int(response.status_code) in (200, 204):
                        LOG.info(f"Successfully fetched from {url},Key ending in.{i[-4:]}") #Only logs last 4 characters of Key (Due to sensitive data)
                        return response
                    else:
                        LOG.info("Retrying......")
                    
                        
            except (HTTPError, JSONDecodeError, Exception) as err:
                print(f"Error whilst Communicating with {full_url},Key ending in.{i[-4:]}")
                LOG.warning(f"{err}")
        LOG.critical("Unable to Connect to API. Returning to Main")
        return None

class UserQuery:
    """
    Stores and manages a short history of user queries.

    The :class:`UserQuery` class keeps a lightweight cache of the most recent
    city names and dates that the user has requested.  The cache is held in a
    dictionary with two keys – ``'cities'`` and ``'dates'`` – each pointing
    to a list of strings.  The class offers two public methods: one to
    add a new query to the cache and one to retrieve a human‑readable
    summary of the cached items.

    The implementation deliberately keeps the logic simple: the cache
    is never cleared automatically and duplicate entries are ignored.
    Dates are validated against the ``%y-%m-%d`` format; if the format is
    invalid the entry is skipped and a warning is logged.  Logging is used
    throughout to aid debugging and to provide a trace of the cache
    operations.

    Errors are caught and logged:

        * ``TypeError`` – raised when a non‑string value is passed as a
          location or date.
        * ``ValueError`` – raised when the supplied date string does not
          match the expected ``%y-%m-%d`` format.
        * ``Exception`` – any other unexpected error that occurs while
          updating the cache.

    Logging here
        * On successful addition of a location or date a ``LOG.info`` entry
          records the cached value.
        * When a query item is empty a ``LOG.info`` message indicates the
          skip.
        * If a date fails validation a ``LOG.warning`` message is emitted.
        * Any other error during caching is logged as a warning with the
          exception details.

    Parameters
    ----------
    None – all required values are supplied when the methods are called.

    Returns
    -------
    str
        A multi‑line string that lists the cached cities and dates, e.g.

        .. code-block:: text

            Recent Cities: New York, London
            Recent Dates:  23-04-01, 23-04-02
    """
    
    def __init__(self) -> None:
        self.querycache: Dict[str, List[str]] = {'cities': [],'dates': []}

    def add_to_cache(self, location: str, date: str):
        if not location or not date:
            LOG.info(f'Empty Query Location:{location} Date:{date}, Skipping')
        try:
            if location and location not in self.querycache['cities']:
                self.querycache['cities'].append(location)
                LOG.info(f'Cached Location:{location}')
            if date:
                dt.strptime(date, '%y-%m-%d')
                if date not in self.querycache['dates']:
                    self.querycache['dates'].append(date)
                    LOG.info(f'Cached Date:{date}')
        except (TypeError, ValueError) as err:
            LOG.warning(f'Error Date formatting or type invalid, Error{err}')
        except Exception as err:
            LOG.warning(f'Error when Caching Query, Error:{err}')

    def fetch_history(self) -> str:
            #returns string summary of session history
            cities = ", ".join(self.querycache['cities']) or "None"
            dates = ", ".join(self.querycache['dates']) or "None"
            return f"Recent Cities: {cities}\nRecent Dates:  {dates}"
            

#--- SAVING FUNCTION ---
def save_report(data:dict) -> None: #Only saves to csv currently
    """
    Append a single weather report to the CSV “reporting.csv” file and
    persist the same record in JSON and plain‑text formats.

    Parameters
    ----------
    fieldnames : list[str]
        Column names for the CSV writer; must match the keys in ``data_array``.
    data_array : dict
        Mapping of field names to values for the record that will be
        written.  The function expects the dictionary to contain all
        required keys.

    Notes
    -----
    * The CSV file is opened in append mode so each call adds a new row
      without erasing previous reports.
    * A timestamp (ISO‑8601 UTC) is automatically added to the record
      under the key ``timestamp`` before any file is written.
    * The same record is written to:
        * ``reporting.json`` – one JSON object per line (JSON‑lines).
        * ``reporting.txt`` – a human‑readable key/value list, one per line.
    * Errors are logged at ``WARNING`` level but do not raise an exception
      to avoid breaking the reporting pipeline.

    Returns
    -------
    None
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
        csvpresent = os.path.isfile('reporting.csv')
        with open('reporting.csv','a', newline='') as f:
            writer = csv.DictWriter(f,fieldnames = report_fields.keys())
            if not csvpresent:
                writer.writeheader()
            writer.writerow(report_fields)
            LOG.info('Report appended to reporting.csv')
        jsonpresent = os.path.isfile('reporting.json')
        txtpresent = os.path.isfile('reporting.txt')


        #with open('reporting.json', 'a') as f:
            #f.write(json.dumps(something) + '\n')
        #with open('reporting.txt', 'a') as f:
            #f.write(f"---(timestamp)---\n")
            #for key, value in something.items():
                #f.write(f"{key}:{value}\n")
            #or save each line of terminal reporting to a list then when saving save each line to replicate the report.
    except Exception as err:
        LOG.warning('Error with saving to reporting.csv',err)

#>> REPORTING FUNCTIONS
def show_simple_report(data: dict, location: str, date_string: str) -> None:
    """
    Print a concise summary of the first day’s weather.

    Parameters
    ----------
    data : dict
        Parsed JSON response from the weather API.
    location : str
        Human‑readable location string (e.g. “New York”).
    date_string : str
        Date in the format used by the user (e.g. ``"2024‑10‑01"``).

    Notes
    -----
    * Calculates average, high, low temperatures and the most common
      weather condition for the day.
    * Displays rain probability as a bar of asterisks.
    * The function logs the start and completion of the analysis.
    """
    
    day_data = data['days'][0]
    hours_data = day_data['hours']
    
    temp_list = []
    condition_list = []
    
    for hour in hours_data:
        celsius = farenheit_to_celcius(hour['temp'])
        temp_list.append(celsius)
        condition_list.append(hour['conditions'])

    #DATA CALCULATIONS, functions describe 
    average_temp = sum(temp_list) / len(temp_list) #mean
    highest_temp = max(temp_list) #max
    lowest_temp = min(temp_list) #min
    most_common_weather = statistics.mode(condition_list) #mode weather type
    rain_percent = day_data.get('precipprob', 0) #chance of rain
    LOG.info('Data Analysis Complete')

    #REPORTING OF CALCULATED DATA
    print(title_print(f"SUMMARY FOR: {location.upper()} | DATE: {date_string}"))

    print(f"Main Condition:  {most_common_weather}")
    print(f"Average Temp:    {average_temp:.1f}°C")
    print(f"High / Low:      {highest_temp:.1f}°C / {lowest_temp:.1f}°C")
    
    star_count = int(rain_percent // 5)
    stars = "*" * star_count
    print(f"Rain Chance:     [{stars:<20}] {rain_percent}%")
    print("="*30)
    LOG.info('Simple Analysis Report Generated')


def show_detailed_report(data: dict) -> None:
    """
    Print a per‑hour table of temperature and weather conditions.

    Parameters
    ----------
    data : dict
        Parsed JSON response from the weather API.

    Notes
    -----
    * Shows time in ``HH:MM`` format, temperature in Celsius, and
      the weather description.
    * The table is formatted for terminal display with fixed column
      widths.
    * Logs the completion of the detailed report.
    """

    day_data = data['days'][0]
    hours_data = day_data['hours']

    print(f"\n{'TIME':<10} | {'TEMP (°C)':<10} | {'WEATHER'}")
    print("-" * 40)

    for hour in hours_data:
        raw_time = hour['datetime']
        short_time = raw_time[0:5] 
        
        raw_farenheit = hour['temp']
        sorted_celcius = farenheit_to_celcius(raw_farenheit)
        
        weather = hour['conditions']
        
        print(f"{short_time:<10} | {sorted_celcius:<10.1f} | {weather}")
    LOG.info('Detailed Table Report Generated')

def run_reports(data, location: str, date_string: str):

    LOG.info('Running Report Menu')

    formatted_date = date_string if date_string else "Today (Current)"

    while True:
        print(title_print('Report Menu'))
        print(f"Current View: {location.upper()}| {formatted_date}")
        print("1. Simple Summary")
        print("2. Detailed Hourly Breakdown")
        print("3. Save this report (CSV/JSON/TXT)")
        print("4. Cancel/Back")
        
        user_choice = input("Enter 1, 2, 3 or 4: ")

        if user_choice == "1":
            show_simple_report(data, location, formatted_date)
        elif user_choice == "2":
            show_detailed_report(data)
        #elif user_choice == "3":
            #save_report(data, location) need to fix
        else:
            print("\nInvalid choice, please try again.\n")


"""MAIN FUNCTION"""
#Function for main code
def main():
    session_cache = UserQuery()
    while True:
        print(title_print('Weather Tool'))
        loc = input("Location (or 'Q' to quit): ").strip()
        if loc.lower() == 'q': break
        if not loc: continue

        date = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
        session_cache.add_to_cache(loc, date)

        handler = APIHandler(loc, date)
        data = handler.connect()

        if data:
            run_reports(data, loc, date)
        else:
            print("Data retrieval failed.")
    
 
"""Initialises Main"""
if __name__ == "__main__":
    main()