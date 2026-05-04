"""
Streamlit Dashboard for Data Collector Hub v1.0

A simple dashboard for viewing and managing:
- Plugin status
- Raw data
- Normalized data
- Task statistics
- Logs
- Runtime plugin configuration

Usage:
    streamlit run dashboard/app.py
"""

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.plugin_config_validator import validate_plugin_runtime_config
from storage.sqlite_store import SQLiteStore

# Page config
st.set_page_config(
    page_title="Data Collector Hub v1.0",
    page_icon="📊",
    layout="wide"
)

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "collector.db"


def get_connection():
    """Create a new database connection for each call (thread-safe)"""
    # Don't use PARSE_DECLTYPES to avoid timestamp parsing issues
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_data(ttl=5)
def get_plugin_list():
    """Get list of plugins (cached)"""
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT * FROM plugins")
        plugins = []
        for row in cursor.fetchall():
            plugin = dict(row)
            plugin['config'] = json.loads(plugin['config']) if plugin['config'] else {}
            plugin['dependencies'] = json.loads(plugin['dependencies']) if plugin['dependencies'] else []

            # Get tags
            tag_cursor = conn.execute("SELECT tag FROM plugin_tags WHERE plugin_id = ?", (plugin['id'],))
            plugin['tags'] = [r['tag'] for r in tag_cursor.fetchall()]
            plugins.append(plugin)
        return plugins
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_plugin_runtime_config(plugin_id):
    """Get plugin runtime config through the shared store layer."""
    runtime = SQLiteStore(DB_PATH).get_plugin_runtime_config(plugin_id)
    return runtime["config"]


def save_plugin_runtime_config(plugin_id, config):
    """Save plugin runtime config through the shared store layer."""
    SQLiteStore(DB_PATH).save_plugin_runtime_config(plugin_id, config)


