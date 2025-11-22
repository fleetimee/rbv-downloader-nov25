import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import json
from download_images import download_images, HEADERS

CONFIG_FILE = "config.json"

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RBV Downloader")
        self.root.geometry("500x720") # Increased height for logo + extra field
        
        # Load saved config
        self.config = self.load_config()
        
        self.create_widgets()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
        
    def load_config(self):
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "RBV-Downloader")
        defaults = {
            "module_code": "", 
            "phpsessid": "", 
            "sucuri_cookie": "",
            "download_path": default_path
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    # Update defaults with loaded data (preserves new keys if missing in file)
                    defaults.update(loaded)
                    return defaults
            except:
                pass
        return defaults

    def save_config(self):
        data = {
            "module_code": self.module_code_var.get(),
            "phpsessid": self.phpsessid_var.get(),
            "sucuri_cookie": self.sucuri_cookie_var.get(),
            "download_path": self.download_path_var.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.download_path_var.get())
        if folder_selected:
            self.download_path_var.set(folder_selected)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Logo & Header (Centered) ---
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Inner container to hold Logo + Text centered together
        logo_container = ttk.Frame(header_frame)
        logo_container.pack(anchor="center")

        # Try to load logo
        try:
            icon_path = self.resource_path("assets/icon.png")
            logo_path = self.resource_path("assets/logo.png")
            
            self.logo_img = tk.PhotoImage(file=icon_path) 
            # 512 / 8 = 64px. Much cleaner.
            self.header_logo = tk.PhotoImage(file=logo_path).subsample(8, 8) 
            
            lbl_logo = ttk.Label(logo_container, image=self.header_logo)
            lbl_logo.pack(side=tk.LEFT, padx=(0, 15))
            
            # Set Window Icon
            self.root.iconphoto(True, self.logo_img)
        except Exception as e:
            print(f"Could not load logo: {e}")
            
        title_label = ttk.Label(logo_container, text="RBV Downloader", font=("Helvetica", 22, "bold"))
        title_label.pack(side=tk.LEFT, anchor="center")
        # ---------------------

        # Input Frame for better alignment
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Module Code
        ttk.Label(input_frame, text="Module Code (e.g., ADBI421103):", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.module_code_var = tk.StringVar(value=self.config.get("module_code"))
        ttk.Entry(input_frame, textvariable=self.module_code_var, font=("Helvetica", 12)).pack(fill=tk.X, pady=(0, 15), ipady=3)
        
        # PHPSESSID
        ttk.Label(input_frame, text="PHPSESSID:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.phpsessid_var = tk.StringVar(value=self.config.get("phpsessid"))
        ttk.Entry(input_frame, textvariable=self.phpsessid_var, font=("Helvetica", 12)).pack(fill=tk.X, pady=(0, 15), ipady=3)
        
        # Sucuri Cookie
        ttk.Label(input_frame, text="Sucuri Cookie:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.sucuri_cookie_var = tk.StringVar(value=self.config.get("sucuri_cookie"))
        ttk.Entry(input_frame, textvariable=self.sucuri_cookie_var, font=("Helvetica", 12)).pack(fill=tk.X, pady=(0, 15), ipady=3)
        
        # Download Path
        ttk.Label(input_frame, text="Download Path:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.download_path_var = tk.StringVar(value=self.config.get("download_path"))
        ttk.Entry(path_frame, textvariable=self.download_path_var, font=("Helvetica", 12)).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT, padx=(5, 0))

        # Save Note
        ttk.Label(main_frame, text="* Settings are saved automatically", font=("Arial", 11, "italic"), foreground="gray").pack(anchor="w", pady=(0, 20))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Style for larger buttons
        style = ttk.Style()
        style.configure("Big.TButton", font=("Helvetica", 12))

        self.start_btn = ttk.Button(btn_frame, text="Start Download", command=self.start_download_thread, style="Big.TButton")
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        
        self.open_btn = ttk.Button(btn_frame, text="Open Folder", command=self.open_folder, style="Big.TButton")
        self.open_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=5)
        
        # Log Area
        ttk.Label(main_frame, text="Logs:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.log_area = scrolledtext.ScrolledText(main_frame, height=15, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, str(message) + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        
    def start_download_thread(self):
        module_code = self.module_code_var.get().strip()
        phpsessid = self.phpsessid_var.get().strip()
        sucuri_cookie = self.sucuri_cookie_var.get().strip()
        download_path = self.download_path_var.get().strip()
        
        if not module_code or not phpsessid or not sucuri_cookie:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if not download_path:
             messagebox.showerror("Error", "Download path is required!")
             return

        self.save_config()
        self.start_btn.config(state='disabled')
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        
        threading.Thread(target=self.run_download, args=(module_code, phpsessid, sucuri_cookie, download_path), daemon=True).start()
        
    def run_download(self, module_code, phpsessid, sucuri_cookie, download_path):
        try:
            subfolder = f"{module_code}/"
            output_dir = os.path.join(download_path, module_code)
            
            headers = HEADERS.copy()
            headers['Referer'] = f'https://pustaka.ut.ac.id/reader/index.php?modul={module_code}'
            headers['Cookie'] = f"PHPSESSID={phpsessid}; {sucuri_cookie}"
            
            self.log(f"Starting download for {module_code}...")
            self.log(f"Saving to: {output_dir}")
            
            # We pass self.log as the log_callback
            download_images(module_code, subfolder, output_dir, headers, log_callback=self.log)
            
            self.log("-----------------------------------")
            self.log("Download Completed!")
            messagebox.showinfo("Success", f"Download for {module_code} completed!")
            
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.root.after(0, lambda: self.start_btn.config(state='normal'))

    def open_folder(self):
        path = self.download_path_var.get().strip()
        if not path:
            path = os.path.abspath("downloads") # Fallback

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                pass # If we can't create it (e.g. empty path), just ignore
        
        if os.name == 'nt': # Windows
            os.startfile(path)
        elif os.name == 'posix': # macOS/Linux
            # Try 'open' for Mac, 'xdg-open' for Linux
            os.system(f'open "{path}"' if sys.platform == 'darwin' else f'xdg-open "{path}"')
            
import sys
if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()