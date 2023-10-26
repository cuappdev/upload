# upload

A Python Flask-SQLAlchemy file upload backend microservice for Cornell AppDev's apps. Made by [Cornell AppDev](cornellappdev.com).

## Installation

# Setup

If running for the first time, run:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Make sure to also create your `.envrc` file by running (we recommend using [`direnv`](https://direnv.net/)):

```
cp envrc.template .envrc
```

Environment variable values can be found by asking a member of Cornell AppDev.

# Run

To run the app, just do:

```
python app.py
```

# Style

So that the repository agrees upon a style standard, we have opted to use [black](https://github.com/psf/black) for Python formatting!

## Setting up linter

Simply run

```
(venv) $ pre-commit
```

# Endpoints

# **/** • GET

Response Body

```
{"success": true, "data": "Hello World!"}
```

# **/upload/** • POST

Images will be passed along as base64 encrypted strings, checkout [this converter](https://www.base64-image.de/) as the format we are using. You can send a POST request to this route and put an image and the bucket name in the form-data. Use `image` key for the image, and `bucket` key for the bucket name.

Request Body

```
{
  "bucket": <bucket_name>,
  "image": "data:image/png;base64,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"
}
```

Response Body

```
{"success": true, "data": "https://<spaces_name>.<spaces_region_name>.digitaloceanspaces.com/<bucket_name>/<filename>"}
```

# **/remove/** • POST

Request Body

```
{
  "bucket": <bucket_name>,
  "image_url": "https://<spaces_name>.<spaces_region_name>.digitaloceanspaces.com/<bucket_name>/<filename>"
}
```

Response Body

```
{
    "success": true,
    "data": "Image successfully deleted!"
}
```
