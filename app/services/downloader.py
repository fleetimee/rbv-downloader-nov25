import os
from typing import Optional, Callable, Dict
from requests.exceptions import ConnectionError, Timeout

from app.core.config import DOCUMENTS
from app.services.network import NetworkService
from app.services.pdf import PDFService
from app.services.logger import Logger

class ModuleDownloader:
    """Orchestrates the download, merging, and cleanup process."""
    
    def __init__(self, network_service: NetworkService, pdf_service: PDFService):
        self.network = network_service
        self.pdf = pdf_service

    def process(self, module_code: str, subfolder: str, output_dir: str, 
                progress_callback: Optional[Callable[[Dict], None]] = None, 
                log_callback: Optional[Callable[[str], None]] = None, 
                stop_event=None):
        
        logger = Logger(log_callback)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created directory: {output_dir}")

        total_docs = len(DOCUMENTS)

        for i, doc in enumerate(DOCUMENTS):
            if stop_event and stop_event.is_set():
                logger.info(f"  [INFO] Download stopped by user.")
                return

            doc_dir = os.path.join(output_dir, doc)
            if not os.path.exists(doc_dir):
                os.makedirs(doc_dir)

            logger.info(f"Processing Document: {doc}")
            self._notify_progress(progress_callback, "processing", doc, "Starting download", i, total_docs)

            self._download_document_pages(doc, subfolder, doc_dir, i, total_docs, progress_callback, logger, stop_event)
            
            # Merge Phase
            self._notify_progress(progress_callback, "processing", doc, "Merging PDF", i, total_docs)
            self.pdf.merge_images_to_pdf(doc, doc_dir, output_dir, logger)
            
            # Cleanup Phase
            self.pdf.cleanup_images(doc_dir, logger)
            
            logger.info(f"Finished {doc}.\n")

    def _download_document_pages(self, doc: str, subfolder: str, doc_dir: str, 
                                 doc_index: int, total_docs: int,
                                 progress_callback, logger: Logger, stop_event):
        page = 1
        consecutive_errors = 0

        while True:
            if stop_event and stop_event.is_set():
                break

            filename = os.path.join(doc_dir, f"{page}.jpg")
            
            # Skip if exists
            if os.path.exists(filename):
                page += 1
                continue
            
            # CLI Feedback (only if no logger callback is active, strictly for CLI feel if needed)
            # But we should rely on logger or progress callback
            if not logger.callback:
                 print(f"  [DOWNLOADING] Page {page}...", end="\r")

            self._notify_progress(progress_callback, "processing", doc, f"Downloading page {page}", doc_index, total_docs)

            try:
                response = self.network.fetch_page(doc, subfolder, page)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'image' in content_type:
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        consecutive_errors = 0
                        page += 1
                    else:
                        logger.info(f"  [INFO] Page {page} reached end (Content-Type: {content_type}).")
                        break
                
                elif response.status_code == 403:
                    msg = "Authentication failed. Cookies expired."
                    logger.error(msg)
                    raise PermissionError(msg)
                
                elif response.status_code == 404:
                    if page == 1:
                        logger.info(f"  [INFO] Document {doc} does not exist. Skipping.")
                    else:
                        logger.info(f"  [INFO] Finished downloading {doc}.")
                    break
                else:
                    logger.info(f"  [FAILED] Page {page} returned status: {response.status_code}")
                    consecutive_errors += 1

            except (ConnectionError, Timeout) as e:
                if isinstance(e, ConnectionError):
                    msg = "Network error. Check connection."
                else:
                    msg = "Connection timed out."
                
                logger.info(f"\n  [WARNING] {msg} Retrying...")
                consecutive_errors += 1
                if consecutive_errors > 3:
                    raise e
            except Exception as e:
                if isinstance(e, PermissionError): raise e
                logger.error(f"Unexpected error: {e}")
                consecutive_errors += 1
            
            if consecutive_errors > 3:
                logger.info(f"\n  [SKIP] Too many errors for {doc}. Moving next.")
                break

    def _notify_progress(self, callback, status, doc, msg, idx, total):
        if callback:
            callback({
                "status": status,
                "doc": doc,
                "message": msg,
                "current_doc_index": idx,
                "total_docs": total
            })
