#!/usr/bin/env python3
"""Generate a self-contained HTML report from a completed kahn scenario planning project."""

import json
import sys
from html import escape
from pathlib import Path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _read_text(path: Path) -> str:
    return path.read_text().strip() if path.exists() else ""


def _rating_class(rating: str) -> str:
    return f"rating-{rating}"


def _badge_class(type_: str) -> str:
    return f"badge-{type_}"


def _impact_class(impact: str) -> str:
    mapping = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}
    return mapping.get(impact, "badge-low")


def _score_color(score: float) -> str:
    if score >= 0.7:
        return "var(--robust)"
    if score >= 0.5:
        return "var(--acceptable)"
    return "var(--fragile)"


def _narrative_to_html(text: str) -> str:
    """Convert narrative text to HTML paragraphs, preserving bold markers."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    html_parts = []
    for p in paragraphs:
        p = p.replace("\n", " ")
        # Convert **text** to <strong>text</strong>
        import re
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        # Convert — to mdash
        p = p.replace(" — ", " &mdash; ")
        p = p.replace("—", "&mdash;")
        html_parts.append(f"<p>{escape(p).replace('&amp;mdash;', '&mdash;').replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')}</p>")
    return "\n".join(html_parts)


def load_project(project_dir: Path) -> dict:
    """Load all project data into a single dict."""
    meta = _read_json(project_dir / "meta.json")

    # Forces
    forces = []
    for subdir in ["trends", "uncertainties"]:
        force_path = project_dir / "forces" / subdir
        if force_path.exists():
            for f in sorted(force_path.glob("*.json")):
                forces.append(_read_json(f))

    # Critical uncertainties
    cu_dir = project_dir / "critical_uncertainties"
    cus = []
    if cu_dir.exists():
        for f in sorted(cu_dir.glob("*.json")):
            cus.append(_read_json(f))

    # Scenarios
    scenarios = []
    sc_dir = project_dir / "scenarios"
    if sc_dir.exists():
        for d in sorted(sc_dir.iterdir()):
            if not d.is_dir():
                continue
            sc_meta = _read_json(d / "meta.json")
            sc_meta["narrative"] = _read_text(d / "narrative.md")
            if (d / "signals.json").exists():
                sc_meta["signals"] = _read_json(d / "signals.json").get("signals", [])
            else:
                sc_meta["signals"] = []
            scenarios.append(sc_meta)

    # Strategic options
    options = []
    opt_dir = project_dir / "strategic_options"
    if opt_dir.exists():
        for d in sorted(opt_dir.iterdir()):
            if not d.is_dir():
                continue
            opt_meta = _read_json(d / "meta.json")
            if (d / "performance.json").exists():
                opt_meta["performance"] = _read_json(d / "performance.json")
            options.append(opt_meta)

    # Strategy matrix & signal dashboard from output
    strategy_matrix = {}
    signal_dashboard = {}
    output_dir = project_dir / "output"
    if (output_dir / "strategy_matrix.json").exists():
        strategy_matrix = _read_json(output_dir / "strategy_matrix.json")
    if (output_dir / "signal_dashboard.json").exists():
        signal_dashboard = _read_json(output_dir / "signal_dashboard.json")

    return {
        "meta": meta,
        "forces": forces,
        "critical_uncertainties": cus,
        "scenarios": scenarios,
        "options": options,
        "strategy_matrix": strategy_matrix,
        "signal_dashboard": signal_dashboard,
    }


CSS = """\
:root {
  --bg: #fafaf9; --fg: #1a1a1a; --muted: #666666; --border: #e0e0e0;
  --ep-green: #428a5f; --accent: #428a5f; --accent-light: #f0f7f2; --card-bg: #ffffff;
  --robust: #166534; --robust-bg: #f0fdf4;
  --acceptable: #854d0e; --acceptable-bg: #fefce8;
  --fragile: #991b1b; --fragile-bg: #fef2f2;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
}
* { margin:0; padding:0; box-sizing:border-box; }
body::before { content:'\1F99C  Expected Parrot'; display:block; background:var(--ep-green); color:#fff;
  font-family:Georgia,'Times New Roman',serif; font-size:0.95rem; font-weight:600;
  padding:0.6rem 1.5rem; letter-spacing:0.02em; }
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
  background:var(--bg); color:var(--fg); line-height:1.65; font-size:16px; }
