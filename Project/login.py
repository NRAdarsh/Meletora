import customtkinter as ctk
import mysql.connector
import re
from tkinter import messagebox
import os

USER_FILE_PATH = 'users.txt'

if not os.path.exists(USER_FILE_PATH):
    with open(USER_FILE_PATH, 'w') as file:
        pass

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", #Enter SQL Password
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS user")
    mycursor.execute("USE user")
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS details (
            UserID VARCHAR(30) PRIMARY KEY,
            Username VARCHAR(30) UNIQUE,
            Password VARCHAR(100)
        )
    """)
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Error connecting to the database: {err}")
    exit()

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[@_#$%^&+=]", password):
        return False
    return True

def generate_unique_user_id():
    mycursor.execute("SELECT UserID FROM details")
    existing_ids = {row[0] for row in mycursor.fetchall()}
    
    i = 1
    while True:
        user_id = f"user{i}"
        if user_id not in existing_ids:
            return user_id
        i += 1

def login_user():
    username = entry_username.get()
    password = entry_password.get()

    if username == "" or password == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    query = "SELECT Password FROM details WHERE Username=%s"
    mycursor.execute(query, (username,))
    result = mycursor.fetchone()

    if result and result[0] == password:
        login_win.destroy()
        
        create_resizable_window(username)
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

def create_resizable_window(username):
    resizable_win = ctk.CTk()
    resizable_win.geometry("1280x720") 
    resizable_win.title("Excalibur")
    resizable_win.configure(bg="#1f1f1f")
    resizable_win.resizable(True, True) 

    resizable_win.columnconfigure(0, weight=1)
    resizable_win.rowconfigure(0, weight=1)
    
    main_frame = ctk.CTkFrame(resizable_win)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)
    
    welcome_label = ctk.CTkLabel(main_frame, text=f"Welcome, {username}", font=("Arial", 36), text_color="white")
    welcome_label.grid(row=0, column=0, pady=(40, 20), sticky="n")

    content_label = ctk.CTkLabel(main_frame, text="This area is for future content.", font=("Arial", 24), text_color="white")
    content_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    btn_logout = ctk.CTkButton(main_frame, text="Logout", command=resizable_win.destroy, width=120, fg_color="#f44336", hover_color="#e53935")
    btn_logout.grid(row=2, column=0, pady=(20, 40), sticky="s")

    resizable_win.mainloop()

def create_user_database_and_tables(user_id):
    try:
        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS `{user_id}`")
        mycursor.execute(f"USE `{user_id}`")

        tables = ['Physics', 'Chemistry', 'Mathematics']
        for table in tables:
            mycursor.execute(f"""
                CREATE TABLE IF NOT EXISTS `{table}` (
                    Chapter VARCHAR(45) PRIMARY KEY,
                    Target_Questions INT,
                    Questions_Solved INT DEFAULT 0,
                    Last_Date_Reviewed DATE,
                    Deadline DATE
                )
            """)
        mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
        messagebox.showerror("Error", f"Error creating user database or tables: {err}")

def register_user():
    username = entry_new_username.get()
    password = entry_new_password.get()

    if username == "" or password == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    if not validate_password(password):
        messagebox.showerror("Error", "Password must be at least 8 characters long, contain uppercase, lowercase, digit, and special character")
        return

    unique_user_id = generate_unique_user_id()

    query = "INSERT INTO details (UserID, Username, Password) VALUES (%s, %s, %s)"
    try:
        mycursor.execute(query, (unique_user_id, username, password))
        mydb.commit()

        create_user_database_and_tables(unique_user_id)

        with open(USER_FILE_PATH, 'a') as file:
            file.write(f"{unique_user_id}\n")

        messagebox.showinfo("Success", f"Registration Successful! Your User ID is {unique_user_id}")
        signup_win.destroy()
        create_login_window()
    except mysql.connector.Error as err:
        mydb.rollback()
        messagebox.showerror("Error", f"Registration failed: {err}")

def sign_up_window():
    global signup_win
    login_win.destroy()

    signup_win = ctk.CTk()
    signup_win.geometry("420x450")
    signup_win.resizable('False', 'False')
    signup_win.title("Sign Up")
    signup_win.configure(bg="#1f1f1f")

    ctk.CTkLabel(signup_win, text="Create an Account", font=("Arial", 26), text_color="white").pack(pady=15)

    ctk.CTkLabel(signup_win, text="Username", text_color="white").pack(pady=5)
    global entry_new_username
    entry_new_username = ctk.CTkEntry(signup_win, width=240, corner_radius=10)
    entry_new_username.pack(pady=5)

    ctk.CTkLabel(signup_win, text="Password", text_color="white").pack(pady=5)
    global entry_new_password
    entry_new_password = ctk.CTkEntry(signup_win, width=240, show="*", corner_radius=10)
    entry_new_password.pack(pady=5)

    btn_register = ctk.CTkButton(signup_win, text="Register", command=register_user, width=160, fg_color="#4CAF50", hover_color="#66bb6a")
    btn_register.pack(pady=20)

    signup_win.mainloop()

def create_login_window():
    global login_win
    login_win = ctk.CTk()
    login_win.geometry("420x500")
    login_win.resizable('False', 'False')
    login_win.title("Login")
    login_win.configure(bg="#1f1f1f")

    ctk.CTkLabel(login_win, text="Excalibur", font=("Arial", 28), text_color="white").pack(pady=20)

    frame = ctk.CTkFrame(login_win, width=320, height=280, corner_radius=15, bg_color="#2f2f2f")
    frame.pack(pady=30)

    ctk.CTkLabel(frame, text="Login", font=("Arial", 20), text_color="white").pack(pady=15)

    ctk.CTkLabel(frame, text="Username", text_color="white").pack(pady=5)
    global entry_username
    entry_username = ctk.CTkEntry(frame, width=200, corner_radius=10)
    entry_username.pack(pady=5)

    ctk.CTkLabel(frame, text="Password", text_color="white").pack(pady=5)
    global entry_password
    entry_password = ctk.CTkEntry(frame, width=200, show="*", corner_radius=10)
    entry_password.pack(pady=5)

    btn_login = ctk.CTkButton(frame, text="Login", command=login_user, width=120, fg_color="#4CAF50", hover_color="#66bb6a")
    btn_login.pack(pady=20)

    lbl_sign_up = ctk.CTkLabel(frame, text="Don't have an account? Sign Up", fg_color=None, text_color="#ADD8E6", cursor="hand2")
    lbl_sign_up.pack(pady=10)
    lbl_sign_up.bind("<Button-1>", lambda e: sign_up_window())

    login_win.mainloop()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

create_login_window()
