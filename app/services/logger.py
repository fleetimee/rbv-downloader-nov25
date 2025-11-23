from typing import Optional, Callable

class Logger:
    """Abstracts logging to support both CLI printing and callbacks."""
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.callback = callback

    def info(self, msg: str):
        if self.callback:
            self.callback(msg)
        else:
            print(msg)
            
    def error(self, msg: str):
        self.info(f"[ERROR] {msg}")
