# What can a doctor do?
# ----------------------
# 1. Define their availabilty for each day of the week and time between 09:00-10:30 (can define/change their availability only if there is no booked appointment)
# 2. See a list of all upcoming appointments
# 3. See a list of all medical record related to a specific patient
# 4. Add a medical record for a specific patient (diagnosis, prescription)
# ----------------------


import psycopg
import tkinter as tk
from tkinter import ttk, messagebox


db_config = {
    'host': 'pgserver.mau.se',
    'dbname': 'health_center_group21',  #Namn på ditt databas
    'user': 'an4263',   #Ditt databas username, laila:an4952, fatima:an4263
    'password': '2ecfcvkm',  #Password, laila:50owi0jd, fatima:2ecfcvkm
    'port': 5432
}


#Doctor GUI
def show_doctor_gui(root):
    admin_window = tk.Toplevel(root)
    admin_window.title("Doctor View")
    admin_window.configure(bg='lightblue')


    #Fixa kod här för Doctor
