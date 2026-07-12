import sys
from pathlib import Path
from fpdf import FPDF

class TechnicalDocPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            # No header on cover page
            return
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "Face Enrollment Service - Technical Documentation and Architecture Manual", 0, 0, "L")
        self.cell(0, 10, "CONFIDENTIAL", 0, 1, "R")
        self.set_draw_color(200, 200, 200)
        self.line(10, 18, 200, 18)
        self.ln(8)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.line(10, 282, 200, 282)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "Antigravity AI Systems", 0, 0, "L")
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")
        self.cell(0, 10, "Version 1.0.0", 0, 1, "R")

    def section_header(self, title):
        self.ln(4)
        self.set_font("helvetica", "B", 14)
        self.set_text_color(26, 54, 93)  # Dark Blue #1A365D
        self.cell(0, 10, title, 0, 1, "L")
        self.set_draw_color(43, 108, 176)  # Accent Blue #2B6CB0
        self.set_fill_color(43, 108, 176)
        self.rect(self.get_x(), self.get_y() - 1, 30, 1.5, "F")
        self.ln(5)

    def subsection_header(self, title):
        self.ln(2)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(43, 108, 176)  # Accent Blue #2B6CB0
        self.cell(0, 8, title, 0, 1, "L")
        self.ln(2)

    def paragraph(self, text, style=""):
        self.set_font("helvetica", style, 9.5)
        self.set_text_color(45, 55, 72)  # Charcoal #2D3748
        self.multi_cell(0, 5, text)
        self.ln(3)

    def code_block(self, code_text):
        self.set_font("courier", "", 8.5)
        self.set_text_color(33, 37, 41)
        self.set_fill_color(248, 249, 250)
        self.set_draw_color(226, 232, 240)
        
        # Calculate height needed
        lines = code_text.split("\n")
        h = len(lines) * 4.5 + 4
        
        # Check page boundary
        if self.get_y() + h > 270:
            self.add_page()
            
        x_start = self.get_x()
        y_start = self.get_y()
        self.rect(x_start, y_start, 190, h, "DF")
        self.set_xy(x_start + 4, y_start + 2)
        for line in lines:
            self.cell(0, 4.5, line, 0, 1, "L")
        self.set_xy(x_start, y_start + h)
        self.ln(4)

    def alert_box(self, title, text, type_="info"):
        # Colors based on type
        if type_ == "warning":
            bg = (255, 243, 205)
            border = (255, 238, 186)
            text_color = (133, 100, 4)
        elif type_ == "success":
            bg = (212, 239, 223)
            border = (195, 230, 203)
            text_color = (21, 87, 36)
        else:
            bg = (226, 242, 253)
            border = (188, 223, 253)
            text_color = (12, 74, 96)
            
        self.set_fill_color(*bg)
        self.set_draw_color(*border)
        self.set_text_color(*text_color)
        
        # Height estimation
        lines = text.split("\n")
        h = len(lines) * 5 + 10
        if self.get_y() + h > 270:
            self.add_page()
            
        x_start = self.get_x()
        y_start = self.get_y()
        self.rect(x_start, y_start, 190, h, "DF")
        self.set_xy(x_start + 4, y_start + 3)
        self.set_font("helvetica", "B", 10)
        self.cell(0, 5, title, 0, 1, "L")
        self.set_xy(x_start + 4, self.get_y())
        self.set_font("helvetica", "", 9)
        for line in lines:
            self.cell(0, 4.5, line, 0, 1, "L")
        self.set_xy(x_start, y_start + h)
        self.ln(4)

    def draw_cover_page(self):
        self.add_page()
        # Top background accent
        self.set_fill_color(26, 54, 93) # #1A365D Dark Navy
        self.rect(0, 0, 210, 100, "F")
        
        # Accent bar
        self.set_fill_color(66, 153, 225) # #4299E1 Accent Blue
        self.rect(0, 100, 210, 8, "F")
        
        # Cover Titles
        self.set_xy(20, 35)
        self.set_font("helvetica", "B", 28)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "Face Enrollment Service", 0, 1, "L")
        
        self.set_xy(20, 50)
        self.set_font("helvetica", "", 14)
        self.cell(0, 10, "Production-Grade API & Pipeline Technical Guide", 0, 1, "L")
        
        # Version and Meta info
        self.set_xy(20, 130)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(26, 54, 93)
        self.cell(0, 6, "TECHNICAL MANUAL & SYSTEM ARCHITECTURE", 0, 1, "L")
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(74, 85, 104)
        self.cell(0, 6, "Phase 1: Real-Time Quality Check & Candidate Enrollment", 0, 1, "L")
        self.ln(15)
        
        # Divider Line
        self.set_draw_color(226, 232, 240)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(10)
        
        # Details metadata
        metadata = [
            ("Document Version:", "1.0.0 (Release)"),
            ("AI Recognition Backend:", "InsightFace buffalo_l (SCRFD + ArcFace w600k_r50)"),
            ("Database Storage:", "PostgreSQL (SQLAlchemy Async / Alembic Migrations)"),
            ("Frontend Client:", "Streamlit UI Application"),
            ("Developed By:", "Antigravity AI Agent Pair-Programmer"),
            ("Date Generated:", "July 8, 2026"),
        ]
        
        for label, val in metadata:
            self.set_x(20)
            self.set_font("helvetica", "B", 9.5)
            self.set_text_color(45, 55, 72)
            self.cell(55, 6, label, 0, 0, "L")
            self.set_font("helvetica", "", 9.5)
            self.set_text_color(74, 85, 104)
            self.cell(0, 6, val, 0, 1, "L")

