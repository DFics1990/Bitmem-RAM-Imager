# Combined and Integrated Code (gui.py + RAM imaging tool)
import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import hashlib
from datetime import datetime
import time
import json

# From your original GUI code
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage

# File to store used IDs
USED_IDS_FILE = "used_ids.json"

# Load used IDs from file (if it exists)
def load_used_ids():
    if os.path.exists(USED_IDS_FILE):
        with open(USED_IDS_FILE, "r") as f:
            data = json.load(f)
            return {
                "investigator_ids": set(data["investigator_ids"]),
                "case_ids": set(data["case_ids"]),
                "memory_ids": set(data["memory_ids"])
            }
    return {"investigator_ids": set(), "case_ids": set(), "memory_ids": set()}

# Save used IDs to file
def save_used_ids(used_ids):
    with open(USED_IDS_FILE, "w") as f:
        json.dump({k: list(v) for k, v in used_ids.items()}, f)

# Global sets to store used IDs
used_ids = load_used_ids()
used_investigator_ids = used_ids["investigator_ids"]
used_case_ids = used_ids["case_ids"]
used_memory_ids = used_ids["memory_ids"]

def calculate_hash(file_path, algorithm="sha256"):
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def generate_report(output_file, investigator_name, investigator_id, case_name, case_id, memory_id, hash_value, image_size, elapsed_time):
    report_file_name = f"Case-{case_name.replace(' ', '_')}_Report.txt"
    report_file = os.path.join(os.path.dirname(output_file), report_file_name)
    
    capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_content = f"""
    Memory Capture Report
    =====================
    Investigator Name: {investigator_name}
    Investigator ID: {investigator_id}
    Case Name: {case_name}
    Case ID: {case_id}
    Memory ID: {memory_id}
    Capture Date and Time: {capture_time}
    Image Size: {image_size} bytes
    Hash Value ({hashlib.new("sha256").name}): {hash_value}
    Image Location: {output_file}
    Time Taken: {elapsed_time:.2f} seconds
    """
    
    with open(report_file, "w") as f:
        f.write(report_content)
    
    return report_file

def validate_unique_ids(investigator_id, case_id, memory_id):
    errors = []
    if investigator_id in used_investigator_ids:
        errors.append("Investigator ID is already in use.")
    if case_id in used_case_ids:
        errors.append("Case ID is already in use.")
    if memory_id in used_memory_ids:
        errors.append("Memory ID is already in use.")
    return errors

def capture_memory_image(progress_bar, progress_label, investigator_name, investigator_id, case_name, case_id, memory_id):
    # Validate ID formats
    try:
        investigator_id = int(investigator_id)
        case_id = int(case_id)
        memory_id = int(memory_id)
    except ValueError:
        messagebox.showerror("Error", "IDs must be integers.")
        return

    # Check for duplicate IDs
    errors = validate_unique_ids(investigator_id, case_id, memory_id)
    if errors:
        messagebox.showerror("Error", "\n".join(errors))
        return

    # Get winpmem path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    winpmem_path = os.path.join(script_dir, "winpmem_mini.exe")

    # File save dialog
    output_file = filedialog.asksaveasfilename(
        parent=window,
        title="Select location to save memory image",
        defaultextension=".raw",
        filetypes=[("RAW files", "*.raw"), ("All Files", "*.*")]
    )

    if not output_file:
        messagebox.showerror("Error", "No file selected. Exiting.")
        return

    # Ensure directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def run_capture():
        try:
            progress_label.config(text="Capturing memory image...")
            progress_bar.start()

            start_time = time.time()
            process = subprocess.run([winpmem_path, output_file], capture_output=True, text=True)

            if not os.path.exists(output_file):
                progress_label.config(text="Capture failed!")
                messagebox.showerror("Error", "Memory image file was not created.")
                return

            hash_value = calculate_hash(output_file)
            image_size = os.path.getsize(output_file)
            elapsed_time = time.time() - start_time

            report_file = generate_report(
                output_file, investigator_name, investigator_id,
                case_name, case_id, memory_id, hash_value,
                image_size, elapsed_time
            )

            # Update used IDs
            used_investigator_ids.add(investigator_id)
            used_case_ids.add(case_id)
            used_memory_ids.add(memory_id)
            save_used_ids({
                "investigator_ids": used_investigator_ids,
                "case_ids": used_case_ids,
                "memory_ids": used_memory_ids,
            })

            progress_label.config(text="Capture complete!")
            messagebox.showinfo("Success", 
                f"RAM image captured successfully!\n"
                f"Saved at: {output_file}\n"
                f"Report saved at: {report_file}"
            )
        except Exception as e:
            progress_label.config(text="Capture failed!")
            messagebox.showerror("Error", f"An exception occurred: {str(e)}")
        finally:
            progress_bar.stop()

    threading.Thread(target=run_capture, daemon=True).start()

