import json

from flask import Flask
from flask import request
from utils import success_response, failure_response, upload_image_helper, remove_image_helper
import os

app = Flask(__name__)


@app.route("/")
def hello_world():
    return success_response("Hello World!")


@app.route("/upload/", methods=["POST"])
def upload():
    body = json.loads(request.data)
    image_data = body.get("image")
    bucket_name = body.get("bucket")  
    if image_data is None:
        return failure_response("No base64 URL to be found!")
    img_url = upload_image_helper(image_data, bucket_name)
    if img_url is None:
        return failure_response("Could not upload image!")
    return success_response(img_url, 201)

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
