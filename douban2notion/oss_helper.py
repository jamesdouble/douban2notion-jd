import os
import uuid
import requests
import oss2
from dotenv import load_dotenv

load_dotenv()

OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT")

print(
    f"OSS_ACCESS_KEY_ID = {OSS_ACCESS_KEY_ID}\n"
    f"OSS_ACCESS_KEY_SECRET = {OSS_ACCESS_KEY_SECRET}\n"
    f"OSS_ENDPOINT = {OSS_ENDPOINT}\n"
    f"OSS_BUCKET_NAME = {OSS_BUCKET_NAME}\n"
)

auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)


def upload_image_to_oss(image_url: str, headers: dict = None) -> str:
    """
    Downloads an image from a URL and uploads it to Alibaba Cloud OSS.
    Returns the new URL of the image in OSS.
    """
    if not OSS_ACCESS_KEY_ID or len(OSS_ACCESS_KEY_ID) <= 0:
        return image_url
    local_filename = f"/tmp/{uuid.uuid4()}.jpg"
    try:
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return image_url
    
    try:
        oss_key = f"images/{uuid.uuid4()}.jpg"
        with open(local_filename, "rb") as file:
            bucket.put_object(oss_key, file)
        oss_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{oss_key}"
        return oss_url
    except Exception as e:
        print(f"Error uploading image {image_url} to OSS: {e}")
        return image_url
