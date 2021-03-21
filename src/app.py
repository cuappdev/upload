import json

from db import db
from flask import Flask
from flask import request
from db import Asset
from utils import success_response, failure_response, upload_image_helper
import os

db_filename = "images.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/")
def hello_world():
    return success_response("Hello World!")


@app.route("/upload/", methods=["POST"])
def upload():
    body = json.loads(request.data)
    image_data = body.get("image")
    bucket_name = body.get("bucket")  # we only support pear right now
    if image_data is None:
        return failure_response("No base64 URL to be found!")
    img_url = upload_image_helper(image_data, bucket_name)
    if img_url is None:
        return failure_response("Could not upload image!")
    return success_response(img_url, 201)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
