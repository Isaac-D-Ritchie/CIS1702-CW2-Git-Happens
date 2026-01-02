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

#   UTILS AND CONSTANTS

#Title formatting for Reporting and Menu Functions
def title_print(x: str) -> str:
    return '\n'*3 + '='*25 + f'\n {x}\n' + '='*25 + '\n'*2
#Farenheit conversion
def farenheit_to_celcius(x: int):
    return (x - 32) / 1.8

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

#   LOG CONFIG
LOG.basicConfig(
    level = LOG.INFO,  #level captures minimum level to log
    format = '%(asctime)s [%(levelname)s] %(message)s', #format for logging
    datefmt = '%Y-%m-%d %H:%M:%S' #dateformat for asctime
)


#   CLASSES

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
                LOG.info(f"Connecting to {url}")
                with requests.get(full_url, timeout=10) as response:
                    response.raise_for_status()
                    LOG.info(STATUS_CODES.get(str(response.status_code)))

                    if int(response.status_code) in (200, 204):
                        LOG.info(f"Successfully fetched from {url},Key ending in.{i[-4:]}") #Only logs last 4 characters of Key (Due to sensitive data)
                        return response
                    else:
                        LOG.info("Retrying......")
                    
                        
            except HTTPError as err:
                print(f"HTTP Error whilst Communicating with {full_url}")
                LOG.info(f"{err}")
            except JSONDecodeError as err:
                print(f"JSON Decode Error whilst Communicating with {full_url}")
                LOG.info(f"{err}")
            except Exception as err:
                print(f"Exception Error whilst Communicating with {full_url}")
                LOG.info(f"{err}")
        LOG.critical("Unable to Connect to API. Returning to Main")
        return None

class UserQuery:

    def __init__(self, cli_query: List[str]) -> None:
        self.cli_query = cli_query
        self.querycache: Dict[str, List[str]] = {'cities': [],'dates': []}

    def querystore(self):
        try:
            for i in self.cli_query:
                if not i:
                    LOG.debug('Skipping empty query item')
                    continue

                if dt.strptime(i,str('%Y-%m-%d')):
                    self.querycache['dates'].append(i)
                    LOG.info('Cached Query Date')

                else:
                    self.querycache['cities'].append(i)
                    LOG.info('Cached Query Location')

        except TypeError as err:
            LOG.warning(f'TypeError when Caching Query "{i}", Error:{err}')
        except ValueError as err:
            LOG.warning(f'ValueError when Caching Query "{i}", Error:{err}')
        except Exception as err:
            LOG.warning(f'Exception when Caching Query "{i}", Error:{err}')
            






def save_report(fieldnames,data_array) -> None:
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
    
    try:
        with open(f"reporting.csv","a", newline='') as f:
            writer = csv.DictWriter(f,fieldnames = fieldnames)
            writer.writeheader()
            writer.writerow(data_array)
        LOG.info('Report appended to reporting.csv')
    except Exception as err:
        LOG.warning('Error with saving to reporting.csv',err)

"""REPORTING FUNCTIONS"""
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
    
    day_info = data['days'][0]
    all_hours = day_info['hours']
    
    temp_list = []
    condition_list = []
    
    for hour in all_hours:
        celsius = farenheit_to_celcius(hour['temp'])
        temp_list.append(celsius)
        condition_list.append(hour['conditions'])

    #DATA CALCULATIONS, functions describe 
    average_temp = sum(temp_list) / len(temp_list) #mean
    highest_temp = max(temp_list) #max
    lowest_temp = min(temp_list) #min
    most_common_weather = statistics.mode(condition_list) #mode weather type
    rain_percent = day_info.get('precipprob', 0) #chance of rain
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

    day_info = data['days'][0]
    all_hours = day_info['hours']

    print(f"\n{'TIME':<10} | {'TEMP (°C)':<10} | {'WEATHER'}")
    print("-" * 40)

    for hour in all_hours:
        raw_time = hour['datetime']
        short_time = raw_time[0:5] 
        
        raw_farenheit = hour['temp']
        sorted_celcius = farenheit_to_celcius(raw_farenheit)
        
        weather = hour['conditions']
        
        print(f"{short_time:<10} | {sorted_celcius:<10.1f} | {weather}")
    LOG.info('Detailed Table Report Generated')

def run_reports(response, userquery[0][1], userquery[0]):
    LOG.info('Running Report Menu')
    try:
        data = response.json()
    except JSONDecodeError as err:
        #!!Need to do something here 
        LOG.info('Error parsing JSON',err)

    #formatting date string for header
    #time_info = TimeBreak(userquery[0]) NEEDS FIXING!!!!
    #formatted_date = time_info.reporting_date
    

    print(title_print('Report Menu'))
    print("1. Simple Summary")
    print("2. Detailed Hourly Breakdown")
    print("3. Cancel")
    
    user_choice = input("Enter 1, 2, or 3: ")

    if user_choice == "1":
        show_simple_report(data, userquery[0][1], formatted_date)
    elif user_choice == "2":
        show_detailed_report(data)
    else:
        return None


"""MAIN FUNCTION"""
#Function for main code
def main():
    #userquery contains Dates then Cities in 2d array
    userquery = [[],[]]
    while True:
        LOG.info('')
        print(title_print('Weather Data'))
        userquery[0][1] = input("Enter location (e.g. London): ")
        if not userquery[0][1]:
            LOG.info('')
            return None

        userquery[0][0] = input("Enter date (YYYY-MM-DD) or leave blank: ")
        
        confirm = input(f"Proceed with {userquery[0][1]} on {userquery[0] if userquery[0] else 'Today'}? (Y/N): ")
        
        if confirm.lower() == "y":
            #Checks Connection
            response = handler(userquery[0][1], userquery[0]).connect()
            
            #If Connection is active then report functions are called with data
            if response:
                run_reports(response, userquery[0][1], userquery[0])
            else:
                print("Failed to retrieve data.") #!! LOG
                return None
        else:
            return None
    
 
"""Initialises Main"""
if __name__ == "__main__":
    main()