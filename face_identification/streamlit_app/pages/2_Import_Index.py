"""Streamlit page to handle bulk dataset imports and FAISS index maintenance."""

import streamlit as st
import ui
from api_client import FaceIdentifyAPIClient

base_url = ui.configure_page("Manage database and index", ":material/database:")

st.title(":material/database: Manage database and index")
st.markdown("Import candidate embedding catalogs or rebuild the vector index on-demand.")

client = FaceIdentifyAPIClient(base_url=base_url)

col1, col2 = st.columns(2)

with col1:
    st.subheader(":material/upload_file: Bulk candidate importers")

    # JSON Upload
    st.markdown("#### Import JSON catalog")
    json_file = st.file_uploader(
        "Select candidate details JSON file...", type=["json"], key="json_uploader"
    )
    if json_file is not None and st.button(
        "Submit JSON import", key="json_btn", icon=":material/upload:", width="stretch"
    ):
        with st.spinner("Uploading and importing candidate records..."):
            resp = client.import_json(json_file.name, json_file.getvalue())

        if "errors" in resp:
            st.success(
                f"Imported {resp.get('imported_count', 0)} candidates. Skipped {resp.get('skipped_count', 0)}."
            )
            if resp.get("errors"):
                with st.expander("Show skipped details / warnings"):
                    for err in resp["errors"]:
                        st.write(err)
        else:
            st.error("Import failed.")
            st.json(resp)

    st.markdown("---")

    # CSV Upload
    st.markdown("#### Import CSV catalog")
    csv_file = st.file_uploader(
        "Select candidate details CSV file...", type=["csv"], key="csv_uploader"
    )
    if csv_file is not None and st.button(
        "Submit CSV import", key="csv_btn", icon=":material/upload:", width="stretch"
    ):
        with st.spinner("Uploading and importing candidate CSV records..."):
            resp = client.import_csv(csv_file.name, csv_file.getvalue())

            if "errors" in resp:
                st.success(
                    f"Imported {resp.get('imported_count', 0)} candidates. Skipped {resp.get('skipped_count', 0)}."
                )
                if resp.get("errors"):
                    with st.expander("Show skipped details / warnings"):
                        for err in resp["errors"]:
                            st.write(err)
            else:
                st.error("Import failed.")
                st.json(resp)

with col2:
    st.subheader(":material/build: Index rebuild and sync")
    st.markdown("Synchronise the in-memory FAISS index with candidates in the PostgreSQL database.")

    # Database Sync button
    if st.button("Sync index with Postgres", icon=":material/sync:", width="stretch"):
        with st.spinner("Rebuilding FAISS index from Postgres database candidates..."):
            resp = client.import_postgres_sync()

        if resp.get("status") == "success":
            st.success(
                f"Successfully synced index! New index size: {resp.get('index_size', 0)} active candidates."
            )
        else:
            st.error(f"Postgres sync failed: {resp.get('detail', 'Unknown error')}")

    st.markdown("---")

    # Manual index rebuild button
    if st.button("Rebuild FAISS index", icon=":material/rocket_launch:", width="stretch"):
        with st.spinner("Rebuilding FAISS index..."):
            resp = client.rebuild_index()

        if resp.get("status") == "success":
            st.success(f"Index rebuilt successfully! Size: {resp.get('size', 0)} vectors.")
        else:
            st.error(f"Rebuild failed: {resp.get('detail', 'Unknown error')}")

    st.markdown("---")
    st.subheader(":material/query_stats: Index details")
    status = client.get_index_status()
    if status:
        st.write(f"- **Active items in vector index:** {status.get('size', 0)}")
        st.write(f"- **Memory index model type:** `{status.get('index_type', 'N/A')}`")
        st.write(f"- **Disk saved index binary:** `{'Yes' if status.get('file_exists') else 'No'}`")
    else:
        st.error("Failed to query index details.")
