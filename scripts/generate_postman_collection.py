#!/usr/bin/env python3
"""
scripts/generate_postman_collection.py
Generates a Postman Collection v2.1 JSON file mapping all API paths, parameters,
and standard headers for both microservices.
"""

import json
from pathlib import Path

def build_postman_collection() -> dict:
    collection = {
        "info": {
            "name": "1:N Face Recognition Platform API Collection",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "description": "API collection for both enrollment_service (port 8000) and face_identification (port 8001) services."
        },
        "item": [
            {
                "name": "Enrollment Service (Port 8000)",
                "item": [
                    {
                        "name": "Service Health Check",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{enrollment_url}}/health",
                                "host": ["{{enrollment_url}}"],
                                "path": ["health"]
                            }
                        }
                    },
                    {
                        "name": "Register Candidate (Metadata Only)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "candidate_id": "TEST_CAND_001",
                                    "name": "John Doe",
                                    "email": "john.doe@example.com",
                                    "dob": "1990-01-01"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{enrollment_url}}/candidates/",
                                "host": ["{{enrollment_url}}"],
                                "path": ["candidates", ""]
                            }
                        }
                    },
                    {
                        "name": "Get Candidate by UUID",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{enrollment_url}}/candidates/:id",
                                "host": ["{{enrollment_url}}"],
                                "path": ["candidates", ":id"],
                                "variable": [{"key": "id", "value": "uuid-here"}]
                            }
                        }
                    },
                    {
                        "name": "List/Search Candidates",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{enrollment_url}}/candidates/?search=John&search_field=name",
                                "host": ["{{enrollment_url}}"],
                                "path": ["candidates", ""],
                                "query": [
                                    {"key": "search", "value": "John"},
                                    {"key": "search_field", "value": "name"}
                                ]
                            }
                        }
                    },
                    {
                        "name": "Update Candidate Metadata",
                        "request": {
                            "method": "PUT",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "name": "John Updated",
                                    "email": "john.updated@example.com",
                                    "dob": "1990-01-01"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{enrollment_url}}/candidates/:id",
                                "host": ["{{enrollment_url}}"],
                                "path": ["candidates", ":id"],
                                "variable": [{"key": "id", "value": "uuid-here"}]
                            }
                        }
                    },
                    {
                        "name": "Enroll Candidate via File Upload",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {"key": "image", "type": "file", "src": ""},
                                    {"key": "candidate_id", "value": "TEST_FACE_001", "type": "text"},
                                    {"key": "name", "value": "Jane Smith", "type": "text"},
                                    {"key": "email", "value": "jane.smith@example.com", "type": "text"},
                                    {"key": "dob", "value": "1992-05-15", "type": "text"}
                                ]
                            },
                            "url": {
                                "raw": "{{enrollment_url}}/face/upload",
                                "host": ["{{enrollment_url}}"],
                                "path": ["face", "upload"]
                            }
                        }
                    },
                    {
                        "name": "Enroll Candidate via Webcam Capture",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "image_b64": "data:image/jpeg;base64,...",
                                    "candidate_id": "TEST_CAP_001",
                                    "name": "Alice Capture",
                                    "email": "alice@example.com",
                                    "dob": "1988-11-23"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{enrollment_url}}/face/capture",
                                "host": ["{{enrollment_url}}"],
                                "path": ["face", "capture"]
                            }
                        }
                    },
                    {
                        "name": "Generate Embedding for Candidate",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {"key": "image", "type": "file", "src": ""}
                                ]
                            },
                            "url": {
                                "raw": "{{enrollment_url}}/embedding/generate/:id",
                                "host": ["{{enrollment_url}}"],
                                "path": ["embedding", "generate", ":id"],
                                "variable": [{"key": "id", "value": "uuid-here"}]
                            }
                        }
                    },
                    {
                        "name": "List Embeddings for Candidate",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{enrollment_url}}/embedding/:id",
                                "host": ["{{enrollment_url}}"],
                                "path": ["embedding", ":id"],
                                "variable": [{"key": "id", "value": "uuid-here"}]
                            }
                        }
                    },
                    {
                        "name": "Export Candidates to JSON",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{enrollment_url}}/export/json",
                                "host": ["{{enrollment_url}}"],
                                "path": ["export", "json"]
                            }
                        }
                    },
                    {
                        "name": "Export Candidates to CSV",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{enrollment_url}}/export/csv",
                                "host": ["{{enrollment_url}}"],
                                "path": ["export", "csv"]
                            }
                        }
                    },
                    {
                        "name": "Import Candidates from JSON",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {"key": "file", "type": "file", "src": ""}
                                ]
                            },
                            "url": {
                                "raw": "{{enrollment_url}}/import/json",
                                "host": ["{{enrollment_url}}"],
                                "path": ["import", "json"]
                            }
                        }
                    },
                    {
                        "name": "Delete Candidate",
                        "request": {
                            "method": "DELETE",
                            "header": [],
                            "url": {
                                "raw": "{{enrollment_url}}/candidates/:id",
                                "host": ["{{enrollment_url}}"],
                                "path": ["candidates", ":id"],
                                "variable": [{"key": "id", "value": "uuid-here"}]
                            }
                        }
                    }
                ]
            },
            {
                "name": "Face Identification Service (Port 8001)",
                "item": [
                    {
                        "name": "Service Health Check",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{identification_url}}/health",
                                "host": ["{{identification_url}}"],
                                "path": ["health"]
                            }
                        }
                    },
                    {
                        "name": "Identify Candidate Face",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {"key": "file", "type": "file", "src": ""},
                                    {"key": "threshold", "value": "0.65", "type": "text"},
                                    {"key": "top_k", "value": "3", "type": "text"}
                                ]
                            },
                            "url": {
                                "raw": "{{identification_url}}/identify",
                                "host": ["{{identification_url}}"],
                                "path": ["identify"]
                            }
                        }
                    },
                    {
                        "name": "Rebuild FAISS Index",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "url": {
                                "raw": "{{identification_url}}/index/rebuild",
                                "host": ["{{identification_url}}"],
                                "path": ["index", "rebuild"]
                            }
                        }
                    },
                    {
                        "name": "Fetch Performance Metrics",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{identification_url}}/metrics",
                                "host": ["{{identification_url}}"],
                                "path": ["metrics"]
                            }
                        }
                    }
                ]
            }
        ],
        "variable": [
            {
                "key": "enrollment_url",
                "value": "http://localhost:8000/api/v1",
                "type": "string"
            },
            {
                "key": "identification_url",
                "value": "http://localhost:8001",
                "type": "string"
            }
        ]
    }
    return collection

def main():
    root = Path(__file__).resolve().parent.parent
    output_path = root / "Postman_Collection.json"
    collection = build_postman_collection()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)
    print(f"[+] Postman collection generated successfully at: {output_path}")

if __name__ == "__main__":
    main()
