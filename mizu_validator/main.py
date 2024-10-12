from typing import Union

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from mizu_validator.embeddings.domain_embeddings import V1_EMBEDDING
from mizu_validator.classifier import classify

app = FastAPI()


class AIRuntimeConfig(BaseModel):
    debug: bool = False


class VerificationJob(BaseModel):
    text: str
    config: Union[AIRuntimeConfig, None] = None
    worker_output: set[str]


class VerificationResult(BaseModel):
    job_id: str
    is_valid: bool
    # only return validator output when debug is enabled
    validator_output: set[str] = None


def verify(job_id: str, job: VerificationJob) -> VerificationResult:
    validator_output = classify(job.text, V1_EMBEDDING)
    is_valid = len(validator_output) == len(job.worker_output) and len(
        validator_output
    ) == len(job.worker_output.intersection(validator_output))
    if (job.config is not None) and job.config.debug:
        return VerificationResult(
            job_id=job_id, is_valid=is_valid, validator_output=validator_output
        )
    else:
        return VerificationResult(job_id=job_id, is_valid=is_valid)


@app.post("/verifyJob/{job_id}")
async def verify_job(job_id: str, payload: VerificationJob):
    verify(payload, job_id)


def start_dev():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000, reload=True)


# the number of workers is defined by $WEB_CONCURRENCY env as default
def start():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000)