.container { max-width:960px; margin:0 auto; padding:3rem 1.5rem; }
h1,h2,h3 { font-family:Georgia,'Times New Roman',serif; }
header { text-align:center; margin-bottom:3.5rem; padding-bottom:2.5rem; border-bottom:1px solid var(--border); }
header .kicker { text-transform:uppercase; letter-spacing:0.12em; font-size:0.75rem; color:var(--accent); font-weight:600; margin-bottom:0.75rem; }
header h1 { font-size:2.25rem; font-weight:700; line-height:1.2; margin-bottom:1rem; letter-spacing:-0.02em; }
header .meta { color:var(--muted); font-size:0.9rem; }
header .meta span+span::before { content:" \\00b7 "; margin:0 0.3em; }
section { margin-bottom:3rem; }
h2 { font-size:1.35rem; font-weight:700; margin-bottom:1.25rem; letter-spacing:-0.01em; padding-bottom:0.5rem; border-bottom:1px solid var(--border); color:var(--accent); }
h3 { font-size:1.05rem; font-weight:600; margin-bottom:0.5rem; }
p { margin-bottom:1rem; }
.focal-question { background:var(--card-bg); border:1px solid var(--border); border-left:4px solid var(--accent);
  border-radius:6px; padding:1.25rem 1.5rem; font-size:1.05rem; font-style:italic; margin-bottom:2.5rem; box-shadow:var(--shadow); }
.card { background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:1.75rem; margin-bottom:1.5rem; box-shadow:var(--shadow); }

