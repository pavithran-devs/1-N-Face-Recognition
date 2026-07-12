"""
Page 2 — Manage Candidates
Features: paginated list, search, view detail, edit, delete
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
import api_client as api
import ui

base_url = ui.configure_page("Manage candidates", ":material/group:")

st.title(":material/group: Manage candidates")

# ── Search + pagination controls ──────────────────────────────────────────────
col_search, col_field, col_limit = st.columns([3, 1, 1], vertical_alignment="bottom")
with col_search:
    search_query = st.text_input("🔍 Search", placeholder="Type a name or ID…", label_visibility="collapsed")
with col_field:
    search_field = st.selectbox("Field", ["name", "candidate_id"], label_visibility="collapsed")
with col_limit:
    page_size = st.selectbox("Per page", [10, 25, 50, 100], label_visibility="collapsed")

if "candidates_page" not in st.session_state:
    st.session_state.candidates_page = 0

offset = st.session_state.candidates_page * page_size

# ── Fetch ─────────────────────────────────────────────────────────────────────
result, err = api.list_candidates(
    base_url,
    offset=offset,
    limit=page_size,
    search=search_query,
    search_field=search_field,
)

if err:
    st.error(f"API error: {err}")
    st.stop()

candidates = result.get("data", [])
pagination = result.get("pagination", {})
total = pagination.get("total", 0)

st.caption(f"Showing {offset + 1}–{min(offset + len(candidates), total)} of **{total}** candidates")

# ── Candidates table ──────────────────────────────────────────────────────────
if not candidates:
    st.info("No candidates found.")
else:
    # Build display dataframe
    rows = [
        {
            "UUID": c["id"],
            "Candidate ID": c["candidate_id"],
            "Name": c["name"],
            "Email": c["email"],
            "Enrolled At": c["created_at"][:19].replace("T", " "),
        }
        for c in candidates
    ]
    df = pd.DataFrame(rows)

    # Allow row selection
    selection = st.dataframe(
        df,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # ── Pagination controls ───────────────────────────────────────────────────
    p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
    with p_col1:
        if st.button("Previous", icon=":material/arrow_back:", disabled=not pagination.get("has_prev")):
            st.session_state.candidates_page -= 1
            st.rerun()
    with p_col2:
        total_pages = max(1, (total + page_size - 1) // page_size)
        st.caption(f"Page {st.session_state.candidates_page + 1} / {total_pages}")
    with p_col3:
        if st.button("Next", icon=":material/arrow_forward:", disabled=not pagination.get("has_next")):
            st.session_state.candidates_page += 1
            st.rerun()

    # ── Detail panel for selected row ─────────────────────────────────────────
    selected_rows = selection.get("selection", {}).get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        candidate = candidates[selected_idx]
        uuid = candidate["id"]

        st.subheader(f":material/description: {candidate['name']}")

        tab_view, tab_edit, tab_delete = st.tabs(["View", "Edit", "Delete"])

        # ── View ──────────────────────────────────────────────────────────────
        with tab_view:
            detail, err2 = api.get_candidate(base_url, uuid)
            if err2:
                st.error(err2)
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**UUID:** `{detail['id']}`")
                    st.markdown(f"**Candidate ID:** {detail['candidate_id']}")
                    st.markdown(f"**Name:** {detail['name']}")
                with c2:
                    st.markdown(f"**Email:** {detail['email']}")
                    st.markdown(f"**DOB:** {detail.get('dob') or '—'}")
                    st.markdown(f"**Enrolled:** {detail['created_at'][:19].replace('T', ' ')}")
                    st.markdown(f"**Updated:** {detail['updated_at'][:19].replace('T', ' ')}")

                # Show embedding count
                embs, _ = api.get_embeddings(base_url, uuid)
                if isinstance(embs, list):
                    st.markdown(f"**Embeddings stored:** {len(embs)}")

        # ── Edit ──────────────────────────────────────────────────────────────
        with tab_edit:
            with st.form(f"edit_{uuid}"):
                new_name  = st.text_input("Name", value=candidate["name"])
                new_email = st.text_input("Email", value=candidate["email"])
                save = st.form_submit_button(
                    "Save changes", icon=":material/save:", type="primary", width="stretch"
                )
            if save:
                payload = {}
                if new_name.strip() != candidate["name"]:
                    payload["name"] = new_name.strip()
                if new_email.strip() != candidate["email"]:
                    payload["email"] = new_email.strip()
                if payload:
                    updated, err3 = api.update_candidate(base_url, uuid, payload)
                    if err3:
                        st.error(err3)
                    else:
                        st.success("✅ Candidate updated.")
                        st.rerun()
                else:
                    st.info("No changes to save.")

        # ── Delete ────────────────────────────────────────────────────────────
        with tab_delete:
            st.warning(
                f"⚠️ This will permanently delete **{candidate['name']}** "
                "and all associated face embeddings. This cannot be undone."
            )
            confirm = st.text_input(
                f"Type the candidate ID **{candidate['candidate_id']}** to confirm deletion:"
            )
            if st.button(
                "Delete permanently",
                icon=":material/delete:",
                type="primary",
                width="stretch",
            ):
                if confirm.strip() == candidate["candidate_id"]:
                    ok, err4 = api.delete_candidate(base_url, uuid)
                    if err4:
                        st.error(err4)
                    else:
                        st.success("✅ Candidate deleted.")
                        st.session_state.candidates_page = 0
                        st.rerun()
                else:
                    st.error("Candidate ID does not match. Deletion cancelled.")
