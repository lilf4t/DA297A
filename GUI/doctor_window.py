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

# Databas konfiguration
db_config = {
    'host': 'pgserver.mau.se',
    'dbname': 'health_center_group21',  # Databas namn
    'user': 'an4263',   # Databas användarnamn, laila: an4952, fatima: an4263
    'password': '2ecfcvkm',  # Lösenord, laila: 50owi0jd, fatima: 2ecfcvkm
    'port': 5432
}

#Doctor GUI
def show_doctor_gui(root, doctor_id):
    doctor_window = tk.Toplevel(root)
    doctor_window.title("Doctor View")
    doctor_window.configure(bg='lightblue')
    
    # Visa ID och namn för läkaren
    try:
        conn = psycopg.connect(**db_config)
        with conn.cursor() as curr:
            curr.execute("SELECT f_name, l_name FROM doctors WHERE doc_id = %s", (doctor_id,))
            doctor_info = curr.fetchone()
            if doctor_info:
                text = f"Doctor ID: {doctor_id}, Name: {doctor_info[0]} {doctor_info[1]}"
    finally:
        if conn is not None:
            conn.close()
            
    label = tk.Label(doctor_window, text=text, bg='lightblue')
    label.pack(pady=10)
    
    # Tabs
    notebook = ttk.Notebook(doctor_window)
    notebook.pack(fill=tk.BOTH, expand=True)

    doctor_frame = tk.Frame(notebook, bg='lightblue')
    patient_frame = tk.Frame(notebook, bg='lightblue')
    notebook.add(doctor_frame, text="Main tab") # Main tab
    notebook.add(patient_frame, text="Schedule") # Läkarens schema
    
    # Lägga till tillgänglighet i schemat
    def add_availability():
        day = day_var.get()
        time = time_var.get()
        date = date_entry.get()
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                # Kolla ifall slot är available eller booked
                curr.execute("""
                    SELECT * FROM doctoravailability 
                    WHERE doc_id = %s AND day_of_week = %s 
                    AND time_slot = %s AND booking_date = %s
                """, (doctor_id, day, time, date))
                
                if curr.fetchone():
                    messagebox.showerror("Error", "This time slot is already defined!")
                    return
                
                # Lägg till ny availability med dag, tid och datum
                curr.execute("""
                    INSERT INTO doctoravailability (doc_id, day_of_week, time_slot, booking_date)
                    VALUES (%s, %s, %s, %s)
                """, (doctor_id, day, time, date))
                conn.commit()
                messagebox.showinfo("Success", "Availability added!")
                show_appointments()  # Refresha listan
        finally:
            if conn is not None:
                conn.close()
                
    def remove_availability():
        day = day_var.get()
        time = time_var.get()
        date = date_entry.get()
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""
                    DELETE FROM doctoravailability 
                    WHERE doc_id = %s AND day_of_week = %s 
                    AND time_slot = %s AND booking_date = %s
                """, (doctor_id, day, time, date))
                conn.commit()
                messagebox.showinfo("Success", "Availability removed!")
                show_appointments()  # Refresha listan
        finally:
            if conn is not None:
                conn.close()

    def show_appointments():
        appointments_list.delete(0, tk.END)
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""
                    SELECT day_of_week, time_slot, pat_id, booking_date 
                    FROM doctoravailability 
                    WHERE doc_id = %s 
                    ORDER BY booking_date, time_slot
                """, (doctor_id,))
                appointments = curr.fetchall()
                
                for day, time, pat_id, date in appointments:
                    status = "BOOKED" if pat_id else "AVAILABLE"
                    appointments_list.insert(tk.END, 
                        f"Day: {day}, Time: {time}, Status: {status}, Date: {date}")
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()
                        
    # Labels, frames, knappar för schemat
    availability_frame = tk.Frame(patient_frame, bg='lightblue')
    availability_frame.pack(pady=10)

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = ['09:00', '09:30', '10:00', '10:30']

    day_var = tk.StringVar(value=days[0]) # Välj den första dagen
    time_var = tk.StringVar(value=times[0]) # Välj den första tiden

    tk.Label(availability_frame, text="Day:", bg='lightblue').pack(side=tk.LEFT)
    day_menu = tk.OptionMenu(availability_frame, day_var, *days)
    day_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(availability_frame, text="Time:", bg='lightblue').pack(side=tk.LEFT)
    time_menu = tk.OptionMenu(availability_frame, time_var, *times)
    time_menu.pack(side=tk.LEFT, padx=5)

    tk.Label(availability_frame, text="Date (YYYY-MM-DD):", bg='lightblue').pack(side=tk.LEFT)
    date_entry = tk.Entry(availability_frame)
    date_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(availability_frame, text="Add Availability", 
              command=add_availability).pack(side=tk.LEFT, padx=5)
    
    tk.Button(availability_frame, text="Remove Availability", 
              command=remove_availability).pack(pady=5)
    
    # Visar the appointments list
    tk.Label(patient_frame, text="Appointments:", bg='lightblue').pack(pady=5)
    appointments_list = tk.Listbox(patient_frame, width=50, height=10)
    appointments_list.pack(pady=5)

    tk.Button(patient_frame, text="Refresh Appointments", 
              command=show_appointments).pack(pady=5)

    # Visar appointments från början
    show_appointments()
    
    
