import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import threading
import os

def load_contacts(file_path):
    """
    Load contacts from a text file.
    File format: Name PhoneNumber (e.g., John Doe +1234567890)
    """
    contacts = []
    try:
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                parts = line.split()
                if len(parts) < 2:  # Check if the line contains at least a name and phone number
                    print(f"Skipping invalid line {line_number}: {line}")
                    continue
                name = " ".join(parts[:-1])  # Combine all parts except the last one as the name
                phone = parts[-1]  # Last part is the phone number
                contacts.append({'name': name, 'phone': phone})
                update_table(name, phone, "Pending")
        messagebox.showinfo("Success", f"Loaded {len(contacts)} contacts from file.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load contacts: {e}")
    return contacts

def add_manual_contact():
    """Add a manually typed number to the list."""
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()
    if name and phone:
        contacts.append({'name': name, 'phone': phone})
        update_table(name, phone, "Pending")
        entry_name.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter both name and phone number.")

def update_table(name, phone, status):
    """Update the table with new contact."""
    table.insert("", tk.END, values=(name, phone, status))

def send_messages():
    """Send messages to contacts using Selenium and WhatsApp Web."""
    if not contacts:
        messagebox.showerror("Error", "No contacts to send messages to.")
        return

    if not driver:
        messagebox.showerror("Error", "WhatsApp Web is not open. Please log in first.")
        return

    message = entry_message.get("1.0", tk.END).strip()
    interval = int(entry_interval.get())

    confirm = messagebox.askyesno("Confirm", f"Send this message to {len(contacts)} contacts?")
    if confirm:
        for contact in contacts:
            personalized_message = message.replace('[firstname]', contact['name'])
            print(f"Sending to {contact['name']} ({contact['phone']}): {personalized_message}")
            try:
                # Open chat with the contact
                chat_url = f"https://web.whatsapp.com/send?phone={contact['phone']}&text={personalized_message}"
                driver.get(chat_url)
                time.sleep(10)  # Wait for the chat to load

                # Send the message
                input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                input_box.send_keys(Keys.ENTER)
                time.sleep(2)  # Wait for the message to be sent

                update_table(contact['name'], contact['phone'], "Sent")
            except Exception as e:
                print(f"Failed to send message to {contact['name']}: {e}")
                update_table(contact['name'], contact['phone'], "Failed")
            time.sleep(interval)
        messagebox.showinfo("Done", "All messages sent!")

def browse_file():
    """Open a file dialog to select a contacts file."""
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)
        loaded_contacts = load_contacts(file_path)
        contacts.extend(loaded_contacts)  # Add loaded contacts to the global list

def insert_variable(variable):
    """Insert a variable into the message box."""
    entry_message.insert(tk.END, variable)

