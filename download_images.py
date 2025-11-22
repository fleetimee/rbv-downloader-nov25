import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import os
import time
import sys
from PIL import Image


BASE_URL = "https://pustaka.ut.ac.id/reader/services/view.php"

HEADERS = {
    'sec-ch-ua-platform': '"macOS"',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
}

DOCUMENTS = [
    "DAFIS",
    "TINJAUAN",
    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"
]


def merge_to_pdf(doc_name, image_dir, output_dir, log_callback=None):
    """Merges all JPGs in the directory into a single PDF."""
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    log(f"  [MERGING] Creating PDF for {doc_name}...")
    
    images = []
    if os.path.exists(image_dir):
        for f in os.listdir(image_dir):
            if f.endswith(".jpg"):
                images.append(f)
    
    try:
        images.sort(key=lambda x: int(x.split('.')[0]))
    except ValueError:
        images.sort()

    if not images:
        log(f"  [WARNING] No images found for {doc_name}. Skipping PDF creation.")
        return

    try:
        first_image_path = os.path.join(image_dir, images[0])
        first_image = Image.open(first_image_path).convert('RGB')
        
        other_images = []
        for img_file in images[1:]:
            img_path = os.path.join(image_dir, img_file)
            img = Image.open(img_path).convert('RGB')
            other_images.append(img)

        pdf_path = os.path.join(output_dir, f"{doc_name}.pdf")
        first_image.save(pdf_path, save_all=True, append_images=other_images)
        log(f"  [SUCCESS] Created {pdf_path}")
        
    except Exception as e:
        log(f"  [ERROR] Failed to create PDF for {doc_name}: {e}")

def download_images(module_code, subfolder, output_dir, headers, progress_callback=None, log_callback=None):
    def log(msg, end="\n"):
        if log_callback:
            # log_callback might not support 'end', so we strip it or just log
            log_callback(msg)
        else:
            print(msg, end=end)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        log(f"Created directory: {output_dir}")

    session = requests.Session()
    session.headers.update(headers)

    for doc in DOCUMENTS:
        doc_dir = os.path.join(output_dir, doc)
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)
        
        log(f"Processing Document: {doc}")
        if progress_callback:
            progress_callback({"status": "processing", "doc": doc, "message": "Starting download"})
        
        page = 1
        consecutive_errors = 0
        
        while True:
            filename = os.path.join(doc_dir, f"{page}.jpg")
            
            if os.path.exists(filename):
                page += 1
                continue

            if not log_callback:
                # Only print the \r style progress if we are in CLI mode (no log_callback)
                print(f"  [DOWNLOADING] Page {page}...", end="\r")
            else:
                 pass

            if progress_callback:
                 progress_callback({"status": "processing", "doc": doc, "page": page, "message": f"Downloading page {page}"})
            
            params = {
                "doc": doc,
                "format": "jpg",
                "subfolder": subfolder,
                "page": page
            }
            
            try:
                response = session.get(BASE_URL, params=params, timeout=20)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'image' in content_type:
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        consecutive_errors = 0
                        page += 1
                    else:
                        # Often returns HTML/Text when page doesn't exist or session expired (though usually 403)
                        log(f"  [INFO] Page {page} reached end of document (Content-Type: {content_type}).")
                        break
                
                elif response.status_code == 403:
                    msg = "Authentication failed. Your cookies (PHPSESSID/Sucuri) might be expired. Please refresh them."
                    log(f"  [CRITICAL] {msg}")
                    raise PermissionError(msg)

                elif response.status_code == 404:
                    if page == 1:
                        log(f"  [INFO] Document {doc} does not exist. Skipping.")
                    else:
                        log(f"  [INFO] Finished downloading {doc}.")
                    break
                
                else:
                    log(f"  [FAILED] Page {page} returned status: {response.status_code}")
                    consecutive_errors += 1

            except ConnectionError:
                msg = "Network error. Unable to connect to the server. Please check your internet connection."
                log(f"\n  [CRITICAL] {msg}")
                raise ConnectionError(msg)
            
            except Timeout:
                log(f"\n  [WARNING] Connection timed out for page {page}. Retrying...")
                consecutive_errors += 1
            
            except RequestException as e:
                log(f"\n  [ERROR] Unexpected network error: {e}")
                consecutive_errors += 1
            
            except Exception as e:
                log(f"\n  [EXCEPTION] {e}")
                # Check if it's the PermissionError we raised above
                if isinstance(e, PermissionError):
                    raise e
                consecutive_errors += 1
            
            if consecutive_errors > 3:
                log(f"\n  [SKIP] Too many errors ({consecutive_errors}) for {doc}. Moving to next document.")
                break
        
        if progress_callback:
            progress_callback({"status": "processing", "doc": doc, "message": "Merging PDF"})
        
        # Pass the log_callback to merge_to_pdf
        merge_to_pdf(doc, doc_dir, output_dir, log_callback)
        log(f"Finished {doc}.\n")

def main():
    print("--- Pustaka UT Downloader Setup ---")
    
    module_code = input("Enter Module Code (e.g. ADBI421103): ").strip()
    if not module_code:
        print("Error: Module Code is required.")
        return

    print("\nPlease enter your cookies:")
    phpsessid = input("  PHPSESSID: ").strip()
    sucuri_cookie = input("  Sucuri Cookie (e.g. sucuricp_tfca_...=1): ").strip()
    
    if not phpsessid or not sucuri_cookie:
        print("Error: Both cookies are required.")
        return

    subfolder = f"{module_code}/"
    output_dir = os.path.join("downloads", module_code)
    
    headers = HEADERS.copy()
    headers['Referer'] = f'https://pustaka.ut.ac.id/reader/index.php?modul={module_code}'
    headers['Cookie'] = f"PHPSESSID={phpsessid}; {sucuri_cookie}"

    print(f"\nStarting download for {module_code}...")
    print(f"Output Directory: {output_dir}")
    print("-----------------------------------")
    
    try:
        download_images(module_code, subfolder, output_dir, headers)
        print("\nAll downloads completed successfully.")
    except PermissionError as e:
        print(f"\n[X] STOPPED: {e}")
    except ConnectionError as e:
        print(f"\n[X] STOPPED: {e}")
    except Exception as e:
        print(f"\n[X] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()