"""MAIN INFO
Git Happens API Scenario Main Program.


Data Flow:

Weather API -> Data Analysis -> Reporting



Program Structure:

Imported Modules
Classes
Background Functions
Front-end Functions
Main Function


TO DOS:

Assist with TimeBreak esque Class or not
Look at Menu Functions
Look at Basic and Detailed Reporting in Terminal
"""

"""IMPORTED MODULES"""
import requests
import json

import csv

"""CLASSES"""
class APIHandler:
    def __init__(self, user_location, user_date):
        #assigning variables to instance 
        self.user_location = user_location
        self.user_date = user_date if user_date else ""
        #API Basic info
        self.api_data = ('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',['247BUSAAULFLBGWM7NVZ49M4B','BACKUPAPIKEY'])
        
        #Connect Function
    def connect(self, index = 0):
        url, key = self.api_data
        if index >= len(key):
            print("CRITICAL ERROR: All API Connections Failed.\n Exiting...") #!! LOG
            return None
        
        full_url = f'{url}{self.user_location}/{self.user_date}?key={key[index]}'

        if index == 0:
            print(f"Attempt {index + 1}: Connecting to {url} (Primary Key)") #!! LOG
        else:
            print(f"Attempt {index + 1}: Connecting to {url} (Backup Key)") #!! LOG
        
        try:
            with requests.get(full_url, timeout=10) as response:
                if response.status_code == 200:
                    print("Connection successful!") #!! LOG 
                    return response
                else:
                    print(f"Error:{response.status_code}") 
                    return self.connect(index+1)
            
        #Recursive step given failed connection
        except Exception as e:
            print(f"Error: {e}\nAttempt {index+1} failed, Trying next option...")#!! LOG
            return self.connect(index+1)
            


        #Function to parse data from API for entered location
        #def load_location_data



"""BACKROUND FUNCTIONS"""
#Handler function x = Location, y = Date
handler = lambda x,y: APIHandler(x,y)
#Title formatting for Reporting and Menu Functions
titleprint = lambda x: '\n'*10 + '='*25 + f'\n {x}\n' + '='*25 + '\n'*2
#Farenheit conversion
farenheit_to_celcius = lambda x: (x - 32) / 1.8
#!!Chance to Log Function Hops
def backout():#!! And Log
    print("Backing Out...\n",('='*25),('\n'*5))


#Function to save report file (.CSV)
def save_report(user_date,fieldnames,data_array):
    user_date = user_date.replace("/","") # Removes the slash from user date used by the API link as it conflicts with file names
    with open(f"WeatherReport-{user_date}.csv","w", newline='') as f:
        writer = csv.DictWriter(f,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerow(data_array)

#Function for printing weather results and returning weather values
def weather_values(location_data, user_date):
    #calls once to save resources
    data = location_data.json()
    day = data['days'][0]

    temp_current = farenheit_to_celcius(day['temp'])
    temp_max = farenheit_to_celcius(day['tempmax'])
    temp_min = farenheit_to_celcius(day['tempmin'])

    if not user_date:
        #Description can only be retrieved for the current weather? API Issue
        weather_desc = location_data.json()['description',"No description available"]
    else:
        weather_desc = day.get('description', day.get('conditions', "No description"))
    return(temp_current, temp_max, temp_min, weather_desc)

#Function for temp by hour
def weather_per_hour(location_data):
    #Calls Json once again to save resources
    data = location_data.json()
    hours = data['days'][0]['hours']
    
    print(f"\n{'Time':<10} | {'Temp (C)':<10}")
    print("-" * 22)
    for h in hours:
        time = h["datetime"]
        temp_c = farenheit_to_celcius(h["temp"])
        print(f"{time:<10} | {temp_c:>8.2f}°C")



"""FRONT-END FUNCTIONS"""
#Function for main code
def main():
    while True:
        print(titleprint('Weather Data'))

        user_location = input("Enter location:\n")
        user_date = input("Enter date in a YYYY-MM-DD format (Leave blank for current weather)")
        user_choice = input(f"Location:{user_location}\n Date:{user_date}\n Continue? (Y/N)")
        user_choice = user_choice.lower()
        if user_date == "":
            user_date = None #Allows user_date to be passed into the function even with no value
        if user_date != "":
            user_date = user_date + "/" #Adds a slash for the API link, slash isnt needed if date isn't input
        if user_choice == "y":
            location_data = handler(user_location,user_date).connect()
            weather_data = weather_values(location_data,user_date)
            print_values(location_data,user_location,user_date,weather_data[0],weather_data[1],weather_data[2],weather_data[3]) 
            #Calls print_value func using the user choices and the 'weather_data' list returned from 'weather_values' func
    


"""UI"""
def print_values(location_data,user_location,user_date,temp_current,temp_max,temp_min,weather_desc):
        print(f"=========={user_location}=={user_date}==========")
        try:
            print(weather_desc)#Only prints weather description when available
        except:
            print("No available description")
        print(f"Maximum temperature is {temp_max:.2f} C")
        print(f"Minimum temperature is {temp_min:.2f} C")
        if user_date == "":
            print(f"Current temperature is {temp_current:.2f} C") #API uses 'temp' as average temp on future dates, if user wants the current date they get the current temp
        else:
            print(f"Average temperature is {temp_current:.2f} C")
        print("===============================")
        csv_dict = {f"Location":user_location, #Parsing API data into a dictionary to be converted to a CSV
                    "Date":user_date,
                    "Maximum Temperature":temp_max,
                    "Minimum Temperature":temp_min,
                    "Current Temperature":temp_current
                    }
        fieldnames = ["Location","Date","Maximum Temperature","Minimum Temperature","Current Temperature"] #Keys from the dict to be plotted into csv
        user_choice = int(input("1) Save Report\n2)In-depth report\n 3) Exit"))
        if user_choice == 1: #Choice for saving to CSV
            save_report(user_date,fieldnames,csv_dict)
        elif user_choice == 2:
            weather_per_hour(location_data)

        return csv_dict
    

    
"""Starts Program"""
if __name__ == "__main__":
    main()
