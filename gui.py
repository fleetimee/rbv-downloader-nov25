import tkinter as tk
import sys
from app.ui.app import DownloaderApp

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
