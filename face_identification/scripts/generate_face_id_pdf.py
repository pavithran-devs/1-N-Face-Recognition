import os
from pathlib import Path
from fpdf import FPDF

# Paths definition
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_PDF_PATH = ROOT_DIR / "Face_Identification_System_Documentation.pdf"

class DocumentPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 6, "1:N Face Identification Service - Complete Technical Documentation", 0, 0, "L")
        self.set_x(-40)
        self.cell(0, 6, f"Release: v1.0.0", 0, 1, "R")
        self.set_draw_color(220, 220, 220)
        self.line(10, 16, 200, 16)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, num, title):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(240, 240, 245)
        self.set_text_color(20, 50, 90)
        self.cell(0, 10, f"Section {num}: {title}", 0, 1, "L", True)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(3)

    def code_block(self, code_text):
        self.set_font("Courier", "", 9)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 4, code_text, 1, "L", True)
        self.ln(3)

    def bullet_point(self, bold_prefix, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 80, 140)
        self.cell(6, 5, "* ", 0, 0, "L")
        self.cell(len(bold_prefix) * 2.2 + 2, 5, bold_prefix, 0, 0, "L")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(1)

def draw_cover_page(pdf):
    pdf.add_page()
    # Blue top banner
    pdf.set_fill_color(20, 50, 90)
    pdf.rect(0, 0, 210, 110, "F")
    
    pdf.set_xy(15, 35)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 26)
    pdf.multi_cell(0, 12, "FACE IDENTIFICATION SERVICE\nCOMPLETE TECHNICAL MANUAL")
    
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "Production-Grade 1:N Biometric Query Microservice", 0, 1, "L")
    
    # Documentation summary
    pdf.set_xy(15, 125)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Manual Overview", 0, 1, "L")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, 
        "This master documentation contains the complete end-to-end technical manual "
        "for the Face Identification microservice (Port 8001). It covers the full technology stack, "
        "database schema, real-time image processing pipeline, modular face detection (SCRFD) "
        "and alignment systems, ArcFace embeddings calculation, and high-performance vector search "
        "operations using Facebook AI Similarity Search (FAISS).\n\n"
        "This PDF was programmatically compiled using FPDF in python."
    )
    
    # Metadata footer
    pdf.set_xy(15, 220)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(15, 215, 195, 215)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(45, 6, "Platform Version:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "v1.0.0-Release", 0, 1)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(45, 6, "Generated Date:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "2026-07-17", 0, 1)

