from enum import Enum
import requests

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from mizu_validator.classifier import classify
from mizu_validator.embeddings.domain_embeddings import V1_EMBEDDING
from mizu_validator.r2 import get_decoded_value


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
    output: str | list[str]


def job_worker(job: WorkerJob):
    if job.job_type == JobType.classification:
        text = get_decoded_value(job.input)
        tags = classify(text, V1_EMBEDDING)
        requests.post(
            job.callback_url,
            json=jsonable_encoder(WorkerJobResult(job_id=job.job_id, output=tags)),
        )
    else:
        raise NotImplementedError(f"Job type {job.job_type} not implemented")
