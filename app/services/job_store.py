from typing import Dict, Any, List
import os

# In-memory storage for job status
# Format: { "job_id": { "status": "...", "progress": {...}, "result": [...] } }
JOBS: Dict[str, Any] = {}

def get_job(job_id: str) -> Dict[str, Any]:
    return JOBS.get(job_id)

def create_job(job_id: str, module_code: str):
    JOBS[job_id] = {
        "id": job_id,
        "module_code": module_code,
        "status": "queued",
        "progress": {},
        "files": []
    }

def update_job_status(job_id: str, status: str, error: str = None):
    if job_id in JOBS:
        JOBS[job_id]["status"] = status
        if error:
            JOBS[job_id]["error"] = error

def update_job_progress(job_id: str, data: dict):
    if job_id in JOBS:
        JOBS[job_id]["progress"] = data
        # Only set to processing if not already completed/failed
        if JOBS[job_id]["status"] == "queued":
            JOBS[job_id]["status"] = "processing"

def set_job_files(job_id: str, files: List[str]):
    if job_id in JOBS:
        JOBS[job_id]["files"] = files

def get_generated_files(module_code: str) -> List[str]:
    """Scans the output directory for generated PDFs."""
    output_dir = os.path.join("downloads", module_code)
    files = []
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith(".pdf"):
                files.append(f)
    return files
