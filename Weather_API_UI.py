import tkinter as tk
from tkinter import *
from tkinter import messagebox

# creates root window
root = tk.Tk(screenName="Weather Report Generator", baseName="Weather Report Generator", className="Weather Report Generator")
root.geometry("450x300")

#creates grid weights for easier placement of widgets

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)

#function for generating basic report

def basic_report():
    location = location_entry.get()
    date = date_entry.get()
    messagebox.showinfo(title="Basic Weather Report", message=f"The weather in {location} on {date} will be xyz")

#function for generating a detailed report

def detailed_report():
    location = location_entry.get()
    date = date_entry.get()
    messagebox.showinfo(title="Detailed Weather Report", message=f"A more detailed report of\n the weather in {location} on {date} would be xyz")

# creates labels so user knows where to inpurt data

location_label = Label(root, text="Please enter a location:")
date_label = Label(root, text="Please enter a date (YYYY-MM-DD):")

#creates entries to take data inputs from the user

location_entry = Entry(root)
date_entry = Entry(root)

#creates button to generate report

report_btn = Button(root, text="Generate Report", command=basic_report)
detailed_report_btn = Button(root, text="Generate In-Depth Report", command=detailed_report)

#grid to arrange labels, buttons, entries and checkboxes

location_label.grid(row=0, column=0, pady=2, padx=2, sticky=tk.W+tk.E)
date_label.grid(row=1, column=0, pady=2, padx=2, sticky=tk.W+tk.E)

location_entry.grid(row=0, column=1, pady=2, padx=2, sticky=tk.W+tk.E)
date_entry.grid(row=1, column=1, pady=2, padx=2, sticky=tk.W+tk.E)

report_btn.grid(row=2, column=0, sticky=tk.S+tk.W+tk.E)
detailed_report_btn.grid(row=2, column=1, sticky=tk.S+tk.W+tk.E)

# tkinter event loop
root.mainloop()