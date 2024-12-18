import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
from GUI.admin_window import show_admin_gui
from GUI.doctor_window import show_doctor_gui
from GUI.patient_window import show_patient_gui, sign_up_patient



db_config = {
    'host': 'pgserver.mau.se',
    'dbname': 'health_center_group21',  #Namn på ditt databas
    'user': 'an4952',   #Ditt databas username, laila:an4952, fatima:an4263
    'password': '50owi0jd',  #Password, laila:50owi0jd, fatima:2ecfcvkm
    'port': 5432
}

# Inloggningsalternativ för user. 
def verify_login(user_type, user_id):
    conn = None
    curr = None 
    try:   
        if user_type == "Admin":
            messagebox.showinfo("Success", "Admin login successful!") #Automatiskt godkännande för en admin. 
            show_admin_gui(root)
            return
        
        conn = psycopg2.connect(**db_config) 
        curr = conn.cursor() #cursor för att hjälpa med SQL operationer, lagrar dessa values som man får av operationerna

        if user_type == "Doctor":
            curr.execute("SELECT * FROM doctors WHERE doc_id = %s", (user_id,))
            result = curr.fetchone()
            if result:
                messagebox.showinfo("Success", f"{user_type} Login successful!")
                show_doctor_gui(root, user_id)
            else:
               messagebox.showerror("Error", "Invalid ID.")
               return

        elif user_type == "Patient":
            curr.execute("SELECT * FROM patients WHERE pat_id = %s", (user_id,))
            result = curr.fetchone()
            if result:
                show_patient_gui(user_id, root)
            else:
                if messagebox.askyesno("Not Found", "ID not found. Would you like to sign up?"):
                    sign_up_patient(root, user_id)

                    
    except Exception as error:
        print(error)
    #finally behövs för att stänga connection och cursor oavsett om det blir error eller inte.
    finally: 
        if curr is not None:
            curr.close()
        if conn is not None:
            conn.close()
# Kollar om user finns för inloggning
def login():
    user_type = user_type_var.get()
    user_id = user_id_entry.get()

    if not user_id:
        messagebox.showerror("Error", "Please enter your ID.")
        return
    verify_login(user_type, user_id)  


# GUI  för login   
root = tk.Tk()
root.title("Health Center Login")

user_type_var = tk.StringVar(value="Admin")
#Knappar för Admin, Doctor, Patient
admin_radio = tk.Radiobutton(root, text="Admin", variable=user_type_var, value="Admin")
doctor_radio = tk.Radiobutton(root, text="Doctor", variable=user_type_var, value="Doctor")
patient_radio = tk.Radiobutton(root, text="Patient", variable=user_type_var, value="Patient")

admin_radio.grid(row=0, column=0, padx=10, pady=10)
doctor_radio.grid(row=0, column=1, padx=10, pady=10)
patient_radio.grid(row=0, column=2, padx=10, pady=10)
# input till user
user_id_label = tk.Label(root, text="Enter ID:")
user_id_label.grid(row=1, column=0, padx=10, pady=10)

user_id_entry = tk.Entry(root)
user_id_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2)

# login knappar
login_button = tk.Button(root, text="Login", command=login)
login_button.grid(row=1, column=3, columnspan=3, pady=20)

root.mainloop()
