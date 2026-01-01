"""MAIN INFO
Git Happens API Scenario Main Program.


Data Flow:

Weather API -> Data Analysis -> Reporting


Program Structure:

Imported Modules
Classes
Background Functions
Reporting Functions
Front-end Functions
Main Function
"""

"""IMPORTED MODULES"""
import request
import requests
from requests.exceptions import HTTPError, JSONDecodeError
import logging as LOG
from datetime import datetime
import json
import csv
import statistics

statuscodes = {
            #success
            '200':'| JSON Recieved | Data Present and Formatted Correctly |',
            '204': '| JSON Recieved|  Data Not Present, Formatted Correctly |',
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

LOG.basicConfig(
    level = LOG.INFO,
    format = '%(asctime)s [%(levelnames)s] %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
)
"""CLASSES"""
class TimeBreak:
    """Handles report timestamps and formatting"""
    def __init__(self, user_date=None):
        LOG.info('TimeBreak Initialized.')
        #if user_date is None then it is formatted to Todays date
        if not user_date:
            self.reporting_date = datetime.now().strftime("%d/%m/%Y")
        else:
            self.reporting_date = user_date

class APIHandler:
    """Handles API Communication"""
    def __init__(self, user_location, user_date, statuscodes):
        LOG.info('API Handler Initialized.')
        #assigning variables to instance 'self'
        self.user_location = user_location
        self.user_date = user_date if user_date else ""
        self.statuscodes = statuscodes
        #API Basic info
        self.api_data = {
            'url':'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
            'keys':['247BUSAAULFLBGWM7NVZ49M4B','BACKUPAPIKEY']
        }
        
        #Connect Function
    def connect(self) -> json | None:
        url = self.api_data['url']
        for i in self.api_data['keys']:
            date_path = f"/{self.user_date}" if self.user_date else ""
            full_url = f'{url}{self.user_location}{date_path}?key={i}'
            try:
                with requests.get(full_url, timeout=10) as response:
                    LOG.info(f"Attempt {i.index()}: Connecting to {url}")
                    LOG.info(f"")
                    if response.statuscode in (200,204):
                        LOG.info(f"Successfully fetched from {full_url}")
                        return response
                    else
                    
                        
            except HTTPError as err:
                print(f"HTTP Error whilst Communicating with {full_url}")
                LOG.info(f"{err}")
            except JSONDecodeError as err:
                print(f"JSON Decode Error whilst Communicating with {full_url}")
                LOG.info(f"{err}")
            except Exception as err:
                print(f"Exception Error whilst Communicating with {full_url}")
                LOG.info(f"{err}")


"""BACKROUND FUNCTIONS"""
#Handler function x = Location, y = Date
handler = lambda x,y: APIHandler(x,y)
#Title formatting for Reporting and Menu Functions
titleprint = lambda x: '\n'*10 + '='*25 + f'\n {x}\n' + '='*25 + '\n'*2
#Farenheit conversion
farenheit_to_celcius = lambda x: (x - 32) / 1.8
#Backout is used to hop out of a function, logging could be utilized in this function
def backout():#!! And Log
    print("Backing Out...\n",('='*25),('\n'*5))



"""I did not touch this function as I'm not sure about csv file handling, 
wish to leave to someone else as this refactoring has killed me off - Caileb"""
#Function to save report file (.CSV)
def save_report(user_date,fieldnames,data_array):
    user_date = user_date.replace("/","") # Removes slash from user date used by the API link as it conflicts with file names
    with open(f"WeatherReport-{user_date}.csv","w", newline='') as f:
        writer = csv.DictWriter(f,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerow(data_array)
    #!! And Log


"""REPORTING FUNCTIONS"""
def show_simple_report(data, location, date_string):
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
    #!! And Log?

    #REPORTING OF CALCULATED DATA
    print(titleprint(f"SUMMARY FOR: {location.upper()} | DATE: {date_string}"))

    print(f"Main Condition:  {most_common_weather}")
    print(f"Average Temp:    {average_temp:.1f}°C")
    print(f"High / Low:      {highest_temp:.1f}°C / {lowest_temp:.1f}°C")
    
    star_count = int(rain_percent // 5)
    stars = "*" * star_count
    print(f"Rain Chance:     [{stars:<20}] {rain_percent}%")
    print("="*30)
    #!! And Log

def show_detailed_report(data):
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
    #!! And Log

def run_reports(response, user_location, user_date):
    #!! And Log: run_reports accessed
    try:
        data = response.json()
    except:
        #!!Need to do something here
        print("Error parsing JSON") #!! And Log
        return backout()

    #formatting date string for header
    time_info = TimeBreak(user_date)
    formatted_date = time_info.reporting_date
    

    print(titleprint('Report Menu'))
    print("1. Simple Summary")
    print("2. Detailed Hourly Breakdown")
    print("3. Cancel")
    
    user_choice = input("Enter 1, 2, or 3: ")

    if user_choice == "1":
        show_simple_report(data, user_location, formatted_date)
    elif user_choice == "2":
        show_detailed_report(data)
    else:
        return backout()


"""MAIN FUNCTION"""
#Function for main code
def main():
    while True:
        #!! And Log: Program Loop Started
        print(titleprint('Weather Data'))
        user_location = input("Enter location (e.g. London): ")
        if not user_location:
            #!! And Log
            break

        user_date = input("Enter date (YYYY-MM-DD) or leave blank: ")
        
        confirm = input(f"Proceed with {user_location} on {user_date if user_date else 'Today'}? (Y/N): ")
        
        if confirm.lower() == "y":
            #Checks Connection
            response = handler(user_location, user_date).connect()
            
            #If Connection is active then report functions are called with data
            if response:
                run_reports(response, user_location, user_date)
            else:
                print("Failed to retrieve data.") #!! LOG
                return backout()
        else:
            return backout()
    
 
"""Initialises Main"""
if __name__ == "__main__":
    main()