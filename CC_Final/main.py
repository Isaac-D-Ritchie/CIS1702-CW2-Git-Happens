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
    CSV comparison Function
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
import tkinter as tk # For UI
from tkinter import *
from tkinter import messagebox
from tkinter import ttk


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

# --- CSV COMPARISON ---

def compare_csv():
    print("\n=== CSV COMPARISON ===")
    try:
        with open("reporting.csv","r",newline="") as f:
            reader = csv.DictReader(f)
            print("All current CSV data:")
            i = 1
            rows = []
            for row in reader:
                print(f"{i}. {row['location']}, {row['date']}, {row['avg_temp']}°C, {row['conditions']}")
                rows.append(row)
                i += 1
                
            if len(rows) < 2:
                print("Not enough values to compare, please try again\n")
                return

            #First data point input
            while True:
                try: 
                    first_data_point = int(input(f"\nPlease select first data point (1-{i-1})"))
                    if 1 <= first_data_point <= i-1:
                        break
                    else:
                        print("Invalid input, please try again\n")
                except ValueError:
                    print("Invalid input, please try again\n")

            #Second data point input
            while True:
                try: 
                    second_data_point = int(input(f"\nPlease select second data point (1-{i-1})"))
                    if 1 <= second_data_point <= i-1:
                        break
                    elif first_data_point == second_data_point:
                        print("Cannot compare identical data points\n")
                    else:
                        print("Invalid input, please try again\n")
                except ValueError:
                    print("Invalid input, please try again\n")
            
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

        #Data Comparison Table
        print("\n=== WEATHER COMPARISON ===\n")
        print("{:<20}  {:<20}  {:<20}  {}".format("Data", "Row 1", "Row 2", "Difference"))
        print("~" * 76)
        print("{:<20}  {:<20}  {:<20}  {}".format("Location", location_1, location_2, "N/A"))
        print("{:<20}  {:<20}  {:<20}  {}".format("Average Temp", 
                "{:.2f}°C".format(avg_temp_1), "{:.2f}°C".format(avg_temp_2), "{:.2f}°C".format(temp_diff)))
        print("{:<20}  {:<20}  {:<20}  {}".format("Humidity", "{:.0f}%".format(humidity_1),
                "{:.0f}%".format(humidity_2), "{:.0f}%".format(humidity_diff)))

        if conditions_1 == conditions_2:
            print(f"\nConditions in {location_1} and {location_2} are the same: {conditions_1}")
        else:
            print(f"\nThe conditions in {location_1} are {conditions_1}.\nWhile the conditions in {location_2} are {conditions_2}")

        input("\nPress Enter to return to menu")

    except FileNotFoundError:
        print("\nCSV file Not found, Please try again")


# --- REPORTING FUNCTIONS ---

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
        print("5. Compare CSV data")
        
        user_choice = input("\nEnter selection (1-5): ")

        if user_choice == "3":
            save_report(data)
        elif user_choice == "4":
            break
        elif user_choice == "5":
            compare_csv()
        else:
            print("\nInvalid choice, please try again.\n")

# Function to generate a basic report

def generate_basic_report():
    """
    Execute the primary application loop for the weather tool.
    """
    session_cache = UserQuery()
    while True:
        print(title_print('Weather Tool'))
        print(session_cache.fetch_history())
        
        loc = location_entry.get()
        if loc.lower() =="":
            messagebox.showerror(title="ERROR", message="Please enter a location")
            break
        if not loc: continue

        date = date_entry.get()
        session_cache.add_to_cache(loc, date)

        handler = APIHandler(loc, date)
        data = handler.connect()

        if data:
            display_basic_report(data, loc, date)
            break
        else:
            messagebox.showerror(title= "ERROR", message="!!! Data retrieval failed. Please check location/date and try again.\n")
            break

#Function to generate an hour-by-hour breakdown

def generate_detailed_report():
    """
    Execute the primary application loop for the weather tool.
    """
    session_cache = UserQuery()
    while True:
        print(title_print('Weather Tool'))
        print(session_cache.fetch_history())
        
        loc = location_entry.get()
        if loc.lower() =="":
            messagebox.showerror(title="ERROR", message="Please enter a location")
            break
        if not loc: continue

        date = date_entry.get()
        session_cache.add_to_cache(loc, date)

        handler = APIHandler(loc, date)
        data = handler.connect()

        if data:
            display_detailed_report(data)
            break
        else:
            messagebox.showerror(title= "ERROR", message="!!! Data retrieval failed. Please check location/date and try again.\n")


