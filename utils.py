import base64
import boto3
import datetime
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string
import json

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
BUCKET_NAMES = os.environ["BUCKET_NAMES"].split(",")


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


def upload_image_helper(image_data, bucket_name):
    if bucket_name not in BUCKET_NAMES:
        return None
    ext = guess_extension(guess_type(image_data)[0])[1:]
    if ext not in EXTENSIONS:
        raise Exception(f"Extension {ext} not supported!")

    # secure way of generating random string for image name
    salt = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))

    # remove header of base64 string
    img_str = re.sub("^data:image/.+;base64,", "", image_data)
    img_data = base64.b64decode(img_str)
    img_filename = f"{salt}.{ext}"

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=os.environ["SPACES_REGION_NAME"],
        endpoint_url=os.environ["SPACES_ENDPOINT_URL"],
        aws_access_key_id=os.environ["SPACES_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SPACES_SECRET_ACCESS_KEY"],
    )

    res = client.put_object(
        Bucket=bucket_name,
        Key=img_filename,
        Body=BytesIO(img_data),
        ACL="public-read",
    )

    img_url = f"{os.environ['SPACES_ENDPOINT_URL']}/{bucket_name}/{img_filename}"
    return img_url
