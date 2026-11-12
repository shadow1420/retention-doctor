import html
from typing import Dict, Any

def generate_html_audit_report(project: Any, analysis: Any) -> str:
    """
    Generates an executive, client-ready branded retention audit report
    optimized for viewing in-browser and 1-click printing to vector PDF.
    """
    hook_score = getattr(analysis, "hook_score", 70)
    hook_grade = getattr(analysis, "hook_grade", "C")
    hook_explanation = getattr(analysis, "hook_explanation", "")
    hook_issues = getattr(analysis, "hook_issues", []) or []
    hook_recs = getattr(analysis, "hook_recommendations", []) or []
    alt_hooks = getattr(analysis, "alternative_hooks", []) or []

    vocal_data = getattr(analysis, "vocal_data", {}) or {}
    visual_data = getattr(analysis, "visual_dynamics_data", {}) or {}
    safe_zone = getattr(analysis, "safe_zone_data", {}) or {}
    retention_curve = getattr(analysis, "retention_curve_data", {}) or {}
    timeline = getattr(analysis, "retention_timeline", []) or []

    title = getattr(project, "title", "Untitled Video")
    filename = getattr(project, "original_filename", "video.mp4")
    duration = getattr(project, "duration", 0.0)
    aspect_ratio = getattr(project, "aspect_ratio", "9:16")

    completion_rate = retention_curve.get("predicted_completion_rate", 65.0)
    vocal_score = vocal_data.get("vocal_energy_score", 75)
    visual_score = visual_data.get("visual_velocity_score", 80)
    safe_score = safe_zone.get("safe_zone_score", 90)

    # Format issues
    issues_html = "".join(f"<li>{html.escape(iss)}</li>" for iss in hook_issues) or "<li>No critical defects detected.</li>"
    recs_html = "".join(f"<li>{html.escape(r)}</li>" for r in hook_recs) or "<li>Follow standard editing rhythm.</li>"

    # Format alternative hooks
    alt_hooks_html = "".join(
        f"""<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:8px;">
            <div style="font-size:11px; font-weight:700; color:#7c3aed; text-transform:uppercase;">{html.escape(h.get('type','Hook'))}</div>
            <div style="font-size:13px; font-weight:600; color:#0f172a; margin:4px 0;">"{html.escape(h.get('hook',''))}"</div>
            <div style="font-size:11px; color:#64748b;">{html.escape(h.get('why_it_works',''))}</div>
        </div>""" for h in alt_hooks[:3]
    )

    # Format cohort distribution gates
    cohort_gates = (retention_curve.get("viral_potential") or {}).get("cohort_gates", [])
    cohort_rows_html = "".join(
        f"""<tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:10px; font-weight:700; color:#1e293b; font-size:12px;">{html.escape(cg.get('name','Gate'))}</td>
            <td style="padding:10px; font-size:11px; color:#64748b; font-family:monospace;">{html.escape(cg.get('sample_size',''))}</td>
            <td style="padding:10px; font-size:11px; color:#475569;">{html.escape(cg.get('pass_threshold',''))}</td>
            <td style="padding:10px; font-size:12px; font-weight:700; color:{'#16a34a' if cg.get('passed') else '#d97706'}; font-family:monospace;">{html.escape(cg.get('video_metric',''))} ({html.escape(cg.get('survival_odds',''))})</td>
            <td style="padding:10px;"><span style="padding:3px 8px; border-radius:4px; font-size:10px; font-weight:800; background:{'#ecfdf5' if cg.get('passed') else '#fffbeb'}; color:{'#16a34a' if cg.get('passed') else '#d97706'}; text-transform:uppercase;">{'GATE CLEARED' if cg.get('passed') else 'AT RISK'}</span></td>
        </tr>""" for cg in cohort_gates
    ) or """<tr><td colspan="5" style="padding:10px; text-align:center; color:#94a3b8; font-size:12px;">Standard Algorithmic Pipeline Evaluated</td></tr>"""

    # Format top friction timeline events
    timeline_html = "".join(
        f"""<tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:10px; font-weight:600; font-family:monospace; color:#475569;">{ev.get('timestamp', 0):.1f}s</td>
            <td style="padding:10px;"><span style="padding:3px 8px; border-radius:4px; font-size:11px; font-weight:700; background:#fef2f2; color:#ef4444; text-transform:uppercase;">{html.escape(ev.get('type','alert'))}</span></td>
            <td style="padding:10px; font-size:12px; color:#1e293b; font-weight:600;">{html.escape(ev.get('title',''))}</td>
            <td style="padding:10px; font-size:12px; color:#475569;">{html.escape(ev.get('actionable_fix',''))}</td>
        </tr>""" for ev in timeline[:6]
    )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>RetentionDoctor Audit — {html.escape(title)}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #0f172a;
      background: #f1f5f9;
      margin: 0;
      padding: 30px;
    }}
    .sheet {{
      max-width: 850px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.06);
      padding: 40px;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }}
    .brand {{
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.5px;
    }}
    .brand span {{ color: #7c3aed; }}
    .badge {{
      display: inline-block;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      background: #f5f3ff;
      color: #7c3aed;
      border: 1px solid #ddd6fe;
    }}
    .hero-card {{
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
      color: #ffffff;
      border-radius: 12px;
      padding: 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
    }}
    .hero-score {{
      font-size: 54px;
      font-weight: 900;
      line-height: 1;
    }}
    .hero-score span {{
      font-size: 20px;
      color: #94a3b8;
      font-weight: 500;
    }}
    .grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 30px;
    }}
    .stat-card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 16px;
      text-align: center;
    }}
    .stat-val {{
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
      margin: 6px 0;
    }}
    .stat-label {{
      font-size: 11px;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
    }}
    h3 {{
      font-size: 16px;
      font-weight: 800;
      margin: 0 0 14px 0;
      color: #0f172a;
    }}
    .section {{
      margin-bottom: 30px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    th {{
      padding: 10px;
      background: #f8fafc;
      font-size: 11px;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      border-bottom: 2px solid #e2e8f0;
    }}
    .print-btn {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #7c3aed;
      color: #ffffff;
      font-weight: 700;
      padding: 14px 24px;
      border-radius: 12px;
      border: none;
      box-shadow: 0 10px 20px rgba(124, 58, 237, 0.35);
      cursor: pointer;
      font-size: 14px;
    }}
    .print-btn:hover {{ background: #6d28d9; }}
    @media print {{
      body {{ background: #ffffff; padding: 0; }}
      .sheet {{ box-shadow: none; padding: 0; max-width: 100%; }}
      .print-btn {{ display: none; }}
    }}
  </style>
</head>
<body>

  <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>

  <div class="sheet">
    <div class="header">
      <div>
        <div class="brand">Retention<span>Doctor</span></div>
        <div style="font-size:12px; color:#64748b; margin-top:4px;">Executive Video Retention Audit & Prescription</div>
      </div>
      <div>
        <span class="badge">Audited: {html.escape(filename)}</span>
      </div>
    </div>

    <!-- Hero Card -->
    <div class="hero-card">
      <div>
        <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#c4b5fd; margin-bottom:8px;">Doctor's Diagnosis</div>
        <div style="font-size:18px; font-weight:700; margin-bottom:6px;">{html.escape(title)}</div>
        <div style="font-size:12px; color:#94a3b8; max-width:440px; line-height:1.5;">{html.escape(hook_explanation)}</div>
      </div>
      <div style="text-align:right;">
        <div class="hero-score">{hook_score}<span>/100</span></div>
        <div style="font-size:12px; font-weight:700; color:#34d399; margin-top:6px;">Grade {html.escape(hook_grade)} &bull; {completion_rate}% Predicted Completion</div>
      </div>
    </div>

    <!-- 4 Diagnostic Pillars -->
    <div class="grid-4">
      <div class="stat-card">
        <div class="stat-label">Opening Hook</div>
        <div class="stat-val" style="color:#7c3aed;">{hook_score}/100</div>
        <div style="font-size:11px; color:#64748b;">Grade {html.escape(hook_grade)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Vocal Energy</div>
        <div class="stat-val" style="color:#2563eb;">{vocal_score}/100</div>
        <div style="font-size:11px; color:#64748b;">Pitch Dynamics</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Visual Velocity</div>
        <div class="stat-val" style="color:#d97706;">{visual_score}/100</div>
        <div style="font-size:11px; color:#64748b;">Short-Form Pacing</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">UI Safe Zone</div>
        <div class="stat-val" style="color:#059669;">{safe_score}/100</div>
        <div style="font-size:11px; color:#64748b;">{aspect_ratio} Framing</div>
      </div>
    </div>

    <!-- Identified Friction & Prescribed Fixes -->
    <div class="section" style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
      <div style="background:#fff1f2; border:1px solid #ffe4e6; border-radius:10px; padding:18px;">
        <h3 style="color:#e11d48; margin-bottom:8px;">⚠️ Retention Friction Identified</h3>
        <ul style="font-size:12px; color:#4c0519; padding-left:18px; line-height:1.6; margin:0;">
          {issues_html}
        </ul>
      </div>

      <div style="background:#f0fdf4; border:1px solid #dcfce7; border-radius:10px; padding:18px;">
        <h3 style="color:#16a34a; margin-bottom:8px;">🩺 Prescribed Doctor's Fixes</h3>
        <ul style="font-size:12px; color:#14532d; padding-left:18px; line-height:1.6; margin:0;">
          {recs_html}
        </ul>
      </div>
    </div>

    <!-- 4 Algorithmic Cohort Gates -->
    <div class="section">
      <h3>📈 Algorithmic Cohort Distribution Gates (YouTube / TikTok Architecture)</h3>
      <table>
        <thead>
          <tr>
            <th>Cohort Gate</th>
            <th>Sample Pool</th>
            <th>Pass Threshold</th>
            <th>Audit Metric</th>
            <th>Gate Status</th>
          </tr>
        </thead>
        <tbody>
          {cohort_rows_html}
        </tbody>
      </table>
    </div>

    <!-- Alternative Hooks -->
    <div class="section">
      <h3>🚀 3 High-Converting Viral Alternative Hooks</h3>
      {alt_hooks_html}
    </div>

    <!-- Timeline Action Items -->
    <div class="section">
      <h3>⏱️ Timestamped Editing Action Plan</h3>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Friction Category</th>
            <th>Issue Detected</th>
            <th>Prescribed Action</th>
          </tr>
        </thead>
        <tbody>
          {timeline_html}
        </tbody>
      </table>
    </div>

    <div style="border-top:1px solid #e2e8f0; padding-top:16px; text-align:center; font-size:11px; color:#94a3b8;">
      Generated by <b>RetentionDoctor AI Engine</b> &bull; Confidential Client Audit Report
    </div>

  </div>

</body>
</html>"""
    return html_content
