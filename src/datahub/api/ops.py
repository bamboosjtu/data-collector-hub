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
h3{font-size:14px;color:#cbd5e1;margin:12px 0 6px;font-weight:600}
.card{background:#1e293b;border-radius:8px;padding:16px;margin-bottom:12px;border:1px solid #334155}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.card-title{font-weight:600;color:#f1f5f9;font-size:14px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.badge-green{background:#065f46;color:#6ee7b7}
.badge-red{background:#7f1d1d;color:#fca5a5}
.badge-yellow{background:#713f12;color:#fde047}
.badge-blue{background:#1e3a5f;color:#7dd3fc}
.badge-gray{background:#374151;color:#9ca3af}
.badge-purple{background:#3b0764;color:#c4b5fd}
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
button:disabled{opacity:0.4;cursor:not-allowed}
input,select,textarea{padding:4px 8px;border-radius:4px;border:1px solid #475569;background:#0f172a;color:#e2e8f0;font-size:12px}
textarea{font-family:"Cascadia Code",Consolas,monospace;resize:vertical}
.mono{font-family:"Cascadia Code",Consolas,monospace;font-size:12px}
.params-cell{max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.error-cell{max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#fca5a5}
.tabs{display:flex;gap:4px;margin-bottom:16px;flex-wrap:wrap}
.tab{padding:8px 16px;border-radius:4px 4px 0 0;background:#1e293b;border:1px solid #334155;border-bottom:none;cursor:pointer;color:#94a3b8;font-size:13px}
.tab.active{background:#334155;color:#38bdf8;border-color:#38bdf8}
.tab-content{display:none}
.tab-content.active{display:block}
.trigger-form{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.trigger-form label{color:#94a3b8;font-size:12px}
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.stat-card{background:#1e293b;border-radius:8px;padding:12px;border:1px solid #334155;text-align:center}
.stat-value{font-size:24px;font-weight:700;color:#38bdf8}
.stat-label{font-size:11px;color:#94a3b8;margin-top:4px}
.job-detail{margin-top:8px;padding:8px;background:#0f172a;border-radius:4px;font-size:12px}
.child-jobs{margin-top:8px}
.child-jobs table{font-size:12px}
.link{color:#38bdf8;cursor:pointer;text-decoration:underline}
.link:hover{color:#7dd3fc}
.toast{position:fixed;top:16px;right:16px;padding:12px 20px;border-radius:8px;font-size:13px;z-index:9999;max-width:500px;word-break:break-word}
.toast-success{background:#065f46;color:#6ee7b7;border:1px solid #047857}
.toast-error{background:#7f1d1d;color:#fca5a5;border:1px solid #991b1b}
.toast-info{background:#1e3a5f;color:#7dd3fc;border:1px solid #1d4ed8}
.filter-bar{display:flex;gap:8px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.filter-bar label{color:#94a3b8;font-size:12px}
.confirm-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:9998}
.confirm-box{background:#1e293b;border:1px solid #475569;border-radius:8px;padding:24px;max-width:500px;width:90%}
.confirm-box h3{color:#f1f5f9;margin-bottom:12px}
.confirm-box p{color:#94a3b8;font-size:13px;margin-bottom:16px;word-break:break-word}
.confirm-box .actions{display:flex;gap:8px;justify-content:flex-end}
</style>
</head>
<body>
<div class="container">
<h1>DataHub Ops Dashboard</h1>

<div class="tabs">
  <div class="tab active" onclick="switchTab('commands')">Commands</div>
  <div class="tab" onclick="switchTab('jobs')">Jobs</div>
  <div class="tab" onclick="switchTab('fanout')">Fan-out</div>
  <div class="tab" onclick="switchTab('schedules')">Schedules</div>
  <div class="tab" onclick="switchTab('tables')">Tables</div>
</div>

<!-- Commands Tab -->
<div id="tab-commands" class="tab-content active">
  <h2>Trigger Command</h2>
  <div class="card">
    <div class="trigger-form">
      <label>Command <select id="cmd-select" onchange="onCmdSelect()"><option value="">-- select --</option></select></label>
      <label>Params JSON <textarea id="cmd-params" rows="2" cols="40">{}</textarea></label>
      <button class="primary" onclick="triggerCommand()">Trigger (source=ui_manual)</button>
    </div>
    <div id="cmd-hint" style="color:#64748b;font-size:12px;margin-top:6px"></div>
  </div>
</div>

<!-- Jobs Tab -->
<div id="tab-jobs" class="tab-content">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2>Ingestion Jobs</h2>
    <button class="primary" onclick="loadJobs()">Refresh</button>
  </div>
  <div class="filter-bar">
    <label>Status <select id="job-status-filter" onchange="loadJobs()"><option value="">All</option><option value="failed">failed</option><option value="partial">partial</option><option value="cancelled">cancelled</option><option value="succeeded">succeeded</option><option value="running">running</option></select></label>
    <label>Source <select id="job-source-filter" onchange="loadJobs()"><option value="">All</option><option value="api">api</option><option value="cli">cli</option><option value="scheduler">scheduler</option><option value="retry">retry</option></select></label>
  </div>
  <div id="job-list"></div>
  <div id="job-detail" style="display:none"></div>
</div>

<!-- Fan-out Tab -->
<div id="tab-fanout" class="tab-content">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2>Fan-out Parents</h2>
    <button class="primary" onclick="loadFanout()">Refresh</button>
  </div>
  <div id="fanout-list"></div>
  <div id="fanout-detail" style="display:none"></div>
</div>

<!-- Schedules Tab -->
<div id="tab-schedules" class="tab-content">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2>Scheduled Plans</h2>
    <button class="primary" onclick="loadSchedules()">Refresh</button>
  </div>
  <div id="schedule-plans"></div>
  <h2>Recent Runs</h2>
  <div id="schedule-runs"></div>
  <div id="run-detail" style="display:none"></div>
</div>

<!-- Tables Tab -->
<div id="tab-tables" class="tab-content">
  <h2>Business Tables</h2>
  <div id="table-stats"></div>
</div>
</div>

<div id="confirm-container"></div>

<script>
const API = '';
const KEY = localStorage.getItem('datahub_api_key') || '';
const headers = {'X-API-Key': KEY, 'Content-Type': 'application/json'};

if (!KEY) {
  document.addEventListener('DOMContentLoaded', function() {
    const key = prompt('Enter API Key (X-API-Key):');
    if (key) { localStorage.setItem('datahub_api_key', key); location.reload(); }
  });
}

const RETRYABLE = new Set(['failed','partial','cancelled']);
const TERMINAL = new Set(['succeeded','failed','partial','cancelled']);

function statusBadge(s) {
  const m = {succeeded:'green',accepted:'blue',running:'yellow',triggering:'yellow',partial:'yellow',failed:'red',cancelled:'red',conflict:'red',submitted:'blue',pending:'gray',skipped:'gray'};
  return `<span class="badge badge-${m[s]||'gray'}">${s}</span>`;
}
function sourceBadge(s) {
  const m = {api:'blue',cli:'purple',scheduler:'green',retry:'yellow',ui_manual:'blue'};
  return s ? `<span class="badge badge-${m[s]||'gray'}">${s}</span>` : '-';
}
function fmtJson(s) { try { return JSON.stringify(JSON.parse(s), null, 2); } catch { return s || '-'; } }
function fmtTime(s) { return s ? s.replace('T',' ').substring(0, 19) : '-'; }
function shortId(s) { return s ? (s.length > 30 ? s.substring(0,30)+'...' : s) : '-'; }
function esc(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function toast(msg, type='info') {
  const el = document.createElement('div');
  el.className = 'toast toast-'+type;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

function confirmAction(msg, onConfirm) {
  const c = document.getElementById('confirm-container');
  c.innerHTML = `<div class="confirm-overlay" onclick="if(event.target===this)this.remove()">
    <div class="confirm-box"><h3>Confirm Action</h3><p>${esc(msg)}</p>
    <div class="actions"><button onclick="this.closest('.confirm-overlay').remove()">Cancel</button>
    <button class="danger" id="confirm-ok">Confirm</button></div></div></div>`;
  document.getElementById('confirm-ok').onclick = function() { c.innerHTML=''; onConfirm(); };
}

function switchTab(name) {
  const idx = {commands:1,jobs:2,fanout:3,schedules:4,tables:5}[name];
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab:nth-child(${idx})`).classList.add('active');
  document.getElementById('tab-'+name).classList.add('active');
  if (name==='jobs') loadJobs();
  if (name==='fanout') loadFanout();
  if (name==='schedules') loadSchedules();
  if (name==='tables') loadTables();
}

// ========== Commands ==========
async function loadCommands() {
  const r = await fetch(API+'/plugins', {headers});
  const data = await r.json();
  const sel = document.getElementById('cmd-select');
  sel.innerHTML = '<option value="">-- select --</option>';
  for (const p of data.items) {
    for (const c of p.commands) {
      if (!c.enabled) continue;
      sel.innerHTML += `<option value="${c.name}" data-params='${JSON.stringify(c.required_params)}'>${c.name}</option>`;
    }
  }
}

function onCmdSelect() {
  const sel = document.getElementById('cmd-select');
  const opt = sel.options[sel.selectedIndex];
  const hint = document.getElementById('cmd-hint');
  if (opt.value) {
    const params = JSON.parse(opt.dataset.params || '[]');
    const defaultParams = {};
    params.forEach(p => defaultParams[p] = '');
    document.getElementById('cmd-params').value = JSON.stringify(defaultParams, null, 2);
    hint.textContent = 'Required params: ' + params.join(', ');
  } else {
    hint.textContent = '';
  }
}

async function triggerCommand() {
  const cmd = document.getElementById('cmd-select').value;
  if (!cmd) return toast('Select a command first', 'error');
  let params;
  try { params = JSON.parse(document.getElementById('cmd-params').value); }
  catch { return toast('Invalid JSON in params', 'error'); }
  confirmAction(`Trigger command "${cmd}" with source=ui_manual?`, async () => {
    try {
      const resp = await fetch(API+'/ingestion/v1/jobs', {
        method:'POST', headers,
        body: JSON.stringify({command:cmd, params, source:'ui_manual'})
      });
      const result = await resp.json();
      if (resp.ok) {
        toast(`Job created: ${result.ingestion_job_id} (status: ${result.status})`, 'success');
      } else {
        toast(`Error: ${result.detail?.error||''} - ${result.detail?.message||JSON.stringify(result)}`, 'error');
      }
    } catch(e) { toast(`Request failed: ${e.message}`, 'error'); }
  });
}

// ========== Jobs ==========
async function loadJobs() {
  const r = await fetch(API+'/ingestion/v1/jobs?limit=100', {headers});
  const data = await r.json();
  const statusFilter = document.getElementById('job-status-filter')?.value || '';
  const sourceFilter = document.getElementById('job-source-filter')?.value || '';
  let items = data.items || [];
  if (statusFilter) items = items.filter(j => j.status === statusFilter);
  if (sourceFilter) items = items.filter(j => j.source === sourceFilter);

  const el = document.getElementById('job-list');
  let html = '<table><tr><th>Job ID</th><th>Command</th><th>Source</th><th>Status</th><th>Parent</th><th>Retry Of</th><th>Rows</th><th>Error</th><th>Created</th><th>Actions</th></tr>';
  for (const j of items) {
    const canRetry = RETRYABLE.has(j.status);
    html += `<tr>
      <td class="mono"><span class="link" onclick="showJobDetail('${j.ingestion_job_id}')">${shortId(j.ingestion_job_id)}</span></td>
      <td>${j.trigger_key||'-'}</td>
      <td>${sourceBadge(j.source)}</td>
      <td>${statusBadge(j.status)}</td>
      <td>${j.parent_job_id ? `<span class="link" onclick="showJobDetail('${j.parent_job_id}')">${shortId(j.parent_job_id)}</span>` : '-'}</td>
      <td>${j.retry_of_job_id ? `<span class="link" onclick="showJobDetail('${j.retry_of_job_id}')">${shortId(j.retry_of_job_id)}</span>` : '-'}</td>
      <td>${j.row_count??'-'}</td>
      <td class="error-cell" title="${esc(j.error||'')}">${j.error ? shortId(j.error) : '-'}</td>
      <td>${fmtTime(j.created_at)}</td>
      <td>
        <button onclick="showJobDetail('${j.ingestion_job_id}')">Detail</button>
        ${canRetry ? `<button class="danger" onclick="retryJob('${j.ingestion_job_id}','${j.trigger_key||''}')">Retry</button>` : ''}
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
  const canRetry = RETRYABLE.has(j.status);

  let html = `<div class="card">
    <div class="card-header"><span class="card-title">Job Detail</span><button onclick="document.getElementById('job-detail').style.display='none'">Close</button></div>
    <table>
      <tr><td style="color:#94a3b8;width:140px">Job ID</td><td class="mono">${j.ingestion_job_id}</td></tr>
      <tr><td style="color:#94a3b8">Command</td><td>${j.trigger_key||'-'}</td></tr>
      <tr><td style="color:#94a3b8">Source</td><td>${sourceBadge(j.source)}</td></tr>
      <tr><td style="color:#94a3b8">Status</td><td>${statusBadge(j.status)}</td></tr>
      <tr><td style="color:#94a3b8">Parent Job</td><td class="mono">${j.parent_job_id ? `<span class="link" onclick="showJobDetail('${j.parent_job_id}')">${j.parent_job_id}</span>` : '-'} ${j.parent_job_id ? `<button onclick="showJobDetail('${j.parent_job_id}')">View</button>` : ''}</td></tr>
      <tr><td style="color:#94a3b8">Retry Of</td><td class="mono">${j.retry_of_job_id ? `<span class="link" onclick="showJobDetail('${j.retry_of_job_id}')">${j.retry_of_job_id}</span>` : '-'}</td></tr>
      <tr><td style="color:#94a3b8">Params</td><td class="mono"><pre style="white-space:pre-wrap">${fmtJson(j.params_json)}</pre></td></tr>
      <tr><td style="color:#94a3b8">Error</td><td class="error-cell">${j.error||'-'}</td></tr>
      <tr><td style="color:#94a3b8">Result</td><td class="mono"><pre style="white-space:pre-wrap">${fmtJson(j.result_json)}</pre></td></tr>
      <tr><td style="color:#94a3b8">Producer Status</td><td class="mono"><pre style="white-space:pre-wrap">${fmtJson(j.producer_status_json)}</pre></td></tr>
      <tr><td style="color:#94a3b8">Row Count</td><td>${j.row_count??'-'}</td></tr>
      <tr><td style="color:#94a3b8">Created</td><td>${fmtTime(j.created_at)}</td></tr>
      <tr><td style="color:#94a3b8">Updated</td><td>${fmtTime(j.updated_at)}</td></tr>
      <tr><td style="color:#94a3b8">Finished</td><td>${fmtTime(j.finished_at)}</td></tr>
    </table>
    ${canRetry ? `<button class="danger" onclick="retryJob('${j.ingestion_job_id}','${j.trigger_key||''}')">Retry This Job</button>` : ''}
  </div>`;

  // Load child jobs
  try {
    const cr = await fetch(API+`/ingestion/v1/jobs/${jobId}/children`, {headers});
    const children = await cr.json();
    if (children.total > 0) {
      html += `<div class="card"><h3>Child Jobs (${children.total})</h3><table>
        <tr><th>Job ID</th><th>Source</th><th>Status</th><th>Retry Of</th><th>Params</th><th>Error</th><th>Action</th></tr>`;
      for (const c of children.items) {
        const cp = fmtJson(c.params_json);
        const cRetry = RETRYABLE.has(c.status);
        html += `<tr>
          <td class="mono"><span class="link" onclick="showJobDetail('${c.ingestion_job_id}')">${shortId(c.ingestion_job_id)}</span></td>
          <td>${sourceBadge(c.source)}</td>
          <td>${statusBadge(c.status)}</td>
          <td>${c.retry_of_job_id ? `<span class="link" onclick="showJobDetail('${c.retry_of_job_id}')">${shortId(c.retry_of_job_id)}</span>` : '-'}</td>
          <td class="mono params-cell" title="${esc(cp)}">${cp.substring(0,50)}</td>
          <td class="error-cell">${c.error||'-'}</td>
          <td>${cRetry ? `<button class="danger" onclick="retryJob('${c.ingestion_job_id}','${c.trigger_key||''}')">Retry</button>` : ''}</td>
        </tr>`;
      }
      html += '</table></div>';
    }
  } catch {}

  el.innerHTML = html;
  el.scrollIntoView({behavior:'smooth'});
}

async function retryJob(jobId, cmd) {
  confirmAction(`Retry job ${jobId}?\nCommand: ${cmd}`, async () => {
    try {
      const resp = await fetch(API+`/ingestion/v1/jobs/${jobId}/retry`, {method:'POST', headers});
      const result = await resp.json();
      if (resp.ok) {
        toast(`Retry job created: ${result.ingestion_job_id} (retry_of: ${result.retry_of_job_id||'-'})`, 'success');
        loadJobs();
      } else {
        const d = result.detail || result;
        toast(`Error: ${d.error||''} - ${d.message||JSON.stringify(d)}${d.ingestion_job_id ? ' (job: '+d.ingestion_job_id+')' : ''}`, 'error');
      }
    } catch(e) { toast(`Retry failed: ${e.message}`, 'error'); }
  });
}

// ========== Fan-out ==========
async function loadFanout() {
  const r = await fetch(API+'/ingestion/v1/jobs?limit=200', {headers});
  const data = await r.json();
  // Find parent jobs (those with children)
  const parents = (data.items||[]).filter(j => j.parent_job_id === null && j.status !== 'triggering');
  const el = document.getElementById('fanout-list');

  let html = '<table><tr><th>Parent Job ID</th><th>Command</th><th>Status</th><th>Source</th><th>Created</th><th>Action</th></tr>';
  for (const j of parents.slice(0, 30)) {
    html += `<tr>
      <td class="mono"><span class="link" onclick="showFanoutDetail('${j.ingestion_job_id}')">${shortId(j.ingestion_job_id)}</span></td>
      <td>${j.trigger_key||'-'}</td>
      <td>${statusBadge(j.status)}</td>
      <td>${sourceBadge(j.source)}</td>
      <td>${fmtTime(j.created_at)}</td>
      <td><button onclick="showFanoutDetail('${j.ingestion_job_id}')">Details</button></td>
    </tr>`;
  }
  html += '</table>';
  el.innerHTML = html;
}

async function showFanoutDetail(parentJobId) {
  const el = document.getElementById('fanout-detail');
  el.style.display = 'block';
  el.innerHTML = '<p style="color:#94a3b8">Loading...</p>';

  try {
    const [parentR, childrenR] = await Promise.all([
      fetch(API+`/ingestion/v1/jobs/${parentJobId}`, {headers}),
      fetch(API+`/ingestion/v1/jobs/${parentJobId}/children`, {headers})
    ]);
    const parent = await parentR.json();
    const children = await childrenR.json();

    // Stats
    const stats = {};
    children.items.forEach(c => { stats[c.status] = (stats[c.status]||0) + 1; });

    let html = `<div class="card">
      <div class="card-header"><span class="card-title">Fan-out Parent: ${shortId(parentJobId)}</span><button onclick="document.getElementById('fanout-detail').style.display='none'">Close</button></div>
      <table>
        <tr><td style="color:#94a3b8;width:140px">Job ID</td><td class="mono">${parent.ingestion_job_id}</td></tr>
        <tr><td style="color:#94a3b8">Command</td><td>${parent.trigger_key||'-'}</td></tr>
        <tr><td style="color:#94a3b8">Status</td><td>${statusBadge(parent.status)}</td></tr>
        <tr><td style="color:#94a3b8">Source</td><td>${sourceBadge(parent.source)}</td></tr>
        <tr><td style="color:#94a3b8">Error</td><td class="error-cell">${parent.error||'-'}</td></tr>
        <tr><td style="color:#94a3b8">Result</td><td class="mono"><pre style="white-space:pre-wrap">${fmtJson(parent.result_json)}</pre></td></tr>
      </table>
    </div>`;

    // Stats cards
    html += '<div class="stats">';
    for (const [s, n] of Object.entries(stats)) {
      html += `<div class="stat-card"><div class="stat-value">${n}</div><div class="stat-label">${s}</div></div>`;
    }
    html += '</div>';

    // Retry failed children button
    const failedCount = (stats['failed']||0) + (stats['partial']||0) + (stats['cancelled']||0);
    if (failedCount > 0) {
      html += `<div class="card">
        <h3>Retry Failed Children</h3>
        <p style="color:#94a3b8;font-size:12px">${failedCount} failed/partial/cancelled children found.</p>
        <div class="trigger-form" style="margin-top:8px">
          <label>Item indexes (optional, comma-sep) <input id="retry-item-indexes" size="30" placeholder="e.g. 322,402 or leave empty for all"></label>
          <button class="danger" onclick="retryFailedChildren('${parentJobId}')">Retry Failed Children</button>
        </div>
      </div>`;
    }

    // Children table
    html += `<div class="card"><h3>Child Jobs (${children.total})</h3>
      <table><tr><th>Job ID</th><th>Source</th><th>Status</th><th>Retry Of</th><th>Params</th><th>Error</th><th>Action</th></tr>`;
    for (const c of children.items) {
      const cp = fmtJson(c.params_json);
      const cRetry = RETRYABLE.has(c.status);
      html += `<tr>
        <td class="mono"><span class="link" onclick="showJobDetail('${c.ingestion_job_id}')">${shortId(c.ingestion_job_id)}</span></td>
        <td>${sourceBadge(c.source)}</td>
        <td>${statusBadge(c.status)}</td>
        <td>${c.retry_of_job_id ? `<span class="link" onclick="showJobDetail('${c.retry_of_job_id}')">${shortId(c.retry_of_job_id)}</span>` : '-'}</td>
        <td class="mono params-cell" title="${esc(cp)}">${cp.substring(0,50)}</td>
        <td class="error-cell">${c.error||'-'}</td>
        <td>${cRetry ? `<button class="danger" onclick="retryJob('${c.ingestion_job_id}','${c.trigger_key||''}')">Retry</button>` : ''}</td>
      </tr>`;
    }
    html += '</table></div>';

    el.innerHTML = html;
    el.scrollIntoView({behavior:'smooth'});
  } catch(e) {
    el.innerHTML = `<p style="color:#fca5a5">Error: ${e.message}</p>`;
  }
}

async function retryFailedChildren(parentJobId) {
  const indexesStr = document.getElementById('retry-item-indexes')?.value?.trim();
  let body = null;
  if (indexesStr) {
    const indexes = indexesStr.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
    if (indexes.length === 0) return toast('Invalid item indexes', 'error');
    body = {item_indexes: indexes};
  }
  confirmAction(`Retry failed children of ${parentJobId}?${body ? ' Items: '+body.item_indexes.join(',') : ' All failed items'}`, async () => {
    try {
      const resp = await fetch(API+`/ingestion/v1/jobs/${parentJobId}/retry-failed-children`, {
        method:'POST', headers,
        body: body ? JSON.stringify(body) : undefined
      });
      const result = await resp.json();
      if (resp.ok) {
        toast(`Retry submitted: ${result.submitted} submitted, ${result.skipped} skipped`, 'success');
        showFanoutDetail(parentJobId);
      } else {
        const d = result.detail || result;
        toast(`Error: ${d.error||''} - ${d.message||JSON.stringify(d)}`, 'error');
      }
    } catch(e) { toast(`Request failed: ${e.message}`, 'error'); }
  });
}

// ========== Schedules ==========
async function loadSchedules() {
  const [plansR, runsR] = await Promise.all([
    fetch(API+'/admin/schedules/plans', {headers}),
    fetch(API+'/admin/schedules/runs?limit=20', {headers})
  ]);
  const plans = await plansR.json();
  const runs = await runsR.json();

  // Plans
  const pel = document.getElementById('schedule-plans');
  let html = '<table><tr><th>Plan</th><th>Enabled</th><th>Schedule</th><th>Next Run</th><th>Last Status</th><th>Actions</th></tr>';
  for (const p of (plans.items||plans)) {
    html += `<tr>
      <td><b>${p.plan_name}</b></td>
      <td>${p.enabled ? '<span class="badge badge-green">enabled</span>' : '<span class="badge badge-gray">disabled</span>'}</td>
      <td>${p.schedule_type} ${p.schedule_time||''}</td>
      <td>${fmtTime(p.next_run_at)}</td>
      <td>${p.last_status ? statusBadge(p.last_status) : '-'}</td>
      <td>
        <button onclick="showPlanRuns('${p.plan_name}')">Runs</button>
        <button class="primary" onclick="runPlanNow('${p.plan_name}')">Run Now</button>
      </td>
    </tr>`;
  }
  html += '</table>';
  pel.innerHTML = html;

  // Recent runs
  const rel = document.getElementById('schedule-runs');
  html = '<table><tr><th>Run ID</th><th>Plan</th><th>Source</th><th>Status</th><th>Started</th><th>Finished</th><th>Action</th></tr>';
  for (const r of (runs.items||runs)) {
    html += `<tr>
      <td class="mono"><span class="link" onclick="showRunDetail('${r.run_id}')">${shortId(r.run_id)}</span></td>
      <td>${r.plan_name}</td>
      <td>${sourceBadge(r.trigger_source)}</td>
      <td>${statusBadge(r.status)}</td>
      <td>${fmtTime(r.started_at)}</td>
      <td>${fmtTime(r.finished_at)}</td>
      <td><button onclick="showRunDetail('${r.run_id}')">Steps</button></td>
    </tr>`;
  }
  html += '</table>';
  rel.innerHTML = html;
}

async function runPlanNow(planName) {
  confirmAction(`Run plan "${planName}" now?`, async () => {
    try {
      const resp = await fetch(API+`/admin/schedules/plans/${planName}/run`, {method:'POST', headers});
      const result = await resp.json();
      if (resp.ok) {
        toast(`Run started: ${result.run_id} (status: ${result.status})`, 'success');
        loadSchedules();
      } else {
        const d = result.detail || result;
        toast(`Error: ${d.error||''} - ${d.message||JSON.stringify(d)}`, 'error');
      }
    } catch(e) { toast(`Request failed: ${e.message}`, 'error'); }
  });
}

async function showPlanRuns(planName) {
  try {
    const r = await fetch(API+`/admin/schedules/runs?plan_name=${planName}&limit=10`, {headers});
    const runs = await r.json();
    const el = document.getElementById('schedule-runs');
    let html = `<h2>Runs for ${planName}</h2><table><tr><th>Run ID</th><th>Source</th><th>Status</th><th>Started</th><th>Finished</th><th>Action</th></tr>`;
    for (const r of (runs.items||runs)) {
      html += `<tr>
        <td class="mono"><span class="link" onclick="showRunDetail('${r.run_id}')">${shortId(r.run_id)}</span></td>
        <td>${sourceBadge(r.trigger_source)}</td>
        <td>${statusBadge(r.status)}</td>
        <td>${fmtTime(r.started_at)}</td>
        <td>${fmtTime(r.finished_at)}</td>
        <td><button onclick="showRunDetail('${r.run_id}')">Steps</button></td>
      </tr>`;
    }
    html += '</table>';
    el.innerHTML = html;
  } catch(e) { toast(`Failed: ${e.message}`, 'error'); }
}

async function showRunDetail(runId) {
  const el = document.getElementById('run-detail');
  el.style.display = 'block';
  try {
    const r = await fetch(API+`/admin/schedules/runs/${runId}`, {headers});
    const run = await r.json();
    let html = `<div class="card">
      <div class="card-header"><span class="card-title">Run: ${shortId(runId)}</span><button onclick="document.getElementById('run-detail').style.display='none'">Close</button></div>
      <table>
        <tr><td style="color:#94a3b8;width:140px">Run ID</td><td class="mono">${run.run_id}</td></tr>
        <tr><td style="color:#94a3b8">Plan</td><td>${run.plan_name}</td></tr>
        <tr><td style="color:#94a3b8">Source</td><td>${sourceBadge(run.trigger_source)}</td></tr>
        <tr><td style="color:#94a3b8">Status</td><td>${statusBadge(run.status)}</td></tr>
        <tr><td style="color:#94a3b8">Error</td><td class="error-cell">${run.error||'-'}</td></tr>
        <tr><td style="color:#94a3b8">Started</td><td>${fmtTime(run.started_at)}</td></tr>
        <tr><td style="color:#94a3b8">Finished</td><td>${fmtTime(run.finished_at)}</td></tr>
      </table>
      <h3>Steps</h3>
      <table><tr><th>Step</th><th>Command</th><th>Status</th><th>Job ID</th><th>Error</th></tr>`;
    for (const s of (run.steps||[])) {
      html += `<tr>
        <td>${s.step_order}</td>
        <td>${s.command_name}</td>
        <td>${statusBadge(s.status)}</td>
        <td>${s.job_id ? `<span class="link" onclick="showJobDetail('${s.job_id}')">${shortId(s.job_id)}</span>` : '-'}</td>
        <td class="error-cell">${s.error||'-'}</td>
      </tr>`;
    }
    html += '</table></div>';
    el.innerHTML = html;
    el.scrollIntoView({behavior:'smooth'});
  } catch(e) { el.innerHTML = `<p style="color:#fca5a5">Error: ${e.message}</p>`; }
}

// ========== Tables ==========
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
