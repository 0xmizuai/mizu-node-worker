from asyncio import sleep
import os
from fastapi.encoders import jsonable_encoder
import uvicorn

from fastapi import FastAPI, requests
from redis import Redis
from rq import Queue, Worker

from mizu_node_worker.worker import WorkerJob, process_job_no_throw

# HTTP server entry point
app = FastAPI()

# Redis configuration
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)
queue_name = os.environ.get("REDIS_QUEUE", "verify_job_queue")
rq_queue_name = "rq_" + queue_name
rq_queue = Queue(rq_queue_name, connection=redis_conn)

@app.post("/classify")
def do_classify(job: WorkerJob):
    job = rq_queue.enqueue(process_job_no_throw, job)
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
    print("Starting worker...")
    while True:
        try:
            message = redis_conn.brpop(queue_name)
            job = WorkerJob.model_validate(message)
            result = process_job_no_throw(job)
            requests.post(
                job.callback_url,
                json=jsonable_encoder(result),
            )
        except Exception as e:
            print(f"Error processing job: {e}")
            sleep(5000)
