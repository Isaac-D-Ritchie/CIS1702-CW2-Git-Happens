"""Developer Notes:
    Hover Over Functions if you do not know what they do, The Docstrings included will help provide context

    There is still some todos (Not All Nessesary) that would be great to implement:

        !!Stability & Security!!
        API Key Security (Calling on .env using os.getenv)

        !!Data Handling!!
        Allow for Saving Simple and Detailed Reporting, only Simple at the minute
        Allow txt to save exactly as is printed in terminal e.g Rain Chance Bar not saved to txt

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
    CSV comparison Function
    Clothing recomendation Function
    Reporting Function
    Main Function
"""


# --- IMPORTED MODULES ---

import requests # Util for API requests
from requests.exceptions import HTTPError, JSONDecodeError # Exceptions for requests related errors
import logging as LOG # For Logging instead of Printing
from datetime import datetime as dt #formatting and timedelta
from typing import List, Dict, Optional, Any #Would've liked JSON import but issues with differing versions of python
import json # Read/Writing to JSON
import csv # Read/Writing to CSV
import statistics #Helps with analysis
import os #helper to find files
import datetime


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

#adds the logging to log file, 'AppErrors.log'
LOG.basicConfig(level=LOG.INFO, format='%(asctime)s [%(levelname)s] %(message)s', filename='final_submission/AppErrors.log', filemode='a')

