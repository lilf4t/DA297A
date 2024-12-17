# What can a patient do?
# ----------------------
# 1. Sign up for the health center by entering their  first name, last name, gender (F, M or NB), address, phone nr, birthdate (registration date should be recorded) (can only sign up once, so patient id should be unique)
# 2. See all their info and edit the information except for Patient ID and registration date.
# 3. Book an appointment for a specific doctor. They should see a list of all doctors, their specilization and visit cost. See the available days and times for visiting the doctor and then book the appointment. (booking can only be made on a friday of the week for the coming week, should be changeable) 
# 4. View their medical record (see all diagnosis and prescription) for each previous visit.
# ----------------------

import psycopg
import tkinter as tk
from tkinter import ttk, messagebox


# Databas konfiguration
db_config = {
    'host': 'pgserver.mau.se',
    'dbname': 'health_center_group21',  # Databas namn
    'user': 'an4263',   # Databas användarnamn, laila: an4952, fatima: an4263
    'password': '2ecfcvkm',  # Lösenord, laila: 50owi0jd, fatima: 2ecfcvkm
    'port': 5432
}

#Patient GUI
def show_patient_gui(root):
    patient_window = tk.Toplevel(root)
    patient_window.title("Patient View")
    patient_window.configure(bg='lightblue')


    #Fixa kod här för patient