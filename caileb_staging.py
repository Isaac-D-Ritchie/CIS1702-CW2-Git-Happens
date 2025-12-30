import datetime as dt
from datetime import timedelta
import json
import urllib.request
import statistics 
###create log class Maybe?

###Class for all API Handling
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
        #Index is the iterator in self.api_data list of pairs.
        if index >= len(self.api_data):
            print("CRITICAL ERROR: ALL API CONNECTION DATA FAILED, EXITING") #!! And Log
            return backout()
        
        #baseurl & key are assigned to each item in pair at 'index' in self.api_data's list
        baseurl, key = self.api_data[index]
        
        full_url = f"{baseurl}?q={self.city}&units={self.units}&appid={key}" # Defines full url
        
        if (index + 1) % 2 == 0:
            print(f"Attempt {index + 1}: Connecting to {baseurl} (Backup Key)") #A
        else:
            print(f"Attempt {index + 1}: Connecting to {baseurl} (Primary Key)") #B
        #!! And Log A/B's Step
        
        try:
            with urllib.request.urlopen(full_url, timeout=10) as response:
                if response.status == 200:
                    print("Connection successful!") #!! And Log 
                    return json.load(response) 
                
        #Recursive step given failed connection
        except Exception as e:
            print(f"Error: {e}\nAttempt {index+1} failed, Trying next option...")#!! And Log
            return self.connect(index+1)

###Class for Date and Time utility
class TimeBreak:
    def __init__(self):
        #CREATE CALLABLE LOG TO STATE USAGE OF ELEMENTS IN TIMEBREAK CLASS

        #Declare now, default formatting is something like "DD-MM-YYY HH:MM:SS"
        now = dt.datetime.now()

        #Declare time as it's components via datetime
        self.year = str(now.year)
        self.month = str(now.month)
        self.day = str(now.day)
        self.hour = str(now.hour)
        self.minute = str(now.minute)

        #Date of report stored in terminal and in report file when saved.
        self.reporting_date = f"{self.day}/{self.month}"

        #Timestamp for appendment, can be stored in logs, in the report file as some sort of metadata, non-intrusive between saved report fields.
        self.filestamp = f"|{self.day}/{self.month}/{self.year} - {self.hour}:{self.minute}|"

        #nexday function recursively saves dates into a list then returns date list when index reaches 0.
        #Needs testing on a weekly report function, and may need changing depending on whether index(whichweek from flow) is 7 or -7
        def nextday(self, index):
            date_list = []
            for i in range(index + 1):
                next_date = self.now + timedelta(days=i)
                date_list.append(next_date.strftime("%d/%m"))
            return date_list
        

###Data Handling Class for fetching data, Organising data to our needs and data analysis.
#We may have to massage data when asked to save depending on the required filetype, this would also be stored in the Handling class.
#Probably best leaving the reporting in local functions
 
###Misc Functions and Variables that are useful globally

#Report & Menu Title formatting Lambda where x is the title
titleprint = lambda x: "\n"*10 + "="*25 + f"\n {x}\n" + "="*25 + "\n"*2
#Api Handler Lambda where x is city
handler = lambda x: WeatherAPIHandler(x, "metric")

#Returns to the previous Menu/Function
def backout():#!! And Log
    print("Backing Out...\n",("="*25),("\n"*5))
    #Could be worth including some logging here



# MENU FUNCTIONS

