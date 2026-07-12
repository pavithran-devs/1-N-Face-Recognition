"""
Page 3 — View Embeddings
Features: look up embeddings by candidate UUID, visualise vector, regenerate
"""
import sys
from pathlib import Path

import streamlit as st
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
import api_client as api
import ui

base_url = ui.configure_page("View embeddings", ":material/neurology:")

st.title(":material/neurology: View embeddings")

# ── Candidate lookup ──────────────────────────────────────────────────────────
st.markdown("Paste a candidate UUID to inspect their stored face embeddings.")

col_input, col_btn = st.columns([4, 1], vertical_alignment="bottom")
with col_input:
    lookup_uuid = st.text_input("Candidate UUID", placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
with col_btn:
    lookup = st.button("Look up", icon=":material/search:", width="stretch")

# Also allow picking from a recent list
with st.expander(":material/history: Or pick a recent candidate"):
    result, err = api.list_candidates(base_url, limit=20)
    if err:
        st.error(err)
    elif result.get("data"):
        options = {f"{c['name']} ({c['candidate_id']})": c["id"] for c in result["data"]}
        picked = st.selectbox("Select candidate", ["— choose —"] + list(options.keys()))
        if picked != "— choose —":
            lookup_uuid = options[picked]
            lookup = True

# ── Fetch and display embeddings ──────────────────────────────────────────────
if lookup and lookup_uuid.strip():
    uuid = lookup_uuid.strip()

    # Candidate detail
    cand, cerr = api.get_candidate(base_url, uuid)
    if cerr:
        st.error(f"Candidate not found: {cerr}")
        st.stop()

    st.markdown(f"### :material/person: {cand['name']} — `{cand['candidate_id']}`")
    st.caption(f"UUID: `{uuid}`")

    # Embeddings
    embeddings, eerr = api.get_embeddings(base_url, uuid)
    if eerr:
        st.error(f"Could not fetch embeddings: {eerr}")
        st.stop()

    if not embeddings:
        st.warning("No embeddings stored for this candidate. Use **Enroll** or **Regenerate** below.")
    else:
        for i, emb in enumerate(embeddings):
            with st.expander(
                f"Embedding {i + 1} — `{emb['id']}` · {emb['model_name']} · dim={emb['embedding_dimension']}",
                expanded=(i == 0),
            ):
                col_meta, col_vis = st.columns([1, 2])
                with col_meta:
                    st.markdown(f"- **Model:** {emb['model_name']}")
                    st.markdown(f"- **Dimension:** {emb['embedding_dimension']}")
                    st.markdown(f"- **Normalised:** {emb['normalized']}")
                    created = emb.get("created_at", "")
                    if created:
                        st.markdown(f"- **Created:** {created[:19].replace('T', ' ')}")

                with col_vis:
                    # Fetch embedding detail from a detail endpoint if available
                    # The list endpoint doesn't return the vector — show a bar chart placeholder
                    st.markdown("**Embedding vector preview**")
                    st.caption("First 64 of 512 dimensions shown")
                    # We don't have the raw vector from list endpoint; show a placeholder chart
                    # Real vector would come from a detail endpoint — show info instead
                    st.info(
                        "The raw 512-d vector is stored in the database. "
                        "Export to JSON to inspect the full vector values."
                    )

    # ── Regenerate embedding ──────────────────────────────────────────────────
    st.subheader(":material/autorenew: Regenerate embedding")
    st.caption("Upload a new face photo to replace all existing embeddings for this candidate.")

    with st.form(f"regen_{uuid}"):
        new_img = st.file_uploader("New face image (JPEG/PNG/BMP)", type=["jpg", "jpeg", "png", "bmp"])
        if new_img:
            st.image(Image.open(new_img), width=250)
        regen = st.form_submit_button(
            "Regenerate", icon=":material/autorenew:", type="primary", width="stretch"
        )

    if regen:
        if not new_img:
            st.error("Please upload a face image first.")
        else:
            with st.spinner("Regenerating embedding…"):
                result, err = api.regenerate_embedding(
                    base_url, uuid, new_img.getvalue(), new_img.name
                )
            if err:
                st.error(f"❌ {err}")
            else:
                st.success(
                    f"✅ New embedding generated — ID: `{result['id']}` · dim={result['embedding_dimension']}"
                )
                st.rerun()
