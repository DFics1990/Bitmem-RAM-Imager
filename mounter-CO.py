import os
import subprocess
from tkinter import Tk, filedialog, Button, Label, messagebox

class RAMImageToolWindows:
    def __init__(self, root):
        self.root = root
        self.root.title("RAM Image Mounting Tool")
        self.root.geometry("400x200")

        self.file_label = Label(root, text="Select a RAM image file (.raw):", pady=10)
        self.file_label.pack()

        self.select_button = Button(root, text="Choose File", command=self.choose_file, pady=5)
        self.select_button.pack()

        self.mount_button = Button(root, text="Mount RAM Image", command=self.mount_raw_image, state="disabled", pady=5)
        self.mount_button.pack()

        self.status_label = Label(root, text="No file selected.", pady=10, fg="blue")
        self.status_label.pack()

        self.file_path = None

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("RAW Files", "*.raw")])
        if self.file_path:
            self.status_label.config(text=f"Selected File: {os.path.basename(self.file_path)}")
            self.mount_button.config(state="normal")
        else:
            messagebox.showinfo("No File Selected", "Please select a valid .raw file.")

    def mount_raw_image(self):
        if self.file_path:
            try:
                mount_point = "Z:"  # Example drive letter
                command = f'imdisk -a -t file -f "{self.file_path}" -m {mount_point}'
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    messagebox.showinfo("Success", f"The RAM image is mounted at {mount_point}.")
                    self.status_label.config(text=f"Mounted at {mount_point}", fg="green")
                else:
                    messagebox.showerror("Mount Failed", f"Error:\n{result.stderr.strip()}")
                    self.status_label.config(text="Failed to mount.", fg="red")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
                self.status_label.config(text=f"Error: {str(e)}", fg="red")
        else:
            messagebox.showwarning("No File", "Please select a file first.")

if __name__ == "__main__":
    root = Tk()
    app = RAMImageToolWindows(root)
    root.mainloop()