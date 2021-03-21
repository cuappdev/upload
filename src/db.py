import base64
import boto3
import datetime
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET = "demo8"


class Asset(db.Model):
    __tablename__ = "asset"

    id = db.Column(db.Integer, primary_key=True)
    base_url = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        self.create(kwargs.get("image_data"))

    def serialize(self):
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at),
        }

    def create(self, image_data):
        try:
            # [1:] strips off leading period
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f"Extension {ext} not supported!")

            # secure way of generating random string for image name
            salt = "".join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                for _ in range(16)
            )

            # remove header of base64 string
            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            # create db object
            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            # upload image to AWS
            img_filename = f"{salt}.{ext}"
            self.upload(img, img_filename)

        except Exception as e:
            print(f"Could not create image because of {e}")

    def upload(self, img, img_filename):
        try:
            # save image temporarily
            img_temploc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temploc)

            # upload image to S3
            # s3_client = boto3.client("s3")
            # s3_client.upload_file(img_temploc, S3_BUCKET, img_filename)

            # # make S3 image url public
            # s3_resource = boto3.resource("s3")
            # object_acl = s3_resource.ObjectAcl(S3_BUCKET, img_filename)
            # object_acl.put(ACL="public-read")
            # os.remove(img_temploc)

            session = boto3.session.Session()

            client = session.client(
                "s3",
                region_name="nyc3",
                endpoint_url="https://appdev-upload.nyc3.digitaloceanspaces.com",
                aws_access_key_id=os.environ["ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
            )

            client.put_object(
                Bucket="pear",
                Key=img_filename,
                Body=b"Does this work lol",
                ACL="public-read",
            )

        except Exception as e:
            print(f"Unable to upload image because of {e}")
