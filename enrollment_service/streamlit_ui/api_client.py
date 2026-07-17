"""
api_client.py — thin wrapper around the Enrollment Service REST API.
All functions return (data, error_message). On success error_message is None.
"""
from __future__ import annotations

import base64
import io
from typing import Any

import requests
from PIL import Image

# ── Base URL (configurable from sidebar) ──────────────────────────────────────
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"


def _url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _handle(resp: requests.Response) -> tuple[Any, str | None]:
    try:
        data = resp.json()
    except Exception:
        data = resp.text
    if resp.ok:
        return data, None
    # Extract error message from our standard error envelope
    if isinstance(data, dict) and "error" in data:
        return None, data["error"].get("message", str(data))
    return None, str(data)


# ── Health ─────────────────────────────────────────────────────────────────────

def get_health(base: str = DEFAULT_BASE_URL) -> tuple[dict, str | None]:
    try:
        resp = requests.get(_url(base, "/health"), timeout=5)
        return _handle(resp)
    except requests.ConnectionError:
        return {}, "Cannot reach the API. Is the server running?"


# ── Candidates ────────────────────────────────────────────────────────────────

def list_candidates(
    base: str,
    offset: int = 0,
    limit: int = 100,
    search: str = "",
    search_field: str = "name",
) -> tuple[dict, str | None]:
    params: dict[str, Any] = {"offset": offset, "limit": limit}
    if search.strip():
        params["search"] = search.strip()
        params["search_field"] = search_field
    try:
        resp = requests.get(_url(base, "/candidates/"), params=params, timeout=10)
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


def get_candidate(base: str, uuid: str) -> tuple[dict, str | None]:
    try:
        resp = requests.get(_url(base, f"/candidates/{uuid}"), timeout=10)
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


def create_candidate(base: str, payload: dict) -> tuple[dict, str | None]:
    try:
        resp = requests.post(_url(base, "/candidates/"), json=payload, timeout=10)
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


def update_candidate(base: str, uuid: str, payload: dict) -> tuple[dict, str | None]:
    try:
        resp = requests.put(_url(base, f"/candidates/{uuid}"), json=payload, timeout=10)
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


def delete_candidate(base: str, uuid: str) -> tuple[bool, str | None]:
    try:
        resp = requests.delete(_url(base, f"/candidates/{uuid}"), timeout=10)
        if resp.status_code == 204:
            return True, None
        return False, _handle(resp)[1]
    except requests.ConnectionError as e:
        return False, str(e)


# ── Face Enrollment ───────────────────────────────────────────────────────────

def enroll_upload(
    base: str,
    image_bytes: bytes,
    filename: str,
    candidate_id: str,
    name: str,
    email: str,
    dob: str | None = None,
) -> tuple[dict, str | None]:
    data: dict[str, Any] = {
        "candidate_id": candidate_id,
        "name": name,
        "email": email,
    }
    if dob:
        data["dob"] = dob
    try:
        resp = requests.post(
            _url(base, "/face/upload"),
            data=data,
            files={"image": (filename, image_bytes, "image/jpeg")},
            timeout=30,
        )
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


def enroll_capture(
    base: str,
    image_bytes: bytes,
    candidate_id: str,
    name: str,
    email: str,
    dob: str | None = None,
) -> tuple[dict, str | None]:
    b64 = base64.b64encode(image_bytes).decode()
    payload: dict[str, Any] = {
        "image_b64": b64,
        "candidate_id": candidate_id,
        "name": name,
        "email": email,
    }
    if dob:
        payload["dob"] = dob
    try:
        resp = requests.post(_url(base, "/face/capture"), json=payload, timeout=30)
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)





# ── Embeddings ────────────────────────────────────────────────────────────────

def get_embeddings(base: str, candidate_uuid: str) -> tuple[list, str | None]:
    try:
        resp = requests.get(_url(base, f"/embedding/{candidate_uuid}"), timeout=10)
        return _handle(resp)
    except requests.ConnectionError as e:
        return [], str(e)


def regenerate_embedding(
    base: str, candidate_uuid: str, image_bytes: bytes, filename: str
) -> tuple[dict, str | None]:
    try:
        resp = requests.put(
            _url(base, f"/embedding/regenerate/{candidate_uuid}"),
            files={"image": (filename, image_bytes, "image/jpeg")},
            timeout=30,
        )
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


# ── Export ────────────────────────────────────────────────────────────────────

def export_json(base: str, candidate_uuid: str | None = None) -> tuple[dict, str | None]:
    params = {}
    if candidate_uuid:
        params["candidate_id"] = candidate_uuid
    try:
        resp = requests.get(_url(base, "/export/json"), params=params, timeout=30)
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


def export_csv(base: str, candidate_uuid: str | None = None) -> tuple[dict, str | None]:
    params = {}
    if candidate_uuid:
        params["candidate_id"] = candidate_uuid
    try:
        resp = requests.get(_url(base, "/export/csv"), params=params, timeout=30)
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


# ── Import ────────────────────────────────────────────────────────────────────

def import_json(base: str, file_bytes: bytes, filename: str) -> tuple[dict, str | None]:
    try:
        resp = requests.post(
            _url(base, "/import/json"),
            files={"file": (filename, file_bytes, "application/json")},
            timeout=30,
        )
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


def import_csv(base: str, file_bytes: bytes, filename: str) -> tuple[dict, str | None]:
    try:
        resp = requests.post(
            _url(base, "/import/csv"),
            files={"file": (filename, file_bytes, "text/csv")},
            timeout=30,
        )
        return _handle(resp)
    except requests.ConnectionError as e:
        return {}, str(e)


# ── Helpers ───────────────────────────────────────────────────────────────────

def pil_to_bytes(img: Image.Image, fmt: str = "JPEG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
