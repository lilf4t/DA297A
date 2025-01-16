import psycopg
import tkinter as tk
from tkinter import ttk

# @author: Fatima Kadum

db_config = {
    'host': 'pgserver.mau.se',
    'dbname': 'health_center_group21',  #Namn på ditt databas
    'user': '',   #Ditt databas username
    'password': '',  #Password
    'port': 5432
}

def show_history_log(root):
    history_log_window = tk.Toplevel(root)
    history_log_window.title("Appointments history log")
    history_log_window.geometry("1500x500")
    
    tree = ttk.Treeview(history_log_window, columns=("Log ID", "Doctor ID", "Doctor Name", 
                                                   "Action Type", "Action Time", "Patient Name",
                                                   "Booking Date", "Time Slot"))
    
    tree.column("Log ID", width=100)
    tree.column("Doctor ID", width=100)
    tree.column("Doctor Name", width=100)
    tree.column("Action Type", width=100)
    tree.column("Action Time", width=100)
    tree.column("Patient Name", width=100)
    tree.column("Booking Date", width=100)
    tree.column("Time Slot", width=100)
    
    tree.heading("Log ID", text="Log ID")
    tree.heading("Doctor ID", text="Doctor ID")
    tree.heading("Doctor Name", text="Doctor Name")
    tree.heading("Action Type", text="Action Type")
    tree.heading("Action Time", text="Action Time")
    tree.heading("Patient Name", text="Patient Name")
    tree.heading("Booking Date", text="Booking Date")
    tree.heading("Time Slot", text="Time Slot")
    
    tree['show'] = 'headings'
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    refresh_button = tk.Button(history_log_window, text="Refresh", command=lambda: show_history_log(root))
    refresh_button.pack(pady=10)

    try:
        conn = psycopg.connect(**db_config)
        with conn.cursor() as curr:
            curr.execute("""SELECT historylog.log_id, 
                             historylog.doc_id, 
                             CONCAT(doctors.f_name, ' ', doctors.l_name) as doctor_name,
                             historylog.action_type, historylog.action_time, 
                             CONCAT(patients.f_name, ' ', patients.l_name) as patient_name,
                             doctoravailability.booking_date, doctoravailability.time_slot
                             FROM historylog 
                             JOIN patients ON historylog.pat_id = patients.pat_id
                             JOIN doctors ON historylog.doc_id = doctors.doc_id
                             JOIN doctoravailability ON historylog.doc_availability_id = doctoravailability.doc_availability_id
                             ORDER BY historylog.log_id DESC, doctoravailability.time_slot ASC""")
            records = curr.fetchall()
            if not records:
                tk.messagebox.showinfo("Info", "No appointments found in the history log.")
            for record in records:
                tree.insert('', 'end', values=record)
    finally:
        if conn is not None:
            conn.close()

