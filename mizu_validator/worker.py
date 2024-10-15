import requests

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from mizu_validator.classifier import classify
from mizu_validator.embeddings.domain_embeddings import V1_EMBEDDING


class AIRuntimeConfig(BaseModel):
    debug: bool = False
    callback_url: str = None


class ClassificationJob(BaseModel):
    job_id: str
    text: str
    config: AIRuntimeConfig | None = None


class ClassificationResult(BaseModel):
    job_id: str
    tags: list[str]


def classification_worker(job: ClassificationJob):
    tags = classify(job.text, V1_EMBEDDING)
    reply = ClassificationResult(job_id=job.job_id, tags=tags)
    requests.post(
        job.config.callback_url,
        json=jsonable_encoder(reply),
    )
