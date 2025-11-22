import os
import logging
import sys
from app.schemas.job import JobRequest
from app.services.job_store import update_job_progress, update_job_status, set_job_files, get_generated_files

# Add project root to sys.path to allow importing download_images
sys.path.append(os.getcwd())

try:
    from download_images import download_images, HEADERS
except ImportError:
    # Fallback if running from inside app directory (though strictly not recommended)
    sys.path.append(os.path.join(os.getcwd(), ".."))
    from download_images import download_images, HEADERS

def background_download_task(job_id: str, request: JobRequest):
    """Wrapper to run the download script in background."""
    try:
        update_job_status(job_id, "processing")
        
        # Construct arguments for the existing function
        subfolder = f"{request.module_code}/"
        output_dir = os.path.join("downloads", request.module_code)
        
        # Headers
        headers = HEADERS.copy()
        headers['Referer'] = f'https://pustaka.ut.ac.id/reader/index.php?modul={request.module_code}'
        headers['Cookie'] = f"PHPSESSID={request.phpsessid}; {request.sucuri_cookie}"

        # Define a specific callback for this job
        def callback(data):
            update_job_progress(job_id, data)

        # Run the synchronous download function
        download_images(request.module_code, subfolder, output_dir, headers, progress_callback=callback)
        
        # Completion
        files = get_generated_files(request.module_code)
        set_job_files(job_id, files)
        update_job_status(job_id, "completed")
        update_job_progress(job_id, {"message": "All tasks finished."})

    except Exception as e:
        logging.error(f"Job {job_id} failed: {e}")
        update_job_status(job_id, "failed", str(e))
