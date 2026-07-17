"""Streamlit page for real-time 1:N face identification (webcam and upload)."""

import streamlit as st
import ui
from api_client import FaceIdentifyAPIClient

base_url = ui.configure_page("Identify candidate", ":material/person_search:")

st.title(":material/person_search: Live candidate identification")
st.markdown("Perform real-time candidate verification using live camera feeds or photo uploads.")

client = FaceIdentifyAPIClient(base_url=base_url)

# Sidebar parameters
st.sidebar.header(":material/tune: Search configuration")
threshold = st.sidebar.slider(
    "Similarity Threshold", min_value=0.0, max_value=1.0, value=0.65, step=0.05
)
top_k = st.sidebar.slider("Top K matches", min_value=1, max_value=10, value=5, step=1)

# Tab separation
tab_cam, tab_file = st.tabs(["Capture live photo", "Upload image file"])


def handle_identification(image_bytes: bytes, filename: str) -> None:
    with st.spinner("Processing image through pipeline and searching database..."):
        resp = client.identify_face(
            image_bytes, filename=filename, threshold=threshold, top_k=top_k
        )

    # Check for HTTP errors or validation errors
    if "status_code" in resp and resp["status_code"] == 422:
        error_detail = resp.get("detail", {}).get("error", {})
        code = error_detail.get("code", "quality_check_failed")
        msg = error_detail.get("message", "Validation failed.")

        st.error(f"Quality reject ({code}): {msg}", icon=":material/error:")
        return

    if "error" in resp:
        st.error(
            f"Error: {resp['error'].get('message', 'Failed to identify.')}", icon=":material/error:"
        )
        return

    # Success Response
    matched = resp.get("matched", False)
    if matched:
        st.success("Match found.", icon=":material/check_circle:")

        # Details Card
        col1, col2 = st.columns(2)
        with col1:
            st.info(
                f"**Candidate Name:** {resp.get('name')}\n\n"
                f"**Candidate ID:** `{resp.get('candidate_id')}`\n\n"
                f"**Email Address:** {resp.get('email')}"
            )
        with col2:
            dob = resp.get("dob")
            dob_val = dob if dob else "N/A"
            st.info(
                f"**Date of Birth:** {dob_val}\n\n"
                f"**Cosine Similarity Score:** `{resp.get('similarity')}`\n\n"
                f"**Similarity Rank:** `{resp.get('rank')}`"
            )
    else:
        st.warning(
            "Unknown candidate. No match met the similarity threshold.", icon=":material/warning:"
        )


with tab_cam:
    cam_image = st.camera_input("Take a photo of the candidate")
    if cam_image is not None:
        handle_identification(cam_image.getvalue(), "webcam.jpg")

with tab_file:
    uploaded_file = st.file_uploader(
        "Choose a photo of the candidate...", type=["jpg", "jpeg", "png", "bmp"]
    )
    if uploaded_file is not None:
        handle_identification(uploaded_file.getvalue(), uploaded_file.name)