@st.cache_data(ttl=5)
def get_counts():
    """Get table counts (cached)"""
    conn = get_connection()
    try:
        result = {}
        cursor = conn.execute("SELECT COUNT(*) as count FROM plugins")
        result['plugins'] = cursor.fetchone()['count']

        cursor = conn.execute("SELECT COUNT(*) as count FROM raw_data")
        result['raw_data'] = cursor.fetchone()['count']

        cursor = conn.execute("SELECT COUNT(*) as count FROM raw_events")
        result['raw_events'] = cursor.fetchone()['count']

        cursor = conn.execute("SELECT COUNT(*) as count FROM normalized_data")
        result['normalized_data'] = cursor.fetchone()['count']

        cursor = conn.execute("SELECT COUNT(*) as count FROM logs")
        result['logs'] = cursor.fetchone()['count']

        return result
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_task_stats():
    """Get task statistics (cached)"""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT plugin_id, run_count, fail_count, last_run, consecutive_fails
            FROM task_stats
            ORDER BY last_run DESC
            LIMIT 10
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_raw_data(plugin_filter, limit):
    """Get raw data (cached)"""
    conn = get_connection()
    try:
        if plugin_filter == "All":
            cursor = conn.execute("""
                SELECT id, plugin_id, source, data, created_at
                FROM raw_data
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
        else:
            cursor = conn.execute("""
                SELECT id, plugin_id, source, data, created_at
                FROM raw_data
                WHERE plugin_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (plugin_filter, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_raw_events(dataset_filter, limit):
    """Get raw SourceEvent rows (cached)."""
    conn = get_connection()
    try:
        if dataset_filter == "All":
            cursor = conn.execute("""
                SELECT id, dataset_key, collection, page_name, api_name, source_file,
                       occurred_at, collected_at, source_system, source_record_id,
                       source_record_hash, source_record_key, raw_event_key
                FROM raw_events
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
        else:
            cursor = conn.execute("""
                SELECT id, dataset_key, collection, page_name, api_name, source_file,
                       occurred_at, collected_at, source_system, source_record_id,
                       source_record_hash, source_record_key, raw_event_key
                FROM raw_events
                WHERE dataset_key = ?
                ORDER BY id DESC
                LIMIT ?
            """, (dataset_filter, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_raw_event_dataset_keys():
    """Get distinct raw event dataset keys."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT DISTINCT dataset_key FROM raw_events WHERE dataset_key IS NOT NULL ORDER BY dataset_key"
        )
        return [row["dataset_key"] for row in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_normalized_data(plugin_filter, event_type_filter, limit):
    """Get normalized data (cached)"""
    conn = get_connection()
    try:
        query = """
            SELECT id, raw_data_id, plugin_id, event_type, event_source,
                   entity, event_timestamp, unique_key, payload, confidence, created_at
            FROM normalized_data
            WHERE 1=1
        """
        params = []

        if plugin_filter != "All":
            query += " AND plugin_id = ?"
            params.append(plugin_filter)

        if event_type_filter != "All":
            query += " AND event_type = ?"
            params.append(event_type_filter)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_logs(level_filter, plugin_filter, limit):
    """Get logs (cached)"""
    conn = get_connection()
    try:
        query = """
            SELECT id, plugin_id, level, message, details, created_at
            FROM logs
            WHERE 1=1
        """
        params = []

        if level_filter != "All":
            query += " AND level = ?"
            params.append(level_filter)

        if plugin_filter != "All":
            query += " AND plugin_id = ?"
            params.append(plugin_filter)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_statistics():
    """Get all task statistics (cached)"""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT plugin_id, run_count, fail_count, last_run, last_fail, consecutive_fails
            FROM task_stats
            ORDER BY last_run DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=5)
def get_event_types():
    """Get distinct event types (cached)"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT DISTINCT event_type FROM normalized_data WHERE event_type IS NOT NULL"
        )
        return [row['event_type'] for row in cursor.fetchall()]
    finally:
        conn.close()


# Sidebar
st.sidebar.title("📊 Data Collector Hub")
st.sidebar.caption("v1.0 Dashboard")

# Check database exists
if not DB_PATH.exists():
    st.sidebar.error(f"Database not found: {DB_PATH}")
    st.sidebar.info("Please run the initialization script first:")
    st.sidebar.code("python init_and_run.py")
    st.stop()

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🔌 Plugins", "📄 Raw Data", "🧾 Raw Events", "📋 Normalized Data", "📈 Statistics", "📝 Logs"]
)

# Home Page
if page == "🏠 Home":
    st.title("🏠 Data Collector Hub Dashboard")
    st.markdown("---")

    # Summary metrics
    counts = get_counts()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Plugins", counts.get('plugins', 0))

    with col2:
        st.metric("Raw Data", counts.get('raw_data', 0))

    with col3:
        st.metric("Raw Events", counts.get('raw_events', 0))

    with col4:
        st.metric("Normalized Data", counts.get('normalized_data', 0))

    with col5:
        st.metric("Logs", counts.get('logs', 0))

    st.markdown("---")

    # Recent activity
    st.subheader("📈 Recent Activity")

    stats = get_task_stats()

    if stats:
        df = pd.DataFrame([
            {
                "Plugin": row["plugin_id"],
                "Run Count": row["run_count"],
                "Fail Count": row["fail_count"],
                "Last Run": row["last_run"],
                "Consecutive Fails": row["consecutive_fails"]
            }
            for row in stats
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No task statistics available yet.")

# Plugins Page
elif page == "🔌 Plugins":
    st.title("🔌 Plugins")
    st.markdown("---")

    plugins = get_plugin_list()

    if not plugins:
        st.info("No plugins registered yet.")
    else:
        for plugin in plugins:
            with st.expander(f"📦 {plugin['name']} (v{plugin['version']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**ID:** {plugin['id']}")
                    st.write(f"**Description:** {plugin['description']}")
                    st.write(f"**Author:** {plugin['author']}")
                    st.write(f"**Tags:** {', '.join(plugin['tags'])}")

                with col2:
                    st.write(f"**Enabled:** {'✅' if plugin['enabled'] else '❌'}")
                    st.write(f"**Health Status:** {plugin['health_status']}")
                    st.write(f"**Created:** {plugin['created_at']}")
                    st.write(f"**Updated:** {plugin['updated_at']}")

                if plugin.get('config_schema'):
                    st.write("**Config Schema:**")
                    st.json(plugin['config_schema'])

                runtime_config = get_plugin_runtime_config(plugin['id'])
                st.write("**Runtime Config:**")
                config_text = st.text_area(
                    "Runtime Config JSON",
                    value=json.dumps(runtime_config, ensure_ascii=False, indent=2),
                    height=260,
                    key=f"runtime_config_{plugin['id']}"
                )
                if st.button("Save Config", key=f"save_config_{plugin['id']}"):
                    try:
                        parsed_config = json.loads(config_text)
                        if not isinstance(parsed_config, dict):
                            st.error("Runtime config must be a JSON object.")
                        else:
                            errors = validate_plugin_runtime_config(plugin['id'], parsed_config)
                            if errors:
                                st.error("Runtime config validation failed:")
                                for error in errors:
                                    st.error(error)
                            else:
                                save_plugin_runtime_config(plugin['id'], parsed_config)
                                st.cache_data.clear()
                                st.success("Runtime config saved.")
                                st.rerun()
                    except json.JSONDecodeError as exc:
                        st.error(f"Invalid JSON: {exc}")

# Raw Data Page
elif page == "📄 Raw Data":
    st.title("📄 Raw Data")
    st.info("raw_data stores embedded pipeline collector output. raw_events stores SourceEvent ingestion payloads.")
    st.markdown("---")

    # Filter by plugin
    plugins = get_plugin_list()
    plugin_options = ["All"] + [p["id"] for p in plugins]
    selected_plugin = st.selectbox("Filter by Plugin", plugin_options)

    # Limit
    limit = st.slider("Limit", 10, 100, 20)

    rows = get_raw_data(selected_plugin, limit)

    if not rows:
        st.info("No raw data available.")
    else:
        st.write(f"Showing {len(rows)} records:")

        for row in rows:
            data = json.loads(row["data"]) if row["data"] else {}

            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.write(f"**ID:** {row['id']}")
                    st.write(f"**Plugin:** {row['plugin_id']}")
                    st.write(f"**Source:** {row['source']}")

                with col2:
                    # Try to extract title from data
                    title = data.get("title", "")
                    if title:
                        st.write(f"**Title:** {title[:50]}..." if len(title) > 50 else f"**Title:** {title}")

                with col3:
                    st.write(f"**Created:** {row['created_at']}")

                with st.expander("View Data"):
                    st.json(data)

                st.markdown("---")

# Raw Events Page
elif page == "🧾 Raw Events":
    st.title("🧾 Raw Events")
    st.markdown("---")

    dataset_options = ["All"] + get_raw_event_dataset_keys()
    selected_dataset = st.selectbox("Filter by Dataset", dataset_options)
    limit = st.slider("Limit", 10, 100, 20)

    rows = get_raw_events(selected_dataset, limit)

    if not rows:
        st.info("No raw events available.")
    else:
        st.write(f"Showing {len(rows)} raw events:")
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

# Normalized Data Page
elif page == "📋 Normalized Data":
    st.title("📋 Normalized Data")
    st.markdown("---")

    # Filter by plugin
    plugins = get_plugin_list()
    plugin_options = ["All"] + [p["id"] for p in plugins]
    selected_plugin = st.selectbox("Filter by Plugin", plugin_options)

    # Filter by event type
    event_types = ["All"] + get_event_types()
    selected_type = st.selectbox("Filter by Event Type", event_types)

    # Limit
    limit = st.slider("Limit", 10, 100, 20)

    rows = get_normalized_data(selected_plugin, selected_type, limit)

    if not rows:
        st.info("No normalized data available.")
    else:
        st.write(f"Showing {len(rows)} records:")

        for row in rows:
            payload = json.loads(row["payload"]) if row["payload"] else {}
            entity = json.loads(row["entity"]) if row["entity"] else []

            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.write(f"**ID:** {row['id']}")
                    st.write(f"**Plugin:** {row['plugin_id']}")
                    st.write(f"**Event Type:** `{row['event_type']}`")
                    st.write(f"**Event Source:** {row['event_source']}")

                with col2:
                    st.write(f"**Entity:** {entity}")
                    st.write(f"**Confidence:** {row['confidence']}")
                    st.write(f"**Event Time:** {row['event_timestamp']}")

                with col3:
                    st.write(f"**Created:** {row['created_at']}")

                with st.expander("View Payload"):
                    st.json(payload)

                st.markdown("---")

# Statistics Page
elif page == "📈 Statistics":
    st.title("📈 Task Statistics")
    st.markdown("---")

    stats = get_statistics()

    if not stats:
        st.info("No statistics available yet.")
    else:
        df = pd.DataFrame([
            {
                "Plugin": row["plugin_id"],
                "Run Count": row["run_count"],
                "Fail Count": row["fail_count"],
                "Success Rate": f"{((row['run_count'] - row['fail_count']) / row['run_count'] * 100):.1f}%"
                if row["run_count"] > 0 else "N/A",
                "Last Run": row["last_run"],
                "Last Fail": row["last_fail"],
                "Consecutive Fails": row["consecutive_fails"]
            }
            for row in stats
        ])

        st.dataframe(df, use_container_width=True)

        # Charts
        st.subheader("📊 Visualizations")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Run Count by Plugin**")
            chart_data = df.set_index("Plugin")["Run Count"]
            st.bar_chart(chart_data)

        with col2:
            st.write("**Fail Count by Plugin**")
            chart_data = df.set_index("Plugin")["Fail Count"]
            st.bar_chart(chart_data)

# Logs Page
elif page == "📝 Logs":
    st.title("📝 Logs")
    st.markdown("---")

    # Filter by level
    level_options = ["All", "INFO", "WARNING", "ERROR"]
    selected_level = st.selectbox("Filter by Level", level_options)

    # Filter by plugin
    plugins = get_plugin_list()
    plugin_options = ["All"] + [p["id"] for p in plugins]
    selected_plugin = st.selectbox("Filter by Plugin", plugin_options)

    # Limit
    limit = st.slider("Limit", 10, 200, 50)

    rows = get_logs(selected_level, selected_plugin, limit)

    if not rows:
        st.info("No logs available.")
    else:
        st.write(f"Showing {len(rows)} log entries:")

        for row in rows:
            # Color code by level
            if row["level"] == "ERROR":
                color = "🔴"
            elif row["level"] == "WARNING":
                color = "🟡"
            else:
                color = "🟢"

            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])

                with col1:
                    st.write(f"{color} **{row['level']}**")
                    st.write(f"ID: {row['id']}")

                with col2:
                    st.write(f"**Message:** {row['message']}")
                    if row["plugin_id"]:
                        st.write(f"**Plugin:** {row['plugin_id']}")

                with col3:
                    st.write(f"**Time:** {row['created_at']}")

                if row["details"]:
                    with st.expander("View Details"):
                        try:
                            details = json.loads(row["details"])
                            st.json(details)
                        except:
                            st.text(row["details"])

                st.markdown("---")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Data Collector Hub v1.0")

# Auto refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