def generate_documentation_pdf(output_path):
    pdf = TechnicalDocPDF()
    pdf.set_margins(10, 20, 10)
    pdf.set_auto_page_break(True, margin=20)
    
    # Page 1: Cover
    pdf.draw_cover_page()
    
    # Page 2: Table of Contents & Executive Summary
    pdf.add_page()
    pdf.section_header("1. Executive Summary")
    pdf.paragraph(
        "The Face Enrollment Service is a production-grade backend application engineered to handle candidate "
        "registration and facial biometric data extraction. It forms the foundational 'Phase 1' of a larger "
        "1:N face recognition system. The core objective of this service is to ensure that only high-quality, "
        "validated facial images are enrolled into the system, and to generate L2-normalized 512-dimensional "
        "embeddings representing the facial characteristics of each candidate. By strictly checking quality parameters "
        "and utilizing state-of-the-art deep learning architectures, the system ensures a high level of accuracy "
        "and reliability for future downstream matching applications."
    )
    
    pdf.subsection_header("Key Architectural Principles")
    pdf.paragraph(
        "- Modularity: Clean separations between Presentation, Application, Domain, and Infrastructure layers.\n"
        "- Robustness: Multi-tiered validation (HTTP, Image payload, and CV/ML quality constraints).\n"
        "- Performance: Fully asynchronous database operations and highly optimized ONNX Runtime execution on CPU.\n"
        "- Portability: Universal export interfaces (JSON & CSV) allowing seamless transfer to search indexes like FAISS."
    )
    
    pdf.alert_box(
        "Phase 1 Boundary Notice",
        "This service implements Face Enrollment, Image Quality Verification, and Embedding Generation only.\n"
        "It does NOT perform face matching, cosine similarity searches, or FAISS index retrieval.",
        "info"
    )

    # Page 3: System Architecture
    pdf.section_header("2. System Architecture")
    pdf.paragraph(
        "The application is structured into a clean, layered architecture to decouple concerns and "
        "ensure maintainability. Below is an overview of the structural layers:"
    )
    
    arch_details = (
        "1. Presentation Layer\n"
        "   - FastAPI Routers: Serve REST endpoints for candidate profiles, webcam captures, and file imports.\n"
        "   - SlowAPI Rate Limiter: Protects endpoints against brute-force calls based on IP addressing.\n"
        "   - Logging Middleware: Custom interceptor capturing response status, latencies, and transaction IDs.\n"
        "   - CORS Middleware: Secures access control policies for multi-origin client requests.\n\n"
        "2. Application Layer\n"
        "   - CandidateService: Handles candidate profile management and CRUD logic.\n"
        "   - EnrollmentService: Coordinates image decoding, uniqueness checks, quality checks, and DB persistence.\n"
        "   - EmbeddingService: Handles manual embedding retrieval and regeneration workflows.\n"
        "   - Export/ImportServices: Executes database extracts and bulk data imports.\n\n"
        "3. Domain Layer\n"
        "   - Pydantic Schemas: Type-safe payload schemas enforcing strict runtime validation.\n"
        "   - Custom Domain Exceptions: Translates infrastructure failures into user-friendly HTTP responses.\n\n"
        "4. Infrastructure Layer\n"
        "   - Repositories: SQLAlchemy async repositories for relational data operations.\n"
        "   - FaceRecognitionPipeline: Encapsulates InsightFace, SCRFD, and ArcFace models.\n"
        "   - PostgreSQL Database: Storage for candidates and high-dimensional float vectors."
    )
    pdf.paragraph(arch_details)

    # Page 4: ML Pipeline Workflow
    pdf.add_page()
    pdf.section_header("3. Machine Learning and Model Pipeline Workflow")
    pdf.paragraph(
        "The core of the application is the FaceRecognitionPipeline. It processes raw images in BGR format "
        "and coordinates four primary steps: Detection, Quality Verification, Alignment, and Embedding Generation."
    )
    
    pdf.subsection_header("Step-by-Step Pipeline Execution Flow")
    
    flow_steps = (
        "Step 1: Face Detection (SCRFD)\n"
        "The system uses the Sample Consensus Robust Face Detector (SCRFD) loaded from the buffalo_l model pack.\n"
        "SCRFD is a high-performance face detector optimized for sub-millisecond execution. It locates face candidates\n"
        "in the input image and returns a bounding box (x1, y1, x2, y2), detection confidence, and 5 facial keypoints\n"
        "(left eye, right eye, nose tip, left mouth corner, right mouth corner).\n\n"
        "Step 2: Quality Check Constraints\n"
        "To ensure high-quality biometric data, the candidate face must pass a series of automated quality checks.\n"
        "If any check fails, the pipeline aborts immediately and returns a detailed failure code:\n"
        "  - Resolution Check: Image size must be at least 64x64 pixels.\n"
        "  - Face Count Check: Exactly one face must be detected (multiple faces or zero faces are rejected).\n"
        "  - Confidence Score: The face detector confidence score must be >= 0.50.\n"
        "  - Face Size Check: Bounding box area must be >= 4,000 px^2 (e.g., approx 63x63 px size inside the frame).\n"
        "  - Blur Detection: Laplacian variance of grayscale image must be >= 50.0 (lower values indicate blurriness).\n"
        "  - Brightness Range: Mean pixel brightness must be between 40.0 (too dark) and 220.0 (too bright).\n\n"
        "Step 3: Face Alignment (norm_crop)\n"
        "To ensure scale and rotation invariance, the face is normalized using an affine transform. The 5 facial keypoints\n"
        "obtained in Step 1 are mapped to target coordinates. The face is cropped and warped to a standard size of\n"
        "112x112 pixels. This aligned image is fed to the embedding model.\n\n"
        "Step 4: Embedding Extraction (ArcFace)\n"
        "The aligned 112x112 RGB image is processed by the ArcFace w600k_r50 ResNet50 model. The neural network maps\n"
        "facial features to a highly discriminative 512-dimensional float vector. Finally, the embedding is L2-normalized\n"
        "so that its Euclidean norm is exactly 1.0. This allows subsequent matching systems to compute cosine similarity\n"
        "using a simple dot product."
    )
    pdf.paragraph(flow_steps)

    # Page 5: Database and ER Schema
    pdf.add_page()
    pdf.section_header("4. Database Design and Entity Relationship")
    pdf.paragraph(
        "The system stores candidate profiles and their corresponding 512-d embeddings in a relational "
        "PostgreSQL database. Below is the relational schema definition:"
    )
    
    pdf.subsection_header("Candidates Table Schema")
    pdf.paragraph(
        "Stores the demographic data of candidates. Each candidate must have a unique candidate_id and email."
    )
    pdf.code_block(
        "Table: candidates\n"
        "-----------------------------------------------------------------\n"
        "Column Name     | Type       | Constraints\n"
        "-----------------------------------------------------------------\n"
        "id              | UUID       | PRIMARY KEY, Default: uuid_generate_v4()\n"
        "candidate_id    | VARCHAR    | UNIQUE, NOT NULL (e.g. Employee ID)\n"
        "name            | VARCHAR    | NOT NULL\n"
        "email           | VARCHAR    | UNIQUE, NOT NULL\n"
        "dob             | DATE       | NULLABLE\n"
        "created_at      | TIMESTAMP  | NOT NULL, Default: timezone('utc', now())\n"
        "updated_at      | TIMESTAMP  | NOT NULL, Default: timezone('utc', now())\n"
        "-----------------------------------------------------------------"
    )
    
    pdf.subsection_header("Face Embeddings Table Schema")
    pdf.paragraph(
        "Stores the high-dimensional biometric vectors. Linked to the candidates table via a foreign key."
    )
    pdf.code_block(
        "Table: face_embeddings\n"
        "-----------------------------------------------------------------\n"
        "Column Name     | Type       | Constraints\n"
        "-----------------------------------------------------------------\n"
        "id              | UUID       | PRIMARY KEY, Default: uuid_generate_v4()\n"
        "candidate_uuid  | UUID       | FOREIGN KEY -> candidates.id, ON DELETE CASCADE\n"
        "embedding       | FLOAT[]    | NOT NULL (512 float array)\n"
        "dimension       | INTEGER    | NOT NULL (default 512)\n"
        "model_name      | VARCHAR    | NOT NULL (default 'buffalo_l')\n"
        "normalized      | BOOLEAN    | NOT NULL (default TRUE)\n"
        "created_at      | TIMESTAMP  | NOT NULL, Default: timezone('utc', now())\n"
        "-----------------------------------------------------------------"
    )

    # Page 6: System Features & Web Client
    pdf.add_page()
    pdf.section_header("5. Features and Client Applications")
    pdf.paragraph(
        "The system provides a rich set of operational capabilities accessible via REST API and a user-friendly UI."
    )
    
    pdf.subsection_header("Key Features")
    pdf.paragraph(
        "- Dual-Channel Enrollment: Register candidates via multipart file uploads or direct webcam capture.\n"
        "- Automated Quality Inspector: Prevents low-quality, dark, blurry, or multi-face images from entering the DB.\n"
        "- Paginated Search: Filter and list candidate profiles and retrieve matching ID records.\n"
        "- Single and Bulk Export: Generate JSON or CSV format files containing candidate data and 512-d embeddings.\n"
        "- Bulk Import: Read exported CSV or JSON sheets, skip duplicates, report detailed errors, and auto-populate DB."
    )
    
    pdf.subsection_header("Streamlit Client UI Layout")
    pdf.paragraph(
        "An intuitive front-end is developed using Streamlit to facilitate testing and administrative tasks:\n"
        "1. Home Dashboard: Visualizes overall system stats (enrolled candidates, total embeddings) and health checks.\n"
        "2. Candidate Enrollment: Allows live camera capture via browser media device, input metadata, and runs real-time checks.\n"
        "3. Explorer View: Interactive tables showing registered candidates, metadata, option to delete or regenerate vector.\n"
        "4. Data Management: Triggers bulk uploads/exports using JSON and CSV files."
    )
    
    pdf.section_header("6. Execution Guide")
    pdf.paragraph("To run the application, use the following bash commands:")
    pdf.code_block(
        "# 1. Activate Virtual Environment\n"
        "source .venv/bin/activate\n\n"
        "# 2. Copy configuration environment variables\n"
        "cp .env.example .env\n\n"
        "# 3. Run database migration schema updates\n"
        "alembic upgrade head\n\n"
        "# 4. Launch FastAPI Server\n"
        "bash scripts/run_server.sh\n\n"
        "# 5. Launch Streamlit UI (runs in separate terminal on port 8501)\n"
        "bash scripts/run_ui.sh"
    )
    
    pdf.output(output_path)
    print(f"Documentation generated successfully at {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    else:
        out_file = "Project_Documentation.pdf"
    generate_documentation_pdf(out_file)
