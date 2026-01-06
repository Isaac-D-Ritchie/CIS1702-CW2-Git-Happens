"""
Weather Application

Structure is as follows:
Imports
Classes
Misc Functions
Main Functions
"""

import requests
import json

import csv


class APIHandler:
    def __init__(self, user_location, user_date)
        #API Basic info
        self.api_data = ('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',['247BUSAAULFLBGWM7NVZ49M4B','BACKUPAPIKEY'])
        url, key = self.api_data

        #Connect Function
        def connect(self, index = 0):
            if index >= len(key):
                print("CRITICAL ERROR: ALL API CONNECTION DATA FAILED, EXITING") #!! LOG
                return None
            
            full_url = f'{url}{user_location}/{user_date}?key={key[index]}'

            if index == 0:
                print(f"Attempt {index + 1}: Connecting to {url} (Primary Key)") #!! LOG
            else:
                print(f"Attempt {index + 1}: Connecting to {url} (Backup Key)") #!! LOG
            
            try:
                with requests.get(full_url, timeout=10) as response:
                    if response.status == 200:
                        print("Connection successful!") #!! LOG 
                        return json.load(response) 
                
            #Recursive step given failed connection
            except Exception as e:
                print(f"Error: {e}\nAttempt {index+1} failed, Trying next option...")#!! LOG
                return self.connect(index+1)
            


        #Function to parse data from API for entered location
        #def load_location_data
handler = lambda x,y: APIHandler(x,y)


"""Main Code"""
#Function for main code
def main():
    while True:
        print("=== Weather Data ===\n")
        user_location = input("Enter location:\n")
        user_date = input("Enter date in a YYYY-MM-DD format (Leave blank for current weather)")
        user_choice = input(f"Location:{user_location}\n Date:{user_date}\n Continue? (Y/N)")
        user_choice = user_choice.lower()
        if user_date == "":
            user_date == None #Allows user_date to be passed into the function even with no value
        if user_date != "":
            user_date = user_date + "/" #Adds a slash for the API link, slash isnt needed if date isn't input
        if user_choice == "y":
            location_data = handler(user_location,user_date).connect()
            weather_data = weather_values(location_data,user_date)
            print_values(location_data,user_location,user_date,weather_data[0],weather_data[1],weather_data[2],weather_data[3]) 
            #Calls print_value func using the user choices and the 'weather_data' list returned from 'weather_values' func




#Functon for farenheight to celcius because visual Crossing API uses farenheit
def farenheit_to_celcius(farenheit):
    celcius = (farenheit - 32) / 1.8
    return celcius
    

#Function for printing weather results and returning weather values
"""Data Gathering"""
def weather_values(location_data, user_date):
    temp_current = farenheit_to_celcius(location_data.json()['days'][0]['temp'])
    temp_max = farenheit_to_celcius(location_data.json()['days'][0]['tempmax'])
    temp_min = farenheit_to_celcius(location_data.json()['days'][0]['tempmin'])

    if user_date == "":
        weather_desc = location_data.json()['description'] #Description can only be retrieved for the current weather? API Issue
    else:
        weather_desc = None
    return(temp_current,temp_max,temp_min,weather_desc)

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
    

#Function to save report file (.CSV)
def save_report(user_date,fieldnames,data_array):
    user_date = user_date.replace("/","") # Removes the slash from user date used by the API link as it conflicts with file names
    with open(f"WeatherReport-{user_date}.csv","w", newline='') as f:
        writer = csv.DictWriter(f,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerow(data_array)


#Function for temp by hour
def weather_per_hour(location_data):
    for i in range(24):
        print (location_data.json()['days'][0]['hours'][0+i]["datetime"])
        print (location_data.json()['days'][0]['hours'][0+i]["temp"])



"""Starts Program"""
main()


