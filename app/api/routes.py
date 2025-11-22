from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
from app.schemas.job import JobRequest
from app.services.job_store import get_job, create_job, get_generated_files
from app.services.tasks import background_download_task

router = APIRouter()

@router.post("/download")
async def start_download(request: JobRequest, background_tasks: BackgroundTasks):
    """Starts a download job."""
    job_id = str(uuid.uuid4())
    
    create_job(job_id, request.module_code)
    
    background_tasks.add_task(background_download_task, job_id, request)
    
    return {"job_id": job_id, "status": "queued"}

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Checks the status of a job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # If completed, ensure file list is up to date
    if job["status"] == "completed":
        # Refresh file list just in case
        job["files"] = get_generated_files(job["module_code"])
        
    return job

@router.get("/files/{module_code}/{filename}")
async def download_file(module_code: str, filename: str):
    """Serves a generated PDF file."""
    # Security check: prevent traversal
    if ".." in module_code or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid path")
        
    file_path = os.path.join("downloads", module_code, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, media_type='application/pdf', filename=filename)
