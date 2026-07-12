import glob
import io
import os
import random
import uuid
from locust import HttpUser, task, between, events
from PIL import Image

# Global list to store LFW face image paths
FACE_IMAGE_PATHS = []

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Scan and find LFW face images on test startup."""
    global FACE_IMAGE_PATHS
    # Search for JPEG files in enrollment_service/lfw-deepfunneled
    lfw_pattern = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "enrollment_service",
        "lfw-deepfunneled",
        "**",
        "*.jpg"
    )
    FACE_IMAGE_PATHS = glob.glob(lfw_pattern, recursive=True)
    print(f"[*] Found {len(FACE_IMAGE_PATHS)} real face images in the LFW dataset.")
    if not FACE_IMAGE_PATHS:
        print("[!] No LFW face images found. Will fallback to generating dummy gray JPEGs.")

class FaceRecognitionLoadTestUser(HttpUser):
    # Base host is required by Locust HttpUser even when overriding full URLs in tasks
    host = "http://localhost:8000"
    # Simulate a user waiting between 1 and 3 seconds between tasks
    wait_time = between(1.0, 3.0)

    def on_start(self):
        """Prepare fallback dummy image bytes in memory."""
        self.fallback_image_bytes = self._generate_dummy_jpeg()

    def _generate_dummy_jpeg(self) -> bytes:
        """Generate a simple gray JPEG in memory for fallback."""
        img = Image.new("RGB", (250, 250), color=(128, 128, 128))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        return img_bytes.getvalue()

    def _get_random_image(self) -> tuple[str, bytes]:
        """Returns a filename and its image bytes (either real or fallback)."""
        if FACE_IMAGE_PATHS:
            path = random.choice(FACE_IMAGE_PATHS)
            try:
                with open(path, "rb") as f:
                    return os.path.basename(path), f.read()
            except Exception as e:
                pass
        return "dummy_face.jpg", self.fallback_image_bytes

    @task(2)
    def test_health_endpoints(self):
        """Low-overhead task checking health of both services."""
        # 1. Enrollment Service Health Check
        with self.client.get(
            "http://localhost:8000/api/v1/health",
            name="Enrollment Service Health Check",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code {response.status_code}")

        # 2. Face Identification Service Health Check
        with self.client.get(
            "http://localhost:8001/health",
            name="Face Identification Service Health Check",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code {response.status_code}")

    @task(2)
    def test_list_candidates(self):
        """Medium-overhead query task listing candidates on the Enrollment Service."""
        with self.client.get(
            "http://localhost:8000/api/v1/candidates/?limit=20",
            name="List Candidates (Limit 20)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code {response.status_code}")

    @task(5)
    def test_face_identification(self):
        """High-overhead 1:N face identification task on the Identification Service."""
        filename, img_bytes = self._get_random_image()
        files = {
            "file": (filename, img_bytes, "image/jpeg")
        }
        # Note: Port 8001 handles identification
        with self.client.post(
            "http://localhost:8001/identify",
            files=files,
            data={"threshold": 0.65, "top_k": 3},
            name="Face Identification (1:N Search)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 422:
                # If image quality check fails (e.g. no face in dummy gray image),
                # it's an expected API response and not a server failure.
                response.success()
            else:
                response.failure(f"Failed with status: {response.status_code}, body: {response.text}")

    @task(1)
    def test_face_enrollment(self):
        """Heavyweight face enrollment task on the Enrollment Service."""
        filename, img_bytes = self._get_random_image()
        # Generate random unique candidate details
        unique_suffix = uuid.uuid4().hex[:8]
        data = {
            "candidate_id": f"LOAD_TEST_{unique_suffix}",
            "name": f"Load Test Candidate {unique_suffix}",
            "email": f"load_{unique_suffix}@example.com",
            "dob": "1990-01-01"
        }
        files = {
            "image": (filename, img_bytes, "image/jpeg")
        }
        # Note: Port 8000 handles enrollment
        with self.client.post(
            "http://localhost:8000/api/v1/face/upload",
            files=files,
            data=data,
            name="Face Enrollment (Upload & Embed)",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 422:
                # Expected if quality validation fails (no face in dummy image)
                response.success()
            else:
                response.failure(f"Failed with status: {response.status_code}, body: {response.text}")
