import boto3
import os


R2 = None
R2_BUCKET = None


def _init_connection():
    cloudflare_r2_id = os.environ["CLOUDFLARE_R2_ID"]
    r2_endpoint = f"https://{cloudflare_r2_id}.r2.cloudflarestorage.com"
    aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    return boto3.resource(
        "s3",
        endpoint_url=r2_endpoint,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )


def init_connection():
    global R2
    global R2_BUCKET
    if R2 is None:
        print("Init R2 connection")
        R2 = _init_connection()
        R2_BUCKET = os.environ["CLOUDFLARE_R2_BUCKET_NAME"]
    return


def get_decoded_value(key: str) -> str:
    init_connection()
    new_key = f"{R2_BUCKET}/{key}"  # for some reason we have to add bucket to the key..
    obj = R2.Object(R2_BUCKET, new_key)
    return obj.get()["Body"].read().decode("utf-8")
