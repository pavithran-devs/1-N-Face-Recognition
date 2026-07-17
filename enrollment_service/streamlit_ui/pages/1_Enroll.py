"""
Page 1 — Enroll Candidate
Supports: Single-Image enrollment (upload or webcam snapshots)
"""
import sys
from pathlib import Path

import streamlit as st
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
import api_client as api
import ui

base_url = ui.configure_page("Enroll candidate", ":material/person_add:")

st.title(":material/person_add: Enroll a new candidate")
st.markdown("Fill in the candidate details and choose the enrollment mode.")

# Initialize session state for webcam multi-capture
if "captured_images" not in st.session_state:
    st.session_state.captured_images = []
if "last_capture" not in st.session_state:
    st.session_state.last_capture = None

mode = "Single-Image"

# ── Candidate info form ────────────────────────────────────────────────────────
st.subheader("Candidate Details")
col1, col2 = st.columns(2)
with col1:
    candidate_id = st.text_input("Candidate ID *", placeholder="e.g. EMP001")
    name         = st.text_input("Full Name *", placeholder="e.g. Alice Smith")
with col2:
    email = st.text_input("Email *", placeholder="alice@example.com")
    dob   = st.date_input("Date of Birth (optional)", value=None)

st.subheader("Face image")

# ── Single-Image Mode ──────────────────────────────────────────────────────────
if mode == "Single-Image":
    tab_upload, tab_webcam = st.tabs(["Upload image", "Webcam capture"])
    
    with tab_upload:
        uploaded = st.file_uploader(
            "Upload a face photo (JPEG / PNG / BMP, max 10 MB)",
            type=["jpg", "jpeg", "png", "bmp"],
            key="enroll_upload",
        )
        if uploaded:
            st.image(uploaded, caption="Uploaded image", width=300)
            
    with tab_webcam:
        webcam_img = st.camera_input("Take a photo", key="enroll_webcam")
        if webcam_img:
            st.image(webcam_img, caption="Captured image", width=300)



st.markdown("---")

enroll_clicked = st.button(
    "Enroll Candidate",
    icon=":material/rocket_launch:",
    width="stretch",
    type="primary",
)

# ── Handle submission ─────────────────────────────────────────────────────────
if enroll_clicked:
    # Validation
    errors = []
    if not candidate_id.strip():
        errors.append("Candidate ID is required.")
    if not name.strip():
        errors.append("Full Name is required.")
    if not email.strip() or "@" not in email:
        errors.append("A valid email is required.")

    # Determine image sources
    image_bytes_list = []
    filenames_list = []
    
    if uploaded is not None:
        image_bytes_list.append(uploaded.getvalue())
        filenames_list.append(uploaded.name)
    elif webcam_img is not None:
        image_bytes_list.append(webcam_img.getvalue())
        filenames_list.append("webcam.jpg")
    else:
        errors.append("Please upload or capture a face image.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        dob_str = dob.isoformat() if dob else None
        
        with st.spinner("Running face detection and generating embedding…"):
            data, err = api.enroll_upload(
                base_url,
                image_bytes=image_bytes_list[0],
                filename=filenames_list[0],
                candidate_id=candidate_id.strip(),
                name=name.strip(),
                email=email.strip(),
                dob=dob_str,
            )

        if err:
            st.error(f"❌ Enrollment failed: {err}")
        else:
            st.success("Candidate enrolled successfully.", icon=":material/check_circle:")
            
            # Clear session state captured images after successful enrollment
            st.session_state.captured_images = []
            st.session_state.last_capture = None

            # ── Summary cards ─────────────────────────────────────────────────
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("### :material/person: Candidate")
                c = data["candidate"]
                st.markdown(f"- **UUID:** `{c['id']}`")
                st.markdown(f"- **Candidate ID:** {c['candidate_id']}")
                st.markdown(f"- **Name:** {c['name']}")
                st.markdown(f"- **Email:** {c['email']}")
                if c.get("dob"):
                    st.markdown(f"- **DOB:** {c['dob']}")
            with col_b:
                st.markdown("### :material/neurology: Embedding")
                e = data["embedding"]
                st.markdown(f"- **Embedding ID:** `{e['id']}`")
                st.markdown(f"- **Dimension:** {e['embedding_dimension']}")
                st.markdown(f"- **Model:** {e['model_name']}")
                st.markdown(f"- **Normalised:** {e['normalized']}")

                q = data.get("quality_code", "—")
                st.markdown(f"- **Last Quality code:** `{q}`")

            # ── Timing breakdown ──────────────────────────────────────────────
            timings = data.get("timings", {})
            if timings:
                st.markdown("### :material/timer: Stage timings (Aggregate)")
                t_cols = st.columns(len(timings))
                for col, (stage, seconds) in zip(t_cols, timings.items()):
                    col.metric(stage.capitalize(), f"{seconds * 1000:.1f} ms")
