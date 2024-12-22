# What can a doctor do?
# ----------------------
# 1. Define their availabilty for each day of the week and time between 09:00-10:30 (can define/change their availability only if there is no booked appointment) - done
# 2. See a list of all upcoming appointments - done
# 3. See a list of all medical record related to a specific patient - done
# 4. Add a medical record for a specific patient (diagnosis, prescription) - done
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

    main_tab = tk.Frame(notebook, bg='lightblue')
    schedule_tab = tk.Frame(notebook, bg='lightblue')
    notebook.add(main_tab, text="Main tab") # Läkarens patiener, patienters medical records
    notebook.add(schedule_tab, text="Schedule") # Läkarens schema
    
    
    #----------------------------------Läkarens schema---------------------------------------------
    
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
                    messagebox.showerror("Error", "This time slot is already booked!")
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
        
        if not date:
            messagebox.showerror("Error", "Please enter a valid date")
        
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
        appointments_list.delete(0, tk.END) # förhindrar duplicering
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""
                    SELECT DISTINCT day_of_week, time_slot, pat_id, booking_date 
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
    availability_frame = tk.Frame(schedule_tab, bg='lightblue')
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
    tk.Label(schedule_tab, text="Appointments:", bg='lightblue').pack(pady=5)
    appointments_list = tk.Listbox(schedule_tab, width=63, height=10)
    appointments_list.pack(pady=5)

    # Visar appointments från början
    show_appointments()
    
    
    #----------------------------------Visa läkarnes patieneter i main tab---------------------------------------------
    
    def fetch_doctor_patients(doctor_id, patient_list):
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                # Join doctoravailability med patienter för att få alla patienter som har bokat med denna läkaren
                curr.execute("""
                    SELECT DISTINCT p.pat_id, p.f_name, p.l_name, p.gender, p.address, p.phone_nr, p.dob, p.registration_date, COALESCE(visit_sum, 0.00) AS visit_sum
                    FROM patients p
                    JOIN doctoravailability da ON p.pat_id = da.pat_id
                    WHERE da.doc_id = %s
                    ORDER BY p.pat_id
                """, (doctor_id,))
                
                patients = curr.fetchall()
                patient_list.delete(0, tk.END)
                
                if patients:
                    for pat_id, f_name, l_name, gender, address, phone_nr, dob, registration_date, visit_sum in patients:
                        patient_info = f"ID: {pat_id}, Name: {f_name} {l_name}, Gender: {gender}, Address: {address}, Phone: {phone_nr}, DOB: {dob}, Registration date: {registration_date}, Visit sum: {visit_sum} SEK"
                        patient_list.insert(tk.END, patient_info)
                else:
                    patient_list.insert(tk.END, "No patients found")
                    
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()
                
    # för att visa läkarens patienter            
    patient_frame = tk.Frame(main_tab, bg='lightblue')
    patient_frame.pack(pady=10)
    
    tk.Label(main_tab, text="My Patients:").pack(pady=5)
    patient_list = tk.Listbox(main_tab, width=150, height=10)
    patient_list.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # Visa patienter
    fetch_doctor_patients(doctor_id, patient_list)
    

    def fetch_medical_records(patient_id_entry, medical_record_list):
        pat_id = patient_id_entry.get().strip()
        if not pat_id:
            messagebox.showerror("Error", "Please enter a patient ID.")
            return
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                #  query för att bara visa records där denna läkare var involverad
                curr.execute("""
                    SELECT DISTINCT medicalrecords.rec_id, doctors.doc_id, 
                           medicalrecords.diagnosis, medicalrecords.prescription, medicalrecords.description, 
                           doctoravailability.booking_date, doctoravailability.time_slot 
                    FROM medicalrecords 
                    JOIN doctors ON medicalrecords.doc_id = doctors.doc_id
                    JOIN doctoravailability 
                    ON doctoravailability.doc_id = medicalrecords.doc_id 
                        AND doctoravailability.pat_id = medicalrecords.pat_id 
                        AND doctoravailability.booking_date = (
                            SELECT MIN(booking_date) 
                            FROM doctoravailability
                            WHERE doctoravailability.pat_id = medicalrecords.pat_id
                            AND doctoravailability.doc_id = medicalrecords.doc_id
                        )
                    WHERE medicalrecords.pat_id = %s 
                    AND medicalrecords.doc_id = %s""", (pat_id, doctor_id))
                
                records = curr.fetchall()
                medical_record_list.delete(0, tk.END)
                if records:
                    for rec_id, doc_id, diagnosis, prescription, description, booking_date, time_slot in records:
                        record_info = (f"Record ID: {rec_id}, Diagnosis: {diagnosis}, "
                                     f"Prescription: {prescription}, "
                                     f"Description: {description}, "
                                     f"Visit Date: {booking_date} at {time_slot}")
                        medical_record_list.insert(tk.END, record_info)
                else: 
                    medical_record_list.insert(tk.END, "No Medical Records found for this patient.")

        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()
                
   # Visa medical records
    medical_frame = tk.Frame(main_tab) 
    medical_frame.pack(pady=10)

    patient_id_label = tk.Label(medical_frame, text="Enter Patient ID:")
    patient_id_label.pack(pady=5)
    patient_id_entry = tk.Entry(medical_frame)
    patient_id_entry.pack(pady=5)

    tk.Label(medical_frame, text="Medical Records:").pack(pady=5)
    medical_record_list = tk.Listbox(medical_frame, width=100, height=10)
    medical_record_list.pack(pady=5)

    tk.Button(medical_frame, text="Show Medical Records", 
             command=lambda: fetch_medical_records(patient_id_entry, medical_record_list)).pack(pady=5)


    def add_medical_record(patient_id_entry, diagnosis_entry, prescription_entry, description_entry):
        pat_id = patient_id_entry.get().strip()
        diagnosis = diagnosis_entry.get().strip()
        prescription = prescription_entry.get().strip()
        description = description_entry.get().strip()
        
        if not all([pat_id, diagnosis, prescription, description]):
            messagebox.showerror("Error", "All fields are required")
            return
            
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                # Kolla så appointment är current date för att kunna lägga till ny medical record
                curr.execute("""
                    SELECT doc_availability_id 
                    FROM doctoravailability 
                    WHERE doc_id = %s 
                    AND pat_id = %s 
                    AND booking_date = CURRENT_DATE
                """, (doctor_id, pat_id))
                
                appointment = curr.fetchone()
                if not appointment:
                    messagebox.showerror("Error", "No appointment found for this patient today")
                    return
            
                # lägg till ny medical record
                curr.execute("""
                    INSERT INTO medicalrecords (pat_id, doc_id, diagnosis, prescription, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (pat_id, doctor_id, diagnosis, prescription, description))
                
                conn.commit()
                messagebox.showinfo("Success", "Medical record added successfully")
                
                # cleara fältet
                diagnosis_entry.delete(0, tk.END)
                prescription_entry.delete(0, tk.END)
                description_entry.delete(0, tk.END)
                
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()
                
    # För att lägga till ny medical record
    record_frame = tk.Frame(medical_frame)
    record_frame.pack(pady=20)
    
    tk.Label(record_frame, text="Diagnosis:").pack()
    diagnosis_entry = tk.Entry(record_frame, width=50)
    diagnosis_entry.pack(pady=5)
    
    tk.Label(record_frame, text="Prescription:").pack()
    prescription_entry = tk.Entry(record_frame, width=50)
    prescription_entry.pack(pady=5)
    
    tk.Label(record_frame, text="Description:").pack()
    description_entry = tk.Entry(record_frame, width=50)
    description_entry.pack(pady=5)

    tk.Button(record_frame, text="Add Medical Record", 
        command=lambda: add_medical_record(patient_id_entry, diagnosis_entry, prescription_entry, description_entry)).pack(pady=10)
    


    


    

    
    
    
    
