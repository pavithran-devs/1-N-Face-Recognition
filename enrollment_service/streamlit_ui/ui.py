from __future__ import annotations

import streamlit as st

DEFAULT_BASE_URL = "http://localhost:8000/api/v1"


def configure_page(title: str, icon: str) -> str:
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    return render_sidebar()


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("## :material/face: Face enrollment")
        base_url = st.text_input(
            "API base URL",
            value=st.session_state.get("base_url", DEFAULT_BASE_URL),
            help="Base path for enrollment APIs",
        )
        st.session_state["base_url"] = base_url

        st.caption("Navigation")
        st.page_link("Home.py", label="Dashboard", icon=":material/dashboard:")
        st.page_link("pages/1_Enroll.py", label="Enroll candidate", icon=":material/person_add:")
        st.page_link("pages/2_Candidates.py", label="Manage candidates", icon=":material/group:")
        st.page_link("pages/3_Embeddings.py", label="View embeddings", icon=":material/neurology:")
        st.page_link(
            "pages/4_Export_Import.py", label="Export and import", icon=":material/import_export:"
        )
        st.caption("Tip: keep this URL shared across pages.")
    return base_url

