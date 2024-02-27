import json
import os

from flask import Flask, request
from utils import failure_response, remove_image_helper, success_response, upload_image_helper

ALLOWED_MIME_TYPES_REGEX = "image/.+|application/pdf"
app = Flask(__name__)


@app.route("/")
def hello_world():
    return success_response("Hello World!")


@app.route("/upload/", methods=["POST"])
def upload():
    body = None
    # Check if they are using form-data or JSON body, handle accordingly
    if request.data:
        body = json.loads(request.data)
        bucket_name = body.get("bucket")
        image_data = body.get("image")
        img_url = upload_image_helper(image_data=image_data, bucket_name=bucket_name)
        if img_url is None:
            return failure_response("Could not upload image!")
        return success_response(img_url, 201)
    else:
        bucket_name = request.form.get("bucket")
        file = request.files.get("image")
        image_data = None
        if file:
            img_url = upload_image_helper(file_data=file, bucket_name=bucket_name)
            return success_response(img_url, 201)
        else:
            return failure_response("No image file provided", 400)


@app.route("/remove/", methods=["POST"])
def remove():
    body = json.loads(request.data)
    image_url = body.get("image_url")
    bucket_name = body.get("bucket")
    if image_url is None or image_url == "":
        return failure_response("No URL to be found!")
    res = remove_image_helper(image_url, bucket_name)
    if not res:
        return failure_response("Image does not exist!")
    elif res != 204:
        return failure_response("Could not delete image!")
    return success_response("Image successfully deleted!")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
