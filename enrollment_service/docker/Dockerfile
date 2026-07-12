# Reference only — Docker is not required to run this service.
# The service runs directly on the host via uvicorn.

FROM python:3.11-slim

WORKDIR /app

# System dependencies for OpenCV / onnxruntime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
