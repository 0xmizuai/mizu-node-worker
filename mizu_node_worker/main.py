import os
import uvicorn

from fastapi import FastAPI
from redis import Redis
from rq import Queue, Worker

from mizu_node_worker.worker import job_worker, WorkerJob

# HTTP server entry point
app = FastAPI()

# Redis configuration
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)
rq_queue_name = "classification_jobs"
redis_queue = os.environ["REDIS_QUEUE"]  # raise exception if not present
queue = Queue(rq_queue_name, connection=redis_conn)


@app.post("/classify")
def do_classify(job: WorkerJob):
    job = queue.enqueue(job_worker, job)
    return {"job_id": job.id, "status": "Job enqueued"}


def start_dev():
    uvicorn.run("mizu_node_worker.main:app", host="0.0.0.0", port=8001, reload=True)


# the number of workers is defined by $WEB_CONCURRENCY env as default
def start():
    uvicorn.run("mizu_node_worker.main:app", host="0.0.0.0", port=8001)


def start_rq_worker():
    worker = Worker([rq_queue_name], connection=redis_conn)
    worker.work()


def start_worker():
    p = redis_conn.pubsub()
    p.subscribe(redis_queue)
    for message in p.listen():
        try:
            worker_job = WorkerJob.parse_obj(message)
            job_worker(worker_job)
        except Exception as e:
            print(e)
