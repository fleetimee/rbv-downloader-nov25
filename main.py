from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
import os
import logging
from typing import Optional, Dict, Any
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import the existing logic
from download_images import download_images, HEADERS

app = FastAPI(title="RBV Downloader API")

# -----------------------------------------------------------------------------
# Data Structures
# -----------------------------------------------------------------------------

class JobRequest(BaseModel):
    module_code: str
    phpsessid: str
    sucuri_cookie: str

# In-memory storage for job status
# Format: { "job_id": { "status": "...", "progress": {...}, "result": [...] } }
JOBS: Dict[str, Any] = {}

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_generated_files(module_code: str):
    """Scans the output directory for generated PDFs."""
    output_dir = os.path.join("downloads", module_code)
    files = []
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith(".pdf"):
                files.append(f)
    return files

def update_job_progress(job_id: str, data: dict):
    """Callback function to update job progress."""
    if job_id in JOBS:
        JOBS[job_id]["progress"] = data
        JOBS[job_id]["status"] = "processing"

def background_download_task(job_id: str, request: JobRequest):
    """Wrapper to run the download script in background."""
    try:
        JOBS[job_id]["status"] = "processing"
        
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
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["files"] = get_generated_files(request.module_code)
        JOBS[job_id]["progress"] = {"message": "All tasks finished."}

    except Exception as e:
        logging.error(f"Job {job_id} failed: {e}")
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/download")
async def start_download(request: JobRequest, background_tasks: BackgroundTasks):
    """Starts a download job."""
    job_id = str(uuid.uuid4())
    
    JOBS[job_id] = {
        "id": job_id,
        "module_code": request.module_code,
        "status": "queued",
        "progress": {},
        "files": []
    }
    
    background_tasks.add_task(background_download_task, job_id, request)
    
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Checks the status of a job."""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # If completed, ensure file list is up to date
    if JOBS[job_id]["status"] == "completed":
        JOBS[job_id]["files"] = get_generated_files(JOBS[job_id]["module_code"])
        
    return JOBS[job_id]

@app.get("/files/{module_code}/{filename}")
async def download_file(module_code: str, filename: str):
    """Serves a generated PDF file."""
    # Security check: prevent traversal
    if ".." in module_code or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid path")
        
    file_path = os.path.join("downloads", module_code, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, media_type='application/pdf', filename=filename)
