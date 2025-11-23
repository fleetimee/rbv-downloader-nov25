import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import json
from download_images import download_images, HEADERS

CONFIG_FILE = "config.json"

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip_window, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, font=("Helvetica", 10))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", textvariable=None, **kwargs):
        super().__init__(master, textvariable=textvariable, **kwargs)
        self.placeholder = placeholder
        self.textvariable = textvariable
        self._is_password = kwargs.get("show") == "*"
        
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        
        self.put_placeholder()

    def put_placeholder(self):
        if self.textvariable:
            current_text = self.textvariable.get()
        else:
            current_text = self.get()

        if not current_text:
            self.insert(0, self.placeholder)
            self.config(foreground='grey')
            if self._is_password:
                self.config(show="")

    def foc_in(self, *args):
        if self.textvariable:
            current_text = self.textvariable.get()
        else:
            current_text = self.get()
            
        if current_text == self.placeholder:
            self.delete(0, 'end')
            self.config(foreground='black')
            if self._is_password:
                self.config(show="*")

    def foc_out(self, *args):
        if self.textvariable:
            current_text = self.textvariable.get()
        else:
            current_text = self.get()
            
        if not current_text:
            self.put_placeholder()

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RBV Downloader")
        self.root.geometry("500x720")
        
        self.config = self.load_config()
        self.stop_event = threading.Event() # Initialize the stop event
        self.create_widgets()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
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
                    defaults.update(loaded)
                    return defaults
            except:
                pass
        return defaults

    def save_config(self):
        mc = self.module_code_var.get()
        php = self.phpsessid_var.get()
        sucuri = self.sucuri_cookie_var.get()
        
        # Don't save placeholders
        if mc == "e.g. ADBI421103": mc = ""
        if php == "e.g. abcdef1234567890abcdef12345678": php = ""
        if sucuri == "e.g. sucuricp_tfca_...=1": sucuri = ""

        data = {
            "module_code": mc,
            "phpsessid": php,
            "sucuri_cookie": sucuri,
            "download_path": self.download_path_var.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.download_path_var.get())
        if folder_selected:
            self.download_path_var.set(folder_selected)

    def create_info_icon(self, parent, text):
        """Creates a small '?' icon with a tooltip."""
        # Using a simple label with '?' text as an icon placeholder
        # You can replace this with an actual image icon if preferred
        lbl = tk.Label(parent, text=" (?)", font=("Helvetica", 10, "bold"), foreground="#007acc", cursor="hand2")
        ToolTip(lbl, text)
        return lbl

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        logo_container = ttk.Frame(header_frame)
        logo_container.pack(anchor="center")

        try:
            icon_path = self.resource_path("assets/icon.png")
            logo_path = self.resource_path("assets/logo.png")
            
            self.logo_img = tk.PhotoImage(file=icon_path) 
            self.header_logo = tk.PhotoImage(file=logo_path).subsample(8, 8) 
            
            lbl_logo = ttk.Label(logo_container, image=self.header_logo)
            lbl_logo.pack(side=tk.LEFT, padx=(0, 15))
            
            self.root.iconphoto(True, self.logo_img)
        except Exception as e:
            print(f"Could not load logo: {e}")
            
        title_label = ttk.Label(logo_container, text="RBV Downloader", font=("Helvetica", 22, "bold"))
        title_label.pack(side=tk.LEFT, anchor="center")

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Module Code
        frame_mc = ttk.Frame(input_frame)
        frame_mc.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(frame_mc, text="Module Code:", font=("Helvetica", 12)).pack(side=tk.LEFT)
        
        help_mc = "The Module Code is part of the URL on pustaka.ut.ac.id.\nExample: 'ADBI421103' in .../index.php?modul=ADBI421103"
        self.create_info_icon(frame_mc, help_mc).pack(side=tk.LEFT)
        
        self.module_code_var = tk.StringVar(value=self.config.get("module_code"))
        PlaceholderEntry(input_frame, textvariable=self.module_code_var, placeholder="e.g. ADBI421103", font=("Helvetica", 12)).pack(fill=tk.X, pady=(0, 15), ipady=3)
        
        # PHPSESSID
        frame_php = ttk.Frame(input_frame)
        frame_php.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(frame_php, text="PHPSESSID:", font=("Helvetica", 12)).pack(side=tk.LEFT)
        
        help_php = "1. Open DevTools (F12) -> Network tab.\n2. Refresh page.\n3. Look for 'view.php' request -> Headers -> Cookie.\n4. Copy the 'PHPSESSID' value."
        self.create_info_icon(frame_php, help_php).pack(side=tk.LEFT)
        
        self.phpsessid_var = tk.StringVar(value=self.config.get("phpsessid"))
        PlaceholderEntry(input_frame, textvariable=self.phpsessid_var, placeholder="e.g. abcdef1234567890abcdef12345678", font=("Helvetica", 12)).pack(fill=tk.X, pady=(0, 15), ipady=3)
        
        # Sucuri Cookie
        frame_sucuri = ttk.Frame(input_frame)
        frame_sucuri.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(frame_sucuri, text="Sucuri Cookie:", font=("Helvetica", 12)).pack(side=tk.LEFT)
        
        help_sucuri = "Found in the same Cookie header as PHPSESSID.\nStarts with 'sucuricp_tfca_...'. Copy the full string including '=1'."
        self.create_info_icon(frame_sucuri, help_sucuri).pack(side=tk.LEFT)
        
        self.sucuri_cookie_var = tk.StringVar(value=self.config.get("sucuri_cookie"))
        PlaceholderEntry(input_frame, textvariable=self.sucuri_cookie_var, placeholder="e.g. sucuricp_tfca_...=1", font=("Helvetica", 12)).pack(fill=tk.X, pady=(0, 15), ipady=3)
        
        # Download Path
        ttk.Label(input_frame, text="Download Path:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.download_path_var = tk.StringVar(value=self.config.get("download_path"))
        ttk.Entry(path_frame, textvariable=self.download_path_var, font=("Helvetica", 12)).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Label(main_frame, text="* Settings are saved automatically", font=("Arial", 11, "italic"), foreground="gray").pack(anchor="w", pady=(0, 20))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        style = ttk.Style()
        style.configure("Big.TButton", font=("Helvetica", 12))

        self.start_btn = ttk.Button(btn_frame, text="Start Download", command=self.start_download_thread, style="Big.TButton")
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        
        self.open_btn = ttk.Button(btn_frame, text="Open Folder", command=self.open_folder, style="Big.TButton")
        self.open_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=5)
        
        # Progress Section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, text="Ready", font=("Helvetica", 10))
        self.status_label.pack(anchor="w", pady=(0, 2))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)

        ttk.Label(main_frame, text="Logs:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.log_area = scrolledtext.ScrolledText(main_frame, height=15, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        def _update():
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
                
                # Calculate percentage based on document index
                # We can add a small increment for pages if we wanted, but just document level is fine for now
                percent = (current_idx / total) * 100
                
                self.progress_var.set(percent)
                self.status_label.config(text=f"[{doc}] {message}")
            except Exception as e:
                print(f"Progress Update Error: {e}")

        self.root.after(0, _update)
        
    def start_download_thread(self):
        module_code = self.module_code_var.get().strip()
        phpsessid = self.phpsessid_var.get().strip()
        sucuri_cookie = self.sucuri_cookie_var.get().strip()
        download_path = self.download_path_var.get().strip()
        
        # Handle Placeholders being submitted as values
        if module_code == "e.g. ADBI421103": module_code = ""
        if phpsessid == "e.g. abcdef1234567890abcdef12345678": phpsessid = ""
        if sucuri_cookie == "e.g. sucuricp_tfca_...=1": sucuri_cookie = ""
        
        if not module_code or not phpsessid or not sucuri_cookie:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if not download_path:
             messagebox.showerror("Error", "Download path is required!")
             return

        self.save_config()
        
        self.start_btn.config(text="Stop Process", command=self.stop_download_thread, state='normal')
        self.open_btn.config(state='disabled') # Disable open folder button during download
        
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        
        # Reset progress
        self.progress_var.set(0)
        self.status_label.config(text="Starting...")
        
        self.stop_event.clear() # Clear the stop event for a new download
        threading.Thread(target=self.run_download, args=(module_code, phpsessid, sucuri_cookie, download_path, self.stop_event), daemon=True).start()
        
    def stop_download_thread(self):
        self.log("Stopping download...")
        self.stop_event.set() # Signal the download thread to stop
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

    def open_folder(self):
        path = self.download_path_var.get().strip()
        if not path:
            path = os.path.abspath("downloads")

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                pass
        
        if os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            os.system(f'open "{path}"' if sys.platform == 'darwin' else f'xdg-open "{path}"')
            
import sys
if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()