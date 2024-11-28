import customtkinter as ctk
import mysql.connector
from tkcalendar import Calendar
from datetime import datetime, date
from tkinter import messagebox
import time
import math

def fetch_subject_data(subject, user_id):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Use your SQL password
            database=user_id
        )
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT Chapter, Target_Questions, Questions_Solved, Deadline FROM `{subject}`")
        data = mycursor.fetchall()
        
        current_date = datetime.now()

        for record in data:
            deadline = record[3]

            #Can't figure out the instance of the SQL date
            if deadline:
                if isinstance(deadline, datetime):
                    if deadline < current_date:
                        chapter = record[0]
                        delete_query = f"DELETE FROM `{subject}` WHERE Chapter = %s AND Deadline = %s"
                        mycursor.execute(delete_query, (chapter, deadline))
                        mydb.commit()
                elif isinstance(deadline, date):
                    if deadline < current_date.date():
                        chapter = record[0] 
                        delete_query = f"DELETE FROM `{subject}` WHERE Chapter = %s AND Deadline = %s"
                        mycursor.execute(delete_query, (chapter, deadline))
                        mydb.commit()

        mycursor.close()
        mydb.close()

        return data

    except mysql.connector.Error as err:
        print(f"Error fetching data for {subject}: {err}")
        return []

def update_analog_clock(clock_canvas, hour_hand, minute_hand, second_hand, center_x, center_y, radius):
    """Update the analog clock hands based on the current time and dynamically scale."""
    current_time = time.localtime()
    second_angle = (current_time.tm_sec * 6)
    minute_angle = (current_time.tm_min * 6) + (current_time.tm_sec * 0.1)
    hour_angle = ((current_time.tm_hour % 12) * 30) + (current_time.tm_min * 0.5)

    clock_canvas.coords(second_hand, center_x, center_y, center_x + radius * 0.9 * math.sin(math.radians(second_angle)),
                        center_y - radius * 0.9 * math.cos(math.radians(second_angle)))

    clock_canvas.coords(minute_hand, center_x, center_y, center_x + radius * 0.7 * math.sin(math.radians(minute_angle)),
                        center_y - radius * 0.7 * math.cos(math.radians(minute_angle)))

    clock_canvas.coords(hour_hand, center_x, center_y, center_x + radius * 0.5 * math.sin(math.radians(hour_angle)),
                         center_y - radius * 0.5 * math.cos(math.radians(hour_angle)))

    clock_canvas.after(1000, update_analog_clock, clock_canvas, hour_hand, minute_hand, second_hand, center_x, center_y, radius)

