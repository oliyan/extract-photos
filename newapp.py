import os
import shutil
import multiprocessing
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class DirectoryWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shortlist Photos - by Oliyan Studios")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)

        # Configuration constants
        self.SUPPORTED_EXTENSIONS = ('.cr2', '.cr3', '.arw', '.nef', '.dng', '.jpg', '.jpeg', '.png')
        self.BG_COLOR = '#f0f8ff'

        # Initialize variables
        self.include_xmp = tk.BooleanVar(value=False)
        self.processing = False
        self.cancel_requested = False
        self.progress_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_progress_checker()

    def load_logo(self, parent):
        try:
            img = Image.open("logo.png")
            img = img.resize((180, 180), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(parent, image=self.logo)
            logo_label.pack(pady=(0, 20))
        except FileNotFoundError:
            print("Logo image not found - proceeding without it")
        except Exception as e:
            print(f"Error loading logo: {str(e)}")

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        self.load_logo(main_frame)
        self.create_input_fields(main_frame)
        self.create_control_buttons(main_frame)
        self.create_status_indicators(main_frame)

        main_frame.columnconfigure(0, weight=1)

    def create_input_fields(self, parent):
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill="x", pady=10)

        self.entries = []
        labels = [
            "Client Selected Photos:",
            "Original Photos (RAW):",
            "Where you want to copy:"
        ]

        for idx, label in enumerate(labels):
            frame = ttk.Frame(input_frame)
            frame.pack(fill="x", pady=5)

            ttk.Label(frame, text=label, width=25, anchor="w").pack(side="left", padx=5)
            entry = ttk.Entry(frame, width=40)
            entry.pack(side="left", padx=5, expand=True, fill="x")
            ttk.Button(frame, text="Browse", command=lambda e=entry: self.browse_directory(e)).pack(side="left")

            if idx == 0:
                self.filtered_entry = entry
                ttk.Button(frame, text="Upload text file", command=self.load_from_txt).pack(side="left")

            self.entries.append(entry)

        xmp_frame = ttk.Frame(input_frame)
        xmp_frame.pack(pady=10)
        ttk.Checkbutton(xmp_frame, text="Include XMP Files", variable=self.include_xmp).pack(side="left")

    def create_control_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Reset", command=self.reset_fields).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Process", command=self.process_directories).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side="right", padx=10)

    def create_status_indicators(self, parent):
        self.progress_frame = ttk.Frame(parent)
        self.progress_frame.pack(fill="x", pady=10)
        
        self.progress = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            mode="determinate",
            length=300
        )
        self.progress.pack(fill="x", pady=(0, 5))

        self.status_label = ttk.Label(
            self.progress_frame,
            text="",
            wraplength=600,
            justify="center"
        )
        self.status_label.pack(pady=5)

        # Create cancel button (hidden initially)
        self.cancel_button = ttk.Button(
            self.progress_frame,
            text="Cancel",
            command=self.cancel_operation,
            state="disabled"
        )
        self.cancel_button.pack(pady=5)
        self.cancel_button.pack_forget()

    def setup_progress_checker(self):
        def check_progress():
            try:
                while True:
                    msg = self.progress_queue.get_nowait()
                    if isinstance(msg, tuple):
                        current, total = msg
                        progress_value = (current / total) * 100
                        self.progress["value"] = progress_value
                        self.status_label.config(text=f"Copying files: {current}/{total}")
                    elif isinstance(msg, str):
                        self.status_label.config(text=msg)
            except queue.Empty:
                pass
            finally:
                self.root.after(50, check_progress)  # Check more frequently
        
        self.root.after(50, check_progress)

    def load_from_txt(self):
        if self.processing:
            return

        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            self.filtered_entry.delete(0, tk.END)
            self.filtered_entry.insert(0, filepath)

    def browse_directory(self, entry):
        if self.processing:
            return

        directory = filedialog.askdirectory()
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)

    def reset_fields(self):
        if self.processing:
            return

        for entry in self.entries:
            entry.delete(0, tk.END)
        self.include_xmp.set(False)
        self.progress["value"] = 0
        self.status_label.config(text="")

    def validate_directories(self):
        directories = [entry.get().strip() for entry in self.entries]

        if not all(directories):
            messagebox.showerror("Error", "All directory fields must be filled")
            return False

        for idx, path in enumerate(directories):
            if idx == 0:
                if not (os.path.isdir(path) or os.path.isfile(path)):
                    messagebox.showerror("Error", f"Invalid directory or file: {path}")
                    return False
            else:
                if not os.path.isdir(path):
                    messagebox.showerror("Error", f"Invalid directory: {path}")
                    return False

        job_dir = directories[2]
        if not os.access(job_dir, os.W_OK):
            messagebox.showerror("Error", f"No write permission for: {job_dir}")
            return False

        return True

    def show_cancel_button(self):
        self.cancel_button.pack(pady=5)
        self.cancel_button.config(state="normal")

    def hide_cancel_button(self):
        self.cancel_button.pack_forget()
        self.cancel_button.config(state="disabled")

    def cancel_operation(self):
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the operation?"):
            self.cancel_requested = True
            self.cancel_button.config(state="disabled")
            self.progress_queue.put("Cancelling operation...")

    def get_filtered_files(self, filtered_input):
        if os.path.isdir(filtered_input):
            return {
                os.path.splitext(f)[0].lower()
                for f in os.listdir(filtered_input)
                if os.path.isfile(os.path.join(filtered_input, f))
            }
        elif os.path.isfile(filtered_input):
            try:
                with open(filtered_input, 'r', encoding='utf-8') as f:
                    return {
                        os.path.splitext(line.strip())[0].lower() 
                        for line in f if line.strip()
                    }
            except UnicodeDecodeError:
                try:
                    with open(filtered_input, 'r', encoding='latin-1') as f:
                        return {
                            os.path.splitext(line.strip())[0].lower() 
                            for line in f if line.strip()
                        }
                except Exception as e:
                    messagebox.showerror("Error", f"Could not read file: {e}")
                    return set()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                return set()
        return set()

    def get_files_to_copy(self, main_dir, filtered_files):
        files_to_copy = []
        for filename in os.listdir(main_dir):
            base, ext = os.path.splitext(filename)
            ext = ext.lower()

            if base.lower() in filtered_files:
                if ext in self.SUPPORTED_EXTENSIONS:
                    files_to_copy.append(filename)
                elif ext == '.xmp' and self.include_xmp.get():
                    files_to_copy.append(filename)

        return files_to_copy

    def copy_files_sequential(self, files_to_copy, main_dir, job_dir):
        total_files = len(files_to_copy)
        errors = []
        successful_copies = 0

        for idx, filename in enumerate(files_to_copy, 1):
            if self.cancel_requested:
                break

            try:
                src = os.path.join(main_dir, filename)
                dest = os.path.join(job_dir, filename)
                shutil.copy2(src, dest)
                successful_copies += 1
                self.progress_queue.put((idx, total_files))
            except Exception as e:
                errors.append(f"Failed to copy {filename}: {str(e)}")

            # More frequent progress updates
            if idx % 5 == 0 or idx == total_files:
                self.progress_queue.put((idx, total_files))

        return successful_copies, errors

    def process_directories(self):
        if self.processing or not self.validate_directories():
            return

        self.processing = True
        self.cancel_requested = False
        self.show_cancel_button()
        
        threading.Thread(target=self.process_directories_thread, daemon=True).start()

    def process_directories_thread(self):
        try:
            filtered_input, main_dir, job_dir = [e.get().strip() for e in self.entries]
            filtered_files = self.get_filtered_files(filtered_input)
            files_to_copy = self.get_files_to_copy(main_dir, filtered_files)
            
            total_files = len(files_to_copy)
            if total_files == 0:
                self.progress_queue.put("No matching files found!")
                self.root.after(0, lambda: messagebox.showwarning("Warning", "No matching files found to copy!"))
                return

            self.progress_queue.put((0, total_files))
            
            # Use sequential copying for better progress tracking
            successful_copies, errors = self.copy_files_sequential(files_to_copy, main_dir, job_dir)

            if self.cancel_requested:
                self.root.after(0, lambda: messagebox.showinfo("Cancelled", 
                    f"Operation cancelled. {successful_copies} files were copied."))
            elif errors:
                error_message = "\n".join(errors[:10])
                if len(errors) > 10:
                    error_message += f"\n... and {len(errors) - 10} more errors"
                self.root.after(0, lambda: messagebox.showwarning(
                    "Partial Copying Complete",
                    f"Copied {successful_copies}/{total_files} files.\n\n"
                    f"Errors encountered:\n{error_message}"
                ))
            else:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Copied {successful_copies} files successfully!"
                ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Operation failed: {str(e)}"))
            self.progress_queue.put(f"Error: {str(e)}")
        finally:
            self.processing = False
            self.cancel_requested = False
            self.progress_queue.put((total_files, total_files))  # Ensure progress bar reaches 100%
            self.progress_queue.put("")  # Clear status label
            self.root.after(0, self.hide_cancel_button)


if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryWizardApp(root)
    root.mainloop()