def validate_location(location: str) -> bool:
    """Validate location string against city list CSV."""
    with open("final_submission/worldcities.csv","r",newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['city'].lower() == location.lower():
                return True
    return False
def validate_date(date_list: List[str]) -> bool:
    """Validate date string is in YYYY-MM-DD format."""
    try:
        for date_str in date_list:
            if date_str:  # Only validate non-empty strings
                dt.strptime(date_str, '%Y-%m-%d')
                continue
            else:
                return False
        return True
    except ValueError:
        return False

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

    def __init__(self, location: str, date: str = "", date2: str = ""):
        """Initializes the APIHandler with user query parameters."""
        LOG.info('API Handler Initialized.')

        self.location = location
        self.date = date
        self.date2 = date2
        self.api_data = {
            'url': 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
            'keys': ['247BUSAAULFLBGWM7NVZ49M4B', 'U4QN48S3UU3XJ2C3LAK6TC8MM','32UK6VYZJELDSBFA2GPRESVGM']
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
            if self.date == "":
                self.date = datetime.date.today()
            
            date_path = f"/{self.date}" if self.date else ""
            if self.date2:
                date_path += f"/{self.date2}"
            full_url = f'{url}{self.location}{date_path}?key={key}&include=hours'

            try:
                LOG.info(f"Connecting to API for location {self.location}...")
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
        LOG.info('Fetched query history for display')
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
        'conditions': day.get('conditions'),
        'tempmax': round(farenheit_to_celcius(day.get('tempmax')), 1),
        'tempmin': round(farenheit_to_celcius(day.get('tempmin')), 1),
        'stations_used': ", ".join(data.get('stations', []))
    }
    
    try:
        # CSV SAVE
        csvpresent = os.path.isfile('final_submission/reporting.csv')
        with open('final_submission/reporting.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report_fields.keys())
            if not csvpresent:
                writer.writeheader()
            writer.writerow(report_fields)
        LOG.info('Validated and saved to reporting.csv')

        # JSON SAVE
        with open('final_submission/reporting.json', 'a') as f:
            f.write(json.dumps(report_fields) + '\n')
        LOG.info('Validated and saved to reporting.json')

        # TXT SAVE
        txtpresent = os.path.isfile('final_submission/reporting.txt')
        with open('final_submission/reporting.txt', 'a') as f:
            if not txtpresent:
                f.write("--- GIT HAPPENS WEATHER LOG START ---\n")
            
            f.write(f"\n[ENTRY: {report_fields['timestamp']}]\n")
            for key, value in report_fields.items():
                f.write(f"{key.upper():<12}: {value}\n")
            f.write("-" * 35 + "\n")
        LOG.info('Validated and saved to reporting.txt')

    except Exception as err:
        LOG.warning(f'Error with saving to files: {err}')
    print("\nReport saved to reporting.csv, reporting.json, and reporting.txt")


# --- CSV COMPARISON ---

def compare_csv():
    """
    Choose and compare saved CSV data

    Parameters
    ----------
    No parameters, data is taken from CSV file.
    """
    print(title_print('CSV COMPARISON'))
    try:
        LOG.info("Starting CSV Comparison Function")
        with open("final_submission/reporting.csv","r",newline="") as f:
            reader = csv.DictReader(f)
            print("All current CSV data:")
            i = 1
            rows = []
            for row in reader:
                print(f"{i}. {row['location']}, {row['date']}, {row['avg_temp']}°C, {row['conditions']}, {row['tempmax']}°C/{row['tempmin']}°C, Stations Used: {row['stations_used']}")
                rows.append(row)
                i += 1
                
            if len(rows) < 2:
                print("Not enough values to compare, please try again\n")
                LOG.warning("not enough values to compare in CSV Comparison Function")
                return

            #First data point input
            while True:
                try: 
                    first_data_point = int(input(f"\nPlease select first data point (1-{i-1})"))
                    if 1 <= first_data_point <= i-1:
                        break
                    else:
                        print("Invalid input, please try again\n")
                        LOG.warning("Invalid input for first data point in CSV comparison")
                except ValueError as err:
                    print("Invalid input, please try again\n")
                    LOG.warning(f"{err} for first data point in CSV comparison")

            #Second data point input
            while True:
                try: 
                    second_data_point = int(input(f"\nPlease select second data point (1-{i-1})"))
                    if 1 <= second_data_point <= i-1:
                        break
                    elif first_data_point == second_data_point:
                        print("Cannot compare identical data points\n")
                        LOG.warning("Attempted to compare identical data points in CSV comparison")
                    else:
                        print("Invalid input, please try again\n")
                        LOG.warning("Invalid input for second data point in CSV comparison")
                except ValueError as err:
                    print("Invalid input, please try again\n")
                    LOG.warning(f"{err} for second data point in CSV comparison")
            
        #Data Comparison variables
        row_1 = rows[first_data_point - 1]
        row_2 = rows[second_data_point - 1]

        location_1 = row_1.get("location")
        location_2 = row_2.get("location")

        avg_temp_1 = float(row_1.get("avg_temp"))
        avg_temp_2 = float(row_2.get("avg_temp"))
        temp_diff = avg_temp_1 - avg_temp_2

        humidity_1 = float(row_1.get("humidity"))
        humidity_2 = float(row_2.get("humidity"))
        humidity_diff = humidity_1 - humidity_2

        conditions_1 = row_1.get("conditions")
        conditions_2 = row_2.get("conditions")

        max_temp_1 = float(row_1.get("tempmax"))
        max_temp_2 = float(row_2.get("tempmax"))
        min_temp_1 = float(row_1.get("tempmin"))
        min_temp_2 = float(row_2.get("tempmin"))


        #Data Comparison Table
        print("\n=== WEATHER COMPARISON ===\n")
        print("{:<20}  {:<20}  {:<20}  {}".format("Data", "Row 1", "Row 2", "Difference"))
        print("~" * 76)
        print("{:<20}  {:<20}  {:<20}  {}".format("Location", location_1, location_2, "N/A"))
        print("{:<20}  {:<20}  {:<20}  {}".format("Average Temp", 
                "{:.2f}°C".format(avg_temp_1), "{:.2f}°C".format(avg_temp_2), "{:.2f}°C".format(temp_diff)))
        print("{:<20}  {:<20}  {:<20}  {}".format("Humidity", "{:.0f}%".format(humidity_1),
                "{:.0f}%".format(humidity_2), "{:.0f}%".format(humidity_diff)))
        print("{:<20}  {:<20}  {:<20}  {}".format("Max Temp",
                "{:.2f}°C".format(max_temp_1), "{:.2f}°C".format(max_temp_2), "{:.2f}°C".format(max_temp_1 - max_temp_2)))
        print("{:<20}  {:<20}  {:<20}  {}".format("Min Temp",
                "{:.2f}°C".format(min_temp_1), "{:.2f}°C".format(min_temp_2), "{:.2f}°C".format(min_temp_1 - min_temp_2)))
        



        if conditions_1 == conditions_2:
            print(f"\nConditions in {location_1} and {location_2} are the same: {conditions_1}")
        else:
            print(f"\nThe conditions in {location_1} are {conditions_1}.\nWhile the conditions in {location_2} are {conditions_2}")
        LOG.info("CSV Comparison Completed Successfully")   
        input("\nPress Enter to return to menu")

    except FileNotFoundError:
        print("\nCSV file Not found, Please try again")
        LOG.warning("CSV file Not found when trying to compare")


# --- CLOTHING RECOMENDATION ---

def clothing_recommendation(average_temp) -> str:
    """
    Print recomended clothing based on temp

    Parameters
    ----------
    average_temp: integer
        Tempreture to compare for recomendation
    """
    if average_temp >= 30:
        return "It's very hot outside, wear light clothing like shorts and a t-shirt"
    elif average_temp >= 20:
        return "The weather is warm, a t-shirt and jeans would be a good choice"
    elif average_temp >= 10:
        return "It's a little cold, a light jumper is recommended"
    elif average_temp >= 0:
        return "It's very cold outside today, wear a thick coat and warm clothes"
    else:
        return "Extremely cold weather! Make sure to wrap up with thermals, a coat and a hat and gloves"


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
    hours_data = day_data.get('hours')
    """
    API Has a limit for data gathering, [hours] can only be accessed in a range for a limited number of days,
    code below checks if hours_data is accesible, if not the program switches to gathering data without it.
    """
    data_source = data['stations']


    if hours_data:
        temp_list = [farenheit_to_celcius(h['temp']) for h in hours_data]
        condition_list = [h['conditions'] for h in hours_data]
        average_temp = statistics.mean(temp_list)
        most_common_weather = statistics.mode(condition_list)
        high_temp = max(temp_list)
        low_temp = min(temp_list)
        LOG.info("Hourly breakdown available for this date, using hourly data")
    else:
        average_temp = farenheit_to_celcius(day_data['temp'])
        most_common_weather = day_data.get('conditions','N/A')
        high_temp = farenheit_to_celcius(day_data['tempmax'])
        low_temp = farenheit_to_celcius(day_data['tempmin'])
        print("Hourly Breakdown Unavailable for this date")
        LOG.warning("Hourly breakdown unavailable for this date, using daily data")
    

    rain_percent = day_data.get('precipprob', 0)
    
    print(title_print(f"SUMMARY FOR: {location.upper()} | DATE: {date_string}"))
    print(f"Main Condition:  {most_common_weather}")
    print(f"Average Temperature:    {average_temp:.1f}°C")
    print(f"Highs of:      {high_temp:.1f}°C")
    print(f"Lows of:     {low_temp:.1f}°C")
    print(clothing_recommendation(average_temp))

    stars = "*" * int(rain_percent // 5)
    print(f"Rain Chance:     [{stars:<20}] {rain_percent}%\n")
    print(f"Data sourced from stations: {', '.join(data_source) if data_source else 'N/A'}")
    print("="*30)
    
    LOG.info('Simple Analysis Report Generated')
    input("\nPress Enter to display further date range, or return to menu")
    return None
    

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
    totaltemp = []
    for hour in day_data['hours']:
        short_time = hour['datetime'][:5]
        celsius = farenheit_to_celcius(hour['temp'])
        print(f"{short_time:<10} | {celsius:<10.1f} | {hour['conditions']}")
        totaltemp.append(celsius)

    print(f"Average Temperature is {statistics.mean(totaltemp):.1f}°C with Highs of {max(totaltemp):.1f}°C and Lows of {min(totaltemp):.1f}°C")
    print(f"Data sourced from stations: {', '.join(data.get('stations', []))}")
    LOG.info('Detailed Table Report Generated')
    input("\nPress Enter to return to menu")

def run_reports(data: dict, location: str, date_string: str, date2: str = ""):
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
    
    
    if date2:
        formatted_date = date_string if date_string else "Today (Current)"
        formatted_date = formatted_date + f" to {date2}"
        is_range = True
    else:
        formatted_date = date_string if date_string else "Today (Current)"
        is_range = False
        

    while True: #both while loops are required here, one for menu looping, one for input validation
        print(title_print('Report Menu'))
        print(f"Current View: {location.upper()} | {formatted_date}")
        print("1. Simple Summary")
        print("2. Detailed Hourly Breakdown")
        print("3. Save this report (CSV/JSON/TXT)")
        print("4. Back to Main Search")
        print("5. Compare CSV data")
        while True:
            user_choice = input("\nEnter selection (1-5): ").strip()
            if user_choice in {"1","2","3","4","5"}:
                break
            else: 
                print("Invalid choice, please try again.\n")
                LOG.warning("Invalid input in Report Menu, retrying...")

        LOG.info(f'User selected option {user_choice} in Report Menu')
        if user_choice == "1":
            if is_range == True:    
                for days in data['days']:
                    temp_data = {'days': [days], 'address': data.get('address')}
                    show_simple_report(temp_data,location,days['datetime'])
            else:
                show_simple_report(data, location, formatted_date)
        elif user_choice == "2":
            show_detailed_report(data)
        elif user_choice == "3":
            save_report(data)
        elif user_choice == "4":
            break
        elif user_choice == "5":
            compare_csv()


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
        if not validate_location(loc):
            print("\n!!! Location not found. Please try again.\n")
            LOG.warning(f"Location not found in : {loc}")
            continue
        else:
            date = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
            date2 = input("OPTIONAL: End date (YYYY-MM-DD) ").strip()
            dates = [date, date2]
            if not validate_date(dates) and "" not in dates:
                print("\n!!! Invalid date format. Please use YYYY-MM-DD.\n")
                LOG.warning(f"Invalid date format input: {date}")
                continue
            else:
                session_cache.add_to_cache(loc, date)
                
                handler = APIHandler(loc, date,date2)
                data = handler.connect()

        if data:
            run_reports(data, loc, date, date2)
        else:
            print("\n!!! Data retrieval failed. Please check location/date and try again.\n")
            LOG.warning("Data retrieval failed after all API key attempts.")

if __name__ == "__main__":
    main()