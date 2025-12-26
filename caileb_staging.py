import datetime as dt
from datetime import timedelta
import json
import urllib.request
import statistics 

#Class to handle API Connections, Retrievals and ULL Requests
class WeatherAPIHandler:
    def __init__(self, city, units):
        self.city = city.replace(" ", "%20")
        self.units = units
    
        # API URLS AND KEYS
        self.api_data = [
            ("https://api.openweathermap.org/data/2.5/forecast", "54bb47ed4ca69c0d0ca37bcb79711b5f"), # OWM Primary
            ("https://api.openweathermap.org/data/2.5/forecast", "011d9bcc33d58317a8ca04ae04c52d91"), # OWM Backup
            ("https://backupapi.example.com/data", "fillerkey1234"),# Backup API Primary
            ("https://backupapi.example.com/data", "anotherfillerkey5678")# Backup API Backup
            ]
        
    def connect(self, index = 0):
        #Index is the iterator in list self.api_data and when end of list is spotted no connection found.
        if index >= len(self.api_data):
            print("CRITICAL ERROR: ALL API CONNECTION DATA FAILED, EXITING") #LOG
            return None
        
        baseurl, key = self.api_data[index] #Var A & B share out paired items in I's point in the list of pairs
        
        full_url = f"{baseurl}?q={self.city}&units={self.units}&appid={key}" # Defines full url when called upon.
        
        if (index + 1) % 2 == 0:
            print(f"Attempt {index + 1}: Connecting to {baseurl} (Backup Key)") #LOG
        else:
            print(f"Attempt {index + 1}: Connecting to {baseurl} (Primary Key)") #LOG
        
        try:
            with urllib.request.urlopen(full_url, timeout=10) as response:
                if response.status == 200:
                    print("Connection successful!") #LOG 
                    return json.load(response) #LOG
        except Exception as e: #Recursive step given failed connection
            print(f"Error: {e}\nAttempt {index+1} failed, Trying next option...")#LOG
            return self.connect(index+1) #LOG
#! TB = Testing TimeBreak
class TimeBreak:
    def __init__(self):
        now = dt.datetime.now()

        #broken up time
        self.year = str(now.year)
        self.month = str(now.month)
        self.day = str(now.day)
        self.hour = str(now.hour)
        self.minute = str(now.minute)

        self.reporting_date = f"{self.day}/{self.month}" # in terminal reporting
        self.filestamp = f"|{self.day}/{self.month}/{self.year} - {self.hour}:{self.minute}|" # For new entry appended to Reporting file

        def nextday(self, index): # Recursive function to return list of dates to use for fetching data from API
            date_list = []
            for i in range(index + 1):
                next_date = self.now + timedelta(days=i)
                date_list.append(next_date.strftime("%d/%m"))
            return date_list
 

        
def backout():
    print("Backing Out...\n",("="*25),("\n"*5))
    #LOG
# MENU FUNCTIONS

