"""Image I/O and conversion utilities."""
import base64
import io

import cv2
import numpy as np
from PIL import Image


def bytes_to_bgr(data: bytes) -> np.ndarray:
    """Convert raw image bytes to a BGR numpy array (OpenCV format)."""
    np_arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes.")
    return img


def base64_to_bgr(b64_string: str) -> np.ndarray:
    """Decode a base64 image string to BGR numpy array."""
    # Strip data URI prefix if present (e.g. "data:image/jpeg;base64,…")
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    data = base64.b64decode(b64_string)
    return bytes_to_bgr(data)


def bgr_to_bytes(image: np.ndarray, ext: str = ".jpg") -> bytes:
    """Encode a BGR numpy array to bytes."""
    ok, buf = cv2.imencode(ext, image)
    if not ok:
        raise ValueError(f"Could not encode image as {ext}.")
    return buf.tobytes()


def pil_to_bgr(pil_image: Image.Image) -> np.ndarray:
    """Convert a PIL Image to BGR numpy array."""
    rgb = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