def create_schedule_window(subject, user_id, main_screen):
    schedule_window = ctk.CTkToplevel(main_screen)
    schedule_window.geometry("400x400")
    schedule_window.title("Create Schedule")
    schedule_window.resizable(False, False)
    schedule_window.configure(bg="#2f2f2f")

    main_screen.withdraw()

    form_frame = ctk.CTkFrame(schedule_window, width=380, height=300, fg_color="#3a3a3a")
    form_frame.place(relx=0.5, rely=0.4, anchor="center")

    chapter_label = ctk.CTkLabel(form_frame, text="Chapter", font=("Arial", 14), text_color="white")
    chapter_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    
    if subject == 'Physics':
        chapters = ['Electric Charges and Fields', 'Electrostatic Potential and Capacitance', 'Current Electricity', 'Moving Charges and Magnetism', 'Magnetism and Matter', 'Electromagnetic Induction', 'Alternating Current', 'Electromagnetic Waves', 'Ray Optics and Optical Instruments', 'Wave Optics', 'Dual Nature of Radiation and Matter', 'Atoms', 'Nuclei', 'Semiconductor Elctronics'] 
    elif subject == 'Chemistry':
        chapters = ['Solutions', 'Electrochemistry', 'Chemical Kinetics', 'The d- and f- Block Elements', 'Coordination Compounds', 'Haloalkanes and Haloarenes', 'Alcohols, Phenols and Ethers', 'Aldehydes, Ketones and Carboxylic Acids', 'Amines', 'Biomolecules']
    elif subject == 'Mathematics':
        chapters = ['Relations and Functions', 'Inverse Trigonometric Functions', 'Matrices', 'Determinants', 'Continuity and Differentiability', 'Application of Derivatives', 'Integrals', 'Application of Integrals', 'Differential Equations', 'Vector Algebra', 'Three Dimensional Geometry', 'Linear Programming', 'Probability']
    chapter_dropdown = ctk.CTkOptionMenu(form_frame, values=chapters)
    chapter_dropdown.grid(row=0, column=1, padx=10, pady=10)

    target_label = ctk.CTkLabel(form_frame, text="Target Questions", font=("Arial", 14), text_color="white")
    target_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    
    target_input = ctk.CTkEntry(form_frame, font=("Arial", 14))
    target_input.grid(row=1, column=1, padx=10, pady=10)

    deadline_label = ctk.CTkLabel(form_frame, text="Deadline", font=("Arial", 14), text_color="white")
    deadline_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    
    calendar = Calendar(form_frame, date_pattern='yyyy-mm-dd')
    calendar.grid(row=2, column=1, padx=10, pady=10)

    def confirm_schedule():
        chapter = chapter_dropdown.get()
        target_questions = target_input.get()
        deadline = calendar.get_date()

        if chapter and target_questions and deadline:
            try:
                if not target_questions.isdigit():
                    messagebox.showerror("Invalid Input", "Target Questions must be an integer.")
                    return
                
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",  # Replace with your password
                    database=user_id
                )
                mycursor = mydb.cursor()
    
                query = f"SELECT COUNT(*) FROM `{subject}` WHERE Chapter = %s AND Deadline = %s"
                mycursor.execute(query, (chapter, deadline))
                count = mycursor.fetchone()[0]
                if count > 0:
                    messagebox.showerror("Duplicate Entry", "This schedule already exists for the selected chapter and deadline.")
                    mycursor.close()
                    mydb.close()
                    return
    
                query = f"""
                    INSERT INTO `{subject}` (Chapter, Target_Questions, Questions_Solved, Deadline)
                    VALUES (%s, %s, %s, %s)
                """
                mycursor.execute(query, (chapter, target_questions, 0, deadline))
                mydb.commit()
    
                mycursor.close()
                mydb.close()
    
                schedule_window.destroy()
                main_screen.deiconify()
    
            except mysql.connector.Error as err:
                print(f"Error inserting schedule: {err}")
                messagebox.showerror("Database Error", f"Error inserting schedule: {err}")
        else:
            messagebox.showerror("Incomplete Information", "Please fill all fields.")

    confirm_button = ctk.CTkButton(schedule_window, text="Confirm", command=confirm_schedule, 
                                    width=150, height=40, fg_color="#4CAF50", hover_color="#45a049", 
                                    text_color="white", font=("Arial", 16, "bold"), corner_radius=10)
    confirm_button.place(relx=0.5, rely=0.9, anchor="center")

    schedule_window.protocol("WM_DELETE_WINDOW", lambda: close_subject_window(schedule_window, main_screen))

    schedule_window.grab_set()
    schedule_window.mainloop()
    
