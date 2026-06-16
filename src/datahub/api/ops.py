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
:root{--bg:#0f172a;--panel:#1e293b;--panel-2:#111827;--border:#334155;--text:#e2e8f0;--muted:#94a3b8;--primary:#38bdf8;--danger:#ef4444;--success:#10b981;--warning:#f59e0b}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5}
.container{width:min(2200px,calc(100vw - 64px));max-width:none;margin:0 auto;padding:24px 32px}
@media(min-width:2200px){.container{width:calc(100vw - 96px)}}
@media(max-width:900px){.container{width:calc(100vw - 24px);padding:12px}}

/* Header */
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
.topbar h1{font-size:22px;color:var(--primary);font-weight:700;letter-spacing:-0.3px}
.topbar-right{display:flex;gap:8px;align-items:center}
.subtitle{color:var(--muted);font-size:13px;margin-bottom:20px}

/* Tabs */
.tabs{display:flex;gap:6px;border-bottom:1px solid var(--border);margin-bottom:20px;flex-wrap:wrap}
.tab{padding:10px 18px;border-radius:8px 8px 0 0;background:var(--panel-2);border:1px solid var(--border);border-bottom:none;cursor:pointer;color:var(--muted);font-size:13px;font-weight:500;transition:all .15s}
.tab:hover{color:var(--text);background:var(--panel)}
.tab.active{background:var(--panel);color:var(--primary);border-color:var(--primary);font-weight:600}
.tab-content{display:none}
.tab-content.active{display:block}

/* Cards & Sections */
h2{font-size:15px;color:var(--muted);margin:18px 0 8px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
h3{font-size:14px;color:var(--text);margin:16px 0 8px;font-weight:600}
.card{background:var(--panel);border-radius:10px;padding:20px;margin-bottom:16px;border:1px solid var(--border)}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.card-title{font-weight:600;color:var(--text);font-size:15px}
.section-label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin:16px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--border)}

/* Summary Cards */
.summary{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px;margin:10px 0 14px}
.summary-card{background:var(--panel);border-radius:8px;padding:12px 16px;border:1px solid var(--border);text-align:center;min-width:120px}
.summary-value{font-size:26px;font-weight:700;line-height:1.2}
.summary-label{font-size:11px;color:var(--muted);margin-top:4px}
.sv-primary{color:var(--primary)}.sv-success{color:var(--success)}.sv-danger{color:var(--danger)}.sv-warning{color:var(--warning)}.sv-muted{color:var(--muted)}

