# What can a patient do?
# ----------------------
# 1. Sign up for the health center by entering their  first name, last name, gender (F, M or NB), address, phone nr, birthdate (registration date should be recorded) (can only sign up once, so patient id should be unique) - done
# 2. See all their info and edit the information except for Patient ID and registration date. - done
# 3. Book an appointment for a specific doctor. They should see a list of all doctors, their specilization and visit cost. See the available days and times for visiting the doctor and then book the appointment. (booking can only be made on a friday of the week for the coming week, should be changeable) - done
# 4. View their medical record (see all diagnosis and prescription) for each previous visit.
# ----------------------

import psycopg
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

db_config = {
    'host': 'pgserver.mau.se',
    'dbname': 'health_center_group21',  #Namn på ditt databas
    'user': 'an4263',   #Ditt databas username, laila:an4952, fatima:an4263
    'password': '2ecfcvkm',  #Password, laila:50owi0jd, fatima:2ecfcvkm
    'port': 5432
}


def sign_up_patient(root, pre_filled_id=None):
    sign_up_window = tk.Toplevel(root)
    sign_up_window.title("Patient Sign-Up")
    sign_up_window.configure(bg='lightblue')


    def register_patient():
        pat_id = pat_id_entry.get().strip()
        f_name = f_name_entry.get().strip()
        l_name = l_name_entry.get().strip()
        address = address_entry.get().strip()
        gender = gender_entry.get().strip()
        phone_nr = phone_entry.get().strip()
        dob = birthdate_entry.get().strip()
        registration_date = datetime.now().strftime("%Y-%m-%d")
        #Felmeddelanden, ifall input är fel.
        if not f_name:
            raise ValueError("First name is required")
        if not l_name:
            raise ValueError("Last name is required")
        if not address:
            raise ValueError("Address is required.")
        if not dob:
            raise ValueError("Date of birth is required.")
        if not gender:
            raise ValueError("Gender is required. Only F/M/NB")
        if not phone_nr:
            raise ValueError("Phone number is required. 10 numbers total")

        try:
            pat_id = int(pat_id)
            conn = psycopg.connect(**db_config) 
            curr = conn.cursor() 
            with conn.cursor() as curr:
                curr.execute("""INSERT INTO patients (pat_id, f_name, l_name, gender, address, phone_nr, dob, registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",(pat_id, f_name, l_name, gender, address, phone_nr, dob, registration_date))
                conn.commit()
                messagebox.showinfo("Success", "Information updated successfully!")
                sign_up_window.destroy()
                show_patient_gui(pat_id, root)

        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()
    tk.Label(sign_up_window, text="Patient ID").grid(row=0, column=0, padx=10, pady=5)
    pat_id_entry = tk.Entry(sign_up_window)
    pat_id_entry.grid(row=0, column=1, padx=10, pady=5)
    if pre_filled_id:
        pat_id_entry.insert(0, pre_filled_id)

    tk.Label(sign_up_window, text="First Name").grid(row=1, column=0, padx=10, pady=5)
    f_name_entry = tk.Entry(sign_up_window)
    f_name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(sign_up_window, text="Last Name").grid(row=2, column=0, padx=10, pady=5)
    l_name_entry = tk.Entry(sign_up_window)
    l_name_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(sign_up_window, text="Gender (F/M/NB)").grid(row=3, column=0, padx=10, pady=5)
    gender_entry = tk.Entry(sign_up_window)
    gender_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(sign_up_window, text="Address").grid(row=4, column=0, padx=10, pady=5)
    address_entry = tk.Entry(sign_up_window)
    address_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(sign_up_window, text="Phone Number").grid(row=5, column=0, padx=10, pady=5)
    phone_entry = tk.Entry(sign_up_window)
    phone_entry.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(sign_up_window, text="Date of Birth (YYYY-MM-DD)").grid(row=6, column=0, padx=10, pady=5)
    birthdate_entry = tk.Entry(sign_up_window)
    birthdate_entry.grid(row=6, column=1, padx=10, pady=5)

    tk.Button(sign_up_window, text="Sign Up", command=register_patient).grid(row=7, column=0, columnspan=2, pady=10)

#Patient GUI
def show_patient_gui(pat_id, root):
    # Skapa nytt fönster
    patient_window = tk.Toplevel(root)
    patient_window.title("Patient View")

    # Skapa flikar (Tabs)
    tab_control = ttk.Notebook(patient_window)
    profile_tab = ttk.Frame(tab_control)
    appointments_tab = ttk.Frame(tab_control)
    diagnoses_tab = ttk.Frame(tab_control)

    tab_control.add(profile_tab, text='Profile')
    tab_control.add(appointments_tab, text='Appointments')
    tab_control.add(diagnoses_tab, text='My medical records')
    tab_control.pack(expand=1, fill="both")

    f_name_var = tk.StringVar()
    l_name_var = tk.StringVar()
    gender_var = tk.StringVar()
    address_var = tk.StringVar()
    phone_var = tk.StringVar()
    dob_var = tk.StringVar()
    reg_date_var = tk.StringVar()
    pat_id_var = tk.StringVar()
    
    tk.Label(diagnoses_tab, text="My Medical Records").pack(pady=5)
    medical_record_list = tk.Listbox(diagnoses_tab, width=100, height=15)
    medical_record_list.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
    def fetch_patient_medical_records():
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""
                    SELECT medicalrecords.rec_id, doctors.f_name, doctors.l_name,
                            medicalrecords.diagnosis, medicalrecords.prescription, 
                            doctoravailability.booking_date, doctoravailability.time_slot 
                    FROM medicalrecords 
                    JOIN doctors ON medicalrecords.doc_id = doctors.doc_id
                    JOIN doctoravailability ON doctoravailability.doc_id = medicalrecords.doc_id 
                        AND doctoravailability.pat_id = medicalrecords.pat_id 
                    WHERE medicalrecords.pat_id = %s
                    ORDER BY doctoravailability.booking_date DESC""", (pat_id,))
                
                records = curr.fetchall()
                medical_record_list.delete(0, tk.END)
                if records:
                    for rec_id, doc_fname, doc_lname, diagnosis, prescription, booking_date, time_slot in records:
                        record_info = (f"Record ID: {rec_id}, Doctor: {doc_fname} {doc_lname}, "
                                        f"Diagnosis: {diagnosis}, Prescription: {prescription}, "
                                        f"Visit Date: {booking_date} at {time_slot}")
                        medical_record_list.insert(tk.END, record_info)
                else: 
                    medical_record_list.insert(tk.END, "No Medical Records found.")

        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()
        
    # Add refresh button
    tk.Button(diagnoses_tab, text="Refresh Medical Records", 
             command=fetch_patient_medical_records).pack(pady=5)
             
    # Initial load of medical records
    fetch_patient_medical_records()

    # Hämtar  patient information med pat_id.
    def fetch_and_display_patient_info():
        try:
            conn = psycopg.connect(**db_config) 
            curr = conn.cursor() 
            with conn.cursor() as curr:
                curr.execute("SELECT pat_id, f_name, l_name, gender, address, dob, phone_nr, registration_date FROM patients WHERE pat_id = %s", (pat_id,))
                patient_info = curr.fetchone()
                if patient_info:
                    pat_id_var.set(patient_info[0])
                    f_name_var.set(patient_info[1])
                    l_name_var.set(patient_info[2])
                    gender_var.set(patient_info[3])
                    address_var.set(patient_info[4])
                    dob_var.set(patient_info[5])
                    phone_var.set(patient_info[6])
                    reg_date_var.set(patient_info[7])
                else:
                    messagebox.showerror("Error", "Patient information not found.")
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()

    fetch_and_display_patient_info()

