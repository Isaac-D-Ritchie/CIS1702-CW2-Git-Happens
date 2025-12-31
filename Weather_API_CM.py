import csv
import requests
import json



# REQUEST BASE URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
api_key = 'KCKABDK2BGULHK7UBHZDEFZ28'

# Main code for program
def main():
    while True:
        print("===Weather Data API Menu===\n")
        userLocation = input("Enter a Location\n")
        userConfirm = input(f"Location = {userLocation}\nWould you like to continue? (yes/no)")

        if userConfirm == "yes":
            locationData = getLocationData(userLocation,api_key)
            maxTemp,minTemp = getWeatherData(locationData)
            weatherReport(userLocation, maxTemp, minTemp)


def getLocationData(userLocation,api_key):
    locationData = requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{userLocation}?unitGroup=uk&key=KCKABDK2BGULHK7UBHZDEFZ28&contentType=json')
    return locationData


def getWeatherData(locationData):
    print(locationData.status_code)
    if locationData.status_code == 200:
        locationTable = locationData.json()
        maxTemp = locationTable['days'][0]['tempmax']
        minTemp = locationTable['days'][0]['tempmin']
        
        return maxTemp, minTemp

def weatherReport(userLocation, maxTemp, minTemp):
    print(f"======={userLocation}=====")
    print(f"Maximum temperature = {maxTemp:.2f}")
    print(f"Minimum Temperature = {minTemp:.2f}") 
    print("===========================")
    dictionary = {"Location": userLocation, "Maximum Temperature" : maxTemp, "Minimum Temperature" : minTemp }
    decision2 = input("Would you like to save the weather report? (yes/no)")
    if decision2 == "yes":
        saveWeatherReport(dictionary, userLocation)
    else:
        exit()  

# Function to save weather report as CSV
def saveWeatherReport(dictionary,userLocation):
    with open(f'{userLocation}_weather_report.csv', mode='w', newline='') as file:
        fieldnames = ['Location', 'Maximum Temperature', 'Minimum Temperature']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(dictionary)
    print(f"Weather report saved as {userLocation}_weather_report.csv")



main()