#GUI Stuff

# creates root window
root = tk.Tk(screenName="Weather Report Generator", baseName="Weather Report Generator", className="Weather Report Generator")
root.geometry("450x300")

#creates variables for dropdown menus

hours = ("00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", 
         "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", 
         "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00")

#creates grid weights for easier placement of widgets

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)
root.rowconfigure(7, weight=1)

#function for generating basic report

def display_basic_report(data: dict, location: str, date_string: str) -> None:

        day_data = data['days'][0]
        hours_data = day_data['hours']
        
        temp_list = [farenheit_to_celcius(h['temp']) for h in hours_data]
        condition_list = [h['conditions'] for h in hours_data]

        average_temp = statistics.mean(temp_list)
        most_common_weather = statistics.mode(condition_list)
        rain_percent = day_data.get('precipprob', 0)

        if date_string == "":
            save_decision_1 = messagebox.askyesno(title="Basic Weather Report", message=f"SUMMARY FOR: {location.upper()} | DATE: TODAY\nMain Condition:  {most_common_weather}\nAverage Temp:    {average_temp:.1f}°C\nHigh / Low:      {max(temp_list):.1f}°C / {min(temp_list):.1f}°C\nRain Chance:     {rain_percent}%\n\n Would you like to save this report?")
            if save_decision_1 == True:
                save_report(data)
            else:
                pass
        else:
            save_decision_2 = messagebox.askyesno(title="Basic Weather Report", message=f"SUMMARY FOR: {location.upper()} | DATE: {date_string}\nMain Condition:  {most_common_weather}\nAverage Temp:    {average_temp:.1f}°C\nHigh / Low:      {max(temp_list):.1f}°C / {min(temp_list):.1f}°C\nRain Chance:     {rain_percent}%\n\n Would you like to save this report?")
            if save_decision_2 == True:
                save_report(data)
            else:
                pass
        

        LOG.info('Simple Analysis Report Generated')


#function for generating a detailed report

def display_detailed_report(data: dict) -> None:
        
    day_data = data['days'][0]

    table = f"\n{'TIME':<10} | {'TEMP (℃)':<10} | {'WEATHER'}\n"
    table += "-" * 40 + "\n"

    for hour in day_data['hours']:
        short_time = hour['datetime'][:5]  # HH:MM
        celsius = farenheit_to_celcius(hour['temp'])
        table += f"{short_time:<10} | {celsius:<10.1f} | {hour['conditions']}\n"
        
    messagebox.showinfo(title="Hour By Hour Breakdown", message=f"{table}\n\n Would you like to save this report?")

    LOG.info('Detailed Table Report Generated')

#function for generating a comparison report

def display_comparison_report():
    print("\n=== CSV COMPARISON ===")
    try:
        with open("reporting.csv","r",newline="") as f:
            reader = csv.DictReader(f)
            print("All current CSV data:")
            i = 1
            rows = []
            for row in reader:
                print(f"{i}. {row['location']}, {row['date']}, {row['avg_temp']}°C, {row['conditions']}")
                rows.append(row)
                i += 1
                
            if len(rows) < 2:
                print("Not enough values to compare, please try again\n")
                return

            #First data point input
            while True:
                try: 
                    first_data_point = int(comparison_file_1_entry.get())
                    if 1 <= first_data_point <= i-1:
                        break
                    else:
                        print("Invalid input, please try again\n")
                except ValueError:
                    print("Invalid input, please try again\n")
                    break

            #Second data point input
            while True:
                try: 
                    second_data_point = int(comparison_file_2_entry.get())
                    if 1 <= second_data_point <= i-1:
                        break
                    elif first_data_point == second_data_point:
                        print("Cannot compare identical data points\n")
                    else:
                        print("Invalid input, please try again\n")
                except ValueError:
                    print("Invalid input, please try again\n")
                    break
            
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

        #Data Comparison Table
        print("\n=== WEATHER COMPARISON ===\n")
        print("{:<20}  {:<20}  {:<20}  {}".format("Data", "Row 1", "Row 2", "Difference"))
        print("~" * 76)
        print("{:<20}  {:<20}  {:<20}  {}".format("Location", location_1, location_2, "N/A"))
        print("{:<20}  {:<20}  {:<20}  {}".format("Average Temp", 
                "{:.2f}°C".format(avg_temp_1), "{:.2f}°C".format(avg_temp_2), "{:.2f}°C".format(temp_diff)))
        print("{:<20}  {:<20}  {:<20}  {}".format("Humidity", "{:.0f}%".format(humidity_1),
                "{:.0f}%".format(humidity_2), "{:.0f}%".format(humidity_diff)))

        if conditions_1 == conditions_2:
            print(f"\nConditions in {location_1} and {location_2} are the same: {conditions_1}")
        else:
            print(f"\nThe conditions in {location_1} are {conditions_1}.\nWhile the conditions in {location_2} are {conditions_2}")

        input("\nPress Enter to return to menu")

    except FileNotFoundError:
        print("\nCSV file Not found, Please try again")

