"""
Face Enrollment Service — Streamlit UI
Entry point: Home / Dashboard
Run: streamlit run streamlit_ui/Home.py
"""
import sys
from pathlib import Path

import streamlit as st

# Make the ui directory importable
sys.path.insert(0, str(Path(__file__).parent))
import api_client as api
import ui

# ── Page config ───────────────────────────────────────────────────────────────
base_url = ui.configure_page("Face enrollment dashboard", ":material/face:")

# ── Health check banner ───────────────────────────────────────────────────────
health, err = api.get_health(base_url)

if err:
    st.error(f"⚠️ API unreachable: {err}")
    st.info("Start the backend first:  `uvicorn app.main:app --reload`")
    st.stop()

with st.container(horizontal=True):
    st.metric(
        "Service status",
        "Online" if health.get("status") == "ok" else "Error",
        border=True,
    )
    loaded = health.get("pipeline_loaded", False)
    st.metric("Recognition pipeline", "Loaded" if loaded else "Not loaded", border=True)
    st.metric("API version", health.get("version", "—"), border=True)

# ── Candidate stats ───────────────────────────────────────────────────────────
st.header(":material/dashboard: Dashboard")

result, err = api.list_candidates(base_url, limit=1)
total = 0
if not err and isinstance(result, dict):
    total = result.get("pagination", {}).get("total", 0)

with st.container(horizontal=True):
    st.metric("Total candidates", total, border=True)
    st.metric("Pipeline model", "ArcFace buffalo_l", border=True)
    st.metric("Embedding dimension", "512-d", border=True)

# ── Recent candidates table ────────────────────────────────────────────────────
st.subheader(":material/history: Recent candidates")

result, err = api.list_candidates(base_url, limit=10)
if err:
    st.error(err)
elif result and result.get("data"):
    import pandas as pd

    rows = [
        {
            "Name": c["name"],
            "Candidate ID": c["candidate_id"],
            "Email": c["email"],
            "Enrolled": c["created_at"][:19].replace("T", " "),
        }
        for c in result["data"]
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True)
else:
    st.info("No candidates enrolled yet. Go to **Enroll Candidate** to get started.")

# ── Quick-start guide ──────────────────────────────────────────────────────────
with st.expander(":material/menu_book: Quick start guide", expanded=(total == 0)):
    st.markdown("""
### Getting started

1. **Enroll a candidate** — go to *Enroll Candidate*, fill in the form, and upload or capture a face photo.
2. **Manage candidates** — view, search, edit, or delete enrollments on the *Manage Candidates* page.
3. **Inspect embeddings** — paste a candidate UUID on the *View Embeddings* page to see the stored 512-d vector.
4. **Export / Import** — download your data as JSON or CSV, and re-import it on the *Export / Import* page.

### Quality requirements for face images

| Check | Requirement |
|-------|-------------|
| Face count | Exactly **1** face |
| Minimum size | Face bbox area ≥ 4,000 px² |
| Blur | Laplacian variance ≥ 50 |
| Brightness | Mean pixel 40 – 220 |
| Resolution | Image ≥ 64 × 64 px |
    """)