/* Forces table */
.forces-table { width:100%; border-collapse:collapse; font-size:0.88rem; margin-bottom:1.5rem; }
.forces-table th { text-align:left; padding:0.6rem 0.75rem; border-bottom:2px solid var(--accent); font-weight:600;
  font-size:0.78rem; text-transform:uppercase; letter-spacing:0.05em; color:#fff; background:var(--accent); }
.forces-table td { padding:0.55rem 0.75rem; border-bottom:1px solid var(--border); vertical-align:top; }
.forces-table tr:last-child td { border-bottom:none; }

.badge { display:inline-block; font-size:0.72rem; padding:0.15em 0.55em; border-radius:3px; font-weight:600; text-transform:uppercase; letter-spacing:0.03em; }
.badge-trend { background:#dbeafe; color:#1e40af; }
.badge-uncertainty { background:#fef3c7; color:#92400e; }
.badge-high { background:#fee2e2; color:#991b1b; }
.badge-medium { background:#fef9c3; color:#854d0e; }
.badge-low { background:#f0fdf4; color:#166534; }

/* 2x2 Matrix */
.matrix { display:grid; grid-template-columns:140px 1fr 1fr; gap:0; font-size:0.9rem; }
.col-header { text-align:center; font-weight:600; padding:0.75rem 0.5rem; font-size:0.8rem; color:var(--muted); border-bottom:2px solid var(--accent); }
.row-header { font-weight:600; font-size:0.8rem; color:var(--muted); display:flex; align-items:center; justify-content:center;
  padding:0.5rem; border-right:2px solid var(--accent); text-align:center; }
.cell { background:var(--card-bg); border:1px solid var(--border); padding:1rem; min-height:100px; }
.cell-id { font-size:0.7rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.2rem; }
.cell-name { font-weight:700; font-size:0.95rem; margin-bottom:0.25rem; color:var(--accent); }
.cell-tagline { font-size:0.82rem; color:var(--muted); line-height:1.45; }
.axis-label { text-align:center; font-size:0.85rem; font-weight:600; margin:0.5rem 0; color:var(--fg); }

/* Poles */
.poles-row { display:flex; gap:1.5rem; margin-top:0.75rem; font-size:0.88rem; }
.pole { flex:1; padding:0.75rem; border-radius:6px; }
.pole-a { background:#f0fdf4; }
.pole-b { background:#fef2f2; }
.pole strong.pa { color:var(--robust); }
.pole strong.pb { color:var(--fragile); }

/* Scenario cards */
.sc-header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.25rem; }
.sc-name { font-size:1.15rem; font-weight:700; }
.sc-id { font-size:0.75rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.05em; }
.sc-tagline { font-size:0.9rem; color:var(--accent); font-style:italic; margin-bottom:1rem; padding-bottom:0.75rem; border-bottom:1px solid var(--border); }
.axes-badge { display:inline-block; font-size:0.72rem; padding:0.2em 0.6em; border-radius:3px; background:#f5f5f4;
  color:var(--muted); margin-right:0.4em; margin-bottom:0.5em; font-weight:500; }
.narrative { font-size:0.92rem; line-height:1.7; margin:0.75rem 0 1.25rem; }
.signals-section h4 { font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--muted); margin-bottom:0.5rem; }
.signal-item { display:flex; gap:0.75rem; font-size:0.85rem; margin-bottom:0.5rem; padding:0.5rem 0.65rem; background:#f5f5f4; border-radius:4px; }
.signal-icon { flex-shrink:0; width:18px; height:18px; border-radius:50%; background:var(--accent); color:#fff;
  font-size:0.65rem; display:flex; align-items:center; justify-content:center; margin-top:2px; font-weight:700; }
.signal-where { font-size:0.78rem; color:var(--muted); margin-top:0.15rem; }

/* Strategy table */
.strategy-table { width:100%; border-collapse:collapse; font-size:0.85rem; margin:1.25rem 0; }
.strategy-table th { padding:0.6rem 0.65rem; border-bottom:2px solid var(--accent); font-weight:600; font-size:0.75rem;
  text-transform:uppercase; letter-spacing:0.04em; color:#fff; background:var(--accent); text-align:center; }
.strategy-table th:first-child { text-align:left; }
.strategy-table td { padding:0.55rem 0.65rem; border-bottom:1px solid var(--border); text-align:center; vertical-align:top; }
.strategy-table td:first-child { text-align:left; font-weight:600; }
.strategy-table tr:last-child td { border-bottom:none; }
.rating { display:inline-block; font-size:0.75rem; padding:0.2em 0.6em; border-radius:4px; font-weight:600; }
.rating-robust { background:var(--robust-bg); color:var(--robust); }
.rating-acceptable { background:var(--acceptable-bg); color:var(--acceptable); }
.rating-fragile { background:var(--fragile-bg); color:var(--fragile); }
.score-bar-wrapper { display:flex; align-items:center; gap:0.5rem; }
.score-bar { flex:1; height:8px; background:#e7e5e4; border-radius:4px; overflow:hidden; }
.score-bar-fill { height:100%; border-radius:4px; }
.score-value { font-size:0.85rem; font-weight:700; min-width:2.5em; text-align:right; }

/* Option detail */
.opt-header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.35rem; }
.opt-name { font-weight:700; font-size:1rem; }
.opt-score { font-weight:700; font-size:0.9rem; }
.opt-desc { font-size:0.88rem; color:var(--muted); margin-bottom:0.75rem; }
.eval-row { display:flex; gap:0.5rem; align-items:baseline; font-size:0.82rem; margin-bottom:0.35rem;
  padding:0.35rem 0.5rem; border-radius:4px; background:#fafaf9; }
.eval-scenario { font-weight:600; min-width:160px; flex-shrink:0; }
.eval-rationale { color:var(--muted); flex:1; }

/* Recommendations */
.rec-card { background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:1.25rem 1.5rem; margin-bottom:1rem; box-shadow:var(--shadow); }
.rec-card.core { border-left:4px solid var(--robust); }
.rec-card.hedge { border-left:4px solid var(--acceptable); }
.rec-card.avoid { border-left:4px solid var(--fragile); opacity:0.8; }
.rec-label { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.25rem; }
.rec-card.core .rec-label { color:var(--robust); }
.rec-card.hedge .rec-label { color:var(--acceptable); }
.rec-card.avoid .rec-label { color:var(--fragile); }
.rec-name { font-size:1.05rem; font-weight:700; margin-bottom:0.35rem; }
.rec-desc { font-size:0.88rem; color:var(--muted); line-height:1.55; }

footer { margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--border); font-size:0.8rem; color:var(--muted); text-align:center; }

@media (max-width:700px) {
  .matrix { grid-template-columns:80px 1fr 1fr; font-size:0.78rem; }
  .cell { padding:0.6rem; }
  header h1 { font-size:1.6rem; }
  .eval-row { flex-direction:column; }
  .eval-scenario { min-width:auto; }
  .poles-row { flex-direction:column; }
}
"""


def render_forces_table(forces: list[dict]) -> str:
    rows = []
    for f in forces:
        type_ = f.get("type", "trend")
        impact = f.get("impact", "medium")
        rows.append(
            f'<tr><td>{escape(f.get("name", ""))}</td>'
            f'<td>{escape(f.get("domain", "").capitalize())}</td>'
            f'<td><span class="badge {_badge_class(type_)}">{escape(type_.capitalize())}</span></td>'
            f'<td><span class="badge {_impact_class(impact)}">{escape(impact.capitalize())}</span></td></tr>'
        )
    return (
        '<table class="forces-table"><thead><tr><th>Force</th><th>Domain</th><th>Type</th><th>Impact</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def render_cu_section(cus: list[dict]) -> str:
    parts = []
    for cu in cus:
        name = escape(cu.get("name", cu.get("id", "")))
        pole_a = escape(cu.get("pole_a", "Pole A"))
        pole_b = escape(cu.get("pole_b", "Pole B"))
        parts.append(
            f'<div class="card"><h3>{name}</h3>'
            f'<div class="poles-row">'
            f'<div class="pole pole-a"><strong class="pa">Pole A:</strong> {pole_a}</div>'
            f'<div class="pole pole-b"><strong class="pb">Pole B:</strong> {pole_b}</div>'
            f'</div></div>'
        )
    return "\n".join(parts)


def render_matrix(scenarios: list[dict]) -> str:
    """Build the 2x2 grid. Assumes sc001..sc004 in standard axis order."""
    sc_map = {s["id"]: s for s in scenarios}

    def _cell(sc_id: str) -> str:
        s = sc_map.get(sc_id, {})
        return (
            f'<div class="cell"><div class="cell-id">{escape(sc_id.upper())}</div>'
            f'<div class="cell-name">{escape(s.get("name", ""))}</div>'
            f'<div class="cell-tagline">{escape(s.get("tagline", ""))}</div></div>'
        )

    # sc001 = pole_a x pole_a (top-left), sc003 = pole_b x pole_a (top-right)
    # sc002 = pole_a x pole_b (bottom-left), sc004 = pole_b x pole_b (bottom-right)
    return (
        '<div class="axis-label">University-Anchored Research</div>'
        '<div class="matrix">'
        '<div></div><div class="col-header">AI as Amplifier</div><div class="col-header">AI as Equalizer</div>'
        '<div class="row-header">University-<br>Anchored<br>Research</div>'
        f'{_cell("sc001")}{_cell("sc003")}'
        '<div class="row-header">Industry-Led<br>Research</div>'
        f'{_cell("sc002")}{_cell("sc004")}'
        '</div>'
        '<div class="axis-label">Industry-Led Research</div>'
    )


def render_scenario_card(sc: dict) -> str:
    sc_id = sc.get("id", "")
    name = escape(sc.get("name", ""))
    tagline = escape(sc.get("tagline", ""))
    narrative_html = _narrative_to_html(sc.get("narrative", ""))

    axis = sc.get("axis", {})
    axis_labels = []
    for cu_id, pole in axis.items():
        axis_labels.append(f'<span class="axes-badge">{escape(cu_id)}: {escape(pole)}</span>')

    signals_html = ""
    signals = sc.get("signals", [])
    if signals:
        items = []
        for i, sig in enumerate(signals, 1):
            desc = escape(sig.get("description", ""))
            where = escape(sig.get("observable_in", ""))
            items.append(
                f'<div class="signal-item"><div class="signal-icon">{i}</div>'
                f'<div><div>{desc}</div><div class="signal-where">Watch: {where}</div></div></div>'
            )
        signals_html = f'<div class="signals-section"><h4>Early Warning Signals</h4>{"".join(items)}</div>'

    return (
        f'<div class="card">'
        f'<div class="sc-header"><span class="sc-name">{name}</span><span class="sc-id">{escape(sc_id.upper())}</span></div>'
        f'<div class="sc-tagline">{tagline}</div>'
        f'<div>{"".join(axis_labels)}</div>'
        f'<div class="narrative">{narrative_html}</div>'
        f'{signals_html}</div>'
    )


def render_strategy_table(options: list[dict], scenarios: list[dict]) -> str:
    # Sort options by robustness score descending
    sorted_opts = sorted(options, key=lambda o: o.get("performance", {}).get("robustness_score", 0), reverse=True)
    sc_ids = [s["id"] for s in scenarios]

    header_cells = "".join(f'<th>{escape(s.get("name", s["id"]))}</th>' for s in scenarios)
    header = f'<thead><tr><th style="width:200px">Option</th>{header_cells}<th style="width:90px">Score</th></tr></thead>'

    rows = []
    for opt in sorted_opts:
        perf = opt.get("performance", {})
        evals = perf.get("evaluations", {})
        score = perf.get("robustness_score", 0)
        name = escape(opt.get("name", ""))
        if opt.get("hedging_value"):
            name += ' <span class="badge" style="background:#fef3c7;color:#92400e;font-size:0.65rem;">HEDGE</span>'

        rating_cells = []
        for sc_id in sc_ids:
            rating = evals.get(sc_id, {}).get("rating", "")
            rating_cells.append(f'<td><span class="rating {_rating_class(rating)}">{escape(rating.capitalize())}</span></td>')

        score_pct = int(score * 100)
        score_color = _score_color(score)
        score_cell = (
            f'<td><div class="score-bar-wrapper">'
            f'<div class="score-bar"><div class="score-bar-fill" style="width:{score_pct}%;background:{score_color};"></div></div>'
            f'<span class="score-value">{score:.2f}</span></div></td>'
        )

        rows.append(f'<tr><td>{name}</td>{"".join(rating_cells)}{score_cell}</tr>')

    return f'<table class="strategy-table">{header}<tbody>{"".join(rows)}</tbody></table>'


def render_option_details(options: list[dict], scenarios: list[dict]) -> str:
    sc_map = {s["id"]: s.get("name", s["id"]) for s in scenarios}
    sorted_opts = sorted(options, key=lambda o: o.get("performance", {}).get("robustness_score", 0), reverse=True)
    parts = []
    for opt in sorted_opts:
        perf = opt.get("performance", {})
        evals = perf.get("evaluations", {})
        score = perf.get("robustness_score", 0)
        name = escape(opt.get("name", ""))
        desc = escape(opt.get("description", ""))
        hedging = opt.get("hedging_value", False)
        name_display = name
        if hedging:
            name_display += ' <span class="badge" style="background:#fef3c7;color:#92400e;font-size:0.65rem;">HEDGE</span>'

        eval_rows = []
        for sc_id, sc_name in sc_map.items():
            ev = evals.get(sc_id, {})
            rating = ev.get("rating", "")
            rationale = escape(ev.get("rationale", ""))
            eval_rows.append(
                f'<div class="eval-row"><span class="eval-scenario">{escape(sc_name)}</span>'
                f'<span class="rating {_rating_class(rating)}" style="margin-right:0.5rem">{escape(rating.capitalize())}</span>'
                f'<span class="eval-rationale">{rationale}</span></div>'
            )

        parts.append(
            f'<div class="card"><div class="opt-header"><span class="opt-name">{name_display}</span>'
            f'<span class="opt-score" style="color:{_score_color(score)}">{score:.2f}</span></div>'
            f'<div class="opt-desc">{desc}</div>'
            f'{"".join(eval_rows)}</div>'
        )
    return "\n".join(parts)


def render_recommendations(options: list[dict]) -> str:
    sorted_opts = sorted(options, key=lambda o: o.get("performance", {}).get("robustness_score", 0), reverse=True)
    parts = []
    for opt in sorted_opts:
        perf = opt.get("performance", {})
        score = perf.get("robustness_score", 0)
        hedging = opt.get("hedging_value", False)
        name = escape(opt.get("name", ""))
        desc = escape(opt.get("description", ""))

        # Determine card class and label
        has_fragile = any(e.get("rating") == "fragile" for e in perf.get("evaluations", {}).values())
        if hedging:
            cls, label = "hedge", "Hedging Strategy"
        elif score >= 0.7 and not has_fragile:
            cls, label = "core", "Core Strategy"
        elif score < 0.5 or has_fragile:
            cls, label = "avoid", "Caution: Fragile in some scenarios"
        else:
            cls, label = "core", "Supporting Strategy"

        parts.append(
            f'<div class="rec-card {cls}"><div class="rec-label">{label}</div>'
            f'<div class="rec-name">{name}</div>'
            f'<div class="rec-desc">{desc}</div></div>'
        )
    return "\n".join(parts)


def render_signal_dashboard(signal_dashboard: dict, scenarios: list[dict]) -> str:
    sc_map = {s["id"]: s.get("name", s["id"]) for s in scenarios}
    rows = []
    for sc_id, data in signal_dashboard.items():
        sc_name = sc_map.get(sc_id, sc_id)
        signals = data.get("signals", [])
        for sig in signals:
            desc = escape(sig.get("description", ""))
            where = escape(sig.get("observable_in", ""))
            rows.append(f'<tr><td>{desc}</td><td><strong>{escape(sc_name)}</strong></td><td>{where}</td></tr>')

    return (
        '<table class="forces-table"><thead><tr><th>Signal</th><th>Indicates</th><th>Where to Watch</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def generate_html(project_dir: Path) -> str:
    data = load_project(project_dir)
    meta = data["meta"]
    title = escape(meta.get("focal_question", "Scenario Planning Report"))
    domain = escape(meta.get("domain", ""))
    horizon = escape(meta.get("horizon", ""))
    created = meta.get("created_at", "")[:10]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">

<header>
  <div class="kicker">Expected Parrot · Scenario Planning</div>
  <h1>{title}</h1>
  <div class="meta">
    <span>{domain}</span>
    <span>{horizon}</span>
    <span>{created}</span>
  </div>
</header>

<div class="focal-question">{title}</div>

<section>
  <h2>Environmental Forces</h2>
  {render_forces_table(data["forces"])}
</section>

<section>
  <h2>Critical Uncertainties</h2>
  {render_cu_section(data["critical_uncertainties"])}
</section>

<section>
  <h2>The 2&times;2 Scenario Matrix</h2>
  {render_matrix(data["scenarios"])}
</section>

<section>
  <h2>Scenario Narratives</h2>
  {"".join(render_scenario_card(sc) for sc in data["scenarios"])}
</section>

<section>
  <h2>Strategic Options &times; Scenarios</h2>
  <p>Each option was evaluated as
    <span class="rating rating-robust">robust</span> (thrives),
    <span class="rating rating-acceptable">acceptable</span> (survives), or
    <span class="rating rating-fragile">fragile</span> (fails).</p>
  {render_strategy_table(data["options"], data["scenarios"])}
</section>

<section>
  <h2>Option Detail: Rationale by Scenario</h2>
  {render_option_details(data["options"], data["scenarios"])}
</section>

<section>
  <h2>Strategic Recommendations</h2>
  {render_recommendations(data["options"])}
</section>

<section>
  <h2>Signal Dashboard: What to Watch</h2>
  {render_signal_dashboard(data["signal_dashboard"], data["scenarios"])}
</section>

<footer>
  <p>Generated by <strong>Expected Parrot</strong> scenario planning &mdash; {created}</p>
  <p style="margin-top:0.25rem;">Method: Herman Kahn 2&times;2 matrix scenario planning. This exercise explores plausible futures, not predictions.</p>
</footer>

</div>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_html_report.py <project-dir> [output-path]")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"Error: {project_dir} does not exist")
        sys.exit(1)

    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else project_dir / "output" / "report.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = generate_html(project_dir)
    output_path.write_text(html)
    print(str(output_path))


if __name__ == "__main__":
    main()
