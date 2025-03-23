import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar
import hashlib
from datetime import datetime
import time
import psutil  # For system information
from fpdf import FPDF  # For PDF report generation
from PIL import Image, ImageTk  # For background image

# Global sets to store used IDs (simulating a database)
used_investigator_ids = set()
used_case_ids = set()
used_memory_ids = set()

# Configure customtkinter appearance
ctk.set_appearance_mode("Dark")  # Set to Dark mode for a sleek look
ctk.set_default_color_theme("dark-blue")  # Use a dark-blue theme for elegance

# Custom colors (Blue Theme)
DARK_BACKGROUND = "#1E2A38"  # Dark blue
DARK_PRIMARY = "#3498DB"     # Sky blue
DARK_SECONDARY = "#2C3E50"   # Darker blue
DARK_ACCENT = "#2980B9"      # Medium blue
DARK_TEXT = "#ECF0F1"        # Light gray

LIGHT_BACKGROUND = "#FFFFFF"  # White
LIGHT_PRIMARY = "#3498DB"     # Sky blue
LIGHT_SECONDARY = "#BDC3C7"   # Light gray
LIGHT_ACCENT = "#2980B9"      # Medium blue
LIGHT_TEXT = "#2C3E50"        # Dark blue

# Global variables for colors
BACKGROUND_COLOR = DARK_BACKGROUND
PRIMARY_COLOR = DARK_PRIMARY
SECONDARY_COLOR = DARK_SECONDARY
ACCENT_COLOR = DARK_ACCENT
TEXT_COLOR = DARK_TEXT

