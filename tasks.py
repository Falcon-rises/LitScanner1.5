# Lightweight task stubs used by main.py background tasks for local scaffold
import time
from typing import Dict

_JOBS: Dict[str, Dict] = {}


def run_pipeline(job: dict):
    project_id = job['project_id']
    _JOBS[project_id] = {"status": "crawling", "progress": 0}
    # 1) Crawl (stub)
    time.sleep(1)
    _JOBS[project_id]["progress"] = 10
    _JOBS[project_id]["status"] = "parsing"
    # 2) Parse (stub)
    time.sleep(1)
    _JOBS[project_id]["progress"] = 30
    _JOBS[project_id]["status"] = "embedding"
    # 3) Embed (stub)
    time.sleep(1)
    _JOBS[project_id]["progress"] = 60
    _JOBS[project_id]["status"] = "summarizing"
    # 4) Summarize (stub - short sample)
    time.sleep(1)
    _JOBS[project_id]["progress"] = 90
    _JOBS[project_id]["status"] = "done"
    _JOBS[project_id]["progress"] = 100
    _JOBS[project_id]["summary"] = "This is a stub summary for project: {}".format(project_id)


def get_job_status(project_id: str):
    return _JOBS.get(project_id, {"status": "not_found"})


def get_summary(project_id: str):
    job = _JOBS.get(project_id)
    return job.get('summary') if job else None