def one_day_data():
    """One Day Data for One City and Offers Report Type"""
    try:
        city = input("Enter City name: ")
        handler = WeatherAPIHandler(city, "metric")
        time = TimeBreak()
        data = handler.connect()
    except Exception as e:
        print(f"\nError occurred:{e}") #LOG
        backout()

    if not data:
        print("Error: Could not retrieve data.") #LOG
        return

    # Take first 8 items of forecast
    try:
        next_24h = data['list'][:8] #LOG
    except:
        print(data) #LOG

    print("\nSelect Report Level:")
    print("1. Simple (Summary)")
    print("2. In-Depth (Hourly Table)")
    print("3. Back to Menu")
    choice = input("Selection: ")
    
    if choice == "1":
        # Simple Report
        # next_24h has 8 items, temps and conditions stores 8 item list of values
        try:
            temps = [item['main']['temp'] for item in next_24h] 
            conditions = [item['weather'][0]['main'] for item in next_24h]
        except Exception as e:
            print(f"Error Occured:{e}")#LOG
            backout()
        # 'pop' is probability of precipitation (0.0 to 1.0) 
        rain_chance = next_24h[0].get('pop', 0) * 100 #LOG
        
        avg_temp = sum(temps) / len(temps) # simple mean #LOG
        most_common_weather = statistics.mode(conditions) #most common weather type in day #LOG

        #Simple Reporting Printing
        try:
            print(f"\n--- Summary for {city.title()} -- Date: {time.reporting_date} ---")
            print(f"Average Temp: {avg_temp:.1f}°C")
            print(f"High/Low:     {max(temps)}°C / {min(temps)}°C")
            print(f"Main Weather: {most_common_weather}")
        
            # Rain Bar Chart  '*' = 5%
            stars = "*" * int(rain_chance / 5)
            print(f"Rain Chance:  [{stars:<20}] {rain_chance:.1f}%")
        except Exception as e:
            print(f"Error Occurred:{e}")#LOG
            backout() 

    elif choice == "2":
        #In-depth Reporting Printing
        try:
            print(f"\n---Detailed Forecast for {city.title()} -- Date: {time.reporting_date} ---")
            print(f"\n{'Time':<12} | {'Temp':<8} | {'Weather':<12} | {'Wind':<8} | {'Humidity'}")
            print("-" * 60)
            #Prints Iterates through 3 hour intervals
            for hour in next_24h:
                # IMPLEMENT TO FIX CONFUSING REPORTING
                #!!if int(hour[:1]) < int(hour-1[:1]) == True:
                #!!    print("Tomorrow:", TimeBreak.nextday(1))

                # Slices "2025-12-21 15:00:00" into "15:00" on time_label
                time_label = hour['dt_txt'][11:16]
                temp = hour['main']['temp']
                weather = hour['weather'][0]['main']
                wind = hour['wind']['speed']
                humid = hour['main']['humidity']
                
                print(f"{time_label:<12} | {temp:<8}°C | {weather:<12} | {wind:<8} | {humid}%")

        except Exception as e:
            print(f"Error Occurred:{e}")#LOG
            backout()

    elif choice == "3":
        return backout()
def week_data():
    city = input("CITY NAME:")
    whichweek = input("Which Week's Data\n1. Last 7 Days\n2. Next 7 Days")
    if whichweek == "1":
        whichweek = int(-7)
    elif whichweek == "2":
        whichweek = int(7)
    #call timebreak with whichweek to find list_dates
    #fetch json data from api using city and list_dates
    #input for type of report (simple/indepth)
    #write "functions" to generate both simple and indepth reporting
    #simple includes "Hottest day", "Sunniest Day", "Coldest Day", "Wettest Day", "Windiest Day"
    #"Highs and Lows", "Averages of each day"
    #in-depth returns a table of Averages for each day, highs and lows of each day, (Similar to one day data)

#MAIN MENU
def weather_menu():
    """Main Navigation Menu"""
    while True:
        print("\n" + "="*25 + "\n Weather System Menu\n" + "="*25)
        print("1. Get One Day Report")
        print("2. Quit")
        try:
            userinput = input("\nPlease enter choice: ")
            
            if userinput == "1":
                one_day_data()
            #elif userinput ==  "2":
                #week_data() BUILD MODULE
            elif userinput == "2":
                print ("Ending Session...")
                break
            else:
                print("Invalid input. Try again.")#LOG
        except Exception as e:
            print(e,"Silly guy!")#LOG
#MAIN
def main():
    weather_menu()

if __name__ == "__main__":
    main()

"""Todo:

- API CONNECTION
    Utilize Backup API from another source and hope we don't have to refactor data as it comes in.
- Error Handling for failed connections *
    Test edge cases and start logging process
- Work in API URL Parameters to save data usage *
    Location based data retrieval
    Date based data retrieval

- DATA HANDLING
    data error handling
    work on other menu functions
    Maybe refactor to sreate Data Structures for reporting functions *
        Hours of day dictionary with list HOUR: [WEATHERTYPE, TEMP, HUMIDITY, ETC]
    
- MENU FUNCTIONS TO BE BUILT
    Compare Cities Function 
    Week Data Function 
    Save to JSON, TXT, CSV
-"""
