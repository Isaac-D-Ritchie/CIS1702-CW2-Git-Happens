"""
WeatherApp
API KEY = 247BUSAAULFLBGWM7NVZ49M4B
VISUAL CROSSING WEATHER API
"""
#TO-DO
#1) Account for edge-cases
#2) Allow the saving to a csv to account for the range of dates

"""Imports"""
import json
import requests
import csv
api_key = '247BUSAAULFLBGWM7NVZ49M4B'

class APIHandler:
    def __init__(self,api_key):
        #API Basic info
        self.url = ('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/')
        self.keys = [api_key,'BACKUPAPIKEY']

        #Connect Function
    def connect(self,location,date1,date2=None, index = 0):
        if index >= len(self.keys):
            print("CRITICAL ERROR: ALL API CONNECTION DATA FAILED, EXITING") #!! LOG
            return None
        #Handles URL Date, decides between using just one date or two for range data
        date_path = f"{date1}{date2}" if date2 else f"{date1}" 
        full_url = f'{self.url}{location}/{date_path}?key={self.keys[index]}'

        if index == 0:
            print(f"Attempt {index + 1}: Connecting to {self.url} (Primary Key)") #!! LOG
        else:
            print(f"Attempt {index + 1}: Connecting to {self.url} (Backup Key)") #!! LOG
        
        try:
            with requests.get(full_url, timeout=10) as response:
                if response.status_code == 200:
                    print("Connection successful!") #!! LOG 
                    return response.json() 
                
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
    handler = APIHandler('247BUSAAULFLBGWM7NVZ49M4B')
    while True:
        print("=== Weather Data ===\n")
        user_location = input("Enter location:\n")
        user_date = input("Enter date in a YYYY-MM-DD format (Leave blank for current weather)")
        user_date_2 = input("OPTIONAL: Enter a 2nd date in a YYYY-MM-DD format (Leave blank to ignore)")
        user_choice = input(f"Location:{user_location}\n Date:{user_date}\n Continue? (Y/N)")
        user_choice = user_choice.lower()

        api_date1 = f"{user_date}/" if user_date != "" else ""
        api_date2 = user_date_2 if user_date_2 != "" else None
        if user_date_2 == "":
            user_date_2 = None

        if user_choice == "y": #This is where they key functions are called
            location_data = handler.connect(user_location,api_date1,api_date2)

            if user_date_2 is not None: #If user has picked a 2nd date, run the weather_value_range function instead of the normal one
                day_index = 0 #Initizaliting
                #This loops recieving the values and printing them for a range of dates
                for day in location_data['days']:
                    weather_data = weather_values_range(location_data,day_index)
                    print_values(user_location,user_date,*weather_data)
                    day_index += 1
                extra_options_menu(user_location,*weather_data,location_data)

            else:
                weather_data = weather_values(location_data,user_date)
                print_values(user_location,user_date,*weather_data)
                extra_options_menu(user_location,*weather_data,location_data)
                #Calls print_value func using the user choices and the 'weather_data' list returned from 'weather_values' func



"""API Code"""



#Function for farenheight to celcius because visual Crossing API uses farenheit
def farenheit_to_celcius(farenheit):
    celcius = (farenheit - 32) / 1.8
    return celcius
    

#Function for printing weather results and returning weather values
"""Data Gathering"""


def weather_values(location_data, user_date):
    date_time = location_data['days'][0]['datetime']
    temp_current = round(farenheit_to_celcius(location_data['days'][0]['temp']),2) #These lines are taking the chosen values from location_data
    temp_max = round(farenheit_to_celcius(location_data['days'][0]['tempmax']),2) #Then operating on them with farenheit to celcius
    temp_min = round(farenheit_to_celcius(location_data['days'][0]['tempmin']),2)#All while rounding it to 2 decimal places
    weather_condition = (location_data['days'][0]['conditions'])

  
    return(date_time,temp_max,temp_min,temp_current,weather_condition)  

def weather_values_range(location_data,day_index):
    date_time = location_data['days'][day_index]['datetime']
    temp_current = round(farenheit_to_celcius(location_data['days'][day_index]['temp']),2)
    temp_max = round(farenheit_to_celcius(location_data['days'][day_index]['tempmax']),2)
    temp_min = round(farenheit_to_celcius(location_data['days'][day_index]['tempmin']),2)
    weather_condition = (location_data['days'][day_index]['conditions'])
    
    return(date_time,temp_max,temp_min,temp_current,weather_condition)  
        




"""UI"""
def print_values(user_location,user_date,date_time,temp_max,temp_min,temp_current,weather_condition):
        print(f"=========={user_location}=={date_time}==========")
        print(weather_condition)
        print(f"Maximum temperature is {temp_max} C")
        print(f"Minimum temperature is {temp_min} C")
        if user_date == "":
            print(f"Current temperature is {temp_current} C") #API uses 'temp' as average temp on future dates, if user wants the current date they get the current temp
        else:
            print(f"Average temperature is {temp_current} C")
        
        suggestion_Clothes = clothing_recommendation(temp_current)
        print(suggestion_Clothes)
        print("===============================")



def extra_options_menu(user_location,date_time,temp_max,temp_min,temp_current,weather_condition,location_data):
        csv_dict = {f"Location":user_location, #Parsing API data into a dictionary to be converted to a CSV
                    "Date":date_time,
                    "Maximum Temperature":temp_max,
                    "Minimum Temperature":temp_min,
                    "Current Temperature":temp_current
                    }
        fieldnames = ["Location","Date","Maximum Temperature","Minimum Temperature","Current Temperature"] #Keys from the dict to be plotted into csv
        user_choice = int(input("1) Save Report\n2)In-depth report\n 3) Exit"))

        if user_choice == 1: #Choice for saving to CSV
            save_report(date_time,fieldnames,csv_dict)
        elif user_choice == 2:
            weather_per_hour(location_data)

        return csv_dict
    

#Function to save report file (.CSV)
def save_report(date_time,fieldnames,data_array):
    with open(f"WeatherReport-{date_time}.csv","w", newline='') as f:
        writer = csv.DictWriter(f,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerow(data_array)


#Function for temp by hour
def weather_per_hour(location_data):
    for i in range(24):
        print (location_data['days'][0]['hours'][0+i]["datetime"])
        hour_temp = (farenheit_to_celcius(location_data['days'][0]['hours'][0+i]["temp"]))
        print(f"{hour_temp:.2f}C")

#Function for clothing recommendation based on the current temperature
def clothing_recommendation(temp_current):
    if temp_current >= 30:
        print("It's very hot outside, wear light clothing like shorts and a t-shirt")
    elif temp_current >= 20:
        print("The weather is warm, a t-shirt and jeans would be a good choice")
    elif temp_current >= 10:
        print("It's a little cold, a light jumper is recommended")
    elif temp_current >= 0:
        print("It's very cold outside today, wear a thick coat and warm clothes")
    else:
        print("Extremely cold weather! Make sure to wrap up with thermals, a coat and a hat and gloves")


"""Starts Program"""
main()