# GUI Setup from Tkinter Designer (modified)
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\HP\Desktop\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.geometry("600x400")
window.configure(bg="#FFFFFF")
window.title("BitMem Memory Capture Tool")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=400,
    width=600,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

# Left sidebar
canvas.create_rectangle(0.0, 0.0, 270.0, 400.0, fill="#344B65", outline="")

# Entries and labels
entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(387.0, 66.5, image=entry_image_1)
entry_1 = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_1.place(x=285.0, y=53.0, width=204.0, height=25.0)

canvas.create_text(282.0, 33.0, anchor="nw", text="Investigator Name:", 
                 fill="#000000", font=("Inter SemiBold", 16 * -1))

entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(387.0, 120.5, image=entry_image_2)
entry_2 = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_2.place(x=285.0, y=107.0, width=204.0, height=25.0)

canvas.create_text(283.0, 86.0, anchor="nw", text="Investigator ID:", 
                 fill="#000000", font=("Inter SemiBold", 16 * -1))

entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(386.0, 174.5, image=entry_image_3)
entry_3 = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_3.place(x=284.0, y=161.0, width=204.0, height=25.0)

canvas.create_text(282.0, 140.0, anchor="nw", text="Case Name:", 
                 fill="#000000", font=("Inter SemiBold", 16 * -1))

entry_image_5 = PhotoImage(file=relative_to_assets("entry_5.png"))
entry_bg_5 = canvas.create_image(386.0, 228.5, image=entry_image_5)
entry_5 = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_5.place(x=284.0, y=215.0, width=204.0, height=25.0)

canvas.create_text(282.0, 194.0, anchor="nw", text="Case ID:", 
                 fill="#000000", font=("Inter SemiBold", 16 * -1))

entry_image_4 = PhotoImage(file=relative_to_assets("entry_4.png"))
entry_bg_4 = canvas.create_image(386.0, 282.5, image=entry_image_4)
entry_4 = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_4.place(x=284.0, y=269.0, width=204.0, height=25.0)

canvas.create_text(282.0, 248.0, anchor="nw", text="Memory ID:", 
                 fill="#000000", font=("Inter SemiBold", 16 * -1))

# Progress elements
progress_label = tk.Label(window, text="", bg="#FFFFFF", fg="#000000",
                         font=("Inter SemiBold", 10))
progress_label.place(x=285, y=340)

progress_bar = ttk.Progressbar(window, mode='indeterminate', length=204)
progress_bar.place(x=285, y=365)

# Capture button with adjusted position
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: capture_memory_image(
        progress_bar,
        progress_label,
        entry_1.get(),
        entry_2.get(),
        entry_3.get(),
        entry_5.get(),
        entry_4.get()
    ),
    relief="flat"
)
button_1.place(x=322.0, y=300.0, width=127.0, height=30.0)

# Logo and branding
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(135.0, 134.0, image=image_image_1)
canvas.create_text(96.0, 248.99998255074024, anchor="nw", text="BitMem",
                  fill="#FFFFFF", font=("Inter SemiBold", 24 * -1))

window.resizable(False, False)
window.mainloop()