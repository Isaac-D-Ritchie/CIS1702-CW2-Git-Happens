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
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)
root.rowconfigure(7, weight=1)

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

#function for generating a comparison report

def comparison_report():
    location = location_entry.get()
    date = date_entry.get()
    hour = hour_dropdown.get()
    comp_location = comparison_location_entry.get()
    comp_date = comparison_date_entry.get()
    comp_hour = comparison_hour_dropdown.get()
    if (check_state.get() == 0) and (comp_check_state.get() == 0):
        messagebox.showinfo(title="Comparison Weather Report", message=f"The weather in {location} on {date} is be xyz, whereas the weather in {comp_location} on {comp_date} is xyz")
    elif (check_state.get() == 1) and (comp_check_state.get() == 0):
        messagebox.showinfo(title="Comparison Weather Report", message=f"The weather in {location} on {date} at {hour} is be xyz, whereas the weather in {comp_location} on {comp_date} is xyz")
    elif (check_state.get() == 0) and (comp_check_state.get() == 1):
        messagebox.showinfo(title="Comparison Weather Report", message=f"The weather in {location} on {date} is be xyz, whereas the weather in {comp_location} on {comp_date} at {comp_hour} is xyz")
    elif (check_state.get() == 1) and (comp_check_state.get() == 1):
        messagebox.showinfo(title="Comparison Weather Report", message=f"The weather in {location} on {date} at {hour} is be xyz, whereas the weather in {comp_location} on {comp_date} at {comp_hour} is xyz")

#function to determine whether the hour dropdown menu should be enabled or disabled

def hour_dropdown_check():
    if (check_state.get() == 0):
        hour_dropdown.configure(state="disabled")
    elif (check_state.get() == 1):
        hour_dropdown.configure(state="enabled")
    
def comp_hour_dropdown_check():
    if (comp_check_state.get() == 0):
        comparison_hour_dropdown.configure(state="disabled")
    elif (comp_check_state.get() == 1):
        comparison_hour_dropdown.configure(state="enabled")

#function to add+arrange widgets and appropriate button when the user wishes to make a comparison

def comparison_ui_change():    
    if radio_variable.get()==2:
        report_btn.grid_remove()
        detailed_report_btn.grid_remove()
        
        comparison_report_btn.grid(row=8, column=0, columnspan=2, sticky=tk.E+tk.W+tk.S)
        
        comparison_location_label.grid(row=5, column=0, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
        comparison_location_entry.grid(row=5, column=1, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
        
        comparison_date_label.grid(row=6, column=0, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
        comparison_date_entry.grid(row=6, column=1, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)

        comparison_hour_label.grid(row=7, column=0, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
        comparison_hour_checkbox.grid(row=7, column=0, pady=2, padx=2, sticky=tk.E+tk.N)
        comparison_hour_dropdown.grid(row=7, column=1, pady=2, padx=2, sticky=tk.N)
        
        
    else:
        report_btn.grid()
        detailed_report_btn.grid()
        comparison_report_btn.grid_remove()
        comparison_location_label.grid_remove()
        comparison_location_entry.grid_remove()
        comparison_date_label.grid_remove()
        comparison_date_entry.grid_remove()
        comparison_hour_label.grid_remove()
        comparison_hour_checkbox.grid_remove()
        comparison_hour_dropdown.grid_remove()

# creates labels so user knows where to inpurt data

location_label = Label(root, text="Please enter a location:")
date_label = Label(root, text="Please enter a date (YYYY-MM-DD):")
hour_label = Label(root, text="Add an hour?")

comparison_label = Label(root, text="Would you like to do a comparison?")

comparison_location_label = Label(root, text="Please enter a location:")
comparison_date_label = Label(root, text="Please enter a date (YYYY-MM-DD):")
comparison_hour_label = Label(root, text="Add an hour?")

#creates widgets to take data inputs from the user

location_entry = Entry(root)
date_entry = Entry(root)

comparison_location_entry = Entry(root)
comparison_date_entry = Entry(root)

#creates checkbox and listbox for hour values

check_state = tk.IntVar()
hour_checkbox = Checkbutton(root, variable=check_state, onvalue=1, offvalue=0, command=hour_dropdown_check)
hour_dropdown = ttk.Combobox(root, values=hours, state=DISABLED)
hour_dropdown.set("Please select an hour")

comp_check_state= tk.IntVar()
comparison_hour_checkbox = Checkbutton(root, variable=comp_check_state, onvalue=1, offvalue=0, command=comp_hour_dropdown_check)
comparison_hour_dropdown = ttk.Combobox(root, values=hours, state=DISABLED)
comparison_hour_dropdown.set("Please select an hour")

#creates button to generate report

report_btn = Button(root, text="Generate Report", command=basic_report)
detailed_report_btn = Button(root, text="Generate In-Depth Report", command=detailed_report)
comparison_report_btn = Button(root, text="Compare These Two Reports", command=comparison_report)

#creates radio buttons so the user can choose to compare

radio_variable = IntVar()
radio_variable.set(1)

radio_no = Radiobutton(root, text="No", variable=radio_variable, value=1, command=comparison_ui_change)
radio_yes = Radiobutton(root, text="Yes", variable=radio_variable, value=2, command=comparison_ui_change)

#grid to arrange labels, buttons, entries and checkboxes

location_label.grid(row=0, column=0, pady=2, padx=2, sticky=tk.W+tk.E)
date_label.grid(row=1, column=0, pady=2, padx=2, sticky=tk.W+tk.E)
hour_label.grid(row=2, column=0, pady=2, padx=2, sticky=tk.W+tk.E+tk.N)
comparison_label.grid(row=3, column=0, pady=13, padx=2, sticky=tk.W+tk.E+tk.N)
comparison_location_label.grid_remove()
comparison_date_label.grid_remove()
comparison_hour_label.grid_remove()

location_entry.grid(row=0, column=1, pady=2, padx=2, sticky=tk.W+tk.E)
date_entry.grid(row=1, column=1, pady=2, padx=2, sticky=tk.W+tk.E)
hour_checkbox.grid(row=2, column=0, pady=2, padx=2, sticky=tk.E+tk.N)
hour_dropdown.grid(row=2, column=1, pady=2, padx=2, sticky=tk.N)
comparison_location_entry.grid_remove()
comparison_date_entry.grid_remove()

radio_yes.grid(row=3, column=1, sticky=tk.N+tk.W)
radio_no.grid(row=3, column=1, pady=25, sticky=tk.N+tk.W)

report_btn.grid(row=8, column=0, sticky=tk.S+tk.W+tk.E)
detailed_report_btn.grid(row=8, column=1, sticky=tk.S+tk.W+tk.E)
comparison_report_btn.grid_remove()

# tkinter event loop
root.mainloop()