def start_whatsapp_web():
    """Start WhatsApp Web using the user's existing Chrome profile."""
    global driver
    try:
        # Get the user's Chrome profile directory
        user_profile_dir = get_user_data_dir()
        
        # Configure Chrome options to use existing profile
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={user_profile_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--start-maximized")
        
        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com")
        messagebox.showinfo("WhatsApp Web", "WhatsApp Web is opening. If you're already logged in, you'll be connected automatically. Otherwise, scan the QR code to log in.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start WhatsApp Web: {e}")

def get_user_data_dir():
    """Get the path to the user's Chrome profile directory."""
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
    elif os.name == 'posix':  # macOS or Linux
        if os.path.exists(os.path.expanduser('~/Library/Application Support/Google/Chrome')):  # macOS
            return os.path.expanduser('~/Library/Application Support/Google/Chrome')
        else:  # Linux
            return os.path.expanduser('~/.config/google-chrome')
    else:
        # Fallback to a default location if OS not recognized
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_profile')

# Create the main window
root = tk.Tk()
root.title("WhatsApp Auto Sender Pro")
root.geometry("1200x800")  # Adjusted window size
root.configure(bg="#f0f0f0")

# Frame for file input
frame_file = tk.Frame(root, bg="#f0f0f0")
frame_file.pack(pady=10, padx=10, fill=tk.X)

label_file_path = tk.Label(frame_file, text="Contacts File:", bg="#f0f0f0")
label_file_path.grid(row=0, column=0, padx=10, pady=10)
entry_file_path = tk.Entry(frame_file, width=40)
entry_file_path.grid(row=0, column=1, padx=10, pady=10)
button_browse = tk.Button(frame_file, text="Browse", command=browse_file)
button_browse.grid(row=0, column=2, padx=10, pady=10)

# Frame for manual input
frame_manual = tk.Frame(root, bg="#f0f0f0")
frame_manual.pack(pady=10, padx=10, fill=tk.X)

label_name = tk.Label(frame_manual, text="Name:", bg="#f0f0f0")
label_name.grid(row=0, column=0, padx=10, pady=10)
entry_name = tk.Entry(frame_manual, width=20)
entry_name.grid(row=0, column=1, padx=10, pady=10)

label_phone = tk.Label(frame_manual, text="Phone Number:", bg="#f0f0f0")
label_phone.grid(row=0, column=2, padx=10, pady=10)
entry_phone = tk.Entry(frame_manual, width=20)
entry_phone.grid(row=0, column=3, padx=10, pady=10)

button_add = tk.Button(frame_manual, text="Add Contact", command=add_manual_contact)
button_add.grid(row=0, column=4, padx=10, pady=10)

# Frame for message input
frame_message = tk.Frame(root, bg="#f0f0f0")
frame_message.pack(pady=10, padx=10, fill=tk.X)

label_message = tk.Label(frame_message, text="Message (use [firstname], [negrito], [sublinhado]):", bg="#f0f0f0")
label_message.grid(row=0, column=0, padx=10, pady=10)
entry_message = tk.Text(frame_message, width=80, height=10)
entry_message.grid(row=1, column=0, columnspan=5, padx=10, pady=10)

# Frame for variables
frame_variables = tk.Frame(root, bg="#f0f0f0")
frame_variables.pack(pady=10, padx=10, fill=tk.X)

button_firstname = tk.Button(frame_variables, text="[firstname]", command=lambda: insert_variable("[firstname]"))
button_firstname.grid(row=0, column=0, padx=5, pady=5)

button_negrito = tk.Button(frame_variables, text="[negrito]", command=lambda: insert_variable("[negrito]"))
button_negrito.grid(row=0, column=1, padx=5, pady=5)

button_sublinhado = tk.Button(frame_variables, text="[sublinhado]", command=lambda: insert_variable("[sublinhado]"))
button_sublinhado.grid(row=0, column=2, padx=5, pady=5)

# Frame for interval input and start button
frame_interval = tk.Frame(root, bg="#f0f0f0")
frame_interval.pack(pady=10, padx=10, fill=tk.X)

label_interval = tk.Label(frame_interval, text="Interval (in seconds):", bg="#f0f0f0")
label_interval.grid(row=0, column=0, padx=10, pady=10)
entry_interval = tk.Entry(frame_interval, width=10)
entry_interval.grid(row=0, column=1, padx=10, pady=10)

button_start = tk.Button(frame_interval, text="Start Sending", command=send_messages, bg="#4CAF50", fg="white", font=("Arial", 12))
button_start.grid(row=0, column=2, padx=10, pady=10)

# Frame for the table
frame_table = tk.Frame(root, bg="#f0f0f0")
frame_table.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

columns = ("Name", "Phone Number", "Status")
table = ttk.Treeview(frame_table, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
table.pack(fill=tk.BOTH, expand=True)

# Button to start WhatsApp Web
button_whatsapp = tk.Button(root, text="Open WhatsApp Web", command=start_whatsapp_web, bg="#2196F3", fg="white", font=("Arial", 12))
button_whatsapp.pack(pady=10)

# Run the application
contacts = []
driver = None  # Selenium WebDriver instance
root.mainloop()
