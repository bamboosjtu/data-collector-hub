"""Minimal ops dashboard for DataHub.

Single-page HTML dashboard served by FastAPI.
No external dependencies — vanilla HTML/CSS/JS calling existing API endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src.datahub.core.plugin_loader import find_command
from src.datahub.core.specs import PluginSpec
from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope


_DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DataHub Ops</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0f172a;color:#e2e8f0;font-size:14px}
.container{max-width:1400px;margin:0 auto;padding:16px}
h1{font-size:20px;color:#38bdf8;margin-bottom:16px;font-weight:600}
h2{font-size:16px;color:#94a3b8;margin:20px 0 10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
.card{background:#1e293b;border-radius:8px;padding:16px;margin-bottom:12px;border:1px solid #334155}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.card-title{font-weight:600;color:#f1f5f9;font-size:14px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.badge-green{background:#065f46;color:#6ee7b7}
.badge-red{background:#7f1d1d;color:#fca5a5}
.badge-yellow{background:#713f12;color:#fde047}
.badge-blue{background:#1e3a5f;color:#7dd3fc}
.badge-gray{background:#374151;color:#9ca3af}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:6px 8px;color:#94a3b8;border-bottom:1px solid #334155;font-weight:600}
td{padding:6px 8px;border-bottom:1px solid #1e293b}
tr:hover td{background:#1e293b}
button{padding:4px 12px;border-radius:4px;border:1px solid #475569;background:#334155;color:#e2e8f0;cursor:pointer;font-size:12px}
button:hover{background:#475569}
button.primary{background:#1d4ed8;border-color:#1d4ed8;color:#fff}
button.primary:hover{background:#2563eb}
button.danger{background:#991b1b;border-color:#991b1b;color:#fff}
button.danger:hover{background:#b91c1c}
input,select{padding:4px 8px;border-radius:4px;border:1px solid #475569;background:#0f172a;color:#e2e8f0;font-size:12px}
.mono{font-family:"Cascadia Code",Consolas,monospace;font-size:12px}
.params-cell{max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.error-cell{max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#fca5a5}
.tabs{display:flex;gap:4px;margin-bottom:16px}
.tab{padding:8px 16px;border-radius:4px 4px 0 0;background:#1e293b;border:1px solid #334155;border-bottom:none;cursor:pointer;color:#94a3b8;font-size:13px}
.tab.active{background:#334155;color:#38bdf8;border-color:#38bdf8}
.tab-content{display:none}
.tab-content.active{display:block}
.trigger-form{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.trigger-form label{color:#94a3b8;font-size:12px}
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.stat-card{background:#1e293b;border-radius:8px;padding:12px;border:1px solid #334155}
.stat-value{font-size:24px;font-weight:700;color:#38bdf8}
.stat-label{font-size:11px;color:#94a3b8;margin-top:4px}
.refresh-btn{float:right}
.job-detail{margin-top:8px;padding:8px;background:#0f172a;border-radius:4px;font-size:12px}
.child-jobs{margin-top:8px}
.child-jobs table{font-size:12px}
</style>
</head>
<body>
<div class="container">
<h1>DataHub Ops Dashboard</h1>

<div class="tabs">
  <div class="tab active" onclick="switchTab('commands')">Commands</div>
  <div class="tab" onclick="switchTab('jobs')">Jobs</div>
  <div class="tab" onclick="switchTab('tables')">Tables</div>
</div>

<div id="tab-commands" class="tab-content active">
  <h2>Commands</h2>
  <div id="command-list"></div>
</div>

<div id="tab-jobs" class="tab-content">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2>Ingestion Jobs</h2>
    <button class="primary" onclick="loadJobs()">Refresh</button>
  </div>
  <div id="job-list"></div>
  <div id="job-detail" style="display:none"></div>
</div>

<div id="tab-tables" class="tab-content">
  <h2>Business Tables</h2>
  <div id="table-stats"></div>
</div>
</div>

<script>
const API = '';
const KEY = localStorage.getItem('datahub_api_key') || '';
const headers = {'X-API-Key': KEY, 'Content-Type': 'application/json'};

if (!KEY) {
  document.addEventListener('DOMContentLoaded', function() {
    const key = prompt('Enter API Key (X-API-Key):');
    if (key) {
      localStorage.setItem('datahub_api_key', key);
      location.reload();
    }
  });
}

function statusBadge(s) {
  const m = {succeeded:'green',accepted:'blue',running:'yellow',triggering:'yellow',partial:'yellow',failed:'red',conflict:'red'};
  return `<span class="badge badge-${m[s]||'gray'}">${s}</span>`;
}

function triggerBadge(t) {
  const m = {'downloader_sync':'blue','plugin_handler':'green'};
  return `<span class="badge badge-${m[t]||'gray'}">${t}</span>`;
}

function fmtJson(s) {
  try { return JSON.stringify(JSON.parse(s), null, 2); } catch { return s || '-'; }
}

function fmtTime(s) {
  if (!s) return '-';
  return s.replace('T',' ').substring(0, 19);
}

function shortId(s) {
  return s ? s.substring(0, 30) + '...' : '-';
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab:nth-child(${name==='commands'?1:name==='jobs'?2:3})`).classList.add('active');
  document.getElementById('tab-'+name).classList.add('active');
  if (name==='jobs') loadJobs();
  if (name==='tables') loadTables();
}

// --- Commands ---
async function loadCommands() {
  const r = await fetch(API+'/plugins', {headers});
  const data = await r.json();
  const el = document.getElementById('command-list');
  let html = '<table><tr><th>Command</th><th>Type</th><th>Params</th><th>Action</th></tr>';
  for (const p of data.items) {
    for (const c of p.commands) {
      if (!c.enabled) continue;
      html += `<tr><td><b>${c.name}</b><br><small style="color:#64748b">${c.description}</small></td>`;
      html += `<td>${triggerBadge(c.trigger_type)}</td>`;
      html += `<td class="mono">${c.required_params.join(', ') || '-'}</td>`;
      html += `<td><div class="trigger-form" id="form-${c.name}">`;
      for (const param of c.required_params) {
        html += `<label>${param}<input id="param-${c.name}-${param}" size="12" placeholder="${param}"></label>`;
      }
      // Add optional params for some commands
      if (c.trigger_type === 'plugin_handler' && c.name.includes('current_plan')) {
        html += `<label>max_items<input id="param-${c.name}-max_items" size="5" placeholder="optional"></label>`;
      }
      if (c.name === 'backfill_daily_meetings_by_range') {
        html += `<label>chunk_days<input id="param-${c.name}-chunk_days" size="5" value="7"></label>`;
      }
      html += `<button class="primary" onclick="triggerCommand('${c.name}')">Trigger</button>`;
      html += '</div></td></tr>';
    }
  }
  html += '</table>';
  el.innerHTML = html;
}

async function triggerCommand(name) {
  const r = await fetch(API+'/plugins', {headers});
  const data = await r.json();
  let cmd = null;
  for (const p of data.items) {
    cmd = p.commands.find(c => c.name === name);
    if (cmd) break;
  }
  if (!cmd) return alert('Command not found');

  const params = {};
  for (const param of cmd.required_params) {
    const v = document.getElementById(`param-${name}-${param}`)?.value;
    if (!v) return alert(`Missing required param: ${param}`);
    params[param] = v;
  }
  // Optional params
  const maxItems = document.getElementById(`param-${name}-max_items`)?.value;
  if (maxItems) params.max_items = parseInt(maxItems);
  const chunkDays = document.getElementById(`param-${name}-chunk_days`)?.value;
  if (chunkDays) params.chunk_days = parseInt(chunkDays);

  try {
    const resp = await fetch(API+'/ingestion/v1/jobs', {
      method: 'POST', headers,
      body: JSON.stringify({command: name, params})
    });
    const result = await resp.json();
    if (resp.ok) {
      alert(`Job created: ${result.ingestion_job_id}\nStatus: ${result.status}`);
      switchTab('jobs');
    } else {
      alert(`Error: ${result.detail?.message || JSON.stringify(result)}`);
    }
  } catch (e) {
    alert(`Request failed: ${e.message}`);
  }
}

// --- Jobs ---
async function loadJobs() {
  const r = await fetch(API+'/ingestion/v1/jobs?limit=50', {headers});
  const data = await r.json();
  const el = document.getElementById('job-list');
  let html = '<table><tr><th>Job ID</th><th>Command</th><th>Status</th><th>Params</th><th>Created</th><th>Actions</th></tr>';
  for (const j of data.items) {
    const params = fmtJson(j.params_json);
    const shortParams = params.length > 60 ? params.substring(0, 60) + '...' : params;
    html += `<tr>
      <td class="mono"><a href="#" onclick="showJobDetail('${j.ingestion_job_id}');return false">${shortId(j.ingestion_job_id)}</a></td>
      <td>${j.trigger_key || '-'}</td>
      <td>${statusBadge(j.status)}</td>
      <td class="mono params-cell" title="${params.replace(/"/g,'&quot;')}">${shortParams}</td>
      <td>${fmtTime(j.created_at)}</td>
      <td>
        <button onclick="showJobDetail('${j.ingestion_job_id}')">Detail</button>
        ${j.status==='failed' ? `<button class="danger" onclick="retryJob('${j.ingestion_job_id}')">Retry</button>` : ''}
      </td>
    </tr>`;
  }
  html += '</table>';
  el.innerHTML = html;
}

async function showJobDetail(jobId) {
  const r = await fetch(API+`/ingestion/v1/jobs/${jobId}`, {headers});
  const j = await r.json();
  const el = document.getElementById('job-detail');
  el.style.display = 'block';

  let html = `<div class="card">
    <div class="card-header"><span class="card-title">Job Detail</span><button onclick="this.closest('#job-detail').style.display='none'">Close</button></div>
    <table>
      <tr><td style="color:#94a3b8;width:120px">Job ID</td><td class="mono">${j.ingestion_job_id}</td></tr>
      <tr><td style="color:#94a3b8">Parent Job</td><td class="mono">${j.parent_job_id || '-'} ${j.parent_job_id ? `<button onclick="showJobDetail('${j.parent_job_id}')">View Parent</button>` : ''}</td></tr>
      <tr><td style="color:#94a3b8">Command</td><td>${j.trigger_key || '-'}</td></tr>
      <tr><td style="color:#94a3b8">Status</td><td>${statusBadge(j.status)}</td></tr>
      <tr><td style="color:#94a3b8">Params</td><td class="mono"><pre style="white-space:pre-wrap">${fmtJson(j.params_json)}</pre></td></tr>
      <tr><td style="color:#94a3b8">Error</td><td class="error-cell">${j.error || '-'}</td></tr>
      <tr><td style="color:#94a3b8">Result</td><td class="mono"><pre style="white-space:pre-wrap">${fmtJson(j.result_json)}</pre></td></tr>
      <tr><td style="color:#94a3b8">Created</td><td>${fmtTime(j.created_at)}</td></tr>
      <tr><td style="color:#94a3b8">Finished</td><td>${fmtTime(j.finished_at)}</td></tr>
    </table>`;

  // Load child jobs
  const cr = await fetch(API+`/ingestion/v1/jobs/${jobId}/children`, {headers});
  const children = await cr.json();
  if (children.total > 0) {
    html += `<div class="child-jobs"><h3>Child Jobs (${children.total})</h3><table>
      <tr><th>Job ID</th><th>Status</th><th>Params</th><th>Error</th><th>Action</th></tr>`;
    for (const c of children.items) {
      const cp = fmtJson(c.params_json);
      html += `<tr>
        <td class="mono">${shortId(c.ingestion_job_id)}</td>
        <td>${statusBadge(c.status)}</td>
        <td class="mono params-cell" title="${cp.replace(/"/g,'&quot;')}">${cp.substring(0,50)}</td>
        <td class="error-cell">${c.error || '-'}</td>
        <td>${c.status==='failed' ? `<button class="danger" onclick="retryChild('${c.trigger_key}',\`${cp.replace(/`/g,'\\`')}\`)">Retry</button>` : ''}</td>
      </tr>`;
    }
    html += '</table></div>';
  }

  html += '</div>';
  el.innerHTML = html;
}

async function retryJob(jobId) {
  try {
    const resp = await fetch(API+`/ingestion/v1/jobs/${jobId}/retry`, {
      method: 'POST', headers
    });
    const result = await resp.json();
    alert(resp.ok ? `Retry job created: ${result.ingestion_job_id}` : `Error: ${JSON.stringify(result)}`);
    loadJobs();
  } catch (e) {
    alert(`Retry failed: ${e.message}`);
  }
}

async function retryChild(command, paramsStr) {
  try {
    const params = JSON.parse(paramsStr);
    const resp = await fetch(API+'/ingestion/v1/jobs', {
      method: 'POST', headers,
      body: JSON.stringify({command, params})
    });
    const result = await resp.json();
    alert(resp.ok ? `Retry job created: ${result.ingestion_job_id}` : `Error: ${JSON.stringify(result)}`);
  } catch (e) {
    alert(`Retry failed: ${e.message}`);
  }
}

// --- Tables ---
async function loadTables() {
  const r = await fetch(API+'/schemas', {headers});
  const data = await r.json();
  const el = document.getElementById('table-stats');

  let html = '<table><tr><th>Table</th><th>Primary Key</th><th>Write Mode</th><th>Columns</th><th>Row Count</th></tr>';
  for (const [name, spec] of Object.entries(data.tables || {})) {
    html += `<tr>
      <td><b>${name}</b></td>
      <td class="mono">${(spec.primary_key||[]).join(', ')}</td>
      <td>${spec.write_mode}</td>
      <td>${Object.keys(spec.columns||{}).length}</td>
      <td id="rows-${name}">...</td>
    </tr>`;
  }
  html += '</table>';
  el.innerHTML = html;

  // Load row counts via query API
  for (const name of Object.keys(data.tables || {})) {
    try {
      const qr = await fetch(API+`/api/v1/ops/table-stats?table=${name}`, {headers});
      if (qr.ok) {
        const qd = await qr.json();
        document.getElementById(`rows-${name}`).textContent = `${qd.row_count} (updated: ${fmtTime(qd.last_updated)})`;
      }
    } catch {}
  }
}

// Init
loadCommands();
</script>
</body>
</html>"""


def build_ops_router(
    *,
    store: DataHubStore,
    plugins: list[PluginSpec],
) -> APIRouter:
    router = APIRouter()

    @router.get("/ops", response_class=HTMLResponse)
    def ops_dashboard():
        return _DASHBOARD_HTML

    @router.get("/api/v1/ops/table-stats", dependencies=[Depends(require_scope(store, "admin"))])
    def table_stats(table: str) -> dict[str, Any]:
        """Get row count and last updated time for a business table."""
        import sqlite3

        row_count = -1
        last_updated = None

        try:
            with sqlite3.connect(store.db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(f"SELECT COUNT(*) as cnt FROM [{table}]").fetchone()
                row_count = row["cnt"] if row else 0
        except Exception:
            pass

        try:
            with sqlite3.connect(store.db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT MAX(im.created_at) as last_updated FROM ingestion_messages im "
                    "JOIN table_writes tw ON im.message_id = tw.message_id "
                    "WHERE tw.table_name = ?",
                    (table,),
                ).fetchone()
                last_updated = row["last_updated"] if row else None
        except Exception:
            pass

        return {"table": table, "row_count": row_count, "last_updated": last_updated}

    return router
