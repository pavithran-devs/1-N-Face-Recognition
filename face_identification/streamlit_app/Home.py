"""Streamlit application landing page showing health, index details, and latency metrics."""

import streamlit as st
import ui
from api_client import FaceIdentifyAPIClient

base_url = ui.configure_page("Face identification dashboard", ":material/verified_user:")

st.title(":material/verified_user: 1:N face identification dashboard")
st.caption("Monitor API health, index state, and real-time identification performance.")

client = FaceIdentifyAPIClient(base_url=base_url)

# Core Status Check
health = client.get_health()
metrics = client.get_metrics()
index_status = client.get_index_status()

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader(":material/sensors: Service status")

    status = health.get("status", "unreachable")
    if status == "healthy":
        st.success("🟢 API Service is healthy and online.")
    elif status == "unhealthy":
        st.warning("🟡 API Service is running but reported unhealthy states.")
    else:
        st.error("🔴 API Service is offline or unreachable.")

    with st.expander("System diagnostics"):
        st.json(health)

with col2:
    st.subheader(":material/hub: FAISS vector index status")
    if index_status:
        st.info(
            f"**Active vectors in index:** {index_status.get('size', 0):,}\n\n"
            f"**Configured search type:** `{index_status.get('index_type', 'N/A')}`\n\n"
            f"**Index File Loaded:** `{'Yes' if index_status.get('file_exists') else 'No'}`"
        )
    else:
        st.error("Failed to query index details.")

st.subheader(":material/bolt: Performance telemetry")

if metrics:
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    m_col1.metric(
        label="Total identification runs",
        value=f"{metrics.get('total_searches', 0):,}",
        border=True,
    )
    m_col2.metric(label="Successful matches", value=f"{metrics.get('hits', 0):,}", border=True)
    m_col3.metric(label="Unknown rejections", value=f"{metrics.get('misses', 0):,}", border=True)

    hit_rate = float(metrics.get("hit_rate", 0.0)) * 100
    m_col4.metric(label="Identification hit rate", value=f"{hit_rate:.1f}%", border=True)

    st.markdown("#### Average API Latencies")
    latencies = metrics.get("average_latencies_ms", {})

    l_col1, l_col2, l_col3, l_col4 = st.columns(4)
    l_col1.metric(label="Face Detection", value=f"{latencies.get('face_detection', 0.0):.1f} ms")
    l_col2.metric(
        label="Embedding Generation", value=f"{latencies.get('embedding_generation', 0.0):.1f} ms"
    )
    l_col3.metric(label="FAISS Search", value=f"{latencies.get('faiss_search', 0.0):.1f} ms")
    l_col4.metric(
        label="Total API roundtrip", value=f"{latencies.get('total_api_response', 0.0):.1f} ms"
    )
else:
    st.info(
        "No query logs or search metrics captured yet. Go to the Identify page to test face matches!"
    )
