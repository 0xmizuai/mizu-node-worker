import os
import uvicorn

from fastapi import FastAPI
from redis import Redis
from rq import Queue, Worker

import mizu_validator.worker as worker

# HTTP server entry point
app = FastAPI()

# Redis configuration
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)
queue_name = "classification_jobs"
queue = Queue(queue_name, connection=redis_conn)


@app.post("/classify")
def do_classify(job: worker.ClassificationJob):
    job = queue.enqueue(worker.classification_worker, job)
    return {"job_id": job.id, "status": "Job enqueued"}


def start_dev():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000, reload=True)


# the number of workers is defined by $WEB_CONCURRENCY env as default
def start():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000)


def start_worker():
    worker = Worker([queue_name], connection=redis_conn)
    worker.work()
