import customtkinter as ctk
import mysql.connector
import re
from tkinter import messagebox

# Set up MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",       # Replace with your MySQL username
    password="",  # Replace with your MySQL password
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS user")
mycursor.execute("USE user")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS details (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        Username VARCHAR(30),
        Password VARCHAR(30)
    )
""")

# Function to validate password
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

# Function for user login
def login_user():
    username = entry_username.get()
    password = entry_password.get()

    if username == "" or password == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    query = "SELECT * FROM details WHERE Username=%s AND Password=%s"
    mycursor.execute(query, (username, password))
    result = mycursor.fetchone()

    if result:
        messagebox.showinfo("Success", "Login Successful!")
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

# Function to open sign up window
def sign_up_window():
    login_win.destroy() 

    signup_win = ctk.CTk()
    signup_win.resizable('False', 'False')
    signup_win.title("Sign Up")

    def register_user():
        username = entry_new_username.get()
        password = entry_new_password.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "All fields are required!")
            return

        if not validate_password(password):
            messagebox.showerror("Error", "Password must be at least 8 characters long, contain uppercase, lowercase, digit, and special character")
            return

        query = "INSERT INTO details (Username, Password) VALUES (%s, %s)"
        mycursor.execute(query, (username, password))
        mydb.commit()

        messagebox.showinfo("Success", "Registration Successful!")
        signup_win.destroy()
        create_login_window()

    ctk.CTkLabel(signup_win, text="Username").grid(row=0, column=0)
    entry_new_username = ctk.CTkEntry(signup_win)
    entry_new_username.grid(row=0, column=1)

    ctk.CTkLabel(signup_win, text="Password").grid(row=1, column=0)
    entry_new_password = ctk.CTkEntry(signup_win, show="*")
    entry_new_password.grid(row=1, column=1)

    btn_register = ctk.CTkButton(signup_win, text="Register", command=register_user)
    btn_register.grid(row=2, column=1)

    signup_win.mainloop()

# Function to create login window
def create_login_window():
    global login_win
    login_win = ctk.CTk()
    login_win.resizable('False', 'False')
    login_win.title("Login")

    ctk.CTkLabel(login_win, text="Username").grid(row=0, column=0)
    global entry_username
    entry_username = ctk.CTkEntry(login_win)
    entry_username.grid(row=0, column=1)

    ctk.CTkLabel(login_win, text="Password").grid(row=1, column=0)
    global entry_password
    entry_password = ctk.CTkEntry(login_win, show="*")
    entry_password.grid(row=1, column=1)

    btn_login = ctk.CTkButton(login_win, text="Login", command=login_user)
    btn_login.grid(row=2, column=1)

    lbl_sign_up = ctk.CTkLabel(login_win, text="Don't have an account? Sign Up", fg_color=None, text_color="blue", cursor="hand2")
    lbl_sign_up.grid(row=3, column=1)
    lbl_sign_up.bind("<Button-1>", lambda e: sign_up_window())

    login_win.mainloop()

# Set CustomTkinter appearance and create login window
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

create_login_window()
