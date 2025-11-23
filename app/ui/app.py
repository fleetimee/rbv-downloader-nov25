import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
from app.ui.layout import LayoutBuilder
from app.ui.config_manager import ConfigManager
from app.ui.utils import open_folder
from download_images import download_images
from app.core.config import HEADERS
from app.services.updater import Updater
from app.core.version import VERSION

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"RBV Downloader v{VERSION}")
        self.root.geometry("500x720")
        
        self.config = ConfigManager.load_config()
        self.stop_event = threading.Event()
        self.updater = Updater()
        
        # Variables
        self.module_code_var = tk.StringVar(value=self.config.get("module_code"))
        self.phpsessid_var = tk.StringVar(value=self.config.get("phpsessid"))
        self.sucuri_cookie_var = tk.StringVar(value=self.config.get("sucuri_cookie"))
        self.download_path_var = tk.StringVar(value=self.config.get("download_path"))
        self.progress_var = tk.DoubleVar()
        
        # UI Components (Placeholder for references)
        self.logo_img = None
        self.header_logo = None
        self.start_btn = None
        self.open_btn = None
        self.status_label = None
        self.progress_bar = None
        self.log_area = None
        
        # Build Layout
        self.layout = LayoutBuilder(self)
        self.layout.create_widgets()

        # Create Menu
        self.create_menu()

        # Bind closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Signal the download thread to stop if it's running
        self.stop_event.set()
        
        # Clear inputs except download path before saving
        data_to_save = {
            "module_code": "",  # Clear this
            "phpsessid": "",    # Clear this
            "sucuri_cookie": "", # Clear this
            "download_path": self.download_path_var.get().strip() # Keep this
        }
        ConfigManager.save_config(data_to_save)
        self.root.destroy()


    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.download_path_var.get())
        if folder_selected:
            self.download_path_var.set(folder_selected)

    def log(self, message):
        def _update():
            if self.log_area:
                self.log_area.config(state='normal')
                self.log_area.insert(tk.END, str(message) + "\n")
                self.log_area.see(tk.END)
                self.log_area.config(state='disabled')
        self.root.after(0, _update)

    def update_progress(self, data):
        def _update():
            try:
                doc = data.get("doc", "")
                message = data.get("message", "")
                current_idx = data.get("current_doc_index", 0)
                total = data.get("total_docs", 1)
                
                percent = (current_idx / total) * 100
                
                self.progress_var.set(percent)
                if self.status_label:
                    self.status_label.config(text=f"[{doc}] {message}")
            except Exception as e:
                print(f"Progress Update Error: {e}")

        self.root.after(0, _update)
        
    def start_download_thread(self):
        module_code = self.module_code_var.get().strip()
        phpsessid = self.phpsessid_var.get().strip()
        sucuri_cookie = self.sucuri_cookie_var.get().strip()
        download_path = self.download_path_var.get().strip()
        
        if module_code == "e.g. ADBI421103": module_code = ""
        if phpsessid == "e.g. abcdef1234567890abcdef12345678": phpsessid = ""
        if sucuri_cookie == "e.g. sucuricp_tfca_...=1": sucuri_cookie = ""
        
        if not module_code or not phpsessid or not sucuri_cookie:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if not download_path:
             messagebox.showerror("Error", "Download path is required!")
             return

        # Save config
        ConfigManager.save_config({
            "module_code": module_code,
            "phpsessid": phpsessid,
            "sucuri_cookie": sucuri_cookie,
            "download_path": download_path
        })
        
        self.start_btn.config(text="Stop Process", command=self.stop_download_thread, state='normal')
        self.open_btn.config(state='disabled')
        
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        
        self.progress_var.set(0)
        self.status_label.config(text="Starting...")
        
        self.stop_event.clear()
        threading.Thread(target=self.run_download, args=(module_code, phpsessid, sucuri_cookie, download_path, self.stop_event), daemon=True).start()
        
    def stop_download_thread(self):
        self.log("Stopping download...")
        self.stop_event.set()
        self.start_btn.config(text="Start Download", command=self.start_download_thread, state='normal')
        self.open_btn.config(state='normal')
        self.status_label.config(text="Download Stopped.")
        
    def run_download(self, module_code, phpsessid, sucuri_cookie, download_path, stop_event):
        try:
            subfolder = f"{module_code}/"
            output_dir = os.path.join(download_path, module_code)
            
            headers = HEADERS.copy()
            headers['Referer'] = f'https://pustaka.ut.ac.id/reader/index.php?modul={module_code}'
            headers['Cookie'] = f"PHPSESSID={phpsessid}; {sucuri_cookie}"
            
            self.log(f"Starting download for {module_code}...")
            self.log(f"Saving to: {output_dir}")
            
            download_images(
                module_code, 
                subfolder, 
                output_dir, 
                headers, 
                log_callback=self.log,
                progress_callback=self.update_progress,
                stop_event=stop_event
            )
            
            self.log("-----------------------------------")
            if not stop_event.is_set():
                self.log("Download Completed!")
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: self.status_label.config(text="Download Completed!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Download for {module_code} completed!"))
            else:
                self.log("Download was stopped.")
                
        except Exception as e:
            self.log(f"Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.start_btn.config(text="Start Download", command=self.start_download_thread, state='normal'))
            self.root.after(0, lambda: self.open_btn.config(state='normal'))

    def open_folder_action(self):
        path = self.download_path_var.get().strip()
        open_folder(path)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Check for Updates", command=self.check_for_updates_ui)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_dialog)
        help_menu.add_command(label=f"Version {VERSION}", state="disabled")
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def show_about_dialog(self):
        about_text = (
            f"RBV Downloader v{VERSION}\n\n"
            "A simple tool to download RBV course materials.\n\n"
            "Developed by fleetimee" # Add your name/handle here if desired
        )
        messagebox.showinfo("About RBV Downloader", about_text)

    def check_for_updates_ui(self):
        self.status_label.config(text="Checking for updates...")
        threading.Thread(target=self._check_update_thread, daemon=True).start()

    def _check_update_thread(self):
        available, version_tag = self.updater.check_for_updates()
        if available:
            self.root.after(0, lambda: self.confirm_update(version_tag))
        else:
            self.root.after(0, lambda: messagebox.showinfo("No Updates", f"You are on the latest version ({VERSION})."))
            self.root.after(0, lambda: self.status_label.config(text="Ready"))

    def confirm_update(self, version_tag):
        if messagebox.askyesno("Update Available", f"New version {version_tag} is available. Update now?"):
            self.start_update_download()
        else:
             self.status_label.config(text="Ready")

    def start_update_download(self):
        # Create a progress window
        self.update_window = tk.Toplevel(self.root)
        self.update_window.title("Updating...")
        self.update_window.geometry("300x150")
        
        tk.Label(self.update_window, text="Downloading Update...", pady=10).pack()
        
        self.update_progress_var = tk.DoubleVar()
        import tkinter.ttk as ttk
        pb = ttk.Progressbar(self.update_window, variable=self.update_progress_var, maximum=100)
        pb.pack(fill=tk.X, padx=20, pady=10)
        
        self.update_status = tk.Label(self.update_window, text="0%")
        self.update_status.pack()
        
        threading.Thread(target=self._download_update_thread, daemon=True).start()

    def _download_update_thread(self):
        def progress(current, total):
            if total > 0:
                pct = (current / total) * 100
                self.root.after(0, lambda: self.update_progress_var.set(pct))
                self.root.after(0, lambda: self.update_status.config(text=f"{int(pct)}%"))
            
        file_path = self.updater.download_update(progress_callback=progress)
        
        if file_path:
             self.root.after(0, lambda: self.install_update_ui(file_path))
        else:
             self.root.after(0, lambda: self.update_window.destroy())
             self.root.after(0, lambda: messagebox.showerror("Error", "Download failed."))

    def install_update_ui(self, file_path):
        self.update_window.destroy()
        success, msg = self.updater.install_update(file_path)
        if success:
            if msg == "restart_required":
                 messagebox.showinfo("Update Complete", "Update installed. The application will now restart.")
                 # On Windows, the batch file restarts it. On Linux, we might need to exit.
                 self.root.destroy() 
            else:
                 messagebox.showinfo("Update Downloaded", msg)
        else:
             messagebox.showerror("Update Failed", msg)