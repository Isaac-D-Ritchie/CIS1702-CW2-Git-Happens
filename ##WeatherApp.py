#WeatherApp
# API KEY = 247BUSAAULFLBGWM7NVZ49M4B
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
        if user_choice == "y":
            location_data = requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{user_location}/{user_date}/?key={api_key}')
            weather_values(location_data,user_location,user_date)
                
def farenheit_to_celcius(farenheit): #Visual Crossing API provides farenheit values
    celcius = (farenheit - 32) / 1.8
    return celcius
    
def weather_values(location_data,user_location,user_date):
    Tempcurrent = farenheit_to_celcius(location_data.json()['days'][0]['temp']) #Parsing data from the API
    Tempmax = farenheit_to_celcius(location_data.json()['days'][0]['tempmax'])
    Tempmin = farenheit_to_celcius(location_data.json()['days'][0]['tempmin'])
    if user_date is "":
        weather_desc = location_data.json()['description'] #Description can only be retrieved for the current weather? API Issue
    print(f"=========={user_location}=={user_date}==========")
    try:
        print(weather_desc)#Only prints weather description when available
    except:
        print("No available description")
    print(f"Maximum temperature is {Tempmax:.2f} C")
    print(f"Minimum temperature is {Tempmin:.2f} C")
    print(f"Current temperature is {Tempcurrent:.2f} C")
    print("===============================")
    data_array = {f"Location":user_location,
                  "Date":user_date,
                  "Maximum Temperature":Tempmax,
                  "Minimum Temperature":Tempmin,
                  "Current Temperature":Tempcurrent
                  }
    fieldnames = ["Location","Date","Maximum Temperature","Minimum Temperature","Current Temperature"] #Keys from the dict to be plotted into csv
    user_choice = int(input("1) Save Report\n 2) Change Date\n 3) Change Location")) #2,3 WIP

    if user_choice == 1:
        save_report(user_date,fieldnames,data_array)



def save_report(user_date,fieldnames,data_array): #Saves report to a csv
    with open(f"WeatherReport-{user_date}.csv","w", newline='') as f:
        writer = csv.DictWriter(f,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerow(data_array)

main()