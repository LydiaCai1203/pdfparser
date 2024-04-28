import base64
import requests


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_binary = image_file.read()
        base64_encoded = base64.b64encode(image_binary)
        base64_string = base64_encoded.decode("utf-8")
    return base64_string


resp = requests.post(
    "http://172.18.0.5:5555/api/pdfparser/content_extraction",
    json={
        "base64_code": [image_to_base64("./page-1.png")],
        "code_of": "picture",
        "extract_method": "best",
    }
)

print(resp.json())
