import os
import sys
import winreg as reg

def add_to_registry():
    script_path = os.path.abspath(sys.argv[0])

    python_path = sys.executable

    key = reg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value_name = "MyDailyNotification" 
    command = f'"{python_path}" "{script_path}"'

    try:
        reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
        reg.SetValueEx(reg_key, value_name, 0, reg.REG_SZ, command)
        reg.CloseKey(reg_key)
        print("Added to startup successfully!")
    except Exception as e:
        print(f"Failed to add to startup: {e}")

def send_notification():
    from plyer import notification
    notification.notify(
        title='Hey there, star pupil!',
        message='Deadline\'s closing in, don\'t forget to brush up those questions!',
        timeout=20,
        app_name = 'Meletora'
    )

add_to_registry()
send_notification()