#24 Hour Weather Report, One Location, "Simple" & "Detailed" Reporting
def one_day_data():#!! And Log

    print(titleprint('24 Hour Weather Reporting'),"If you're here by accident please type 'quit' in the next prompt\n")

    try:
        city = input("Enter City name: ")
        if city.lower() == 'quit':
            return backout()
        
        time = TimeBreak()
        #Calls Lambda function from Misc Functions
        data = handler(city).connect()

    except Exception as e:
        print(f"\nError occurred:{e}") #!! And Log
        backout()

    if not data:
        print("Error: Could not retrieve data.") #!! And Log
        return backout()

    # Calls first 8 Fields of Forecast. 3 Hour Data * 8 = 24 Hours
    try:
        next_24h = data['list'][:8] #!! And Log
    except:
        #!!Need to do something here
        print(data) #!! And Log

    print("\nSelect Report Level:")
    print("1. Simple (Summary)")
    print("2. Detailed (Hourly Table)")
    print("3. Back to Menu\n")
    choice = input("Selection: ")
    
    if choice == "1":
        # Simple Report
        # next_24h has 8 fields, with various pairs of data, e.g. ('Temp','12.6')
        try:
            temps = [item['main']['temp'] for item in next_24h] 
            conditions = [item['weather'][0]['main'] for item in next_24h]
        except Exception as e:
            print(f"Error Occured:{e}")#!! And Log
            return backout()

        #DATA ANALYSIS

        # 'pop' is probability of precipitation (0.0 to 1.0) 
        rain_chance = next_24h[0].get('pop', 0) * 100 #!! And Log?
        #Calc Mean Temp
        avg_temp = sum(temps) / len(temps) #!! And Log?
        #Calc Mode Temp
        most_common_weather = statistics.mode(conditions) #!! And Log?

        #Simple Reporting Printing
        try:
            print(f"\n--- Summary for {city.title()} -- Date: {time.reporting_date} ---")
            print(f"Average Temp: {avg_temp:.1f}°C")
            print(f"High/Low:     {max(temps)}°C / {min(temps)}°C")
            print(f"Main Weather: {most_common_weather}")
        
            # Rain Bar Chart  '*' = 5%
            stars = "*" * int(rain_chance / 5)
            print(f"Rain Chance:  [{stars:<20}] {rain_chance:.1f}%")
            #!! And Log
            postrepnav()
            return backout()

        except Exception as e:
            print(f"Error Occurred:{e}") #!! And Log
            backout() 


    elif choice == "2":
        #Detailed Reporting Printing
        try:
            print(f"\n---Detailed Forecast for {city.title()} -- Date: {time.reporting_date} ---")
            print(f"\n{'Time':<8} | {'Temperature':<10} | {'Weather':<12} | {'WindSpeed':<8} | {'Humidity'}")
            print("-" * 60)
            #Prints Iterates through 3 hour intervals
            for hour in next_24h:
                if time.hour + dt.timedelta(hour,-1) > time.hour:
                    print("\nNew day:",(time.reporting_date + dt.timedelta(time.day,+1)), "Continuing...")

                # Slices "2025-12-21 15:00:00" into "15:00" on time_label
                time_label = hour['dt_txt'][11:16]
                temp = hour['main']['temp']
                weather = hour['weather'][0]['main']
                wind = hour['wind']['speed']
                humid = hour['main']['humidity']
                
                print(f"{time_label:<8} | {(temp,'°C'):<10} | {weather:<12} | {wind:<8} | {humid}%")
                #!! And Log
                postrepnav()
                return backout()
                

        except Exception as e:
            print(f"Error Occurred:{e}")#!! And Log
            return backout()


    elif choice == "3":
        return backout()
    

def week_data():#!! And Log
    #menu print
    city = input("CITY NAME:")
    whichweek = input("Which Week's Data\n1. Last 7 Days\n2. Next 7 Days")
    if whichweek == "1":
        whichweek = int(-7)
    elif whichweek == "2":
        whichweek = int(7)
    TimeBreak.nextday()
    #call timebreak with whichweek to find list_dates
    #fetch json data from api using city and list_dates
    #input for type of report (simple/indepth)
    #write "functions" to generate both simple and indepth reporting
    #simple includes "Hottest day", "Sunniest Day", "Coldest Day", "Wettest Day", "Windiest Day"
    #"Highs and Lows", "Averages of each day"
    #in-depth returns a table of Averages for each day, highs and lows of each day, (Similar to one day data)


def compare_cities():#!! And Log
    #menu print
    #give asks user for number of cities to compare, max 5
    pass


#MAIN MENU
def weather_menu():
    """Main Navigation Menu"""
    while True:
        print(titleprint('Weather System Menu'))
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
                print("Invalid input. Try again.")#!! And Log
        except Exception as e:
            print(e,"Silly guy!")#!! And Log
            return backout()

#SAVE REPORT DATA
def save_data(printreport):
    filetype = input("Please Enter Filetype you wish to save to ('txt','csv','json')")
    try:
        pass
        #with open f"report.{filetype} 'append' as updatereport
        #updatereport.append("\n",printreport)
    except Exception as e:
        return backout()
        #print exceptions and log them also
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
        
        #Could use SQLlite implementation to sort our data locally for reporting, was an idea thrown around by a friend in industry, 
        # it's core python library and should only be worked on if everything else is done.
    
- MENU FUNCTIONS TO BE BUILT
    Compare Cities Function 
    Week Data Function 
    Save to JSON, TXT, CSV
-"""
