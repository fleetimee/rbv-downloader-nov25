# app/core/config.py

import platform

BASE_URL = "https://pustaka.ut.ac.id/reader/services/view.php"

def get_headers():
    system = platform.system()
    if system == "Windows":
        ua_platform = '"Windows"'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    elif system == "Darwin":
        ua_platform = '"macOS"'
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    else: # Linux and others
        ua_platform = '"Linux"'
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    return {
        'sec-ch-ua-platform': ua_platform,
        'User-Agent': user_agent,
        'sec-ch-ua': '"Chromium";v="120", "Google Chrome";v="120", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
    }

HEADERS = get_headers()

DOCUMENTS = [
    "DAFIS",
    "TINJAUAN",
    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"
]
