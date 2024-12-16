# What can an admin do?
# ----------------------
# 1. Add doctor (including their doctor ID, full name, specilization, visit cost and phone number)
# 2. Add more specilizations for doctors
# 3. See a list of information about the patients registered in the health center
# 4. See a list of all upcoming appointments
# 5. See a list of all medical record related to a specific patient
# 6. See a list of all patients (including their patient ID, full name, and their total (sum of all) visit costs.)
# ----------------------


import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox


db_config = {
    'host': 'pgserver.mau.se',
    'dbname': 'health_center_group21',  #Namn på ditt databas
    'user': 'an4952',   #Ditt databas username, laila:an4952, fatima:an4263
    'password': '50owi0jd',  #Password, laila:50owi0jd, fatima:2ecfcvkm
    'port': 5432
}

#Admin GUI
def show_admin_gui(root):
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin View")
    admin_window.configure(bg='lightblue')

#Byta flik. (Tabs)
    notebook = ttk.Notebook(admin_window)
    notebook.pack(fill=tk.BOTH, expand=True)

    doctor_frame = tk.Frame(notebook, bg='lightblue')
    patient_frame = tk.Frame(notebook, bg='lightblue')
    notebook.add(doctor_frame, text="Doctors") #En tab där man visar läkare
    notebook.add(patient_frame, text="Patients") #En tab där man visar patienter.
    


    #Hämtar alla specialiseringar för läkare
    def fetch_specializations():
        try:
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("SELECT spec_id, spec_name FROM specialization")
                specializations = curr.fetchall()
                spec_list.delete(0, tk.END)
                for spec_id, spec_name in specializations:
                    spec_list.insert(tk.END, f" ID:{spec_id},  "f"{spec_name}")
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()

    # Hämtar alla läkare
    def fetch_doctors():
        try:
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""SELECT d.doc_id, d.f_name, d.l_name, s.spec_name, d.phone_nr, d.visit_cost  FROM doctors d JOIN specialization s ON d.spec_id = s.spec_id""")
                doctors = curr.fetchall()
                doctor_list.delete(0, tk.END)
                for doc_id, f_name, l_name, spec_name, phone_nr, visit_cost in doctors:
                        doctor_info = (f"ID: {doc_id}, Name: {f_name} {l_name}, "f"Specialization: {spec_name}, Phone: {phone_nr}, "f"Visit Cost: {visit_cost}")
                        doctor_list.insert(tk.END, doctor_info)
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()

    # Lägger till specialiseringar. 
    def add_specialization():
        spec_name = spec_entry.get()
        if not spec_name:
            messagebox.showerror("Error", "Please provide Specialization.")
            return
        try:
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("INSERT INTO specialization (spec_name) VALUES (%s)", (spec_name,))
                conn.commit()
                messagebox.showinfo("Success", "Specialization added successfully!")
                fetch_specializations()  #Hämtar alla specialiseringar och id. 
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()

    #Lägger till läkare till listan
    def add_doctor():
        try:
            doc_id = doc_id_entry.get().strip()
            f_name = f_name_entry.get().strip()
            l_name = l_name_entry.get().strip()
            spec_id = spec_id_entry.get().strip()
            phone_nr = phone_entry.get().strip()
            visit_cost = visit_cost_entry.get().strip()
            #Felmeddelanden, ifall input är fel.
            if not doc_id:
                raise ValueError("Doctor ID is required and must be an integer.")
            if not spec_id:
                raise ValueError("Specialization ID is required and must be an integer.")
            if not phone_nr:
                raise ValueError("Phone number is required.")
        
        # Konverterar till rätt datatyp
            doc_id = int(doc_id)
            spec_id = int(spec_id)
            visit_cost = float(visit_cost) if visit_cost else 0.0  # Default blit 0.0 om man inte lägger till pris. 
        
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
             curr.execute(
                "INSERT INTO doctors (doc_id, f_name, l_name, spec_id, phone_nr, visit_cost) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (doc_id, f_name, l_name, spec_id, phone_nr, visit_cost)
            )
            conn.commit()
        
            messagebox.showinfo("Success", "Doctor added successfully!")
            fetch_doctors()

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    # Raderar en läkare från listan
    def delete_doctor():
        try:
            doc_id = doctor_id_entry.get().strip() 
            print(f"Attempting to delete doctor with ID: {doc_id}")


            if not doc_id:
                raise ValueError("Doctor ID doesn't exist. Try again!")
            doc_id = int(doc_id)

            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("DELETE FROM doctors WHERE doc_id = %s", (doc_id,))
                conn.commit()
            messagebox.showinfo("Success", "Doctor removed successfully!")
            fetch_doctors() #Uppdaterar listan
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()
                
    #Hämtar patienter. 
    def fetch_patients():
        try:
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""SELECT pat_id, f_name, l_name, gender, phone_nr, dob FROM patients """)
                patients = curr.fetchall()
                patient_list.delete(0, tk.END)
                for pat_id, f_name, l_name, gender, phone_nr, dob in patients: #LÄGG ÄVEN TILL SUM OF VISIT COST.
                        patient_info = (f"Medical number: {pat_id}, Full name: {f_name} {l_name}, Gender: {gender}, Phone: {phone_nr}, "f"Date of birth: {dob}")
                        patient_list.insert(tk.END, patient_info)
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()

    def fetch_medical_records(patient_id_entry, medical_record_list):
        pat_id = patient_id_entry.get().strip()
        if not pat_id:
            messagebox.showerror("Error", "Please enter a patient ID.")
            return
        try:
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""SELECT rec_id, doc_id, diagnosis, prescription, visit_date FROM medicalrecords WHERE pat_id = %s""", (pat_id,))
                records = curr.fetchall()
                medical_record_list.delete(0, tk.END)
                if records:
                    for rec_id, doc_id, diagnosis, prescription, visit_date in records:
                        record_info = ( f"Record ID: {rec_id}, Doctor ID: {doc_id}, Diagnosis: {diagnosis}, Prescription: {prescription}, Visit Date: {visit_date}")
                        medical_record_list.insert(tk.END, record_info)
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()

    def fetch_appointments(patient_id_entry, appointment_list):
        pat_id = patient_id_entry.get().strip()
        if not pat_id:
            messagebox.showerror("Error", "Please enter a patient ID.")
            return
        try:
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""SELECT historylog.log_id, historylog.doc_availability_id, historylog.doc_id, historylog.action_type, historylog.action_time FROM historylog WHERE historylog.pat_id = %s AND historylog.action_type = 'booked'""", (pat_id,))
                appointments = curr.fetchall()
                appointment_list.delete(0, tk.END)
                if appointments:
                    for log_id, doc_avail_id, doc_id, action_type, action_time in appointments:
                        appointment_info = (  f"Log ID: {log_id}, Doctor Availability ID: {doc_avail_id}, Doctor ID: {doc_id}, Action Time: {action_time}")
                        appointment_list.insert(tk.END, appointment_info)
                else: 
                    appointment_list.insert(tk.END, "No upcoming appointments found for this patient.")
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()

    # Vänstra frame, för specialiseringar. 
    left_frame = tk.Frame(doctor_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)

    tk.Label(left_frame, text="Specializations").pack(pady=5)
    spec_list = tk.Listbox(left_frame, width=20)
    spec_list.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)  
    tk.Button(left_frame, text="Show Specializations", command=fetch_specializations).pack(pady=10)

    tk.Label(left_frame, text="Specialization Name:").pack(padx=10, pady=5)
    spec_entry = tk.Entry(left_frame)
    spec_entry.pack(padx=10, pady=5)
    tk.Button(left_frame, text="Add Specialization", command=add_specialization).pack(pady=10)

    # Högra frame, funktioner för läkare
    right_frame = tk.Frame(doctor_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=100, pady=10)

    tk.Label(right_frame, text="Doctors").pack(pady=5)
    doctor_list = tk.Listbox(right_frame, width=100, height=5)
    doctor_list.pack(padx=100, pady=5, fill=tk.BOTH, expand=True)
    tk.Button(right_frame, text="Show Doctors", command=fetch_doctors).pack(pady=10)

    tk.Label(right_frame, text="Doctor ID:").pack(padx=10, pady=5)
    doc_id_entry = tk.Entry(right_frame)
    doc_id_entry.pack(padx=10, pady=5)

    tk.Label(right_frame, text="Doctor First Name:").pack(padx=10, pady=5)
    f_name_entry = tk.Entry(right_frame)
    f_name_entry.pack(padx=10, pady=5)

    tk.Label(right_frame, text="Doctor Last Name:").pack(padx=10, pady=5)
    l_name_entry = tk.Entry(right_frame)
    l_name_entry.pack(padx=10, pady=5)

    tk.Label(right_frame, text="Phone Number:").pack(padx=10, pady=5)
    phone_entry = tk.Entry(right_frame)
    phone_entry.pack(padx=10, pady=5)

    tk.Label(right_frame, text="Visit Cost:").pack(padx=10, pady=5)
    visit_cost_entry = tk.Entry(right_frame)
    visit_cost_entry.pack(padx=10, pady=5)

    tk.Label(right_frame, text="Specialization ID:").pack(padx=10, pady=5)
    spec_id_entry = tk.Entry(right_frame)
    spec_id_entry.pack(padx=10, pady=5)

    tk.Button(right_frame, text="Add Doctor", command=add_doctor).pack(pady=10)

    tk.Label(right_frame, text="Doctor ID to Remove:").pack(padx=10, pady=5)
    doctor_id_entry = tk.Entry(right_frame)
    doctor_id_entry.pack(padx=10, pady=5)

    tk.Button(right_frame, text="Remove Doctor", command=delete_doctor).pack(pady=10)


    #Patienters sida
    tk.Label(patient_frame, text="Patients").pack(pady=5)
    patient_list = tk.Listbox(patient_frame, width=100, height=5)
    patient_list.pack(padx=100, pady=5, fill=tk.BOTH, expand=True)
    tk.Button(patient_frame, text="Show Patients", command=fetch_patients).pack(pady=5)
    
    patient_id_label = tk.Label(patient_frame, text="Enter Patient ID:")
    patient_id_label.pack(pady=5)
    patient_id_entry = tk.Entry(patient_frame)
    patient_id_entry.pack(pady=5, padx=10)
    
    tk.Label(patient_frame, text="Medical Records:").pack(pady=5)
    medical_record_list = tk.Listbox(patient_frame, width=100, height=5)
    medical_record_list.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    tk.Button(patient_frame, text="Show Medical Records", 
    command=lambda: fetch_medical_records(patient_id_entry, medical_record_list)).pack(pady=5)

    tk.Label(patient_frame, text="Upcoming Appointments:").pack(pady=5)
    appointment_list = tk.Listbox(patient_frame, width=100, height=10)
    appointment_list.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    tk.Button(patient_frame, text="Show Upcoming Appointments", command=lambda: 
    fetch_appointments(patient_id_entry, appointment_list)).pack(pady=10)
