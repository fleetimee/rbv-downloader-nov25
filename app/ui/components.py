import tkinter as tk
from tkinter import ttk

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
