import os
from requests.exceptions import ConnectionError

from app.core.config import HEADERS, DOCUMENTS
from app.services.network import NetworkService
from app.services.pdf import PDFService
from app.services.downloader import ModuleDownloader

# --- Facade for Backward Compatibility ---

def download_images(module_code, subfolder, output_dir, headers, 
                    progress_callback=None, log_callback=None, stop_event=None):
    """
    Legacy entry point that initializes the services and starts the downloader.
    """
    network_service = NetworkService(headers)
    pdf_service = PDFService()
    downloader = ModuleDownloader(network_service, pdf_service)
    
    downloader.process(
        module_code, 
        subfolder, 
        output_dir, 
        progress_callback=progress_callback, 
        log_callback=log_callback, 
        stop_event=stop_event
    )


# --- CLI Entry Point ---

def main():
    print("--- Pustaka UT Downloader Setup ---")
    
    print("\nTo get the Module Code:")
    print("1. Go to https://pustaka.ut.ac.id/reader/ and navigate to your module.")
    module_code = input("Enter Module Code (e.g. ADBI421103): ").strip()
    if not module_code:
        print("Error: Module Code is required.")
        return

    print("\nPlease enter your cookies (PHPSESSID and Sucuri):")
    phpsessid = input("  PHPSESSID: ").strip()
    sucuri_cookie = input("  Sucuri Cookie (sucuricp_tfca_...): ").strip()
    
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
        from tqdm import tqdm
        # Initialize tqdm with total documents
        pbar = tqdm(total=len(DOCUMENTS), unit="doc", 
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]")
        
        last_doc_index = [0]

        def cli_logger(msg):
            tqdm.write(msg)

        def cli_progress(data):
            doc = data.get("doc", "?")
            message = data.get("message", "")
            current = data.get("current_doc_index", 0)
            
            pbar.set_description(f"Processing {doc}")
            pbar.set_postfix_str(message, refresh=True)
            
            if current > last_doc_index[0]:
                pbar.update(current - last_doc_index[0])
                last_doc_index[0] = current

        download_images(
            module_code, 
            subfolder, 
            output_dir, 
            headers, 
            progress_callback=cli_progress,
            log_callback=cli_logger
        )
        
        if pbar.n < len(DOCUMENTS):
             pbar.update(len(DOCUMENTS) - pbar.n)
        pbar.close()
        print("\nAll downloads completed successfully.")

    except KeyboardInterrupt:
        print("\n\n[!] Process interrupted by user. Exiting...")
    except ImportError:
        print("Error: 'tqdm' library not found. Please run 'pip install tqdm'.")
    except PermissionError as e:
        print(f"\n[X] STOPPED: {e}")
    except ConnectionError as e:
        print(f"\n[X] STOPPED: {e}")
    except Exception as e:
        print(f"\n[X] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()