#function to add+arrange widgets and appropriate button when the user wishes to make a comparison

def comparison_ui_change():    
    if radio_variable.get()==2:
        report_btn.grid_remove()
        detailed_report_btn.grid_remove()
        
        comparison_report_btn.grid(row=8, column=0, columnspan=2, sticky=tk.E+tk.W+tk.S)
        
        comparison_file_1_label.grid(row=5, column=0, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
        comparison_file_1_entry.grid(row=5, column=1, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
        
        comparison_file_2_label.grid(row=6, column=0, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
        comparison_file_2_entry.grid(row=6, column=1, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)

        location_label.configure(state="disabled")
        location_entry.configure(state="disabled")
        date_label.configure(state="disabled")
        date_entry.configure(state="disabled")
        
    else:
        report_btn.grid()
        detailed_report_btn.grid()
        comparison_report_btn.grid_remove()
        comparison_file_1_label.grid_remove()
        comparison_file_1_entry.grid_remove()
        comparison_file_2_label.grid_remove()
        comparison_file_2_entry.grid_remove()
        location_label.configure(state="normal")
        location_entry.configure(state="normal")
        date_label.configure(state="normal")
        date_entry.configure(state="normal")

# creates labels so user knows where to inpurt data

location_label = Label(root, text="Please enter a location:")
date_label = Label(root, text="Please enter a date (YYYY-MM-DD):")

comparison_label = Label(root, text="Would you like to do a comparison?")

comparison_file_1_label = Label(root, text="Please select the 1st file you would like to compare:")
comparison_file_2_label = Label(root, text="Please select the 2nd file you would like to compare:")

#creates widgets to take data inputs from the user

location_entry = Entry(root)
date_entry = Entry(root)

comparison_file_1_entry = ttk.Combobox(root)
comparison_file_2_entry = ttk.Combobox(root)

#creates button to generate report

report_btn = Button(root, text="Generate Report", command=generate_basic_report)
detailed_report_btn = Button(root, text="Generate In-Depth Report", command=generate_detailed_report)
comparison_report_btn = Button(root, text="Compare These Two Reports", command=display_comparison_report)

#creates radio buttons so the user can choose to compare

radio_variable = IntVar()
radio_variable.set(1)

radio_no = Radiobutton(root, text="No", variable=radio_variable, value=1, command=comparison_ui_change)
radio_yes = Radiobutton(root, text="Yes", variable=radio_variable, value=2, command=comparison_ui_change)

#grid to arrange labels, buttons, entries and checkboxes

location_label.grid(row=0, column=0, pady=2, padx=2, sticky=tk.W+tk.E)
date_label.grid(row=1, column=0, pady=2, padx=2, sticky=tk.W+tk.E)
comparison_label.grid(row=3, column=0, pady=13, padx=2, sticky=tk.W+tk.E+tk.N)
comparison_file_1_label.grid_remove()
comparison_file_2_label.grid_remove()

location_entry.grid(row=0, column=1, pady=2, padx=2, sticky=tk.W+tk.E)
date_entry.grid(row=1, column=1, pady=2, padx=2, sticky=tk.W+tk.E)
comparison_file_1_entry.grid_remove()
comparison_file_2_entry.grid_remove()

radio_yes.grid(row=3, column=1, sticky=tk.N+tk.W)
radio_no.grid(row=3, column=1, pady=25, sticky=tk.N+tk.W)

report_btn.grid(row=8, column=0, sticky=tk.S+tk.W+tk.E)
detailed_report_btn.grid(row=8, column=1, sticky=tk.S+tk.W+tk.E)
comparison_report_btn.grid_remove()

# tkinter event loop
root.mainloop() 