def calculate_hash(file_path, algorithm="sha256"):
    """Calculate the hash value of a file."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def generate_report(output_file, investigator_name, investigator_id, case_name, case_id, memory_id, hash_value, image_size, elapsed_time, report_format):
    """Generate a report with the capture details, including elapsed time."""
    report_file_name = f"Case-{case_name.replace(' ', '_')}_Report.{report_format}"
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
    
    if report_format == "txt":
        with open(report_file, "w") as f:
            f.write(report_content)
    elif report_format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, report_content)
        pdf.output(report_file)
    
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

def capture_memory_image(progress_bar, progress_label, time_left_label, investigator_name, investigator_id, case_name, case_id, memory_id, report_format):
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
    
    # Ensure winpmem_mini.exe exists
    if not os.path.exists(winpmem_path):
        messagebox.showerror("Error", "winpmem_mini.exe not found. Please ensure it is in the same directory as this script.")
        return
    
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
        progress_label.configure(text="Capturing memory image...", fg_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        progress_bar.set(0)
        time_left_label.configure(text="", fg_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        
        try:
            # Record the start time
            start_time = time.time()
            
            # Run the command and capture output
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Simulate progress (since winpmem doesn't provide real-time progress)
            total_steps = 100
            for i in range(total_steps):
                if process.poll() is not None:
                    break
                time.sleep(0.1)  # Simulate delay
                progress_bar.set((i + 1) / total_steps)
                elapsed_time = time.time() - start_time
                time_left = (total_steps - (i + 1)) * (elapsed_time / (i + 1))
                time_left_label.configure(text=f"Time left: {time_left:.1f} seconds")
                root.update_idletasks()  # Update the GUI
            
            # Check if the memory image file was created
            if not os.path.exists(output_file):
                progress_label.configure(text="Capture failed!")
                time_left_label.configure(text="")
                messagebox.showerror("Error", "Memory image file was not created.")
                return
            
            # Calculate hash value
            hash_value = calculate_hash(output_file)
            
            # Get image size
            image_size = os.path.getsize(output_file)
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Generate report
            report_file = generate_report(output_file, investigator_name, investigator_id, case_name, case_id, memory_id, hash_value, image_size, elapsed_time, report_format)
            
            # Add IDs to the used sets (simulating database insertion)
            used_investigator_ids.add(investigator_id)
            used_case_ids.add(case_id)
            used_memory_ids.add(memory_id)
            
            # Treat the capture as successful if the memory image file was created
            progress_label.configure(text="Capture complete!")
            time_left_label.configure(text="")
            messagebox.showinfo("Success", f"RAM image captured successfully!\nSaved at: {output_file}\nReport saved at: {report_file}")
        except Exception as e:
            progress_label.configure(text="Capture failed!")
            time_left_label.configure(text="")
            messagebox.showerror("Error", f"An exception occurred: {str(e)}")
        finally:
            progress_bar.set(1)
    
    threading.Thread(target=run_capture, daemon=True).start()

def create_gui():
    global root  # Make root global to avoid the "root not defined" error
    root = ctk.CTk()
    root.title("BitMem - Memory Capture Tool")
    root.geometry("900x700")  # Slightly larger window for better spacing

    # Set the icon
    icon_path = "C:\\Users\\rama44\\Downloads\\BitMemicon.ico"
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    # Load and set the background image
    background_image_path = "C:\\Users\\rama44\\Pictures\\backgroundforbitmimjpg.jpg"
    if os.path.exists(background_image_path):
        background_image = Image.open(background_image_path)
        background_image = background_image.resize((900, 700), Image.Resampling.LANCZOS)  # Resize to fit the window
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = ctk.CTkLabel(root, image=background_photo)
        background_label.place(relwidth=1, relheight=1)  # Cover the entire window
        background_label.image = background_photo  # Keep a reference to avoid garbage collection

    # Custom font
    custom_font = ("Segoe UI", 14)

    # Main container frame
    main_frame = ctk.CTkFrame(root, corner_radius=15, fg_color=BACKGROUND_COLOR)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    # Title label
    title_label = ctk.CTkLabel(
        main_frame,
        text="BitMem",
        font=("Segoe UI", 32, "bold"),
        text_color=PRIMARY_COLOR,
    )
    title_label.pack(pady=(20, 10))

    # System Information Button (Top-left corner)
    def show_system_info():
        ram = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/')
        uptime = time.time() - psutil.boot_time()
        uptime_hours = int(uptime // 3600)
        uptime_minutes = int((uptime % 3600) // 60)
        
        info = (
            f"Total RAM: {ram.total / (1024 ** 3):.2f} GB\n"
            f"Used RAM: {ram.used / (1024 ** 3):.2f} GB\n"
            f"CPU Usage: {cpu_usage}%\n"
            f"Disk Usage: {disk_usage.percent}%\n"
            f"System Uptime: {uptime_hours}h {uptime_minutes}m"
        )
        messagebox.showinfo("System Information", info)

    sys_info_button = ctk.CTkButton(main_frame, text="System Info", font=custom_font, fg_color=PRIMARY_COLOR, hover_color=ACCENT_COLOR, command=show_system_info)
    sys_info_button.place(x=20, y=20)  # Place in the top-left corner

    # Input frame
    input_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=SECONDARY_COLOR)
    input_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Centering the input fields
    input_frame.grid_columnconfigure(0, weight=1)
    input_frame.grid_columnconfigure(1, weight=1)

    # Investigator Details (Side by side)
    ctk.CTkLabel(input_frame, text="Investigator Name:", font=custom_font, text_color=TEXT_COLOR).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    investigator_name_entry = ctk.CTkEntry(input_frame, font=custom_font, fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
    investigator_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    ctk.CTkLabel(input_frame, text="Investigator ID:", font=custom_font, text_color=TEXT_COLOR).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    investigator_id_entry = ctk.CTkEntry(input_frame, font=custom_font, fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
    investigator_id_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # Case Details (Side by side)
    ctk.CTkLabel(input_frame, text="Case Name:", font=custom_font, text_color=TEXT_COLOR).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    case_name_entry = ctk.CTkEntry(input_frame, font=custom_font, fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
    case_name_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    ctk.CTkLabel(input_frame, text="Case ID:", font=custom_font, text_color=TEXT_COLOR).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    case_id_entry = ctk.CTkEntry(input_frame, font=custom_font, fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
    case_id_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # Memory ID (Side by side)
    ctk.CTkLabel(input_frame, text="Memory ID:", font=custom_font, text_color=TEXT_COLOR).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    memory_id_entry = ctk.CTkEntry(input_frame, font=custom_font, fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
    memory_id_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    # Report Format Selection (Side by side)
    ctk.CTkLabel(input_frame, text="Report Format:", font=custom_font, text_color=TEXT_COLOR).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    report_format_var = StringVar(value="txt")
    report_format_menu = ctk.CTkOptionMenu(input_frame, variable=report_format_var, values=["txt", "pdf"], font=custom_font, fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
    report_format_menu.grid(row=5, column=1, padx=10, pady=10, sticky="w")

    # Start Capturing Button
    start_capturing_button = ctk.CTkButton(
        main_frame,
        text="Start Capturing",
        font=("Segoe UI", 18, "bold"),
        fg_color=PRIMARY_COLOR,
        hover_color=ACCENT_COLOR,
        width=200,
        height=50,
        command=lambda: capture_memory_image(
            progress_bar,
            progress_label,
            time_left_label,
            investigator_name_entry.get(),
            investigator_id_entry.get(),
            case_name_entry.get(),
            case_id_entry.get(),
            memory_id_entry.get(),
            report_format_var.get()
        )
    )
    start_capturing_button.pack(pady=20)

    # Progress Bar and Label
    progress_label = ctk.CTkLabel(main_frame, text="", font=custom_font, text_color=TEXT_COLOR, fg_color=SECONDARY_COLOR)
    progress_label.pack(pady=10)

    progress_bar = ctk.CTkProgressBar(main_frame, mode="determinate", width=400, fg_color=SECONDARY_COLOR, progress_color=PRIMARY_COLOR)
    progress_bar.pack(pady=10)

    # Time Left Label (Initially empty)
    time_left_label = ctk.CTkLabel(main_frame, text="", font=custom_font, text_color=TEXT_COLOR, fg_color=SECONDARY_COLOR)
    time_left_label.pack(pady=10)

    # Mode Selection Button
    def toggle_mode():
        global BACKGROUND_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, TEXT_COLOR
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            new_mode = "Light"
            BACKGROUND_COLOR = LIGHT_BACKGROUND
            PRIMARY_COLOR = LIGHT_PRIMARY
            SECONDARY_COLOR = LIGHT_SECONDARY
            ACCENT_COLOR = LIGHT_ACCENT
            TEXT_COLOR = LIGHT_TEXT
            mode_button.configure(text="Switch to Dark Mode")
        else:
            new_mode = "Dark"
            BACKGROUND_COLOR = DARK_BACKGROUND
            PRIMARY_COLOR = DARK_PRIMARY
            SECONDARY_COLOR = DARK_SECONDARY
            ACCENT_COLOR = DARK_ACCENT
            TEXT_COLOR = DARK_TEXT
            mode_button.configure(text="Switch to Light Mode")
        ctk.set_appearance_mode(new_mode)
        update_colors(new_mode)

    def update_colors(mode):
        main_frame.configure(fg_color=BACKGROUND_COLOR)
        input_frame.configure(fg_color=SECONDARY_COLOR)
        title_label.configure(text_color=PRIMARY_COLOR)
        progress_label.configure(fg_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        time_left_label.configure(fg_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        for widget in input_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=TEXT_COLOR)
            elif isinstance(widget, ctk.CTkEntry):
                widget.configure(fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)

    mode_button = ctk.CTkButton(main_frame, text="Switch to Light Mode", font=custom_font, fg_color=PRIMARY_COLOR, hover_color=ACCENT_COLOR, command=toggle_mode)
    mode_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()