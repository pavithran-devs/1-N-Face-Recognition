from __future__ import annotations

import streamlit as st

DEFAULT_BASE_URL = "http://localhost:8001"


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
        st.markdown("## :material/verified_user: Face identification")
        base_url = st.text_input(
            "API base URL",
            value=st.session_state.get("id_base_url", DEFAULT_BASE_URL),
            help="Base URL for identification APIs",
        )
        st.session_state["id_base_url"] = base_url

        st.caption("Navigation")
        st.page_link("Home.py", label="Dashboard", icon=":material/dashboard:")
        st.page_link("pages/1_Identify.py", label="Identify", icon=":material/person_search:")
        st.page_link(
            "pages/2_Import_Index.py", label="Import and index", icon=":material/database:"
        )
    return base_url