# Skapa widgets för att visa och redigera patientinformationen i profile-tab
    tk.Label(profile_tab, text="Medical Number:").grid(row=0, column=0)
    tk.Entry(profile_tab, textvariable=pat_id_var, state='readonly').grid(row=0, column=1)

    tk.Label(profile_tab, text="First Name:").grid(row=1, column=0)
    tk.Entry(profile_tab, textvariable=f_name_var).grid(row=1, column=1)

    tk.Label(profile_tab, text="Last Name:").grid(row=2, column=0)
    tk.Entry(profile_tab, textvariable=l_name_var).grid(row=2, column=1)

    tk.Label(profile_tab, text="Gender:").grid(row=3, column=0)
    tk.Entry(profile_tab, textvariable=gender_var).grid(row=3, column=1)

    tk.Label(profile_tab, text="Address:").grid(row=4, column=0)
    tk.Entry(profile_tab, textvariable=address_var).grid(row=4, column=1)

    tk.Label(profile_tab, text="Phone Number:").grid(row=5, column=0)
    tk.Entry(profile_tab, textvariable= phone_var).grid(row=5, column=1)

    tk.Label(profile_tab, text="Date of Birth:").grid(row=6, column=0)
    tk.Entry(profile_tab, textvariable=dob_var).grid(row=6, column=1)

    tk.Label(profile_tab, text="Registration Date:").grid(row=7, column=0)
    tk.Entry(profile_tab, textvariable=reg_date_var, state='readonly').grid(row=7, column=1)


     # Funktion för att uppdatera patientinformation
    def update_patient_info():
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""
                    UPDATE patients
                    SET f_name = %s, l_name = %s, gender = %s, address = %s, phone_nr = %s, dob = %s
                    WHERE pat_id = %s""", (f_name_var.get(), l_name_var.get(), gender_var.get(), address_var.get(),phone_var.get(), dob_var.get(), pat_id))
                conn.commit()
                messagebox.showinfo("Success", "Patient information updated successfully.")
        except Exception as error:
            messagebox.showerror("Error", str(error))
        finally:
            if conn is not None:
                conn.close()
    # Uppdatera knapp
    tk.Button(profile_tab, text="Update Info", command=update_patient_info).grid(row=8, column=1)

    # Lägg till widgets för appointments och diagnoses flikarna 
    tk.Label(appointments_tab, text="---Select a Specifik Specialization---").pack()

    #Hämtar alla specialiseringar dom finns. 
    def get_specializations():
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("SELECT spec_id, spec_name FROM specialization")
                return curr.fetchall()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return []
        finally:
            if conn is not None:
                conn.close()

    #Hämtar alla läkare med en specifik specialisering
    def get_doctors_by_specialization(spec_id):
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""SELECT d.doc_id, d.f_name, d.l_name, s.spec_name, d.phone_nr, d.visit_cost 
                    FROM doctors d 
                    JOIN specialization s ON d.spec_id = s.spec_id
                    WHERE d.spec_id = %s""", (spec_id,))
                return curr.fetchall()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return []
        finally:
            if conn is not None:
                conn.close()

    #Hanterar läkare som man väljer 
    def handle_specialization_selection(event):
        selected_spec = specialization_combobox.get()
        selected_spec_id = next((spec_id for spec_id, spec_name in specializations if spec_name == selected_spec), None)
        if selected_spec_id:
            doctors = get_doctors_by_specialization(selected_spec_id)
            doctors_listbox.delete(0, tk.END)
            if doctors:
                for doc_id, f_name, l_name, spec_name, phone_nr, visit_cost in doctors:
                    doctor_info = f"ID: {doc_id}, Name: {f_name} {l_name}, Phone: {phone_nr}, Cost: {visit_cost}"
                    doctors_listbox.insert(tk.END, doctor_info)
            else:
                doctors_listbox.insert(tk.END, "No doctors found for this specialization.")
    

    #Hämtar alla läkare
    def fetch_doctors():
        try:
            conn = psycopg.connect(**db_config)
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


        #Hämtar alla tillgängliga tider för denna läkaren. 
    def fetch_available_slots(doc_id):
        try:
            conn = psycopg.connect(**db_config)
            with conn.cursor() as curr:
                curr.execute("""SELECT day_of_week, time_slot, booking_date FROM doctoravailability WHERE doc_id = %s AND pat_id IS NULL""", (doc_id,))
                slots = curr.fetchall()
            return slots
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return []
        finally:
            if conn is not None:
                conn.close()

    def is_today_friday():
        #  (måndag=0, tisdag=1, ..., fredag=4)
        return datetime.now().weekday() == 4


    #Hanterar en vald läkare.
    def handle_doctor_selection(event):
        widget = event.widget

        selected_index = widget.curselection()
        if not selected_index:
            return

        selected_doctor = widget.get(selected_index)
        doctor_info = selected_doctor.split(', ')
        doctor_details = {kv.split(": ")[0]: kv.split(": ")[1] for kv in doctor_info}

        open_booking_window(doctor_details)

    def open_booking_window(doctor_details):
        booking_window = tk.Toplevel()
        booking_window.title("Doctor Booking")
    
        tk.Label(booking_window, text="Doctor Booking Details", font=('Arial', 14)).pack(pady=10)
    
    # Visar läkarens info
        for key, value in doctor_details.items():
            tk.Label(booking_window, text=f"{key}: {value}", font=('Arial', 11)).pack()
        
        doctor_id = doctor_details['ID']
        available_slots = fetch_available_slots(doctor_id)
        if not available_slots:
            tk.Label(booking_window, text="No available slots", font=('Arial', 11)).pack()
            return

        #Visar hur många tillgängliga platser det finns. 
        tk.Label(booking_window, text="Available Slots:", font=('Arial', 12)).pack(pady=10)
        slots_listbox = tk.Listbox(booking_window, width=50, height=10)
        slots_listbox.pack(pady=10)
        for slot in available_slots:
            slots_listbox.insert(tk.END, f"Day: {slot[0]}, Time: {slot[1]}, Date: {slot[2]}")
    

    # Tidsbokning, Går ej att boka om det INTE är en fredag.
        def book_appointment():
             #KOMMENTERA BORT IF-SATSEN OM DU VILL TESTA BOKA.
            #if not is_today_friday():   
            #    messagebox.showwarning("Unavailable", "Bookings can only be made on Fridays for the upcoming week.")
            #    return
            selected_slot_indices = slots_listbox.curselection()
            if not selected_slot_indices:
                messagebox.showwarning("Selection Error", "Please select a time slot.")
                return

            selected_slot = available_slots[selected_slot_indices[0]]

            booking_date = selected_slot[2] # innehåller booking date!!
            slot_day = selected_slot[0]
            slot_time = selected_slot[1]
            try:
                conn = psycopg.connect(**db_config) 
                cursor = conn.cursor()
                
                cursor.execute("SELECT visit_cost FROM doctors WHERE doc_id = %s", (doctor_id,))
                visit_cost = cursor.fetchone()[0]

            # Uppdatera i doctoravailability att en tid är bokad för en specifik läkare. 
                cursor.execute("""
                UPDATE doctoravailability
                SET pat_id = %s, booking_date = %s
                WHERE doc_id = %s AND day_of_week = %s AND time_slot = %s AND pat_id IS NULL
                RETURNING doc_availability_id""", (pat_id, booking_date, doctor_id, slot_day, slot_time))


            # Insert i historylog så att det loggas. 
                doc_availability_id = cursor.fetchone() # Assumes this is an auto-increment field
                if not doc_availability_id:
                    messagebox.showerror("Error", "Slot is no longer available.")
                    return
                doc_availability_id = doc_availability_id[0]
                
                # Uppdateras patientens visit_sum varje gång de bokar
                cursor.execute("""
                UPDATE patients
                SET visit_sum = COALESCE(visit_sum, 0) + %s
                WHERE pat_id = %s""", (visit_cost, pat_id))

                cursor.execute("""
                INSERT INTO historylog (doc_availability_id, pat_id, doc_id, action_type, action_time)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)""", (doc_availability_id, pat_id, doctor_id, 'booked'))

                conn.commit()
                messagebox.showinfo("Booking", f"Booking confirmed for {slot_day} at {slot_time}.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()
            booking_window.destroy()

        tk.Button(booking_window, text="Book Appointment", command=book_appointment).pack(pady=20)

    
    # En Combobox med de olika specialiseringar för läkare.
    specializations = get_specializations()
    specialization_combobox = ttk.Combobox(appointments_tab, values=[spec_name for _, spec_name in specializations])
    specialization_combobox.pack(pady=5)
    specialization_combobox.bind("<<ComboboxSelected>>", handle_specialization_selection)

    doctors_listbox = tk.Listbox(appointments_tab, width=100, height=10)
    doctors_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
     #Visar alla läkare
    tk.Label(appointments_tab, text="All Doctors in the Health Center").pack(pady=5)
    doctor_list = tk.Listbox(appointments_tab, width=100, height=5)
    doctor_list.pack(padx=100, pady=5, fill=tk.BOTH, expand=True)

    fetch_doctors()

    doctor_list.bind("<<ListboxSelect>>", handle_doctor_selection)
    doctors_listbox.bind("<<ListboxSelect>>", handle_doctor_selection)
    
    

  