def create_update_window(subject, user_id, main_screen):
    update_window = ctk.CTkToplevel(main_screen)
    update_window.geometry("400x400")
    update_window.title("Update Schedule")
    update_window.resizable(False, False)
    update_window.configure(bg="#2f2f2f")

    main_screen.withdraw()

    form_frame = ctk.CTkFrame(update_window, width=380, height=300, fg_color="#3a3a3a")
    form_frame.place(relx=0.5, rely=0.4, anchor="center")

    chapter_label = ctk.CTkLabel(form_frame, text="Chapter", font=("Arial", 14), text_color="white")
    chapter_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    
    if subject == 'Physics':
        chapters = ['Electric Charges and Fields', 'Electrostatic Potential and Capacitance', 'Current Electricity', 'Moving Charges and Magnetism', 'Magnetism and Matter', 'Electromagnetic Induction', 'Alternating Current', 'Electromagnetic Waves', 'Ray Optics and Optical Instruments', 'Wave Optics', 'Dual Nature of Radiation and Matter', 'Atoms', 'Nuclei', 'Semiconductor Elctronics']  # Placeholder, replace with actual chapters
    elif subject == 'Chemistry':
        chapters = ['Solutions', 'Electrochemistry', 'Chemical Kinetics', 'The d- and f- Block Elements', 'Coordination Compounds', 'Haloalkanes and Haloarenes', 'Alcohols, Phenols and Ethers', 'Aldehydes, Ketones and Carboxylic Acids', 'Amines', 'Biomolecules']
    elif subject == 'Mathematics':
        chapters = ['Relations and Functions', 'Inverse Trigonometric Functions', 'Matrices', 'Determinants', 'Continuity and Differentiability', 'Application of Derivatives', 'Integrals', 'Application of Integrals', 'Differential Equations', 'Vector Algebra', 'Three Dimensional Geometry', 'Linear Programming', 'Probability']
    chapter_dropdown = ctk.CTkOptionMenu(form_frame, values=chapters)
    chapter_dropdown.grid(row=0, column=1, padx=10, pady=10)

    update_label = ctk.CTkLabel(form_frame, text="Solved Questions", font=("Arial", 14), text_color="white")
    update_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    
    update_input = ctk.CTkEntry(form_frame, font=("Arial", 14))
    update_input.grid(row=1, column=1, padx=10, pady=10)

    def confirm_schedule():
        chapter = chapter_dropdown.get()
        update_questions = update_input.get()

        if chapter and update_questions:
            try:
                if not update_questions.isdigit():
                    messagebox.showerror("Invalid Input", "Target Questions must be an integer.")
                    return
                
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database=user_id
                )
                mycursor = mydb.cursor()
                
                query = f"SELECT Target_Questions FROM `{subject}` WHERE Chapter = %s"
                mycursor.execute(query, (chapter,))
                target = mycursor.fetchone()[0]
                if int(target) < int(update_questions):
                    raise mysql.connector.Error('Invalid Solved Questions')
    
                query = f"""
                    UPDATE `{subject}` SET Questions_Solved = %s WHERE Chapter = %s
                """
                mycursor.execute(query, (update_questions, chapter))
                mydb.commit()
    
                mycursor.close()
                mydb.close()
    
                update_window.destroy()
                main_screen.deiconify()
    
            except mysql.connector.Error as err:
                print(f"Error inserting schedule: {err}")
                messagebox.showerror("Database Error", f"Error inserting schedule: {err}")
                
            except TypeError:
                messagebox.showerror("Database Error", "Chapter doesn't exist in records")
        else:
            messagebox.showerror("Incomplete Information", "Please fill all fields.")

    confirm_button = ctk.CTkButton(update_window, text="Confirm", command=confirm_schedule, 
                                    width=150, height=40, fg_color="#4CAF50", hover_color="#45a049", 
                                    text_color="white", font=("Arial", 16, "bold"), corner_radius=10)
    confirm_button.place(relx=0.5, rely=0.9, anchor="center")

    update_window.protocol("WM_DELETE_WINDOW", lambda: close_subject_window(update_window, main_screen))

    update_window.grab_set()
    update_window.mainloop()

