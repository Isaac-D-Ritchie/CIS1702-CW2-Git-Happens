#WeatherApp
#API KEY = 247BUSAAULFLBGWM7NVZ49M4B
#VISUAL CROSSING WEATHER API
import requests
import csv
api_key = '247BUSAAULFLBGWM7NVZ49M4B'


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
            location_data = load_location_data(user_location,user_date,api_key)
            weather_values(location_data,user_location,user_date)

def load_location_data(user_location,user_date,api_key):
    location_data = requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{user_location}/{user_date}?key={api_key}')
    return location_data


def farenheit_to_celcius(farenheit): #Visual Crossing API provides farenheit values
    celcius = (farenheit - 32) / 1.8
    return celcius
    
def weather_values(location_data,user_location,user_date):
    temp_current = farenheit_to_celcius(location_data.json()['days'][0]['temp']) #Parsing data from the API
    temp_max = farenheit_to_celcius(location_data.json()['days'][0]['tempmax'])
    temp_min = farenheit_to_celcius(location_data.json()['days'][0]['tempmin'])
    if user_date == "":
        weather_desc = location_data.json()['description'] #Description can only be retrieved for the current weather? API Issue
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
    data_array = {f"Location":user_location, #Parsing API data into a dictionary to be converted to a CSV
                  "Date":user_date,
                  "Maximum Temperature":temp_max,
                  "Minimum Temperature":temp_min,
                  "Current Temperature":temp_current
                  }
    fieldnames = ["Location","Date","Maximum Temperature","Minimum Temperature","Current Temperature"] #Keys from the dict to be plotted into csv
    user_choice = int(input("1) Save Report\n2)In-depth report\n 3) Exit"))

    if user_choice == 1:
        save_report(user_date,fieldnames,data_array)
    elif user_choice == 2:
        weather_per_hour(location_data)
    

def save_report(user_date,fieldnames,data_array): #Saves report to a csv
    user_date = user_date.replace("/","") # Removes the slash from user date used by the API link as it conflicts with file names
    with open(f"WeatherReport-{user_date}.csv","w", newline='') as f:
        writer = csv.DictWriter(f,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerow(data_array)


def weather_per_hour(location_data): #Function which provides the temperature by hour for the selected date
    for i in range(24):
        print (location_data.json()['days'][0]['hours'][0+i]["datetime"])
        print (location_data.json()['days'][0]['hours'][0+i]["temp"])




main()