/* Badges */
.badge{display:inline-block;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:600;vertical-align:middle}
.badge-green{background:#065f46;color:#6ee7b7}
.badge-red{background:#7f1d1d;color:#fca5a5}
.badge-yellow{background:#713f12;color:#fde047}
.badge-blue{background:#1e3a5f;color:#7dd3fc}
.badge-gray{background:#374151;color:#9ca3af}
.badge-purple{background:#3b0764;color:#c4b5fd}

/* Tables */
.table-wrap{width:100%;overflow-x:auto;overflow-y:visible;border:1px solid var(--border);border-radius:10px;background:var(--panel)}
.data-table{width:max-content;min-width:1800px;border-collapse:separate;border-spacing:0;font-size:13px}
.data-table th{position:sticky;top:0;z-index:1;background:#172033;text-align:left;padding:10px 12px;color:var(--muted);border-bottom:1px solid var(--border);font-weight:600;font-size:12px;white-space:nowrap}
.data-table td{padding:10px 12px;border-bottom:1px solid #1a2744;vertical-align:middle;white-space:nowrap}
.data-table tr:hover td{background:#162033}
.col-id{width:340px;max-width:340px}.col-command{width:260px;max-width:260px}.col-source{width:100px}.col-status{width:100px}.col-parent{width:300px;max-width:300px}.col-retry{width:300px;max-width:300px}.col-rows{width:90px;text-align:right}.col-error{width:360px;max-width:360px}.col-created{width:180px}.col-actions{width:150px}
.text-ellipsis{display:inline-block;max-width:100%;overflow:hidden;text-overflow:ellipsis;vertical-align:bottom}

/* Buttons */
button{min-height:30px;padding:6px 12px;border-radius:6px;border:1px solid var(--border);background:var(--panel-2);color:var(--text);cursor:pointer;font-size:12px;font-weight:500;transition:all .15s;white-space:nowrap}
button:hover{background:#2a3a52}
button.primary{background:#1d4ed8;border-color:#1d4ed8;color:#fff}
button.primary:hover{background:#2563eb}
button.danger{background:transparent;border-color:var(--danger);color:var(--danger)}
button.danger:hover{background:var(--danger);color:#fff}
button:disabled{opacity:0.4;cursor:not-allowed}
.action-stack{display:flex;gap:8px;align-items:center;flex-wrap:nowrap}
.action-stack button{min-width:64px}

/* Inputs */
input,select,textarea{padding:6px 10px;border-radius:6px;border:1px solid var(--border);background:var(--panel-2);color:var(--text);font-size:12px}
textarea{font-family:"Cascadia Code",Consolas,monospace;resize:vertical}
select{height:30px}

/* Utilities */
.mono{font-family:"Cascadia Code",Consolas,monospace;font-size:12px}
.error-cell{color:#fca5a5}
.link{color:var(--primary);cursor:pointer;text-decoration:none;border-bottom:1px dashed transparent;transition:border-color .15s}
.link:hover{color:#7dd3fc;border-bottom-color:#7dd3fc}

/* Commands layout */
.cmd-grid{display:grid;grid-template-columns:1fr 2fr;gap:16px;align-items:start}
@media(max-width:900px){.cmd-grid{grid-template-columns:1fr}}
.cmd-left{display:flex;flex-direction:column;gap:12px}
.cmd-right{display:flex;flex-direction:column;gap:12px}
.cmd-right textarea{width:100%;height:160px}

/* Filter bar */
.filter-bar{display:flex;gap:10px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.filter-bar label{color:var(--muted);font-size:12px;display:flex;align-items:center;gap:6px}

/* Right-side Drawer */
.drawer-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:9000;display:flex;justify-content:flex-end}
.drawer-aside{width:min(920px,52vw);min-width:720px;height:100vh;background:var(--panel);border-left:1px solid var(--border);overflow:auto;box-shadow:-12px 0 40px rgba(0,0,0,.35)}
@media(max-width:1200px){.drawer-aside{width:100vw;min-width:0}}
.drawer-header{position:sticky;top:0;z-index:2;background:var(--panel);border-bottom:1px solid var(--border);padding:16px;display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.drawer-body{padding:16px}
.drawer-title{font-size:16px;font-weight:700;color:var(--primary)}
.drawer-subtitle{color:var(--muted);font-size:12px;margin-top:4px;word-break:break-all}
.detail-grid{display:grid;grid-template-columns:140px 1fr;gap:2px 12px;font-size:13px}
.detail-grid dt{color:var(--muted);font-weight:500;padding:4px 0}
.detail-grid dd{padding:4px 0;word-break:break-all}
.detail-grid pre{white-space:pre-wrap;word-break:break-all;max-height:200px;overflow:auto;background:var(--bg);padding:8px;border-radius:6px;font-size:12px}
.error-box{background:#7f1d1d;color:#fca5a5;padding:12px;border-radius:6px;font-size:13px}

/* Toast */
.toast{position:fixed;top:16px;right:16px;padding:14px 22px;border-radius:8px;font-size:13px;z-index:9999;max-width:520px;word-break:break-word;animation:slideIn .2s}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
.toast-success{background:#065f46;color:#6ee7b7;border:1px solid #047857}
.toast-error{background:#7f1d1d;color:#fca5a5;border:1px solid #991b1b;font-weight:500}
.toast-info{background:#1e3a5f;color:#7dd3fc;border:1px solid #1d4ed8}

/* Confirm */
.confirm-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:9998}
.confirm-box{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:24px;max-width:520px;width:90%}
.confirm-box h3{color:var(--text);margin-bottom:12px;font-size:16px}
.confirm-box p{color:var(--muted);font-size:13px;margin-bottom:20px;word-break:break-word;white-space:pre-line}
.confirm-box .actions{display:flex;gap:10px;justify-content:flex-end}

/* Stats row for fanout */
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin:12px 0}
.stat-card{background:var(--panel);border-radius:8px;padding:12px;border:1px solid var(--border);text-align:center}
.stat-value{font-size:24px;font-weight:700;color:var(--primary)}
.stat-label{font-size:11px;color:var(--muted);margin-top:2px}
</style>
</head>
<body>
<div class="container">
<div class="topbar">
  <h1>DataHub Ops</h1>
  <div class="topbar-right">
    <span class="badge badge-blue" id="api-key-badge">API Key</span>
    <button class="primary" onclick="refreshCurrentTab()" title="Refresh current tab data">Refresh</button>
  </div>
</div>
<p class="subtitle">Operational console for ingestion jobs, fan-out retries, and scheduled collection plans.</p>

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
    <div class="cmd-grid">
      <div class="cmd-left">
        <label style="color:var(--muted);font-size:12px;font-weight:600">Command</label>
        <select id="cmd-select" onchange="onCmdSelect()" style="width:100%"><option value="">-- select --</option></select>
        <div id="cmd-hint" style="color:var(--muted);font-size:12px"></div>
        <div><span class="badge badge-blue">source: ui_manual</span></div>
        <button class="primary" onclick="triggerCommand()" title="Trigger selected command with source=ui_manual">Trigger</button>
      </div>
      <div class="cmd-right">
        <label style="color:var(--muted);font-size:12px;font-weight:600">Params JSON</label>
        <textarea id="cmd-params">{}</textarea>
      </div>
    </div>
  </div>
</div>

<!-- Jobs Tab -->
<div id="tab-jobs" class="tab-content">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2 style="margin-bottom:0">Ingestion Jobs</h2>
  </div>
  <div id="job-summary" class="summary" style="margin-top:12px"></div>
  <div class="filter-bar">
    <label>Status <select id="job-status-filter" onchange="loadJobs()"><option value="">All</option><option value="failed">failed</option><option value="partial">partial</option><option value="cancelled">cancelled</option><option value="succeeded">succeeded</option><option value="running">running</option></select></label>
    <label>Source <select id="job-source-filter" onchange="loadJobs()"><option value="">All</option><option value="api">api</option><option value="cli">cli</option><option value="scheduler">scheduler</option><option value="retry">retry</option></select></label>
    <label>Search <input id="job-q" size="20" placeholder="job ID, command, error..." onkeydown="if(event.key==='Enter')loadJobs()"></label>
    <label>Parent <input id="job-parent-filter" size="20" placeholder="parent_job_id" onkeydown="if(event.key==='Enter')loadJobs()"></label>
    <label>Page Size <select id="job-page-size" onchange="loadJobs()"><option value="100">100</option><option value="200">200</option><option value="500">500</option><option value="1000">1000</option></select></label>
    <button onclick="loadJobs()">Go</button>
  </div>
  <div id="job-pager" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;font-size:13px;color:var(--muted)"></div>
  <div id="job-list"></div>
</div>

<!-- Fan-out Tab -->
<div id="tab-fanout" class="tab-content">
  <h2>Fan-out Parents</h2>
  <div id="fanout-summary" class="summary"></div>
  <div id="fanout-list"></div>
</div>

<!-- Schedules Tab -->
<div id="tab-schedules" class="tab-content">
  <h2>Scheduled Plans</h2>
  <div id="schedule-summary" class="summary"></div>
  <div id="schedule-plans"></div>
  <h2>Recent Runs</h2>
  <div id="schedule-runs"></div>
</div>

<!-- Tables Tab -->
<div id="tab-tables" class="tab-content">
  <h2>Business Tables</h2>
  <div id="table-stats"></div>
</div>
</div>

<!-- Right-side Drawer -->
<div id="drawer-overlay" class="drawer-overlay" style="display:none" onclick="closeDrawerIfOverlay(event)">
  <aside id="detail-drawer" class="drawer-aside">
    <div class="drawer-header">
      <div>
        <div id="drawer-title" class="drawer-title"></div>
        <div id="drawer-subtitle" class="drawer-subtitle"></div>
      </div>
      <button onclick="closeDrawer()" title="Close drawer">Close</button>
    </div>
    <div id="drawer-body" class="drawer-body"></div>
  </aside>
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
} else {
  document.addEventListener('DOMContentLoaded', function() {
    const b = document.getElementById('api-key-badge');
    if (b) b.textContent = KEY.length > 12 ? KEY.substring(0,8)+'...' : KEY;
  });
}

const RETRYABLE = new Set(['failed','partial','cancelled']);
let _currentTab = 'commands';

function esc(s) { return (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function jsArg(v) { return esc(JSON.stringify(v||'')); }
function htmlJson(s) { return esc(fmtJson(s)); }
function fmtJson(s) { try { return JSON.stringify(JSON.parse(s), null, 2); } catch { return s || '-'; } }
function fmtTime(s) { return s ? String(s).replace('T',' ').substring(0, 19) : '-'; }
function shortId(s) { return s ? (s.length > 56 ? s.substring(0,56)+'...' : s) : '-'; }

function statusBadge(s) {
  const m = {succeeded:'green',accepted:'blue',running:'yellow',triggering:'yellow',partial:'yellow',failed:'red',cancelled:'red',conflict:'red',submitted:'blue',pending:'gray',skipped:'gray'};
  return '<span class="badge badge-'+(m[s]||'gray')+'">'+esc(s)+'</span>';
}
function sourceBadge(s) {
  const m = {api:'blue',cli:'purple',scheduler:'green',retry:'yellow',ui_manual:'blue'};
  return s ? '<span class="badge badge-'+(m[s]||'gray')+'">'+esc(s)+'</span>' : '-';
}

function toast(msg, type='info') {
  const el = document.createElement('div');
  el.className = 'toast toast-'+type;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), type==='error' ? 8000 : 6000);
}

function confirmAction(msg, onConfirm) {
  const c = document.getElementById('confirm-container');
  c.innerHTML = '<div class="confirm-overlay" onclick="if(event.target===this)this.remove()">'
    +'<div class="confirm-box"><h3>Confirm Action</h3><p>'+esc(msg)+'</p>'
    +'<div class="actions"><button onclick="this.closest(\'.confirm-overlay\').remove()">Cancel</button>'
    +'<button class="danger" id="confirm-ok">Confirm</button></div></div></div>';
  document.getElementById('confirm-ok').onclick = function() { c.innerHTML=''; onConfirm(); };
}

// ========== Drawer ==========
function openDrawer(title, subtitle, html) {
  document.getElementById('drawer-title').textContent = title || 'Detail';
  document.getElementById('drawer-subtitle').textContent = subtitle || '';
  document.getElementById('drawer-body').innerHTML = html || '';
  document.getElementById('drawer-overlay').style.display = 'flex';
}
function closeDrawer() {
  document.getElementById('drawer-overlay').style.display = 'none';
}
function closeDrawerIfOverlay(event) {
  if (event.target.id === 'drawer-overlay') closeDrawer();
}
document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeDrawer(); });

function switchTab(name) {
  _currentTab = name;
  const idx = {commands:1,jobs:2,fanout:3,schedules:4,tables:5}[name];
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector('.tab:nth-child('+idx+')').classList.add('active');
  document.getElementById('tab-'+name).classList.add('active');
  if (name==='jobs') loadJobs();
  if (name==='fanout') loadFanout();
  if (name==='schedules') loadSchedules();
  if (name==='tables') loadTables();
}

function refreshCurrentTab() { switchTab(_currentTab); }

// ========== Commands ==========
async function loadCommands() {
  const r = await fetch(API+'/plugins', {headers});
  const data = await r.json();
  const sel = document.getElementById('cmd-select');
  sel.innerHTML = '<option value="">-- select --</option>';
  for (const p of data.items) {
    for (const c of p.commands) {
      if (!c.enabled) continue;
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.dataset.params = JSON.stringify(c.required_params);
      opt.textContent = c.name;
      sel.appendChild(opt);
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
  confirmAction('Trigger command "'+cmd+'" with source=ui_manual?', async () => {
    try {
      const resp = await fetch(API+'/ingestion/v1/jobs', {
        method:'POST', headers,
        body: JSON.stringify({command:cmd, params, source:'ui_manual'})
      });
      const result = await resp.json();
      if (resp.ok) {
        toast('Job created: '+result.ingestion_job_id+' (status: '+result.status+')', 'success');
      } else {
        const d = result.detail || result;
        toast('Error: '+(d.error||'')+' - '+(d.message||JSON.stringify(d)), 'error');
      }
    } catch(e) { toast('Request failed: '+e.message, 'error'); }
  });
}

// ========== Jobs ==========
let _jobOffset = 0;

async function loadJobs(resetPage) {
  if (resetPage !== false) _jobOffset = 0;
  const limit = parseInt(document.getElementById('job-page-size')?.value || '100');
  const statusFilter = document.getElementById('job-status-filter')?.value || '';
  const sourceFilter = document.getElementById('job-source-filter')?.value || '';
  const q = document.getElementById('job-q')?.value?.trim() || '';
  const parentJobId = document.getElementById('job-parent-filter')?.value?.trim() || '';

  const params = new URLSearchParams({limit, offset: _jobOffset});
  if (statusFilter) params.set('status', statusFilter);
  if (sourceFilter) params.set('source', sourceFilter);
  if (q) params.set('q', q);
  if (parentJobId) params.set('parent_job_id', parentJobId);

  const summaryParams = new URLSearchParams();
  if (statusFilter) summaryParams.set('status', statusFilter);
  if (sourceFilter) summaryParams.set('source', sourceFilter);
  if (q) summaryParams.set('q', q);
  if (parentJobId) summaryParams.set('parent_job_id', parentJobId);

  const [r, sr] = await Promise.all([
    fetch(API+'/ingestion/v1/jobs?'+params.toString(), {headers}),
    fetch(API+'/ingestion/v1/jobs/summary?'+summaryParams.toString(), {headers}),
  ]);
  const data = await r.json();
  const summary = await sr.json();
  const items = data.items || [];
  const total = data.total || 0;
  const offset = data.offset || 0;
  const showing = items.length;

  // Summary cards (from summary API — full filtered counts, not page-only)
  const se = document.getElementById('job-summary');
  se.innerHTML = summaryCard('Total',summary.total||0,'sv-primary') + summaryCard('Running',summary.running||0,'sv-warning') + summaryCard('Failed',summary.failed||0,'sv-danger') + summaryCard('Partial',summary.partial||0,'sv-warning') + summaryCard('Retry',summary.retry||0,'sv-primary');

  // Pager
  const pagerEl = document.getElementById('job-pager');
  const from = total > 0 ? offset + 1 : 0;
  const to = offset + showing;
  let pagerHtml = '<span>Showing '+from+'-'+to+' of '+total+'</span><div style="display:flex;gap:8px">';
  pagerHtml += '<button onclick="_jobOffset=0;loadJobs(false)"'+(offset===0?' disabled':'')+'>First</button>';
  pagerHtml += '<button onclick="_jobOffset=Math.max(0,_jobOffset-limit);loadJobs(false)"'+(offset===0?' disabled':'')+'>Prev</button>';
  pagerHtml += '<button onclick="_jobOffset=_jobOffset+'+limit+';loadJobs(false)"'+(to>=total?' disabled':'')+'>Next</button>';
  pagerHtml += '</div>';
  pagerEl.innerHTML = pagerHtml;

  const el = document.getElementById('job-list');
  let html = '<div class="table-wrap"><table class="data-table"><tr>'
    +'<th class="col-id">Job ID</th><th class="col-command">Command</th><th class="col-source">Source</th><th class="col-status">Status</th><th class="col-parent">Parent</th><th class="col-retry">Retry Of</th><th class="col-rows">Rows</th><th class="col-error">Error</th><th class="col-created">Created</th><th class="col-actions">Actions</th></tr>';
  for (const j of items) {
    const canRetry = RETRYABLE.has(j.status);
    html += '<tr>'
      +'<td class="mono col-id"><span class="link text-ellipsis" title="'+esc(j.ingestion_job_id)+'" onclick="showJobDetail('+jsArg(j.ingestion_job_id)+')">'+esc(shortId(j.ingestion_job_id))+'</span></td>'
      +'<td class="col-command"><span class="text-ellipsis" title="'+esc(j.trigger_key||'')+'">'+esc(j.trigger_key||'-')+'</span></td>'
      +'<td class="col-source">'+sourceBadge(j.source)+'</td>'
      +'<td class="col-status">'+statusBadge(j.status)+'</td>'
      +'<td class="mono col-parent">'+(j.parent_job_id ? '<span class="link text-ellipsis" title="'+esc(j.parent_job_id)+'" onclick="showJobDetail('+jsArg(j.parent_job_id)+')">'+esc(shortId(j.parent_job_id))+'</span>' : '-')+'</td>'
      +'<td class="mono col-retry">'+(j.retry_of_job_id ? '<span class="link text-ellipsis" title="'+esc(j.retry_of_job_id)+'" onclick="showJobDetail('+jsArg(j.retry_of_job_id)+')">'+esc(shortId(j.retry_of_job_id))+'</span>' : '-')+'</td>'
      +'<td class="col-rows">'+(j.row_count!=null?j.row_count:'-')+'</td>'
      +'<td class="error-cell col-error"><span class="text-ellipsis" title="'+esc(j.error||'')+'">'+esc(j.error ? shortId(j.error) : '-')+'</span></td>'
      +'<td class="col-created">'+esc(fmtTime(j.created_at))+'</td>'
      +'<td class="col-actions"><div class="action-stack">'
        +'<button onclick="showJobDetail('+jsArg(j.ingestion_job_id)+')" title="View job detail">Detail</button>'
        +(canRetry ? '<button class="danger" onclick="retryJob('+jsArg(j.ingestion_job_id)+','+jsArg(j.trigger_key||'')+')" title="Retry this job">Retry</button>' : '')
      +'</div></td></tr>';
  }
  html += '</table></div>';
  el.innerHTML = html;
}

function summaryCard(label, value, cls) {
  return '<div class="summary-card"><div class="summary-value '+(cls||'sv-primary')+'">'+value+'</div><div class="summary-label">'+esc(label)+'</div></div>';
}

// ========== Render functions (pure HTML, no fetch) ==========
function renderJobDetail(j) {
  const canRetry = RETRYABLE.has(j.status);
  let html = '<div class="section-label">Basic</div>'
    +'<dl class="detail-grid">'
    +'<dt>Job ID</dt><dd class="mono">'+esc(j.ingestion_job_id)+'</dd>'
    +'<dt>Command</dt><dd>'+esc(j.trigger_key||'-')+'</dd>'
    +'<dt>Source</dt><dd>'+sourceBadge(j.source)+'</dd>'
    +'<dt>Status</dt><dd>'+statusBadge(j.status)+'</dd>'
    +'<dt>Parent Job</dt><dd class="mono">'+(j.parent_job_id ? '<span class="link" onclick="showJobDetail('+jsArg(j.parent_job_id)+')">'+esc(j.parent_job_id)+'</span>' : '-')+'</dd>'
    +'<dt>Retry Of</dt><dd class="mono">'+(j.retry_of_job_id ? '<span class="link" onclick="showJobDetail('+jsArg(j.retry_of_job_id)+')">'+esc(j.retry_of_job_id)+'</span>' : '-')+'</dd>'
    +'<dt>Row Count</dt><dd>'+(j.row_count!=null?j.row_count:'-')+'</dd>'
    +'<dt>Created</dt><dd>'+esc(fmtTime(j.created_at))+'</dd>'
    +'<dt>Updated</dt><dd>'+esc(fmtTime(j.updated_at))+'</dd>'
    +'<dt>Finished</dt><dd>'+esc(fmtTime(j.finished_at))+'</dd>'
    +'</dl>'
    +'<div class="section-label">Params</div>'
    +'<pre>'+htmlJson(j.params_json)+'</pre>'
    +'<div class="section-label">Error</div>'
    +'<pre style="color:#fca5a5">'+esc(j.error||'-')+'</pre>'
    +'<div class="section-label">Producer Status</div>'
    +'<pre>'+htmlJson(j.producer_status_json)+'</pre>'
    +'<div class="section-label">Result</div>'
    +'<pre>'+htmlJson(j.result_json)+'</pre>';
  if (canRetry) {
    html += '<div style="margin-top:12px"><button class="danger" onclick="retryJob('+jsArg(j.ingestion_job_id)+','+jsArg(j.trigger_key||'')+')" title="Retry this failed/partial/cancelled job">Retry This Job</button></div>';
  }
  return html;
}

function renderFanoutDetail(data, parentJobId) {
  const run = data.fanout_run;
  const stats = data.stats;
  const items = data.items;

  let html = '<div class="section-label">Parent Summary</div>'
    +'<dl class="detail-grid">'
    +'<dt>Job ID</dt><dd class="mono">'+esc(parentJobId)+'</dd>'
    +'<dt>Child Command</dt><dd>'+esc(run.child_command||'-')+'</dd>'
    +'<dt>Run Status</dt><dd>'+statusBadge(run.status)+'</dd>'
    +'<dt>Total Items</dt><dd>'+run.total+'</dd>'
    +'<dt>Circuit Opened</dt><dd>'+(run.circuit_opened?'Yes':'No')+'</dd>'
    +'</dl>'
    +'<div class="section-label">Item Stats</div>'
    +'<div class="stats">';
  for (const [s, n] of Object.entries(stats)) {
    const cls = s==='succeeded'?'sv-success':s==='failed'?'sv-danger':s==='running'?'sv-warning':'sv-primary';
    html += '<div class="stat-card"><div class="stat-value '+cls+'">'+n+'</div><div class="stat-label">'+esc(s)+'</div></div>';
  }
  html += '</div>';

  const failedCount = (stats['failed']||0) + (stats['skipped']||0);
  const childRetryable = items.filter(i => i.child_status && RETRYABLE.has(i.child_status)).length;
  const totalRetryable = failedCount + childRetryable;
  if (totalRetryable > 0) {
    html += '<div class="section-label">Retry Failed Children</div>'
      +'<div class="card" style="margin-bottom:0">'
      +'<p style="color:var(--muted);font-size:12px;margin-bottom:8px">'+totalRetryable+' retryable items (failed/skipped items or failed/partial/cancelled child jobs).</p>'
      +'<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">'
      +'<label style="color:var(--muted);font-size:12px">Item indexes <input id="retry-item-indexes" size="30" placeholder="e.g. 322,402 or leave empty for all"></label>'
      +'<button class="danger" onclick="retryFailedChildren('+jsArg(parentJobId)+')" title="Retry failed/skipped fan-out items">Retry Failed Children</button>'
      +'</div>'
      +'<p style="color:var(--muted);font-size:11px;margin-top:6px">Copy item_index from table below. Leave empty to retry all failed/skipped items.</p>'
      +'</div>';
  }

  html += '<div class="section-label">Fan-out Items ('+items.length+')</div>'
    +'<div class="table-wrap"><table class="data-table" style="min-width:1100px"><tr><th style="width:70px">Index</th><th style="width:100px">Item Status</th><th style="width:60px">Retry#</th><th class="col-parent">Child Job</th><th class="col-source">Child Source</th><th class="col-status">Child Status</th><th class="col-retry">Retry Of</th><th>Params</th><th class="col-error">Error</th><th class="col-actions">Action</th></tr>';
  for (const i of items) {
    const cp = fmtJson(i.params_json);
    const cRetry = i.child_status && RETRYABLE.has(i.child_status);
    html += '<tr>'
      +'<td>'+i.item_index+'</td>'
      +'<td>'+statusBadge(i.status)+'</td>'
      +'<td>'+i.retry_count+'</td>'
      +'<td class="mono">'+(i.child_job_id ? '<span class="link" onclick="showJobDetail('+jsArg(i.child_job_id)+')">'+esc(shortId(i.child_job_id))+'</span>' : '-')+'</td>'
      +'<td>'+sourceBadge(i.child_source)+'</td>'
      +'<td>'+(i.child_status ? statusBadge(i.child_status) : '-')+'</td>'
      +'<td class="mono">'+(i.child_retry_of_job_id ? '<span class="link" onclick="showJobDetail('+jsArg(i.child_retry_of_job_id)+')">'+esc(shortId(i.child_retry_of_job_id))+'</span>' : '-')+'</td>'
      +'<td class="mono"><span class="text-ellipsis" title="'+esc(cp)+'">'+esc(cp.substring(0,50))+'</span></td>'
      +'<td class="error-cell">'+esc(i.error||i.child_error||'-')+'</td>'
      +'<td>'+(cRetry ? '<button class="danger" onclick="retryJob('+jsArg(i.child_job_id)+','+jsArg('')+')" title="Retry this child">Retry</button>' : '')+'</td>'
      +'</tr>';
  }
  html += '</table></div>';
  return html;
}

function renderRunDetail(run) {
  let html = '<dl class="detail-grid">'
    +'<dt>Run ID</dt><dd class="mono">'+esc(run.run_id)+'</dd>'
    +'<dt>Plan</dt><dd>'+esc(run.plan_name)+'</dd>'
    +'<dt>Source</dt><dd>'+sourceBadge(run.trigger_source)+'</dd>'
    +'<dt>Status</dt><dd>'+statusBadge(run.status)+'</dd>'
    +'<dt>Error</dt><dd class="error-cell">'+esc(run.error||'-')+'</dd>'
    +'<dt>Started</dt><dd>'+esc(fmtTime(run.started_at))+'</dd>'
    +'<dt>Finished</dt><dd>'+esc(fmtTime(run.finished_at))+'</dd>'
    +'</dl>'
    +'<div class="section-label">Steps</div>'
    +'<div class="table-wrap"><table class="data-table" style="min-width:600px"><tr><th style="width:50px">Step</th><th>Command</th><th>Status</th><th>Job ID</th><th>Error</th></tr>';
  for (const s of (run.steps||[])) {
    html += '<tr>'
      +'<td>'+s.step_order+'</td>'
      +'<td>'+esc(s.command_name)+'</td>'
      +'<td>'+statusBadge(s.status)+'</td>'
      +'<td class="mono">'+(s.job_id ? '<span class="link" onclick="showJobDetail('+jsArg(s.job_id)+')">'+esc(s.job_id)+'</span>' : '-')+'</td>'
      +'<td class="error-cell">'+esc(s.error||'-')+'</td>'
      +'</tr>';
  }
  html += '</table></div>';
  return html;
}

// ========== Detail show functions (fetch + drawer) ==========
async function showJobDetail(jobId) {
  openDrawer('Job Detail', jobId, '<p style="color:var(--muted)">Loading...</p>');
  try {
    const r = await fetch(API+'/ingestion/v1/jobs/'+encodeURIComponent(jobId), {headers});
    const data = await r.json();
    if (!r.ok) {
      const d = data.detail || data;
      openDrawer('Job Detail Error', jobId, '<div class="error-box">'+esc(d.error||'error')+' - '+esc(d.message||JSON.stringify(d))+'</div>');
      toast('Failed to load job: '+(d.error||'')+' - '+(d.message||''), 'error');
      return;
    }
    // Also load children
    let childHtml = '';
    try {
      const cr = await fetch(API+'/ingestion/v1/jobs/'+encodeURIComponent(jobId)+'/children', {headers});
      const children = await cr.json();
      if (children.total > 0) {
        childHtml = '<div class="section-label">Children ('+children.total+')</div>'
          +'<div class="table-wrap"><table class="data-table" style="min-width:800px"><tr><th>Job ID</th><th>Source</th><th>Status</th><th>Retry Of</th><th>Params</th><th>Error</th><th>Action</th></tr>';
        for (const c of children.items) {
          const cp = fmtJson(c.params_json);
          const cRetry = RETRYABLE.has(c.status);
          childHtml += '<tr>'
            +'<td class="mono"><span class="link" onclick="showJobDetail('+jsArg(c.ingestion_job_id)+')">'+esc(shortId(c.ingestion_job_id))+'</span></td>'
            +'<td>'+sourceBadge(c.source)+'</td>'
            +'<td>'+statusBadge(c.status)+'</td>'
            +'<td class="mono">'+(c.retry_of_job_id ? '<span class="link" onclick="showJobDetail('+jsArg(c.retry_of_job_id)+')">'+esc(shortId(c.retry_of_job_id))+'</span>' : '-')+'</td>'
            +'<td class="mono"><span class="text-ellipsis" title="'+esc(cp)+'">'+esc(cp.substring(0,50))+'</span></td>'
            +'<td class="error-cell">'+esc(c.error||'-')+'</td>'
            +'<td>'+(cRetry ? '<button class="danger" onclick="retryJob('+jsArg(c.ingestion_job_id)+','+jsArg(c.trigger_key||'')+')" title="Retry child">Retry</button>' : '')+'</td>'
            +'</tr>';
        }
        childHtml += '</table></div>';
      }
    } catch {}
    document.getElementById('drawer-body').innerHTML = renderJobDetail(data) + childHtml;
  } catch(e) {
    openDrawer('Job Detail Error', jobId, '<div class="error-box">'+esc(e.message)+'</div>');
    toast('Failed to load job: '+e.message, 'error');
  }
}

async function showFanoutDetail(parentJobId) {
  openDrawer('Fan-out Detail', parentJobId, '<p style="color:var(--muted)">Loading...</p>');
  try {
    const r = await fetch(API+'/ingestion/v1/jobs/'+encodeURIComponent(parentJobId)+'/fanout', {headers});
    if (!r.ok) {
      const err = await r.json();
      const detail = err.detail || err;
      if (detail.error === 'not_fanout_parent') {
        openDrawer('Not Fan-out Parent', parentJobId,
          '<p style="color:var(--warning)">This job is not a fan-out parent. No fanout_run found.</p>'
          +'<button onclick="showJobDetail('+jsArg(parentJobId)+')">View Job Detail</button>');
      } else {
        openDrawer('Fan-out Error', parentJobId, '<div class="error-box">'+esc(detail.error||'')+' - '+esc(detail.message||'unknown')+'</div>');
        toast('Failed to load fan-out: '+(detail.error||''), 'error');
      }
      return;
    }
    const data = await r.json();
    document.getElementById('drawer-body').innerHTML = renderFanoutDetail(data, parentJobId);
  } catch(e) {
    openDrawer('Fan-out Error', parentJobId, '<div class="error-box">'+esc(e.message)+'</div>');
    toast('Failed to load fan-out: '+e.message, 'error');
  }
}

async function showRunDetail(runId) {
  openDrawer('Run Detail', runId, '<p style="color:var(--muted)">Loading...</p>');
  try {
    const r = await fetch(API+'/admin/schedules/runs/'+encodeURIComponent(runId), {headers});
    const run = await r.json();
    if (!r.ok) {
      const d = run.detail || run;
      openDrawer('Run Detail Error', runId, '<div class="error-box">'+esc(d.error||'error')+' - '+esc(d.message||JSON.stringify(d))+'</div>');
      toast('Failed to load run: '+(d.error||''), 'error');
      return;
    }
    document.getElementById('drawer-body').innerHTML = renderRunDetail(run);
  } catch(e) {
    openDrawer('Run Detail Error', runId, '<div class="error-box">'+esc(e.message)+'</div>');
    toast('Failed to load run: '+e.message, 'error');
  }
}

async function retryJob(jobId, cmd) {
  confirmAction('Retry job '+jobId+'?\nCommand: '+cmd, async () => {
    try {
      const resp = await fetch(API+'/ingestion/v1/jobs/'+encodeURIComponent(jobId)+'/retry', {method:'POST', headers});
      const result = await resp.json();
      if (resp.ok) {
        toast('Retry job created: '+result.ingestion_job_id+' (retry_of: '+(result.retry_of_job_id||'-')+')', 'success');
        loadJobs();
      } else {
        const d = result.detail || result;
        toast('Error: '+(d.error||'')+' - '+(d.message||JSON.stringify(d))+(d.ingestion_job_id ? ' (job: '+d.ingestion_job_id+')' : ''), 'error');
      }
    } catch(e) { toast('Retry failed: '+e.message, 'error'); }
  });
}

// ========== Fan-out ==========
async function loadFanout() {
  const r = await fetch(API+'/ingestion/v1/jobs?limit=200', {headers});
  const data = await r.json();
  const parents = (data.items||[]).filter(j => j.parent_job_id === null && j.status !== 'triggering');

  // Summary
  const se = document.getElementById('fanout-summary');
  const counts = {total:parents.length, running:0, partial:0, failed:0, succeeded:0};
  parents.forEach(j => { if(j.status==='running') counts.running++; if(j.status==='partial') counts.partial++; if(j.status==='failed') counts.failed++; if(j.status==='succeeded') counts.succeeded++; });
  se.innerHTML = summaryCard('Parents',counts.total,'sv-primary') + summaryCard('Running',counts.running,'sv-warning') + summaryCard('Partial',counts.partial,'sv-warning') + summaryCard('Failed',counts.failed,'sv-danger') + summaryCard('Succeeded',counts.succeeded,'sv-success');

  const el = document.getElementById('fanout-list');
  let html = '<div class="table-wrap"><table class="data-table" style="min-width:800px"><tr><th>Parent Job ID</th><th>Command</th><th>Status</th><th>Source</th><th>Created</th><th>Action</th></tr>';
  for (const j of parents.slice(0, 30)) {
    html += '<tr>'
      +'<td class="mono"><span class="link text-ellipsis" title="'+esc(j.ingestion_job_id)+'" onclick="showFanoutDetail('+jsArg(j.ingestion_job_id)+')">'+esc(shortId(j.ingestion_job_id))+'</span></td>'
      +'<td><span class="text-ellipsis" title="'+esc(j.trigger_key||'')+'">'+esc(j.trigger_key||'-')+'</span></td>'
      +'<td>'+statusBadge(j.status)+'</td>'
      +'<td>'+sourceBadge(j.source)+'</td>'
      +'<td>'+esc(fmtTime(j.created_at))+'</td>'
      +'<td><button onclick="showFanoutDetail('+jsArg(j.ingestion_job_id)+')" title="View fan-out details">Details</button></td>'
      +'</tr>';
  }
  html += '</table></div>';
  el.innerHTML = html;
}

async function retryFailedChildren(parentJobId) {
  const indexesStr = document.getElementById('retry-item-indexes')?.value?.trim();
  let body = null;
  if (indexesStr) {
    const indexes = indexesStr.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
    if (indexes.length === 0) return toast('Invalid item indexes', 'error');
    body = {item_indexes: indexes};
  }
  confirmAction('Retry failed children of '+parentJobId+'?'+(body ? ' Items: '+body.item_indexes.join(',') : ' All failed items'), async () => {
    try {
      const resp = await fetch(API+'/ingestion/v1/jobs/'+encodeURIComponent(parentJobId)+'/retry-failed-children', {
        method:'POST', headers,
        body: body ? JSON.stringify(body) : undefined
      });
      const result = await resp.json();
      if (resp.ok) {
        toast('Retry submitted: '+result.submitted+' submitted, '+result.skipped+' skipped', 'success');
        showFanoutDetail(parentJobId);
      } else {
        const d = result.detail || result;
        toast('Error: '+(d.error||'')+' - '+(d.message||JSON.stringify(d)), 'error');
      }
    } catch(e) { toast('Request failed: '+e.message, 'error'); }
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
  const plansArr = plans.items||plans;
  const runsArr = runs.items||runs;

  // Summary
  const se = document.getElementById('schedule-summary');
  const pc = {total:plansArr.length, enabled:0, running:0, failed:0};
  plansArr.forEach(p => { if(p.enabled) pc.enabled++; });
  runsArr.forEach(r => { if(r.status==='running') pc.running++; if(r.status==='failed') pc.failed++; });
  se.innerHTML = summaryCard('Plans',pc.total,'sv-primary') + summaryCard('Enabled',pc.enabled,'sv-success') + summaryCard('Running Runs',pc.running,'sv-warning') + summaryCard('Failed Runs',pc.failed,'sv-danger');

  // Plans table
  const pel = document.getElementById('schedule-plans');
  let html = '<div class="table-wrap"><table class="data-table" style="min-width:700px"><tr><th>Plan</th><th>Enabled</th><th>Schedule</th><th>Next Run</th><th>Last Status</th><th>Actions</th></tr>';
  for (const p of plansArr) {
    html += '<tr>'
      +'<td><b>'+esc(p.plan_name)+'</b></td>'
      +'<td>'+(p.enabled ? '<span class="badge badge-green">enabled</span>' : '<span class="badge badge-gray">disabled</span>')+'</td>'
      +'<td>'+esc(p.schedule_type)+' '+esc(p.schedule_time||'')+'</td>'
      +'<td>'+esc(fmtTime(p.next_run_at))+'</td>'
      +'<td>'+(p.last_status ? statusBadge(p.last_status) : '-')+'</td>'
      +'<td><div class="action-stack">'
        +'<button onclick="showPlanRuns('+jsArg(p.plan_name)+')" title="View runs for this plan">Runs</button>'
        +'<button class="primary" onclick="runPlanNow('+jsArg(p.plan_name)+')" title="Trigger this plan now">Run Now</button>'
      +'</div></td></tr>';
  }
  html += '</table></div>';
  pel.innerHTML = html;

  // Runs table
  const rel = document.getElementById('schedule-runs');
  html = '<div class="table-wrap"><table class="data-table" style="min-width:700px"><tr><th>Run ID</th><th>Plan</th><th>Source</th><th>Status</th><th>Started</th><th>Finished</th><th>Action</th></tr>';
  for (const r of runsArr) {
    html += '<tr>'
      +'<td class="mono"><span class="link text-ellipsis" title="'+esc(r.run_id)+'" onclick="showRunDetail('+jsArg(r.run_id)+')">'+esc(shortId(r.run_id))+'</span></td>'
      +'<td>'+esc(r.plan_name)+'</td>'
      +'<td>'+sourceBadge(r.trigger_source)+'</td>'
      +'<td>'+statusBadge(r.status)+'</td>'
      +'<td>'+esc(fmtTime(r.started_at))+'</td>'
      +'<td>'+esc(fmtTime(r.finished_at))+'</td>'
      +'<td><button onclick="showRunDetail('+jsArg(r.run_id)+')" title="View run steps">Steps</button></td>'
      +'</tr>';
  }
  html += '</table></div>';
  rel.innerHTML = html;
}

async function runPlanNow(planName) {
  confirmAction('Run plan "'+planName+'" now?', async () => {
    try {
      const resp = await fetch(API+'/admin/schedules/plans/'+encodeURIComponent(planName)+'/run', {method:'POST', headers});
      const result = await resp.json();
      if (resp.ok) {
        toast('Run started: '+result.run_id+' (status: '+result.status+')', 'success');
        loadSchedules();
      } else {
        const d = result.detail || result;
        toast('Error: '+(d.error||'')+' - '+(d.message||JSON.stringify(d)), 'error');
      }
    } catch(e) { toast('Request failed: '+e.message, 'error'); }
  });
}

async function showPlanRuns(planName) {
  try {
    const r = await fetch(API+'/admin/schedules/runs?plan_name='+encodeURIComponent(planName)+'&limit=10', {headers});
    const runs = await r.json();
    const el = document.getElementById('schedule-runs');
    let html = '<div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">Runs for '+esc(planName)+'</h2><button onclick="loadSchedules()" title="Back to all runs">Back</button></div>'
      +'<div class="table-wrap"><table class="data-table" style="min-width:700px"><tr><th>Run ID</th><th>Source</th><th>Status</th><th>Started</th><th>Finished</th><th>Action</th></tr>';
    for (const r of (runs.items||runs)) {
      html += '<tr>'
        +'<td class="mono"><span class="link text-ellipsis" title="'+esc(r.run_id)+'" onclick="showRunDetail('+jsArg(r.run_id)+')">'+esc(shortId(r.run_id))+'</span></td>'
        +'<td>'+sourceBadge(r.trigger_source)+'</td>'
        +'<td>'+statusBadge(r.status)+'</td>'
        +'<td>'+esc(fmtTime(r.started_at))+'</td>'
        +'<td>'+esc(fmtTime(r.finished_at))+'</td>'
        +'<td><button onclick="showRunDetail('+jsArg(r.run_id)+')">Steps</button></td>'
        +'</tr>';
    }
    html += '</table></div>';
    el.innerHTML = html;
  } catch(e) { toast('Failed: '+e.message, 'error'); }
}

// ========== Tables ==========
async function loadTables() {
  const r = await fetch(API+'/schemas', {headers});
  const data = await r.json();
  const el = document.getElementById('table-stats');
  let html = '<div class="table-wrap"><table class="data-table" style="min-width:600px"><tr><th>Table</th><th>Primary Key</th><th>Write Mode</th><th>Columns</th><th>Row Count</th></tr>';
  for (const [name, spec] of Object.entries(data.tables || {})) {
    html += '<tr>'
      +'<td><b>'+esc(name)+'</b></td>'
      +'<td class="mono">'+esc((spec.primary_key||[]).join(', '))+'</td>'
      +'<td>'+esc(spec.write_mode)+'</td>'
      +'<td>'+Object.keys(spec.columns||{}).length+'</td>'
      +'<td id="rows-'+esc(name)+'">...</td>'
      +'</tr>';
  }
  html += '</table></div>';
  el.innerHTML = html;
  for (const name of Object.keys(data.tables || {})) {
    try {
      const qr = await fetch(API+'/api/v1/ops/table-stats?table='+encodeURIComponent(name), {headers});
      if (qr.ok) {
        const qd = await qr.json();
        const cell = document.getElementById('rows-'+name);
        if (cell) cell.textContent = qd.row_count+' (updated: '+fmtTime(qd.last_updated)+')';
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
