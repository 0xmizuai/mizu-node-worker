from enum import Enum
from typing import Union
import requests

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from mizu_node_worker.classifier import classify
from mizu_node_worker.embeddings.domain_embeddings import V1_EMBEDDING


class JobType(str, Enum):
    pow = "pow"
    classification = "classification"


class WorkerJob(BaseModel):
    job_id: str
    job_type: JobType
    input: str
    callback_url: str = None


class WorkerJobResult(BaseModel):
    job_id: str
    output: Union[str, list[str]]


class WorkerJobError(BaseModel):
    message: str


def process_job_no_throw(job: WorkerJob):
    try:
        if job.job_type == JobType.classification:
            text = requests.get(job.input).json()
            tags = classify(text, V1_EMBEDDING)
            return WorkerJobResult(job_id=job.job_id, output=tags)
        else:
            print(f"Error: invalid job type: " + job.job_type)
            return WorkerJobError(message="unknown job type")
    except Exception as e:
        print(f"Error: {e}")
        return WorkerJobError(message=str(e))
