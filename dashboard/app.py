from __future__ import annotations

import json
from urllib import error, request

import pandas as pd
import streamlit as st


st.set_page_config(page_title="DataHub MVP", layout="wide")


def api_json(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    base_url = st.session_state.get("api_base_url", "http://localhost:8000").rstrip("/")
    token = st.session_state.get("api_key", "dev-admin-key")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{base_url}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json", "X-API-Key": token},
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8")
            return resp.status, json.loads(text) if text else {}
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(text)
        except json.JSONDecodeError:
            return exc.code, {"detail": text}
    except Exception as exc:
        return 0, {"detail": str(exc)}


def show_table(rows: list[dict]) -> None:
    if not rows:
        st.info("No records.")
        return
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


st.sidebar.title("DataHub")
st.sidebar.caption("MVP management console")
st.session_state["api_base_url"] = st.sidebar.text_input(
    "API Base URL",
    value=st.session_state.get("api_base_url", "http://localhost:8000"),
)
st.session_state["api_key"] = st.sidebar.text_input(
    "API Key",
    value=st.session_state.get("api_key", "dev-admin-key"),
    type="password",
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Schema Registry",
        "Ingestion Jobs",
        "Messages / Table Writes",
        "downloader-dcp Connector",
        "API Keys",
        "Query Explorer",
    ],
)

if page == "Overview":
    st.title("DataHub Overview")
    status, health = api_json("GET", "/health")
    meta_status, metadata = api_json("GET", "/metadata")
    col1, col2, col3 = st.columns(3)
    col1.metric("Health", health.get("status") if status == 200 else "unavailable")
    col2.metric("Schema Tables", len(metadata.get("tables", [])) if meta_status == 200 else 0)
    col3.metric("Connector", metadata.get("connector", "unknown") if meta_status == 200 else "unknown")
    st.json(metadata)

elif page == "Schema Registry":
    st.title("Schema Registry")
    status, schemas = api_json("GET", "/schemas")
    if status == 200:
        for table_name, spec in schemas.get("tables", {}).items():
            with st.expander(table_name):
                st.json(spec)
    else:
        st.error(schemas)

elif page == "Ingestion Jobs":
    st.title("Ingestion Jobs")
    with st.form("trigger_job"):
        job_type = st.selectbox("Job Type", ["project_tech_full", "daily_meeting_today_snapshot", "daily_meeting_yesterday_final"])
        params_text = st.text_area("Params JSON", value='{"projectCode": "P001"}' if job_type == "project_tech_full" else '{"date": "2026-05-29"}')
        debug = st.checkbox("Debug")
        if st.form_submit_button("Trigger downloader-dcp"):
            try:
                params = json.loads(params_text)
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")
            else:
                status, body = api_json("POST", "/ingestion/v1/jobs", {"job_type": job_type, "params": params, "debug": debug})
                st.json({"status_code": status, "body": body})
    status, jobs = api_json("GET", "/ingestion/v1/jobs")
    show_table(jobs.get("items", []) if status == 200 else [])

elif page == "Messages / Table Writes":
    st.title("Messages / Table Writes")
    msg_status, messages = api_json("GET", "/ingestion/v1/messages")
    write_status, writes = api_json("GET", "/ingestion/v1/table-writes")
    st.subheader("Messages")
    show_table(messages.get("items", []) if msg_status == 200 else [])
    st.subheader("Table Writes")
    show_table(writes.get("items", []) if write_status == 200 else [])

elif page == "downloader-dcp Connector":
    st.title("downloader-dcp Connector")
    st.write("DataHub only triggers downloader-dcp `/sync` and receives table batch callbacks.")
    st.code(
        json.dumps(
            {
                "sync": "POST /sync",
                "status": "GET /sync/jobs/{downloader_job_id}",
                "callback": "/ingestion/v1/table-batches",
            },
            indent=2,
        ),
        language="json",
    )

elif page == "API Keys":
    st.title("API Keys")
    with st.form("create_key"):
        name = st.text_input("Name", value="downstream-app")
        scopes = st.multiselect("Scopes", ["admin", "ingestion", "query"], default=["query"])
        if st.form_submit_button("Create API Key"):
            status, body = api_json("POST", "/admin/api-keys", {"name": name, "scopes": scopes})
            st.json({"status_code": status, "body": body})

elif page == "Query Explorer":
    st.title("Query Explorer")
    query = st.selectbox(
        "Query",
        [
            "single projects by projectCode",
            "towers by singleProjectCode",
            "substations by singleProjectCode",
            "line sections by singleProjectCode",
            "daily meetings by date",
        ],
    )
    value = st.text_input("Value")
    if st.button("Run Query") and value:
        paths = {
            "single projects by projectCode": f"/api/v1/projects/{value}/single-projects",
            "towers by singleProjectCode": f"/api/v1/single-projects/{value}/towers",
            "substations by singleProjectCode": f"/api/v1/single-projects/{value}/substations",
            "line sections by singleProjectCode": f"/api/v1/single-projects/{value}/line-sections",
            "daily meetings by date": f"/api/v1/daily-meetings?date={value}",
        }
        status, body = api_json("GET", paths[query])
        if status == 200:
            show_table(body.get("items", []))
        else:
            st.error(body)

