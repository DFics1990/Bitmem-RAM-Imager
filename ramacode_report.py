import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import hashlib
from datetime import datetime
import time
import json  # For saving and loading used IDs

# File to store used IDs
USED_IDS_FILE = "used_ids.json"

# Load used IDs from file (if it exists)
def load_used_ids():
    if os.path.exists(USED_IDS_FILE):
        with open(USED_IDS_FILE, "r") as f:
            return json.load(f)
    return {"investigator_ids": set(), "case_ids": set(), "memory_ids": set()}

# Save used IDs to file
def save_used_ids(used_ids):
    with open(USED_IDS_FILE, "w") as f:
        json.dump({k: list(v) for k, v in used_ids.items()}, f)

# Global sets to store used IDs (loaded from file)
used_ids = load_used_ids()
used_investigator_ids = set(used_ids["investigator_ids"])
used_case_ids = set(used_ids["case_ids"])
used_memory_ids = set(used_ids["memory_ids"])

def calculate_hash(file_path, algorithm="sha256"):
    """Calculate the hash value of a file."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def generate_report(output_file, investigator_name, investigator_id, case_name, case_id, memory_id, hash_value, image_size, elapsed_time):
    """Generate a report with the capture details, including elapsed time."""
    # Create a professional report file name based on the case name
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
    """Validate that the entered IDs are unique."""
    errors = []
    
    if investigator_id in used_investigator_ids:
        errors.append("Investigator ID is already in use.")
    if case_id in used_case_ids:
        errors.append("Case ID is already in use.")
    if memory_id in used_memory_ids:
        errors.append("Memory ID is already in use.")
    
    return errors

def capture_memory_image(progress_bar, progress_label, investigator_name, investigator_id, case_name, case_id, memory_id):
    # Validate IDs
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
    
    # Determine the path to winpmem_mini executable relative to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    winpmem_path = os.path.join(script_dir, "winpmem_mini.exe")
    
    # Ask user where to save the memory image
    output_file = filedialog.asksaveasfilename(
        title="Select location to save memory image",
        defaultextension=".raw",
        filetypes=[("RAW files", "*.raw"), ("All Files", "*.*")]
    )
    
    if not output_file:
        messagebox.showerror("Error", "No file selected. Exiting.")
        return
    
    # Ensure the directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Command to capture memory image
    command = [winpmem_path, output_file]
    
    def run_capture():
        progress_label.config(text="Capturing memory image...")
        progress_bar.start()
        
        try:
            # Record the start time
            start_time = time.time()
            
            # Run the command and capture output
            process = subprocess.run(command, capture_output=True, text=True)
            
            # Check if the memory image file was created
            if not os.path.exists(output_file):
                progress_label.config(text="Capture failed!")
                messagebox.showerror("Error", "Memory image file was not created.")
                return
            
            # Calculate hash value
            hash_value = calculate_hash(output_file)
            
            # Get image size
            image_size = os.path.getsize(output_file)
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Generate report
            report_file = generate_report(output_file, investigator_name, investigator_id, case_name, case_id, memory_id, hash_value, image_size, elapsed_time)
            
            # Add IDs to the used sets (simulating database insertion)
            used_investigator_ids.add(investigator_id)
            used_case_ids.add(case_id)
            used_memory_ids.add(memory_id)
            
            # Save used IDs to file
            save_used_ids({
                "investigator_ids": used_investigator_ids,
                "case_ids": used_case_ids,
                "memory_ids": used_memory_ids,
            })
            
            # Treat the capture as successful if the memory image file was created
            progress_label.config(text="Capture complete!")
            messagebox.showinfo("Success", f"RAM image captured successfully!\nSaved at: {output_file}\nReport saved at: {report_file}")
        except Exception as e:
            progress_label.config(text="Capture failed!")
            messagebox.showerror("Error", f"An exception occurred: {str(e)}")
        finally:
            progress_bar.stop()
    
    threading.Thread(target=run_capture, daemon=True).start()

def create_gui():
    root = tk.Tk()
    root.title("Memory Capture Tool")
    root.geometry("400x350")
    
    # Investigator Details
    tk.Label(root, text="Investigator Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    investigator_name_entry = tk.Entry(root)
    investigator_name_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(root, text="Investigator ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    investigator_id_entry = tk.Entry(root)
    investigator_id_entry.grid(row=1, column=1, padx=10, pady=5)
    
    # Case Details
    tk.Label(root, text="Case Name:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    case_name_entry = tk.Entry(root)
    case_name_entry.grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(root, text="Case ID:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    case_id_entry = tk.Entry(root)
    case_id_entry.grid(row=3, column=1, padx=10, pady=5)
    
    # Memory ID
    tk.Label(root, text="Memory ID:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    memory_id_entry = tk.Entry(root)
    memory_id_entry.grid(row=4, column=1, padx=10, pady=5)
    
    # Capture Button
    capture_button = tk.Button(
        root,
        text="Capture Memory Image",
        command=lambda: capture_memory_image(
            progress_bar,
            progress_label,
            investigator_name_entry.get(),
            investigator_id_entry.get(),
            case_name_entry.get(),
            case_id_entry.get(),
            memory_id_entry.get()
        )
    )
    capture_button.grid(row=5, column=0, columnspan=2, pady=10)
    
    # Progress Bar and Label
    progress_label = tk.Label(root, text="")
    progress_label.grid(row=6, column=0, columnspan=2, pady=5)
    
    progress_bar = ttk.Progressbar(root, mode='indeterminate', length=200)
    progress_bar.grid(row=7, column=0, columnspan=2, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()