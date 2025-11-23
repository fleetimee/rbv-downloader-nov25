import tkinter as tk
from tkinter import ttk, scrolledtext
from app.ui.components import ToolTip, PlaceholderEntry
from app.ui.utils import resource_path

class LayoutBuilder:
    def __init__(self, app):
        self.app = app
        self.root = app.root

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_header(main_frame)
        self._create_inputs(main_frame)
        self._create_buttons(main_frame)
        self._create_progress_section(main_frame)
        self._create_log_area(main_frame)

    def _create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        logo_container = ttk.Frame(header_frame)
        logo_container.pack(anchor="center")

        try:
            icon_path = resource_path("assets/icon.png")
            logo_path = resource_path("assets/logo.png")
            
            self.app.logo_img = tk.PhotoImage(file=icon_path) 
            self.app.header_logo = tk.PhotoImage(file=logo_path).subsample(8, 8) 
            
            lbl_logo = ttk.Label(logo_container, image=self.app.header_logo)
            lbl_logo.pack(side=tk.LEFT, padx=(0, 15))
            
            self.root.iconphoto(True, self.app.logo_img)
        except Exception as e:
            print(f"Could not load logo: {e}")
            
        title_label = ttk.Label(logo_container, text="RBV Downloader", font=("Helvetica", 22, "bold"))
        title_label.pack(side=tk.LEFT, anchor="center")

    def _create_inputs(self, parent):
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Module Code
        self._create_input_field(input_frame, "Module Code:", self.app.module_code_var, 
                                 "e.g. ADBI421103",
                                 "The Module Code is part of the URL on pustaka.ut.ac.id.\nExample: 'ADBI421103' in .../index.php?modul=ADBI421103")
        
        # PHPSESSID
        self._create_input_field(input_frame, "PHPSESSID:", self.app.phpsessid_var, 
                                 "e.g. abcdef1234567890abcdef12345678",
                                 "1. Open DevTools (F12) -> Network tab.\n2. Refresh page.\n3. Look for 'view.php' request -> Headers -> Cookie.\n4. Copy the 'PHPSESSID' value.")
        
        # Sucuri Cookie
        self._create_input_field(input_frame, "Sucuri Cookie:", self.app.sucuri_cookie_var, 
                                 "e.g. sucuricp_tfca_...=1",
                                 "Found in the same Cookie header as PHPSESSID.\nStarts with 'sucuricp_tfca_...'. Copy the full string including '=1'.")
        
        # Download Path
        ttk.Label(input_frame, text="Download Path:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Entry(path_frame, textvariable=self.app.download_path_var, font=("Helvetica", 12)).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        ttk.Button(path_frame, text="Browse", command=self.app.browse_folder).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Label(parent, text="* Settings are saved automatically", font=("Arial", 11, "italic"), foreground="gray").pack(anchor="w", pady=(0, 20))

    def _create_input_field(self, parent, label_text, variable, placeholder, tooltip_text):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(frame, text=label_text, font=("Helvetica", 12)).pack(side=tk.LEFT)
        self._create_info_icon(frame, tooltip_text).pack(side=tk.LEFT)
        PlaceholderEntry(parent, textvariable=variable, placeholder=placeholder, font=("Helvetica", 12)).pack(fill=tk.X, pady=(0, 15), ipady=3)

    def _create_info_icon(self, parent, text):
        lbl = tk.Label(parent, text=" (?) ", font=("Helvetica", 10, "bold"), foreground="#007acc", cursor="hand2")
        ToolTip(lbl, text)
        return lbl

    def _create_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        style = ttk.Style()
        style.configure("Big.TButton", font=("Helvetica", 12))

        self.app.start_btn = ttk.Button(btn_frame, text="Start Download", command=self.app.start_download_thread, style="Big.TButton")
        self.app.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        
        self.app.open_btn = ttk.Button(btn_frame, text="Open Folder", command=self.app.open_folder_action, style="Big.TButton")
        self.app.open_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=5)

    def _create_progress_section(self, parent):
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.app.status_label = ttk.Label(progress_frame, text="Ready", font=("Helvetica", 10))
        self.app.status_label.pack(anchor="w", pady=(0, 2))
        
        self.app.progress_bar = ttk.Progressbar(progress_frame, variable=self.app.progress_var, maximum=100)
        self.app.progress_bar.pack(fill=tk.X)

    def _create_log_area(self, parent):
        ttk.Label(parent, text="Logs:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.app.log_area = scrolledtext.ScrolledText(parent, height=15, state='disabled')
        self.app.log_area.pack(fill=tk.BOTH, expand=True)
