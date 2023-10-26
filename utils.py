import base64
import json
import os
import random
import re
import string
from io import BytesIO
from mimetypes import guess_extension, guess_type

import boto3
from PIL import Image

ALLOWED_MIME_TYPES_REGEX = "image/.+|application/pdf"
BUCKET_NAMES = os.environ["BUCKET_NAMES"].split(",")


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


def upload_image_helper(bucket_name,image_data=None, file_data=None):
    """
    Function that uploads image data to s3 based on the bucket name and data.
    
    Parameters
    ----
    bucket_name : str
    The name of the bucket to place the image in
    image_data : str | None
    The raw base 64 passed in from the HTML post request, potentially None if
    the client is using form-data
    file_data: FileStore | None
    The file from the form-data of the user's HTML request, or None if it was
    passed in the request body instead.
    
    Returns
    ----
    The image URL associated to the image that was uploaded to s3
    """
    if bucket_name not in BUCKET_NAMES:
        return None
    # Guess the file type, depending on whether we have image data or file data
    to_guess = image_data if image_data else file_data.filename
    mime_type = guess_type(to_guess)[0]
    ext = guess_extension(mime_type)[1:]
    if re.fullmatch(ALLOWED_MIME_TYPES_REGEX, mime_type) is None:
        raise Exception(f"Extension {ext} not supported!")

    # secure way of generating random string for image name
    salt = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))
    img_filename = f"{salt}.{ext}" 
    
    # We won't use these if user uploaded file in form data
    if image_data:
        # remove header of Base64 string
        img_str = re.sub("^.*?;base64,", "", image_data)
        # get the decoded bytes of the base 64 image, or process FileStore object
        img_bytes = base64.b64decode(img_str)

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=os.environ["SPACES_REGION_NAME"],
        endpoint_url=os.environ["SPACES_ENDPOINT_URL"],
        aws_access_key_id=os.environ["SPACES_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SPACES_SECRET_ACCESS_KEY"],
    )
    
    if file_data:
        client.put_object(
            Bucket=bucket_name,
            Key=img_filename,
            Body=file_data.read(),
            ACL="public-read",
        )
    else:
        client.put_object(
            Bucket=bucket_name,
            Key=img_filename,
            Body=BytesIO(img_bytes),
            ACL="public-read",
        )

    img_url = f"{os.environ['SPACES_ENDPOINT_URL']}/{bucket_name}/{img_filename}"
    return img_url


def remove_image_helper(img_url, bucket_name):
    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=os.environ["SPACES_REGION_NAME"],
        endpoint_url=os.environ["SPACES_ENDPOINT_URL"],
        aws_access_key_id=os.environ["SPACES_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SPACES_SECRET_ACCESS_KEY"],
    )
    img_filename = img_url.split("/")[-1]
    # Check if `img_filename` exists
    try:
        client.get_object(Bucket=bucket_name, Key=img_filename)
    except Exception as e:
        return None
    res = client.delete_object(
        Bucket=bucket_name,
        Key=img_filename,
    )
    return res["ResponseMetadata"]["HTTPStatusCode"]