def create_subject_window(subject, user_id, main_screen):
    subject_window = ctk.CTk()
    subject_window.geometry("1100x800")
    subject_window.resizable(False, False)
    subject_window.title(f"{subject}")
    subject_window.configure(bg="#1f1f1f")

    subject_data = fetch_subject_data(subject, user_id)

    table_frame = ctk.CTkFrame(subject_window, width=400, height=600, fg_color="#2f2f2f")
    table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
    
    refresh_button_frame = ctk.CTkFrame(subject_window, width=400, height=40, fg_color="#242424")
    refresh_button_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")

    def refresh_table():
        subject_data = fetch_subject_data(subject, user_id)

        for widget in table_frame.winfo_children():
            widget.destroy()

        headers = ["Chapter", "Target Questions", "Questions Solved", "Deadline"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"), text_color="white")
            label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        for row_num, row_data in enumerate(subject_data, start=1):
            for col_num, data in enumerate(row_data):
                label = ctk.CTkLabel(table_frame, text=str(data), font=("Arial", 12), text_color="white")
                label.grid(row=row_num, column=col_num, padx=5, pady=5, sticky="nsew")

    refresh_button = ctk.CTkButton(refresh_button_frame, text="Refresh Table", command=refresh_table,
                                    width=150, height=40, fg_color="#4CAF50", hover_color="#45a049",
                                    text_color="white", font=("Arial", 16, "bold"), corner_radius=10)
    refresh_button.place(relx=0.5, rely=0.5, anchor="center")
    
    headers = ["Chapter", "Target Questions", "Questions Solved", "Deadline"]
    for col, header in enumerate(headers):
        label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"), text_color="white")
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    table_frame.grid_columnconfigure(0, weight=2)
    table_frame.grid_columnconfigure(1, weight=1)
    table_frame.grid_columnconfigure(2, weight=1)
    table_frame.grid_columnconfigure(3, weight=1)

    for row_num, row_data in enumerate(subject_data, start=1):
        for col_num, data in enumerate(row_data):
            label = ctk.CTkLabel(table_frame, text=str(data), font=("Arial", 12), text_color="white")
            label.grid(row=row_num, column=col_num, padx=5, pady=5, sticky="nsew")

    schedule_button = ctk.CTkButton(subject_window, text="Schedule", command=lambda: create_schedule_window(subject, user_id, subject_window), 
                                    width=150, height=60, 
                                    fg_color="#90A4AE", hover_color="#78909C", text_color="white", font=("Arial", 18, "bold"),
                                    corner_radius=20, border_width=2, border_color="#607D8B")
    schedule_button.place(relx=0.1, rely=0.4, anchor="w", x=800)
    
    update_button = ctk.CTkButton(subject_window, text="Update", command=lambda: create_update_window(subject, user_id, subject_window), 
                                    width=150, height=60, 
                                    fg_color="#90A4AE", hover_color="#78909C", text_color="white", font=("Arial", 18, "bold"),
                                    corner_radius=20, border_width=2, border_color="#607D8B")
    update_button.place(relx=0.1, rely=0.6, anchor="w", x=800)

    subject_window.grid_columnconfigure(0, weight=1)
    subject_window.grid_columnconfigure(1, weight=1)

    main_screen.withdraw()

    subject_window.protocol("WM_DELETE_WINDOW", lambda: close_subject_window(subject_window, main_screen))

    subject_window.mainloop()

def close_subject_window(subject_window, main_screen):
    subject_window.destroy()
    main_screen.deiconify()

def create_main_screen(username, user_id):
    main_screen = ctk.CTk()
    main_screen.geometry("1280x720") 
    main_screen.title("Meletora")
    main_screen.configure(bg="#1f1f1f")
    main_screen.resizable(False, False)

    main_screen.columnconfigure(0, weight=1)
    main_screen.rowconfigure(0, weight=1)

    top_frame = ctk.CTkFrame(main_screen)
    top_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    top_frame.columnconfigure(0, weight=1)

    welcome_label = ctk.CTkLabel(top_frame, text=f"Welcome, {username}", font=("Arial", 36), text_color="white")
    welcome_label.grid(row=0, column=0, pady=(40, 10), sticky="n")

    current_date = time.strftime("%B %d, %Y")
    
    date_label = ctk.CTkLabel(top_frame, text=f"Today is {current_date}", font=("Arial", 24), text_color="white")
    date_label.grid(row=1, column=0, pady=(0, 20), sticky="n")

    clock_canvas = ctk.CTkCanvas(main_screen, width=400, height=400, background="#2b2b2b", highlightthickness=0)
    clock_canvas.place(relx=0.0, rely=0.5, anchor="w", x=20)

    clock_canvas.create_oval(50, 50, 350, 350, outline="white", width=3)

    hour_hand = clock_canvas.create_line(150, 150, 150, 100, width=8, fill="white", capstyle="round", smooth=True)
    minute_hand = clock_canvas.create_line(150, 150, 150, 70, width=6, fill="white", capstyle="round", smooth=True)
    second_hand = clock_canvas.create_line(150, 150, 150, 50, width=2, fill="red", capstyle="round", smooth=True)

    center_x, center_y = 200, 200
    radius = 150

    update_analog_clock(clock_canvas, hour_hand, minute_hand, second_hand, center_x, center_y, radius)

    btn_physics = ctk.CTkButton(main_screen, text="Physics", command=lambda: create_subject_window("Physics", user_id, main_screen), 
                                width=180, height=60, 
                                fg_color="#90A4AE", hover_color="#78909C", text_color="white", font=("Arial", 18, "bold"),
                                corner_radius=20, border_width=2, border_color="#607D8B")
    btn_physics.place(relx=0.1, rely=0.5, anchor="w", x=320)

    btn_chemistry = ctk.CTkButton(main_screen, text="Chemistry", command=lambda: create_subject_window("Chemistry", user_id,  main_screen), 
                                  width=180, height=60,
                                  fg_color="#90A4AE", hover_color="#78909C", text_color="white", font=("Arial", 18, "bold"),
                                  corner_radius=20, border_width=2, border_color="#607D8B")
    btn_chemistry.place(relx=0.3, rely=0.5, anchor="w", x=320)

    btn_math = ctk.CTkButton(main_screen, text="Math", command=lambda: create_subject_window("Mathematics", user_id, main_screen), 
                             width=180, height=60,
                             fg_color="#90A4AE", hover_color="#78909C", text_color="white", font=("Arial", 18, "bold"),
                             corner_radius=20, border_width=2, border_color="#607D8B")
    btn_math.place(relx=0.5, rely=0.5, anchor="w", x=320)

    main_screen.mainloop()