def build_pdf():
    pdf = DocumentPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Page 1: Cover
    draw_cover_page(pdf)
    
    # Page 2: System Architecture
    pdf.add_page()
    pdf.chapter_title("1", "Architecture & Technology Stack")
    pdf.chapter_body(
        "The Face Identification Service runs as an independent FastAPI microservice on Port 8001. "
        "It acts as a query node that handles all read requests for 1:N real-time matches. "
        "The stack combines high-performance web routing with deep learning inference and in-memory vector databases:"
    )
    
    pdf.bullet_point("Core Web Framework: ", "FastAPI (using Uvicorn) for async request handling.")
    pdf.bullet_point("Database Layer: ", "PostgreSQL 16+ accessed asynchronously using SQLAlchemy 2.0 and asyncpg.")
    pdf.bullet_point("Computer Vision: ", "InsightFace (buffalo_l pack containing SCRFD and ArcFace) with ONNX Runtime on CPU.")
    pdf.bullet_point("Vector Search: ", "FAISS-CPU using IndexFlatIP index for inner product calculation.")
    pdf.bullet_point("Image Engine: ", "OpenCV (cv2) and NumPy for matrix manipulation.")
    
    # Page 3: Face Processing Pipeline
    pdf.ln(4)
    pdf.chapter_title("2", "Biometric Processing Pipeline")
    pdf.chapter_body(
        "When an image is submitted to the API, it goes through a multi-stage face processing pipeline. "
        "Each stage must succeed to proceed to the next:"
    )
    
    pdf.bullet_point("1. Face Detection: ", "SCRFD detects bounding boxes and 5 facial landmark keypoints (eyes, nose, mouth). Detections are sorted by box area.")
    pdf.bullet_point("2. Quality Validation: ", "Filters out poor quality images. Verifies resolution (min 160x160), face count (exactly 1), detection score (>=0.55), size (area >=2500px), brightness (40-220), blur (variance >=50), pose angles (<=35 deg), and symmetry.")
    pdf.bullet_point("3. Face Alignment: ", "InsightFace's norm_crop helper performs an affine transform using the 5 keypoints to rotate, scale, and center the face to a standard 112x112 pixel crop.")
    pdf.bullet_point("4. Embedding Extraction: ", "The ArcFace w600k_r50 model extracts a 512-dimensional floating-point vector representing the face feature space.")
    pdf.bullet_point("5. L2 Normalization: ", "The vector is normalized to a unit length so that inner product search calculates exact Cosine Similarity.")

    # Page 4: DB Schema & FAISS Search
    pdf.add_page()
    pdf.chapter_title("3", "Database Schema")
    pdf.chapter_body(
        "The service interfaces with a PostgreSQL schema that links candidate profiles to their biometric embeddings:"
    )
    
    pdf.bullet_point("Candidates Table (candidates): ", "Stores ID (UUID PK), candidate_id (unique, e.g. employee ID), name, email, and date of birth.")
    pdf.bullet_point("Embeddings Table (face_embeddings): ", "Stores ID (UUID PK), candidate_uuid (FK), embedding (ARRAY(FLOAT) of size 512), model_name, and normalized status.")
    
    pdf.ln(4)
    pdf.chapter_title("4", "In-Memory Vector Search (FAISS)")
    pdf.chapter_body(
        "To achieve sub-millisecond search latencies, all candidate embeddings are cached in memory using a FAISS Flat IP index. "
        "The FAISSManager uses a reentrant lock (RLock) to ensure thread safety during lookups and rebuilds."
    )
    
    pdf.heading_2("Cosine Similarity Metric via Inner Product")
    pdf.chapter_body(
        "Because both the database embeddings and the query embedding vector (q) are L2-normalized to unit space, "
        "their dot product is mathematically equal to the Cosine Similarity:"
    )
    pdf.code_block("Similarity = sum(q[i] * db[i]) for i in range(512)")
    
    # Page 5: Step-by-Step API Flow & Hardening
    pdf.add_page()
    pdf.chapter_title("5", "End-to-End API Match Flow")
    pdf.chapter_body(
        "The execution path for a face identification query is as follows:"
    )
    
    pdf.bullet_point("1. Intake: ", "The endpoint receives an image upload, checks the 10MB size limit, and decodes the image using cv2.imdecode.")
    pdf.bullet_point("2. Extraction: ", "The image is processed through the pipeline. If a quality test fails, an HTTP 422 error is returned.")
    pdf.bullet_point("3. Index Query: ", "The query embedding vector is searched in the FAISS index to find the closest matches.")
    pdf.bullet_point("4. Match Decision: ", "If the top match score meets the threshold (default >=0.67), a database query is triggered to fetch candidate metadata. Otherwise, it returns 'Unknown Candidate'.")
    pdf.bullet_point("5. Telemetry: ", "Processing latencies for all sub-operations are saved and returned in the HTTP response JSON.")

    pdf.ln(4)
    pdf.chapter_title("6", "Production Hardening Checklist")
    pdf.bullet_point("CORS Isolation: ", "Restrict CORS origins in the .env file to client origins instead of wildcards.")
    pdf.bullet_point("GPU Execution: ", "Install onnxruntime-gpu and load the CUDAExecutionProvider to lower ArcFace latency from ~90ms to ~15ms.")
    pdf.bullet_point("Index Scale: ", "Change FAISS index type from IndexFlatIP to HNSW or IndexIVFFlat when candidate size exceeds 100,000 records.")

    # Write PDF output
    pdf.output(str(OUTPUT_PDF_PATH))
    print(f"Documentation PDF compiled successfully at: {OUTPUT_PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
