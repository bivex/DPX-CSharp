"""
DPX Architecture HUD — IDE-like Observability Dashboard for C# / .NET codebases.
3-pane layout: Navigator · Findings Stream · Inspector Drawer · AI Actions.
"""

from __future__ import annotations

import html
import json
import os
from typing import Any

from pattern_detector.domain.detection import DetectionReport
from pattern_detector.domain.value_objects import (
    ConfidenceLevel,
    PatternCategory,
)
from pattern_detector.ports.outbound import ReportFormatterPort

CATEGORY_CONFIG: dict[PatternCategory, dict[str, str]] = {
    PatternCategory.TYPE_SYSTEM: {
        "name": "Type System & Records",
        "short": "Type System",
        "icon": "🔷",
        "color": "#38D9FF",
        "bg": "rgba(56, 217, 255, 0.12)",
        "border": "rgba(56, 217, 255, 0.3)",
    },
    PatternCategory.CREATIONAL: {
        "name": "Creational Patterns",
        "short": "Creational",
        "icon": "🟢",
        "color": "#35D07F",
        "bg": "rgba(53, 208, 127, 0.12)",
        "border": "rgba(53, 208, 127, 0.3)",
    },
    PatternCategory.STRUCTURAL: {
        "name": "Structural Patterns",
        "short": "Structural",
        "icon": "🟣",
        "color": "#A78BFA",
        "bg": "rgba(167, 139, 250, 0.12)",
        "border": "rgba(167, 139, 250, 0.3)",
    },
    PatternCategory.BEHAVIORAL: {
        "name": "Behavioral & Events",
        "short": "Behavioral",
        "icon": "🟠",
        "color": "#FBBF24",
        "bg": "rgba(251, 191, 36, 0.12)",
        "border": "rgba(251, 191, 36, 0.3)",
    },
    PatternCategory.ENTERPRISE: {
        "name": "Enterprise & .NET Arch",
        "short": "Enterprise",
        "icon": "🏛️",
        "color": "#9333EA",
        "bg": "rgba(147, 51, 234, 0.12)",
        "border": "rgba(147, 51, 234, 0.3)",
    },
    PatternCategory.CONCURRENCY_ASYNC: {
        "name": "Channels & Concurrency",
        "short": "Channels / TPL",
        "icon": "⚡",
        "color": "#FBBF24",
        "bg": "rgba(251, 191, 36, 0.12)",
        "border": "rgba(251, 191, 36, 0.3)",
    },
    PatternCategory.RESILIENCE: {
        "name": "Resilience & Safety Hazards",
        "short": "Resilience",
        "icon": "🔴",
        "color": "#FF5C6C",
        "bg": "rgba(255, 92, 108, 0.12)",
        "border": "rgba(255, 92, 108, 0.3)",
    },
    PatternCategory.PRINCIPLE: {
        "name": "SOLID & Clean Architecture",
        "short": "Quality",
        "icon": "⚖️",
        "color": "#FBBF24",
        "bg": "rgba(251, 191, 36, 0.12)",
        "border": "rgba(251, 191, 36, 0.3)",
    },
}

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>λ DPX Architecture HUD — {project_name} (C# / .NET)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-void: #080B10; --bg-panel: #0E131A; --bg-surface: #141A23;
            --bg-card: #18202C; --bg-card-hover: #1E2938; --border-dim: #202832;
            --border-bright: #2C3847; --text-pure: #FFFFFF; --text-main: #E6EDF3;
            --text-muted: #7D8996; --text-dim: #54606E;
            --cyan: #38D9FF; --violet: #9333EA; --amber: #FBBF24;
            --red: #FF5C6C; --green: #35D07F; --dotnet-purple: #512BD4;
            --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html, body {{ height: 100%; font-family: var(--font-ui); background: var(--bg-void); color: var(--text-main); font-size: 13.5px; line-height: 1.5; }}
        .hud-app {{ display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}

        /* ── Header ── */
        .hud-header {{ background: var(--bg-panel); border-bottom: 1px solid var(--border-dim); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; z-index: 100; }}
        .header-brand {{ display: flex; align-items: center; gap: 12px; }}
        .lambda-logo {{ width: 32px; height: 32px; background: rgba(81, 43, 212, 0.18); border: 1px solid #7D56F4; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #A78BFA; font-family: var(--font-mono); font-weight: 800; font-size: 14px; }}
        .app-title {{ font-size: 15px; font-weight: 700; color: var(--text-pure); }}
        .project-pill {{ font-family: var(--font-mono); font-size: 14px; font-weight: 700; color: var(--cyan); background: rgba(56,217,255,0.08); padding: 2px 10px; border-radius: 6px; border: 1px solid rgba(56,217,255,0.25); }}
        .engine-label {{ font-size: 11.5px; color: var(--text-muted); font-weight: 500; }}
        .header-metrics {{ display: flex; align-items: center; gap: 16px; font-size: 12.5px; color: var(--text-muted); font-family: var(--font-mono); }}
        .metric-val {{ color: var(--text-main); font-weight: 700; }}
        .header-actions {{ display: flex; align-items: center; gap: 10px; }}
        .status-badge {{ display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 700; font-family: var(--font-mono); color: var(--green); background: rgba(53,208,127,0.1); border: 1px solid rgba(53,208,127,0.25); padding: 4px 10px; border-radius: 6px; margin-right: 8px; }}
        .status-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); }}
        .hud-btn {{ background: var(--bg-surface); border: 1px solid var(--border-dim); color: var(--text-main); padding: 6px 12px; border-radius: 6px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all .15s ease; font-family: var(--font-ui); }}
        .hud-btn:hover {{ background: var(--bg-card); border-color: var(--border-bright); color: var(--text-pure); }}
        .hud-btn.primary {{ background: var(--cyan); border-color: var(--cyan); color: #04060C; font-weight: 700; }}
        .hud-btn.primary:hover {{ background: #5EE2FF; }}

        /* ── Health Strip ── */
        .health-strip {{ background: #0A0E15; border-bottom: 1px solid var(--border-dim); padding: 8px 20px; display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-family: var(--font-mono); flex-shrink: 0; }}
        .health-bar-wrap {{ display: flex; align-items: center; gap: 12px; flex-grow: 1; max-width: 650px; }}
        .health-label {{ color: var(--text-muted); font-weight: 700; font-size: 11px; letter-spacing: .5px; }}
        .health-meter {{ display: flex; height: 8px; border-radius: 4px; background: #141A23; overflow: hidden; flex-grow: 1; }}
        .health-seg {{ height: 100%; transition: width .3s; }}
        .health-seg.red {{ background: var(--red); }} .health-seg.amber {{ background: var(--amber); }}
        .health-seg.violet {{ background: var(--violet); }} .health-seg.green {{ background: var(--green); }}
        .health-badges {{ display: flex; align-items: center; gap: 14px; }}
        .health-badge {{ display: inline-flex; align-items: center; gap: 5px; color: var(--text-muted); }}

        /* ── 3-Pane Body ── */
        .hud-body {{ display: grid; grid-template-columns: 280px 1fr 420px; flex-grow: 1; overflow: hidden; height: calc(100vh - 105px); }}

        /* ── Left Nav ── */
        .nav-pane {{ background: var(--bg-panel); border-right: 1px solid var(--border-dim); display: flex; flex-direction: column; overflow-y: auto; user-select: none; }}
        .nav-section {{ padding: 16px 14px 8px 14px; border-bottom: 1px solid var(--border-dim); }}
        .nav-section-title {{ font-size: 10.5px; font-weight: 800; letter-spacing: .8px; text-transform: uppercase; color: var(--text-dim); margin-bottom: 8px; padding-left: 8px; }}
        .nav-item {{ display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; border-radius: 6px; cursor: pointer; color: var(--text-muted); font-size: 12.5px; font-weight: 500; margin-bottom: 2px; transition: all .12s; }}
        .nav-item:hover {{ background: var(--bg-surface); color: var(--text-main); }}
        .nav-item.active {{ background: var(--bg-surface); color: var(--text-pure); font-weight: 600; border-left: 3px solid var(--cyan); }}
        .nav-item-left {{ display: flex; align-items: center; gap: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .nav-item-count {{ font-family: var(--font-mono); font-size: 11px; font-weight: 700; background: var(--bg-surface); padding: 1px 6px; border-radius: 4px; color: var(--text-muted); }}

        /* ── Workspace ── */
        .workspace-pane {{ background: var(--bg-void); display: flex; flex-direction: column; overflow: hidden; border-right: 1px solid var(--border-dim); }}
        .workspace-toolbar {{ background: var(--bg-panel); border-bottom: 1px solid var(--border-dim); padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; gap: 12px; }}
        .toolbar-left {{ display: flex; align-items: center; gap: 12px; }}
        .density-toggle {{ display: flex; align-items: center; gap: 4px; font-size: 11.5px; color: var(--text-muted); }}
        .density-btn {{ background: transparent; border: 1px solid var(--border-dim); color: var(--text-muted); font-size: 11px; padding: 2px 7px; border-radius: 4px; cursor: pointer; }}
        .density-btn.active {{ background: var(--bg-surface); color: var(--cyan); border-color: var(--cyan); }}
        .search-wrap {{ position: relative; flex-grow: 1; max-width: 320px; }}
        .search-input {{ width: 100%; background: var(--bg-void); border: 1px solid var(--border-dim); border-radius: 6px; color: var(--text-pure); font-size: 12px; padding: 6px 10px 6px 28px; outline: none; font-family: var(--font-ui); }}
        .search-input:focus {{ border-color: var(--cyan); }}
        .search-icon {{ position: absolute; left: 9px; top: 50%; transform: translateY(-50%); font-size: 12px; color: var(--text-dim); }}
        .findings-stream {{ flex-grow: 1; overflow-y: auto; padding: 14px 16px; }}

        /* ── Finding Cards ── */
        .finding-row {{ background: var(--bg-panel); border: 1px solid var(--border-dim); border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; cursor: pointer; transition: all .12s; position: relative; border-left: 3px solid var(--cyan); }}
        .finding-row:hover {{ background: var(--bg-surface); border-color: var(--border-bright); transform: translateX(2px); }}
        .finding-row.active {{ background: var(--bg-surface); border-color: var(--cyan); box-shadow: 0 0 12px rgba(56,217,255,.15); }}
        .finding-row-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
        .row-id-pattern {{ display: flex; align-items: center; gap: 8px; }}
        .row-id {{ font-family: var(--font-mono); font-size: 11.5px; font-weight: 700; color: var(--text-dim); }}
        .row-pattern {{ font-family: var(--font-mono); font-size: 13.5px; font-weight: 700; color: var(--text-pure); }}
        .row-cat-pill {{ font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; font-family: var(--font-mono); }}
        .row-target {{ font-family: var(--font-mono); font-size: 12.5px; color: var(--cyan); margin-bottom: 6px; }}
        .row-summary {{ font-size: 12.5px; color: var(--text-main); margin-bottom: 8px; line-height: 1.4; }}
        .row-footer {{ display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; font-family: var(--font-mono); color: var(--text-muted); border-top: 1px solid rgba(32,40,50,.6); padding-top: 6px; }}
        .findings-stream.compact .finding-row {{ padding: 6px 12px; margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between; }}
        .findings-stream.compact .row-summary, .findings-stream.compact .row-footer {{ display: none; }}
        .findings-stream.compact .finding-row-header {{ margin-bottom: 0; gap: 12px; }}

        /* ── Hotspots ── */
        .overview-screen {{ padding: 20px; overflow-y: auto; height: 100%; display: none; }}
        .hotspots-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-top: 12px; margin-bottom: 24px; }}
        .hotspot-card {{ background: var(--bg-panel); border: 1px solid var(--border-dim); border-radius: 8px; padding: 14px; cursor: pointer; transition: all .15s; }}
        .hotspot-card:hover {{ border-color: var(--cyan); transform: translateY(-2px); }}

        /* ── Inspector ── */
        .inspector-pane {{ background: var(--bg-panel); display: flex; flex-direction: column; overflow-y: auto; padding: 18px 20px; }}
        .inspector-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; border-bottom: 1px solid var(--border-dim); padding-bottom: 12px; }}
        .inspector-id {{ font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: var(--text-dim); }}
        .inspector-pattern {{ font-family: var(--font-mono); font-size: 15px; font-weight: 800; color: var(--cyan); margin: 2px 0 6px; }}
        .field-label {{ font-size: 10.5px; font-weight: 800; letter-spacing: .7px; text-transform: uppercase; color: var(--text-dim); margin-top: 14px; margin-bottom: 4px; }}
        .inspector-target {{ font-family: var(--font-mono); font-size: 13.5px; font-weight: 700; color: var(--text-pure); background: var(--bg-surface); padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border-dim); word-break: break-all; }}
        .metrics-grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 6px; }}
        .metric-box {{ background: var(--bg-surface); border: 1px solid var(--border-dim); border-radius: 6px; padding: 8px 10px; }}
        .metric-box-val {{ font-family: var(--font-mono); font-size: 14px; font-weight: 800; margin-top: 2px; }}
        .evidence-card {{ background: var(--bg-surface); border: 1px solid var(--border-dim); border-left: 3px solid var(--cyan); border-radius: 0 6px 6px 0; padding: 8px 12px; margin-bottom: 6px; font-size: 12px; line-height: 1.45; }}
        .ai-action-btn {{ width: 100%; background: var(--bg-surface); border: 1px solid var(--border-dim); color: var(--text-main); padding: 8px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between; transition: all .15s; font-family: var(--font-ui); }}
        .ai-action-btn:hover {{ background: var(--bg-card); border-color: var(--violet); color: #C4B5FD; }}

        #toast {{ display: none; position: fixed; bottom: 24px; right: 24px; background: #141E2E; border: 1px solid var(--cyan); color: var(--cyan); padding: 12px 18px; border-radius: 8px; font-family: var(--font-mono); font-size: 12px; font-weight: 700; box-shadow: 0 10px 30px rgba(0,0,0,.6); z-index: 10000; }}
    </style>
</head>
<body>
<div class="hud-app">

  <!-- Header -->
  <header class="hud-header">
    <div class="header-brand">
      <div class="lambda-logo">C#</div>
      <div style="display:flex;align-items:center;gap:10px;">
        <span class="app-title">DPX Architecture HUD</span>
        <span class="project-pill">{project_name}</span>
        <span class="engine-label">C# / .NET Observability Engine</span>
      </div>
    </div>
    <div class="header-metrics">
      <span>📁 <span class="metric-val">{scanned_files}</span> files</span>
      <span>⏱️ <span class="metric-val">{elapsed}s</span></span>
      <span>🔷 <span class="metric-val">{total}</span> findings</span>
      <span style="color:var(--red)">🔴 <span class="metric-val" style="color:var(--red)">{violations}</span> action required</span>
    </div>
    <div class="header-actions">
      <div class="status-badge"><span class="status-dot"></span>SCAN COMPLETE</div>
      <button class="hud-btn" onclick="copyLlmPrompt()">🤖 AI Context</button>
      <button class="hud-btn primary" onclick="exportJson()">💾 Export</button>
    </div>
  </header>

  <!-- Health Strip -->
  <section class="health-strip">
    <div class="health-bar-wrap">
      <span class="health-label">ARCHITECTURE HEALTH</span>
      <div class="health-meter">
        <div class="health-seg red" style="width:{pct_red}%"></div>
        <div class="health-seg amber" style="width:{pct_amber}%"></div>
        <div class="health-seg violet" style="width:{pct_violet}%"></div>
        <div class="health-seg green" style="width:{pct_green}%"></div>
      </div>
      <span style="font-weight:800;color:var(--text-pure)">{health_score}%</span>
    </div>
    <div class="health-badges">
      <span class="health-badge"><strong style="color:var(--red)">{violations}</strong> Action</span>
      <span class="health-badge"><strong style="color:var(--amber)">{resilience_count}</strong> Hazards</span>
      <span class="health-badge"><strong style="color:var(--cyan)">{type_count}</strong> Type System</span>
      <span class="health-badge"><strong style="color:var(--green)">{clean_count}</strong> Patterns</span>
    </div>
  </section>

  <!-- 3-Pane Body -->
  <div class="hud-body">

    <!-- Left Nav -->
    <nav class="nav-pane">
      <div class="nav-section">
        <div class="nav-section-title">Views</div>
        <div class="nav-item active" id="viewNavFindings" onclick="switchView('findings')">
          <div class="nav-item-left">📋 Findings Explorer</div>
          <span class="nav-item-count">{total}</span>
        </div>
        <div class="nav-item" id="viewNavOverview" onclick="switchView('overview')">
          <div class="nav-item-left">🗺️ Module Hotspots</div>
          <span class="nav-item-count">{module_count}</span>
        </div>
      </div>

      <div class="nav-section">
        <div class="nav-section-title">Findings Filter</div>
        <div class="nav-item active" onclick="setCategoryFilter('all', this)">
          <div class="nav-item-left">◉ All Findings</div>
          <span class="nav-item-count">{total}</span>
        </div>
        <div class="nav-item" onclick="setCategoryFilter('action_required', this)">
          <div class="nav-item-left">🔴 Action Required</div>
          <span class="nav-item-count" style="color:var(--red)">{violations}</span>
        </div>
        {cat_nav_items}
      </div>

      <div class="nav-section" style="flex-grow:1">
        <div class="nav-section-title">Namespace Hotspots</div>
        {module_nav_items}
      </div>
    </nav>

    <!-- Workspace -->
    <main class="workspace-pane">
      <div class="workspace-toolbar">
        <div class="toolbar-left">
          <span style="font-weight:700;color:var(--text-pure)" id="streamTitle">FINDINGS</span>
          <span style="color:var(--text-muted);font-size:11.5px" id="streamSubtitle">({total} total)</span>
          <div class="density-toggle">
            <span>Density:</span>
            <button class="density-btn active" id="densComfortable" onclick="setDensity('comfortable')">Comfortable</button>
            <button class="density-btn" id="densCompact" onclick="setDensity('compact')">Compact</button>
          </div>
        </div>
        <div class="search-wrap">
          <span class="search-icon">🔍</span>
          <input type="text" class="search-input" id="quickSearch" placeholder="Filter by namespace, pattern, class...">
        </div>
      </div>

      <div class="findings-stream" id="findingsStream">
        {finding_rows}
      </div>

      <div class="overview-screen" id="overviewScreen">
        <h3 style="font-size:16px;font-weight:700;color:var(--text-pure);margin-bottom:6px">🗺️ C# Namespace Hotspots</h3>
        <p style="color:var(--text-muted);font-size:12.5px;margin-bottom:16px">Namespaces and modules with concentrated architectural patterns or safety hazards.</p>
        <div class="hotspots-grid">{hotspot_cards}</div>
      </div>
    </main>

    <!-- Inspector -->
    <aside class="inspector-pane" id="inspectorPane">
      <div class="inspector-header">
        <div>
          <div class="inspector-id" id="inspId">#1</div>
          <div class="inspector-pattern" id="inspPattern">cqrs_mediatr_handler</div>
          <span class="row-cat-pill" id="inspCatPill" style="background:rgba(147,51,234,.12);color:#A78BFA">Enterprise</span>
        </div>
      </div>

      <div class="field-label">Target Symbol</div>
      <div class="inspector-target" id="inspTarget">App.Orders.CreateOrderCommandHandler</div>

      <div class="metrics-grid-2">
        <div class="metric-box">
          <div class="field-label" style="margin-top:0">Impact</div>
          <div class="metric-box-val" id="inspImpact" style="color:var(--cyan)">HIGH</div>
        </div>
        <div class="metric-box">
          <div class="field-label" style="margin-top:0">Confidence</div>
          <div class="metric-box-val" id="inspConf" style="color:var(--green)">90% [VERY HIGH]</div>
        </div>
      </div>

      <div class="field-label">Architectural Summary</div>
      <p style="font-size:13px;line-height:1.5;color:var(--text-main)" id="inspSummary">Select a finding to inspect.</p>

      <div class="field-label">Evidence Trail</div>
      <div id="inspEvidences"></div>

      <div class="field-label">Source Location</div>
      <div style="display:flex;justify-content:space-between;align-items:center;background:var(--bg-surface);padding:8px 10px;border-radius:6px;border:1px solid var(--border-dim);font-family:var(--font-mono);font-size:11.5px;color:var(--cyan)">
        <span id="inspLocation">—</span>
      </div>

      <div class="field-label">AI Architect Actions</div>
      <button class="ai-action-btn" onclick="copyAiAction('review')"><span>💡 Generate C# Architectural Review</span><span>→</span></button>
      <button class="ai-action-btn" onclick="copyAiAction('refactor')"><span>🛠️ Suggest Modern C# 12 Refactoring</span><span>→</span></button>
      <button class="ai-action-btn" onclick="copyAiAction('explain')"><span>🔍 Explain Pattern & Best Practices</span><span>→</span></button>
    </aside>

  </div>
</div>

<div id="toast">✓ Copied to clipboard!</div>

<script>
const FINDINGS = {findings_json};
const LLM_PROMPT = {llm_json};
let currentIdx = FINDINGS.length > 0 ? FINDINGS[0].idx : 1;
let currentCat = 'all';
let currentMod = 'all';

function renderInspector(f) {{
  if (!f) return;
  document.getElementById('inspId').textContent = '#' + f.idx;
  document.getElementById('inspPattern').textContent = f.pattern_type;
  const pill = document.getElementById('inspCatPill');
  pill.textContent = f.category_name;
  pill.style.color = f.category_color;
  pill.style.background = f.category_bg;
  document.getElementById('inspTarget').textContent = f.target_name + ' (' + f.target_kind + ')';
  document.getElementById('inspImpact').textContent = f.impact;
  document.getElementById('inspImpact').style.color = f.impact_color;
  document.getElementById('inspConf').textContent = f.confidence_str + ' [' + f.confidence_level + ']';
  document.getElementById('inspSummary').textContent = f.summary;
  document.getElementById('inspLocation').textContent = f.location_display;
  const ec = document.getElementById('inspEvidences');
  ec.innerHTML = '';
  (f.evidences || []).forEach(ev => {{
    const d = document.createElement('div');
    d.className = 'evidence-card';
    d.style.borderLeftColor = f.category_color;
    d.innerHTML = '<strong style="color:' + f.category_color + ';font-family:var(--font-mono)">+' + Math.round(ev.weight * 100) + '% [' + ev.rule_code + ']</strong><div style="margin-top:3px;color:var(--text-main)">' + ev.description + '</div>';
    ec.appendChild(d);
  }});
}}

function selectFinding(idx) {{
  currentIdx = idx;
  document.querySelectorAll('.finding-row').forEach(r => r.classList.toggle('active', parseInt(r.dataset.idx) === idx));
  renderInspector(FINDINGS.find(x => x.idx === idx));
}}

function filterFindings() {{
  const q = document.getElementById('quickSearch').value.toLowerCase();
  let count = 0;
  document.querySelectorAll('.finding-row').forEach(row => {{
    const cat = row.dataset.category || '';
    const mod = row.dataset.module || '';
    const isAction = row.dataset.isAction === 'true';
    const matchCat = currentCat === 'all' || (currentCat === 'action_required' ? isAction : cat === currentCat);
    const matchMod = currentMod === 'all' || mod === currentMod;
    const matchQ = !q || row.textContent.toLowerCase().includes(q);
    const show = matchCat && matchMod && matchQ;
    row.style.display = show ? 'block' : 'none';
    if (show) count++;
  }});
  document.getElementById('streamSubtitle').textContent = '(' + count + ' filtered)';
}}

function setCategoryFilter(cat, elem) {{
  currentCat = cat;
  currentMod = 'all';
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  if (elem) elem.classList.add('active');
  switchView('findings');
  filterFindings();
}}

function filterByModule(mod) {{
  currentMod = mod;
  currentCat = 'all';
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  switchView('findings');
  filterFindings();
}}

function switchView(view) {{
  const fs = document.getElementById('findingsStream');
  const ov = document.getElementById('overviewScreen');
  const nf = document.getElementById('viewNavFindings');
  const no = document.getElementById('viewNavOverview');
  if (view === 'overview') {{
    fs.style.display = 'none'; ov.style.display = 'block';
    nf.classList.remove('active'); no.classList.add('active');
    document.getElementById('streamTitle').textContent = 'HOTSPOTS MATRIX';
  }} else {{
    fs.style.display = 'block'; ov.style.display = 'none';
    no.classList.remove('active'); nf.classList.add('active');
    document.getElementById('streamTitle').textContent = 'FINDINGS';
  }}
}}

function setDensity(d) {{
  const stream = document.getElementById('findingsStream');
  stream.classList.toggle('compact', d === 'compact');
  document.getElementById('densComfortable').classList.toggle('active', d === 'comfortable');
  document.getElementById('densCompact').classList.toggle('active', d === 'compact');
}}

document.getElementById('quickSearch').addEventListener('input', filterFindings);

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg || '✓ Copied!';
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 2200);
}}

function copyLlmPrompt() {{
  navigator.clipboard.writeText(LLM_PROMPT).then(() => showToast('✓ C# AI Architecture Context Copied!'));
}}

function copyAiAction(type) {{
  const f = FINDINGS.find(x => x.idx === currentIdx);
  if (!f) return;
  const prompts = {{
    review: '# 🔍 C# Architecture Review: ' + f.target_name + '\\nPattern: ' + f.pattern_type + ' (' + f.category_name + ')\\nLocation: ' + f.location_display + '\\nSummary: ' + f.summary + '\\n\\nAnalyze architectural coupling, async safety, and adherence to clean .NET architecture.',
    refactor: '# 🛠️ C# Refactoring: ' + f.target_name + '\\nIssue/Pattern: ' + f.pattern_type + '\\nSummary: ' + f.summary + '\\n\\nProvide idiomatic modern C# 12 (.NET 8/9) refactored implementation.',
    explain: '# 📚 Explain Finding: ' + f.pattern_type + '\\nTarget: ' + f.target_name + '\\nSummary: ' + f.summary + '\\n\\nExplain why this pattern or hazard matters in enterprise .NET applications.'
  }};
  navigator.clipboard.writeText(prompts[type]).then(() => showToast('✓ ' + type.toUpperCase() + ' prompt copied!'));
}}

function exportJson() {{
  const a = document.createElement('a');
  a.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(FINDINGS, null, 2));
  a.download = '{project_name}_dpx_csharp_findings.json';
  document.body.appendChild(a); a.click(); a.remove();
}}

if (FINDINGS.length > 0) renderInspector(FINDINGS[0]);
</script>
</body>
</html>
"""


class HtmlReportFormatter(ReportFormatterPort):
    """Generates C# / .NET IDE Architecture Observability HUD."""

    def format(self, report: DetectionReport) -> str:
        project_name = self._resolve_project_name(report.project_path)

        violations_count = 0
        resilience_count = 0
        type_count = 0
        clean_count = 0

        module_findings_map: dict[str, list[dict[str, Any]]] = {}
        findings_json_list: list[dict[str, Any]] = []
        finding_rows: list[str] = []

        for idx, d in enumerate(report.detections, 1):
            cfg = CATEGORY_CONFIG.get(d.pattern_category, CATEGORY_CONFIG[PatternCategory.TYPE_SYSTEM])
            raw_loc = str(d.primary_location) if d.primary_location else "N/A"
            disp_loc, _full_loc = self._format_location(raw_loc, report.project_path)

            is_action = d.pattern_category in (PatternCategory.RESILIENCE, PatternCategory.PRINCIPLE)
            if is_action:
                violations_count += 1
            if d.pattern_category == PatternCategory.RESILIENCE:
                resilience_count += 1
            elif d.pattern_category == PatternCategory.TYPE_SYSTEM:
                type_count += 1
            else:
                clean_count += 1

            impact = "CRITICAL" if is_action else "HIGH" if d.level == ConfidenceLevel.VERY_HIGH else "MEDIUM"
            impact_color = "#FF5C6C" if is_action else "#38D9FF"
            module_name = d.target_name.split(".")[0] if "." in d.target_name else d.target_name

            ev_list = [
                {
                    "rule_code": ev.rule_code,
                    "weight": ev.weight,
                    "description": ev.description,
                    "location": str(ev.location) if ev.location else "",
                }
                for ev in d.evidences
            ]

            finding_obj: dict[str, Any] = {
                "idx": idx,
                "pattern_type": d.pattern_type.value,
                "category": d.pattern_category.value,
                "category_name": cfg["name"],
                "category_color": cfg["color"],
                "category_bg": cfg["bg"],
                "target_name": d.target_name,
                "target_kind": d.target_kind,
                "summary": d.summary,
                "confidence_str": d.confidence.percentage_str,
                "confidence_level": d.level.value.upper(),
                "impact": impact,
                "impact_color": impact_color,
                "is_action": is_action,
                "location_display": disp_loc,
                "module": module_name,
                "evidences": ev_list,
            }
            findings_json_list.append(finding_obj)
            module_findings_map.setdefault(module_name, []).append(finding_obj)

            active_cls = "active" if idx == 1 else ""
            action_badge = (
                f'<span class="row-cat-pill" style="background:rgba(255,92,108,.12);color:#FF5C6C;border:1px solid rgba(255,92,108,.3)">🔴 ACTION</span>'
                if is_action
                else f'<span class="row-cat-pill" style="background:{cfg["bg"]};color:{cfg["color"]}">{cfg["icon"]} {cfg["short"]}</span>'
            )

            finding_rows.append(
                f"""
                <div class="finding-row {active_cls}" data-idx="{idx}" data-category="{d.pattern_category.value}"
                     data-module="{html.escape(module_name)}" data-is-action="{'true' if is_action else 'false'}"
                     style="border-left-color:{cfg['color']}" onclick="selectFinding({idx})">
                  <div class="finding-row-header">
                    <div class="row-id-pattern">
                      <span class="row-id">#{idx}</span>
                      <span class="row-pattern">{html.escape(d.pattern_type.value)}</span>
                    </div>
                    {action_badge}
                  </div>
                  <div class="row-target">{html.escape(d.target_name)} <span style="color:var(--text-dim);font-size:11px">({html.escape(d.target_kind)})</span></div>
                  <div class="row-summary">{html.escape(d.summary)}</div>
                  <div class="row-footer">
                    <span>📍 {html.escape(disp_loc)}</span>
                    <span style="color:{cfg['color']}">{d.confidence.percentage_str} [{d.level.value.upper()}]</span>
                  </div>
                </div>"""
            )

        # Category nav
        cat_nav_items: list[str] = []
        for cat, cfg in CATEGORY_CONFIG.items():
            cnt = report.summary_by_category.get(cat.value, 0)
            if cnt > 0:
                cat_nav_items.append(
                    f"""<div class="nav-item" onclick="setCategoryFilter('{cat.value}', this)">
                      <div class="nav-item-left">{cfg['icon']} {cfg['short']}</div>
                      <span class="nav-item-count">{cnt}</span>
                    </div>"""
                )

        # Module nav + hotspot cards
        module_nav_items: list[str] = []
        hotspot_cards: list[str] = []
        for mod, items in sorted(module_findings_map.items(), key=lambda x: len(x[1]), reverse=True):
            mod_actions = sum(1 for x in items if x["is_action"])
            dot_color = "var(--red)" if mod_actions > 0 else "var(--green)"
            module_nav_items.append(
                f"""<div class="nav-item" style="font-family:var(--font-mono);font-size:11.5px;padding:5px 8px" onclick="filterByModule('{html.escape(mod)}')">
                  <div class="nav-item-left"><span style="color:{dot_color};font-size:9px">●</span> {html.escape(mod)}</div>
                  <span class="nav-item-count">{len(items)}</span>
                </div>"""
            )
            top_tags = " ".join(
                f'<span style="font-size:10.5px;font-family:var(--font-mono);background:var(--bg-surface);padding:2px 6px;border-radius:4px;color:{x["category_color"]}">{x["pattern_type"]}</span>'
                for x in items[:3]
            )
            hotspot_cards.append(
                f"""<div class="hotspot-card" onclick="filterByModule('{html.escape(mod)}')">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span style="font-family:var(--font-mono);font-weight:700;color:var(--text-pure);font-size:13.5px">{html.escape(mod)}</span>
                    <span style="font-family:var(--font-mono);font-size:11.5px;font-weight:700;color:{dot_color}">{len(items)} signals</span>
                  </div>
                  <div style="font-size:12px;color:var(--text-muted);margin-bottom:8px">{mod_actions} action required issues.</div>
                  <div style="display:flex;gap:6px;flex-wrap:wrap">{top_tags}</div>
                </div>"""
            )

        total = report.total_detections_count or 1
        pct_red = int((violations_count / total) * 100)
        pct_amber = int((resilience_count / total) * 100)
        pct_violet = int((type_count / total) * 100)
        pct_green = max(0, 100 - pct_red - pct_amber - pct_violet)
        health_score = max(20, 100 - violations_count * 4)

        llm_prompt = self._make_llm_prompt(report, project_name)

        return _HTML_TEMPLATE.format(
            project_name=project_name,
            total=report.total_detections_count,
            violations=violations_count,
            resilience_count=resilience_count,
            type_count=type_count,
            clean_count=clean_count,
            scanned_files=report.scanned_files_count,
            elapsed=f"{report.elapsed_seconds:.3f}",
            health_score=health_score,
            pct_red=pct_red,
            pct_amber=pct_amber,
            pct_violet=pct_violet,
            pct_green=pct_green,
            module_count=len(module_findings_map),
            cat_nav_items="\n".join(cat_nav_items),
            module_nav_items="\n".join(module_nav_items),
            finding_rows="\n".join(finding_rows),
            hotspot_cards="\n".join(hotspot_cards),
            findings_json=json.dumps(findings_json_list),
            llm_json=json.dumps(llm_prompt),
        )

    def _format_location(self, loc_str: str, project_path: str) -> tuple[str, str]:
        if not loc_str or loc_str == "N/A":
            return "N/A", ""
        clean_proj = project_path.rstrip("/\\")
        if clean_proj and loc_str.startswith(clean_proj):
            rel = loc_str[len(clean_proj):].lstrip("/\\")
            return rel, loc_str
        parts = loc_str.replace("\\", "/").split("/")
        if len(parts) > 4:
            return ".../" + "/".join(parts[-3:]), loc_str
        return loc_str, loc_str

    def _resolve_project_name(self, path: str) -> str:
        if not path or path == ".":
            return "Current Project"
        return os.path.basename(path.rstrip("/\\")) or path

    def _make_llm_prompt(self, report: DetectionReport, project_name: str) -> str:
        lines = [
            f"# 🎯 DPX-CSharp: Architectural Context & Refactoring Prompt for {project_name}",
            f"- Scanned Files: {report.scanned_files_count}",
            f"- Total Detections: {report.total_detections_count}",
            "",
            "## Identified Patterns & Smells:",
        ]
        for d in report.detections:
            loc = f" in {d.primary_location}" if d.primary_location else ""
            lines.append(f"- [{d.pattern_category.value}] {d.pattern_type.value} on `{d.target_name}` ({d.confidence.percentage_str}){loc}: {d.summary}")
        lines += [
            "",
            "## Instructions for AI Architect:",
            "1. Audit CQRS handlers and MediatR pipelines for clean boundary separation.",
            "2. Eliminate all sync-over-async blocking (.Result / .Wait() / .GetAwaiter().GetResult()).",
            "3. Enforce IDisposable/IAsyncDisposable scope with `using var` declarations.",
            "4. Leverage C# 12 Primary Constructors and record struct value immutability.",
        ]
        return "\n".join(lines)
