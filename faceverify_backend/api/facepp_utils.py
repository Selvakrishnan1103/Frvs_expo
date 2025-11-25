# api/facepp_utils.py
import requests
from django.conf import settings
from PIL import Image
import io

# Choose endpoint that matches your Face++ region:
# if your Face++ app is in US region use api-us, else use api-cn
FACEPP_URL = "https://api-us.faceplusplus.com/facepp/v3/compare"

def resize_image_filelike(file_like, max_dim=1920):
    """
    Accepts a file-like object (Django InMemoryUploadedFile or io.BytesIO),
    returns io.BytesIO containing JPEG data (resized if needed).
    """
    try:
        img = Image.open(file_like)
    except Exception:
        # If Pillow cannot read, re-open from bytes
        file_like.seek(0)
        img = Image.open(io.BytesIO(file_like.read()))

    # convert to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize only if too large
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim))

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return buffer

def resize_image_path(path, max_dim=1920):
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return buffer

def compare_faces(stored_image_path, live_image_file):
    """
    stored_image_path: path on disk (student.parent_face_image.path)
    live_image_file: Django InMemoryUploadedFile (request.FILES['face'])
    """

    # prepare stored image bytes (resized)
    img1_buf = resize_image_path(stored_image_path, max_dim=1920)

    # prepare live image bytes (resized)
    # live_image_file may be InMemoryUploadedFile — ensure we can read it
    live_image_file.seek(0)
    img2_buf = resize_image_filelike(live_image_file, max_dim=1920)

    # Build payload — Face++ wants api_key/api_secret in form data, images in files
    data = {
        "api_key": settings.FACEPP_API_KEY,
        "api_secret": settings.FACEPP_API_SECRET,
    }

    files = {
        "image_file1": ("stored.jpg", img1_buf, "image/jpeg"),
        "image_file2": ("live.jpg", img2_buf, "image/jpeg")
    }

    resp = requests.post(FACEPP_URL, data=data, files=files, timeout=30)
    print("FACE++ RAW:", resp.text)
    resp.raise_for_status()
    result = resp.json()

    # If Face++ returns an error with 'error_message' or missing confidence -> return False, None
    if 'error_message' in result:
        print("FACE++ ERROR:", result.get('error_message'))
        return False, None

    if 'confidence' not in result:
        return False, None

    confidence = result['confidence']
    # choose threshold as you like; 70–85 typical
    matched = confidence >= 70
    return matched, confidence
