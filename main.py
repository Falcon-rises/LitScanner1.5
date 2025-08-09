from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import config
import tasks

app = FastAPI(title="LitHybrid - Flat Scaffold")

class ProjectRequest(BaseModel):
    title: str
    sources: Optional[list] = ["openalex", "semantic_scholar"]
    max_papers: Optional[int] = 7000

@app.post("/api/projects")
def create_project(req: ProjectRequest, background_tasks: BackgroundTasks):
    project_id = str(uuid.uuid4())
    job = {
        "project_id": project_id,
        "title": req.title,
        "sources": req.sources,
        "max_papers": req.max_papers,
        "status": "queued"
    }
    # enqueue background job (simple in-process background for scaffold)
    background_tasks.add_task(tasks.run_pipeline, job)
    return {"project_id": project_id, "status": "started"}

@app.get("/api/projects/{project_id}/status")
def get_status(project_id: str):
    return tasks.get_job_status(project_id)

@app.get("/api/projects/{project_id}/summary")
def get_summary(project_id: str):
    summary = tasks.get_summary(project_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not ready")
    return {"project_id": project_id, "summary": summary}
