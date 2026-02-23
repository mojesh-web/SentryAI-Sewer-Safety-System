import streamlit as st
import json
import os
import pandas as pd

EVENTS_JSON_PATH = "outputs/events_log.json"
SNAPSHOT_DIR = "outputs/event_snapshots"

st.set_page_config(page_title="SentryAI Dashboard", layout="wide")

st.title("🚨 SentryAI - Sewer Safety Monitoring Dashboard")

if not os.path.exists(EVENTS_JSON_PATH):
    st.warning("No events detected yet. Run detect_people.py first.")
    st.stop()

with open(EVENTS_JSON_PATH, "r") as f:
    events = json.load(f)

if len(events) == 0:
    st.info("No entry events recorded.")
    st.stop()

df = pd.DataFrame(events)

# Summary Metrics
high_count = sum(df["risk_level"] == "HIGH")
low_count = sum(df["risk_level"] == "LOW")

col1, col2 = st.columns(2)
col1.metric("🔴 High Risk Entries", high_count)
col2.metric("🟢 Low Risk Entries", low_count)

st.divider()

st.subheader("📋 Event Log")
st.dataframe(df, use_container_width=True)

st.divider()

st.subheader("🖼 Event Snapshots")

for event in reversed(events):
    st.markdown(f"### {event['risk_level']} - {event['timestamp']}")
    if os.path.exists(event["snapshot_path"]):
        st.image(event["snapshot_path"], width=400)
