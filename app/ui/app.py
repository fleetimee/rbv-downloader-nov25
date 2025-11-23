import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
from app.ui.layout import LayoutBuilder
from app.ui.config_manager import ConfigManager
from app.ui.utils import open_folder
from download_images import download_images
from app.core.config import HEADERS

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RBV Downloader")
        self.root.geometry("500x720")
        
        self.config = ConfigManager.load_config()
        self.stop_event = threading.Event()
        
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