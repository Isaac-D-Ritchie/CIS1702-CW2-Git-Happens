import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

# creates root window
root = tk.Tk(screenName="Weather Report Generator", baseName="Weather Report Generator", className="Weather Report Generator")
root.geometry("450x300")

#creates variables for dropdown menus

hours = ("00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", 
         "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", 
         "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", )

#creates grid weights for easier placement of widgets

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)


#function for generating basic report

def basic_report():
    location = location_entry.get()
    date = date_entry.get()
    hour = hour_dropdown.get()
    if (check_state.get() == 0):
        messagebox.showinfo(title="Basic Weather Report", message=f"The weather in {location} on {date} will be xyz")
    else:
        messagebox.showinfo(title="Basic Weather Report", message=f"The weather in {location} on {date} at {hour} will be xyz")

#function for generating a detailed report

def detailed_report():
    location = location_entry.get()
    date = date_entry.get()
    hour = hour_dropdown.get()
    if (check_state.get() == 0):
        messagebox.showinfo(title="Detailed Weather Report", message=f"A more detailed report of\n the weather in {location} on {date} would be xyz")
    else:
        messagebox.showinfo(title="Detailed Weather Report", message=f"A more detailed report of\n the weather in {location} on {date} at {hour} \nwould be xyz")

#function to determine whether the hour dropdown menu should be enabled or disabled

def hour_dropdown_check():
    if (check_state.get() == 0):
        hour_dropdown.configure(state="disabled")
    else:
        hour_dropdown.configure(state="enabled")

#function to add widgets and appropriate button when the user wishes to make a comparison

def comparison_ui_change():
    if radio_variable.get()==2:
        print("FUNCTION UNDER CONSTRUCTION")
    else:
        print("FUNCTION STILL UNDER CONRSTRUCTION")

# creates labels so user knows where to inpurt data

location_label = Label(root, text="Please enter a location:")
date_label = Label(root, text="Please enter a date (YYYY-MM-DD):")
hour_label = Label(root, text="Add an hour?")
comparison_label = Label(root, text="Would you like to do a comparison?")

#creates widgets to take data inputs from the user

location_entry = Entry(root)
date_entry = Entry(root)

#creates checkbox and listbox for hour values

check_state = tk.IntVar()
hour_checkbox = Checkbutton(root, variable=check_state, onvalue=1, offvalue=0, command=hour_dropdown_check)
hour_dropdown = ttk.Combobox(root, values=hours, state=DISABLED)
hour_dropdown.set("Please select an hour")

#creates button to generate report

report_btn = Button(root, text="Generate Report", command=basic_report)
detailed_report_btn = Button(root, text="Generate In-Depth Report", command=detailed_report)

#creates radio buttons so the user can choose to compare

radio_variable = IntVar()
radio_variable.set(1)

radio_no = Radiobutton(root, text="No", variable=radio_variable, value=1, command=comparison_ui_change)
radio_yes = Radiobutton(root, text="Yes", variable=radio_variable, value=2, command=comparison_ui_change)

#grid to arrange labels, buttons, entries and checkboxes

location_label.grid(row=0, column=0, pady=2, padx=2, sticky=tk.W+tk.E)
date_label.grid(row=1, column=0, pady=2, padx=2, sticky=tk.W+tk.E)
hour_label.grid(row=2, column=0, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
comparison_label.grid(row=3, column=0, pady=13, padx=2, sticky=tk.W+tk.E+tk.N )

location_entry.grid(row=0, column=1, pady=2, padx=2, sticky=tk.W+tk.E)
date_entry.grid(row=1, column=1, pady=2, padx=2, sticky=tk.W+tk.E)
hour_checkbox.grid(row=2, column=0, pady=2, padx=2, sticky=tk.E+tk.N)
hour_dropdown.grid(row=2, column=1, pady=2, padx=2, sticky=tk.N)
radio_yes.grid(row=3, column=1, sticky=tk.N+tk.W)
radio_no.grid(row=3, column=1, pady=25, sticky=tk.N+tk.W)

report_btn.grid(row=4, column=0, sticky=tk.S+tk.W+tk.E)
detailed_report_btn.grid(row=4, column=1, sticky=tk.S+tk.W+tk.E)

# tkinter event loop
root.mainloop()
