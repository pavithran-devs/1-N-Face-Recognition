#!/usr/bin/env python3
"""
bulk_enroll_lfw.py

Automates face enrollment by parsing the LFW dataset (lfw-deepfunneled directory),
filtering out folders containing <= 1 photo, and enrolling exactly one photo 
for each of the remaining folders to the Face Enrollment API.
"""

import os
import sys
import argparse
import glob
from pathlib import Path
import requests

def check_server_health(api_url: str) -> bool:
    """Verifies that the API server is online and reachable."""
    health_url = f"{api_url}/health"
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            return True
        print(f"[-] Server returned status code {response.status_code} on health check.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection to {health_url} failed: {e}")
    return False

def format_name(folder_name: str) -> str:
    """Converts a folder name like 'AJ_Cook' to 'AJ Cook'."""
    return folder_name.replace("_", " ")

def format_email(folder_name: str) -> str:
    """Converts 'AJ_Cook' to 'aj_cook@example.com'."""
    return f"{folder_name.lower()}@example.com"

def bulk_enroll(api_url: str, lfw_dir: str, target_limit: int):
    """Parses directories, filters, and enrolls candidates up to target_limit successes."""
    print("=" * 80)
    print("                     LFW Bulk Face Enrollment Script                    ")
    print("=" * 80)
    
    lfw_path = Path(lfw_dir)
    if not lfw_path.is_dir():
        print(f"[-] Error: LFW directory '{lfw_dir}' does not exist.")
        sys.exit(1)

    print(f"[*] Scanning directory: {lfw_path.resolve()}")
    
    # Get all subdirectories and sort alphabetically
    subdirs = sorted([d for d in lfw_path.iterdir() if d.is_dir()])
    total_dirs = len(subdirs)
    print(f"[+] Found {total_dirs} subdirectories in total.")
    print(f"[*] Enrolling until reaching {target_limit} successful candidates...")
    print("-" * 80)

    success_count = 0
    skipped_count = 0
    duplicate_count = 0
    quality_fail_count = 0
    other_fail_count = 0

    processed_dirs = 0

    upload_endpoint = f"{api_url}/face/upload"

    for subdir in subdirs:
        if success_count >= target_limit:
            print(f"\n[+] Reached success target of {target_limit} candidates. Stopping.")
            break

        processed_dirs += 1
        folder_name = subdir.name

        # Count image files inside directory (supporting jpg, jpeg, png)
        image_patterns = ["*.jpg", "*.jpeg", "*.png"]
        images = []
        for pattern in image_patterns:
            images.extend(sorted(subdir.glob(pattern)))
        
        photo_count = len(images)

        # Rule: skip if folder has exactly 1 photo (or 0)
        if photo_count <= 1:
            # print(f"[*] Skipping {folder_name} (contains {photo_count} photo/s)")
            skipped_count += 1
            continue

        # We keep the directory and pick exactly one photo (the first alphabetically)
        selected_image_path = images[0]
        
        name = format_name(folder_name)
        candidate_id = folder_name
        email = format_email(folder_name)

        print(f"[{success_count + 1}/{target_limit}] Enrolling: {folder_name} ({photo_count} photos) -> ", end="", flush=True)

        try:
            with open(selected_image_path, "rb") as img_file:
                # Prepare multipart request
                files = {
                    "image": (selected_image_path.name, img_file, "image/jpeg")
                }
                data = {
                    "candidate_id": candidate_id,
                    "name": name,
                    "email": email
                }
                
                response = requests.post(upload_endpoint, files=files, data=data, timeout=30)
                
                if response.status_code in (200, 201):
                    print("SUCCESS")
                    success_count += 1
                elif response.status_code == 409:
                    print("DUPLICATE (409 Candidate already exists)")
                    duplicate_count += 1
                elif response.status_code == 422:
                    # Quality check failed (e.g. face detection) or validation error
                    try:
                        error_detail = response.json().get("error", {}).get("message", "Validation error")
                    except Exception:
                        error_detail = response.text
                    print(f"FAILED (422: {error_detail})")
                    quality_fail_count += 1
                else:
                    print(f"FAILED (Status {response.status_code})")
                    other_fail_count += 1

        except Exception as exc:
            print(f"ERROR ({exc})")
            other_fail_count += 1

    print("\n" + "=" * 80)
    print("                               Summary Report                               ")
    print("=" * 80)
    print(f"Total Subdirectories Scanned : {processed_dirs}/{total_dirs}")
    print(f"Successfully Enrolled        : {success_count}")
    print(f"Skipped (<=1 photo)          : {skipped_count}")
    print(f"Duplicates (Already exists)  : {duplicate_count}")
    print(f"Quality Check / Val Failures : {quality_fail_count}")
    print(f"Other Connection Failures    : {other_fail_count}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Bulk enroll candidates from the LFW dataset directories."
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/api/v1",
        help="FastAPI server API v1 URL endpoint (default: http://localhost:8000/api/v1)"
    )
    parser.add_argument(
        "--dir",
        default="./lfw-deepfunneled",
        help="Path to the lfw-deepfunneled directory containing face image folders (default: ./lfw-deepfunneled)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Target number of successful candidate enrollments (default: 500)"
    )

    args = parser.parse_args()

    # Pre-checks
    if not check_server_health(args.url):
        print("[-] Error: Enrollment API is not reachable. Please verify the server is running.")
        sys.exit(1)

    bulk_enroll(
        api_url=args.url,
        lfw_dir=args.dir,
        target_limit=args.limit
    )

if __name__ == "__main__":
    main()
