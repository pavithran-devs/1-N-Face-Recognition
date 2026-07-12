"""
Page 4 — Export / Import
Features: export all/single as JSON or CSV, import from JSON or CSV
"""
import io
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
import api_client as api
import ui

base_url = ui.configure_page("Export and import", ":material/import_export:")

st.title(":material/import_export: Export and import")

export_tab, import_tab = st.tabs(["Export", "Import"])

# ════════════════════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════════════════════
with export_tab:
    st.subheader("Export candidates to JSON or CSV")
    st.markdown(
        "Exports are written to the server's `exports/` directory. "
        "The file path is returned so you can retrieve it."
    )

    col_scope, col_fmt = st.columns(2)
    with col_scope:
        scope = st.segmented_control("Scope", ["All candidates", "Single candidate"])
    with col_fmt:
        fmt = st.segmented_control("Format", ["JSON", "CSV"])

    single_uuid = None
    if scope == "Single candidate":
        # Quick picker
        result, _ = api.list_candidates(base_url, limit=200)
        if result and result.get("data"):
            options = {f"{c['name']} ({c['candidate_id']})": c["id"] for c in result["data"]}
            picked = st.selectbox("Candidate", ["— choose —"] + list(options.keys()))
            if picked != "— choose —":
                single_uuid = options[picked]
        else:
            single_uuid = st.text_input("Candidate UUID")

    if st.button(
        f"Export as {fmt}",
        icon=":material/download:",
        type="primary",
        width="stretch",
    ):
        with st.spinner(f"Exporting…"):
            if fmt == "JSON":
                data, err = api.export_json(base_url, single_uuid)
            else:
                data, err = api.export_csv(base_url, single_uuid)

        if err:
            st.error(f"❌ {err}")
        else:
            st.success(
                f"✅ Exported **{data['exported_count']}** record(s) → `{data['file_path']}`"
            )
            st.metric("Format", data["format"].upper())
            st.metric("Records", data["exported_count"])
            st.info(
                f"File saved on the server at: `{data['file_path']}`\n\n"
                "Copy it from the server or use the Import tab to re-import it."
            )

# ════════════════════════════════════════════════════════════════════════════════
# IMPORT
# ════════════════════════════════════════════════════════════════════════════════
with import_tab:
    st.subheader("Import candidates from a JSON or CSV file")

    import_fmt = st.segmented_control("File format", ["JSON", "CSV"], key="import_fmt")

    if import_fmt == "JSON":
        st.markdown("""
**Expected format** — array of candidate objects:
```json
[
  {
    "candidate_id": "EMP001",
    "name": "Alice",
    "email": "alice@example.com",
    "dob": "1990-01-15",
    "embeddings": [
      {
        "embedding": [0.01, -0.02, ...],
        "embedding_dimension": 512,
        "model_name": "buffalo_l",
        "normalized": true
      }
    ]
  }
]
```
        """)
        uploaded = st.file_uploader("Upload JSON", type=["json"], key="import_json_file")
    else:
        st.markdown("""
**Expected columns:** `candidate_id`, `name`, `email`, `dob` (optional), `embedding` (512 semicolon-separated floats).
        """)
        uploaded = st.file_uploader("Upload CSV", type=["csv"], key="import_csv_file")

    if uploaded:
        # Preview
        with st.expander("📄 Preview file contents"):
            raw = uploaded.read()
            uploaded.seek(0)
            if import_fmt == "JSON":
                try:
                    preview = json.loads(raw)
                    st.json(preview[:3] if len(preview) > 3 else preview)
                    if len(preview) > 3:
                        st.caption(f"…and {len(preview) - 3} more records")
                except Exception as e:
                    st.error(f"Invalid JSON: {e}")
            else:
                try:
                    import csv
                    text = raw.decode("utf-8-sig")
                    reader = list(csv.DictReader(io.StringIO(text)))
                    df = pd.DataFrame(reader[:5])
                    # Truncate the long embedding column for display
                    if "embedding" in df.columns:
                        df["embedding"] = df["embedding"].str[:60] + "…"
                    st.dataframe(df, hide_index=True)
                    st.caption(f"Showing first 5 of {len(reader)} rows")
                except Exception as e:
                    st.error(f"Could not parse CSV: {e}")

        if st.button(
            f"Import {import_fmt}",
            icon=":material/upload:",
            type="primary",
            width="stretch",
        ):
            file_bytes = uploaded.read()
            with st.spinner("Importing…"):
                if import_fmt == "JSON":
                    result, err = api.import_json(base_url, file_bytes, uploaded.name)
                else:
                    result, err = api.import_csv(base_url, file_bytes, uploaded.name)

            if err:
                st.error(f"❌ Import failed: {err}")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("✅ Imported", result.get("imported_count", 0))
                with col2:
                    st.metric("⏭ Skipped", result.get("skipped_count", 0))

                errors = result.get("errors", [])
                if errors:
                    with st.expander(f"⚠️ {len(errors)} warnings / errors"):
                        for e in errors:
                            st.warning(e)
                else:
                    st.success("Import completed with no errors!")
