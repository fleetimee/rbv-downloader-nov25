import requests
from typing import Dict
from app.core.config import BASE_URL

class NetworkService:
    """Handles HTTP requests and session management."""
    
    def __init__(self, headers: Dict[str, str]):
        self.session = requests.Session()
        self.session.headers.update(headers)

    def fetch_page(self, doc: str, subfolder: str, page: int) -> requests.Response:
        params = {
            "doc": doc,
            "format": "jpg",
            "subfolder": subfolder,
            "page": page
        }
        return self.session.get(BASE_URL, params=params, timeout=20)
