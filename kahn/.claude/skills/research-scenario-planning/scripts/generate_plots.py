#!/usr/bin/env python3
"""Generate publication-quality matplotlib figures from a kahn scenario planning project.

Produces three figures:
  1. scenario_matrix.png  — 2x2 conceptual diagram of the four scenarios
  2. force_landscape.png  — scatter of forces by impact vs predictability
  3. robustness_heatmap.png — strategy evaluation heatmap (options x scenarios)

Usage:
    python generate_plots.py <project-dir> [output-dir]

Output defaults to <project-dir>/output/plots/.
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# EP Visual Standards
# ---------------------------------------------------------------------------
EP_GREEN = "#428a5f"
EP_LIGHT_GREEN = "#5ba97a"
EP_DARK = "#1a1a1a"
EP_GRAY = "#666666"
EP_LIGHT_GRAY = "#f5f5f5"

RATING_COLORS = {
    "robust": "#166534",
    "acceptable": "#854d0e",
    "fragile": "#991b1b",
}

# Quadrant tint colors (very light, low saturation)
QUADRANT_FILLS = [
    "#e8f5e9",  # top-left  — light green
    "#e3f2fd",  # top-right — light blue
    "#fff8e1",  # bottom-left — light amber
    "#fce4ec",  # bottom-right — light rose
]

FORCE_COLORS = {
    "trend": "#3b82f6",
    "uncertainty": "#f59e0b",
}

# Matplotlib defaults
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.dpi": 200,
})

DPI = 200


# ---------------------------------------------------------------------------
# Data loading (mirrors generate_html_report.load_project)
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


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

    return {
        "meta": meta,
        "forces": forces,
        "critical_uncertainties": cus,
        "scenarios": scenarios,
        "options": options,
    }


def _truncate(text: str, max_len: int = 25) -> str:
    """Truncate text with ellipsis if it exceeds max_len."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "\u2026"


def _level_to_num(level: str) -> int:
    """Convert low/medium/high to 1/2/3."""
    mapping = {"low": 1, "medium": 2, "high": 3}
    return mapping.get(level.lower().strip(), 2)


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to (r, g, b) floats in [0, 1]."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _score_to_color(score: float) -> str:
    """Map a robustness score to a rating color."""
    if score >= 0.7:
        return RATING_COLORS["robust"]
    if score >= 0.5:
        return RATING_COLORS["acceptable"]
    return RATING_COLORS["fragile"]


def _extract_pole_short(pole_text: str) -> str:
    """Extract the short label from a pole description.

    Poles are formatted as 'Short Label: long description...'.
    Returns just the short label portion.
    """
    if ":" in pole_text:
        return pole_text.split(":")[0].strip()
    return _truncate(pole_text, 30)


def _wrap_text(text: str, width: int = 35) -> str:
    """Simple word-wrap for matplotlib text."""
    words = text.split()
    lines = []
    current = []
    length = 0
    for w in words:
        if length + len(w) + 1 > width and current:
            lines.append(" ".join(current))
            current = [w]
            length = len(w)
        else:
            current.append(w)
            length += len(w) + 1
    if current:
        lines.append(" ".join(current))
    # Limit to 3 lines to keep quadrant text compact
    if len(lines) > 3:
        lines = lines[:3]
        lines[-1] = lines[-1].rstrip() + "\u2026"
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Figure 1: Scenario Matrix (2x2 conceptual diagram)
# ---------------------------------------------------------------------------

def plot_scenario_matrix(data: dict, output_path: Path) -> None:
    """Draw a 2x2 conceptual scenario matrix with axis arrows and quadrant cards."""
    scenarios = data["scenarios"]
    cus = data["critical_uncertainties"]

    if len(scenarios) < 4 or len(cus) < 2:
        print("  Skipping scenario_matrix.png -- need 4 scenarios and 2 critical uncertainties")
        return

    cu_map = {cu["id"]: cu for cu in cus}

    # Determine axis assignments from the first scenario's axis mapping.
    # Convention: the first CU listed maps to the horizontal axis,
    # the second to the vertical axis.
    sc0_axis = scenarios[0].get("axis", {})
    cu_ids = list(sc0_axis.keys())
    cu_x = cu_map[cu_ids[0]]  # horizontal axis
    cu_y = cu_map[cu_ids[1]]  # vertical axis

    # Build a map: (pole_x, pole_y) -> scenario
    grid = {}
    for sc in scenarios:
        ax_data = sc.get("axis", {})
        px = ax_data.get(cu_ids[0], "pole_a")
        py = ax_data.get(cu_ids[1], "pole_a")
        grid[(px, py)] = sc

    # Quadrant layout:
    # top-left: pole_a x, pole_a y  |  top-right: pole_b x, pole_a y
    # bot-left: pole_a x, pole_b y  |  bot-right: pole_b x, pole_b y
    quadrant_positions = [
        ("pole_a", "pole_a", 0, 1),   # top-left
        ("pole_b", "pole_a", 1, 1),   # top-right
        ("pole_a", "pole_b", 0, 0),   # bottom-left
        ("pole_b", "pole_b", 1, 0),   # bottom-right
    ]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.22, 1.22)
    ax.set_aspect("equal")
    ax.axis("off")

    # Quadrant origins in data coordinates
    quad_w, quad_h = 0.48, 0.48
    quad_origins = {
        (0, 1): (0.01, 0.51),   # top-left
        (1, 1): (0.51, 0.51),   # top-right
        (0, 0): (0.01, 0.01),   # bottom-left
        (1, 0): (0.51, 0.01),   # bottom-right
    }

    for i, (px, py, col, row) in enumerate(quadrant_positions):
        ox, oy = quad_origins[(col, row)]
        rect = mpatches.FancyBboxPatch(
            (ox, oy), quad_w, quad_h,
            boxstyle="round,pad=0.02",
            facecolor=QUADRANT_FILLS[i],
            edgecolor="#cccccc",
            linewidth=0.8,
            zorder=1,
        )
        ax.add_patch(rect)

        sc = grid.get((px, py))
        if sc:
            cx = ox + quad_w / 2
            cy = oy + quad_h / 2
            name = sc.get("name", "")
            tagline = sc.get("tagline", "")
            wrapped = _wrap_text(tagline, 38)
            ax.text(cx, cy + 0.06, name, ha="center", va="center",
                    fontsize=10, fontweight="bold", color=EP_DARK, zorder=3)
            ax.text(cx, cy - 0.06, wrapped, ha="center", va="center",
                    fontsize=7, color=EP_GRAY, zorder=3, style="italic",
                    linespacing=1.3)

    # Axis arrows through center
    arrow_props = dict(
        arrowstyle="-|>",
        color=EP_DARK,
        linewidth=1.5,
        mutation_scale=14,
        zorder=5,
    )
    ax.annotate("", xy=(1.08, 0.5), xytext=(-0.08, 0.5),
                arrowprops=arrow_props)
    ax.annotate("", xy=(0.5, 1.10), xytext=(0.5, -0.10),
                arrowprops=arrow_props)

    # Pole labels at ends of arrows
    x_pole_a_label = _extract_pole_short(cu_x.get("pole_a", "Pole A"))
    x_pole_b_label = _extract_pole_short(cu_x.get("pole_b", "Pole B"))
    ax.text(-0.10, 0.5, x_pole_a_label, ha="right", va="center",
            fontsize=8, color=EP_DARK, fontweight="bold", zorder=6)
    ax.text(1.10, 0.5, x_pole_b_label, ha="left", va="center",
            fontsize=8, color=EP_DARK, fontweight="bold", zorder=6)

    y_pole_a_label = _extract_pole_short(cu_y.get("pole_a", "Pole A"))
    y_pole_b_label = _extract_pole_short(cu_y.get("pole_b", "Pole B"))
    ax.text(0.5, 1.14, y_pole_a_label, ha="center", va="bottom",
            fontsize=8, color=EP_DARK, fontweight="bold", zorder=6)
    ax.text(0.5, -0.14, y_pole_b_label, ha="center", va="top",
            fontsize=8, color=EP_DARK, fontweight="bold", zorder=6)

    # CU names along axes
    ax.text(0.5, -0.20, cu_x.get("name", "Uncertainty 1"),
            ha="center", va="top", fontsize=9, color=EP_GREEN, fontweight="bold")
    ax.text(-0.13, 0.5, cu_y.get("name", "Uncertainty 2"),
            ha="center", va="center", fontsize=9, color=EP_GREEN, fontweight="bold",
            rotation=90)

    plt.tight_layout(pad=0.5)
    fig.savefig(output_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {output_path}")


# ---------------------------------------------------------------------------
# Figure 2: Force Landscape (Impact vs Predictability scatter)
# ---------------------------------------------------------------------------

def plot_force_landscape(data: dict, output_path: Path) -> None:
    """Scatter plot of all forces: impact vs predictability, colored by type."""
    forces = data["forces"]
    if not forces:
        print("  Skipping force_landscape.png -- no forces found")
        return

    fig, ax = plt.subplots(figsize=(7, 5.5))

    # Collect coordinates and metadata
    xs, ys, labels, types = [], [], [], []
    for f in forces:
        impact_raw = f.get("impact_magnitude", f.get("impact", "medium"))
        pred_raw = f.get("predictability", "medium")
        xs.append(_level_to_num(pred_raw))
        ys.append(_level_to_num(impact_raw))
        types.append(f.get("type", "trend"))
        labels.append(_truncate(f.get("name", f.get("id", "")), 25))

    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)

    # Small jitter so overlapping points are visible
    rng = np.random.RandomState(42)
    xs_j = xs + rng.uniform(-0.12, 0.12, size=len(xs))
    ys_j = ys + rng.uniform(-0.12, 0.12, size=len(ys))

    # Highlight "high impact, low predictability" quadrant
    highlight = mpatches.Rectangle(
        (0.5, 2.5), 1.0, 1.0,
        linewidth=1.5, edgecolor=RATING_COLORS["fragile"],
        facecolor=RATING_COLORS["fragile"], alpha=0.07,
        linestyle="--", zorder=0,
    )
    ax.add_patch(highlight)
    ax.text(1.0, 3.42, "Critical uncertainty zone",
            ha="center", va="bottom", fontsize=7.5, color=RATING_COLORS["fragile"],
            fontstyle="italic")

    # Plot each type separately for legend
    types_arr = np.array(types)
    for ftype, color, label in [("trend", FORCE_COLORS["trend"], "Trend"),
                                 ("uncertainty", FORCE_COLORS["uncertainty"], "Uncertainty")]:
        mask = types_arr == ftype
        if mask.any():
            ax.scatter(xs_j[mask], ys_j[mask], c=color, s=80,
                       edgecolors="white", linewidths=0.5, zorder=3,
                       label=label, alpha=0.9)

    # Label each point
    try:
        from adjustText import adjust_text
        texts = [ax.text(xs_j[i], ys_j[i], labels[i], fontsize=7, color=EP_GRAY)
                 for i in range(len(labels))]
        adjust_text(texts, x=xs_j, y=ys_j, ax=ax,
                    arrowprops=dict(arrowstyle="-", color="#cccccc", lw=0.5),
                    force_text=0.5, force_points=0.3,
                    expand_text=(1.2, 1.4))
    except ImportError:
        # Manual offset: alternate above/below
        for i, lbl in enumerate(labels):
            offset_y = 12 if i % 2 == 0 else -12
            ax.annotate(lbl, (xs_j[i], ys_j[i]),
                        xytext=(6, offset_y),
                        textcoords="offset points",
                        fontsize=6.5, color=EP_GRAY,
                        arrowprops=dict(arrowstyle="-", color="#cccccc", lw=0.4))

    # Axes styling
    ax.set_xlim(0.4, 3.6)
    ax.set_ylim(0.4, 3.6)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["Low", "Medium", "High"])
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["Low", "Medium", "High"])
    ax.set_xlabel("Predictability", fontsize=10, color=EP_DARK, fontweight="bold")
    ax.set_ylabel("Impact", fontsize=10, color=EP_DARK, fontweight="bold")
    ax.set_title("Force Landscape: Impact vs Predictability",
                 fontsize=12, color=EP_DARK, fontweight="bold", pad=12)

    ax.grid(True, linestyle=":", linewidth=0.5, color="#dddddd", zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color("#cccccc")
        spine.set_linewidth(0.5)

    ax.legend(loc="upper right", framealpha=0.9, fontsize=8, edgecolor="#cccccc")

    plt.tight_layout()
    fig.savefig(output_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {output_path}")


# ---------------------------------------------------------------------------
# Figure 3: Robustness Heatmap (options x scenarios)
# ---------------------------------------------------------------------------

def plot_robustness_heatmap(data: dict, output_path: Path) -> None:
    """Heatmap of option ratings across scenarios with robustness scores."""
    options = data["options"]
    scenarios = data["scenarios"]

    if not options or not scenarios:
        print("  Skipping robustness_heatmap.png -- no options or scenarios")
        return

    # Filter to options that have performance data
    options_with_perf = [o for o in options if "performance" in o]
    if not options_with_perf:
        print("  Skipping robustness_heatmap.png -- no performance evaluations found")
        return

    # Sort by robustness score descending
    options_with_perf.sort(
        key=lambda o: o["performance"].get("robustness_score", 0), reverse=True
    )

    sc_ids = [s["id"] for s in scenarios]
    n_opts = len(options_with_perf)
    n_cols = len(sc_ids) + 1  # +1 for robustness score column

    cell_colors = {
        "robust": (*_hex_to_rgb(RATING_COLORS["robust"]), 0.3),
        "acceptable": (*_hex_to_rgb(RATING_COLORS["acceptable"]), 0.3),
        "fragile": (*_hex_to_rgb(RATING_COLORS["fragile"]), 0.3),
    }

    # Compute figure height based on number of options
    row_height = 0.55
    fig_height = max(3.0, 1.2 + n_opts * row_height)
    fig, ax = plt.subplots(figsize=(7, fig_height))

    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_opts)
    ax.invert_yaxis()
    ax.axis("off")

    # Column headers (scenario names, rotated slightly)
    for j, sc_id in enumerate(sc_ids):
        sc_name = next(
            (s.get("name", s["id"]) for s in scenarios if s["id"] == sc_id), sc_id
        )
        ax.text(j + 0.5, -0.3, _truncate(sc_name, 18), ha="center", va="bottom",
                fontsize=8, fontweight="bold", color=EP_DARK, rotation=25)

    # Score column header
    ax.text(n_cols - 0.5, -0.3, "Score", ha="center", va="bottom",
            fontsize=8, fontweight="bold", color=EP_DARK)

    # Draw each row
    for i, opt in enumerate(options_with_perf):
        perf = opt["performance"]
        evals = perf.get("evaluations", {})
        score = perf.get("robustness_score", 0)

        # Row label (option name)
        name = opt.get("name", opt.get("id", ""))
        if opt.get("hedging_value"):
            name += " (H)"
        ax.text(-0.08, i + 0.5, _truncate(name, 30), ha="right", va="center",
                fontsize=8, color=EP_DARK, fontweight="bold")

        # Rating cells for each scenario
        for j, sc_id in enumerate(sc_ids):
            rating = evals.get(sc_id, {}).get("rating", "")
            color = cell_colors.get(rating, (0.9, 0.9, 0.9, 0.3))
            text_color = RATING_COLORS.get(rating, EP_GRAY)

            rect = mpatches.FancyBboxPatch(
                (j + 0.02, i + 0.02), 0.96, 0.96,
                boxstyle="round,pad=0.02",
                facecolor=color,
                edgecolor="#e0e0e0",
                linewidth=0.5,
                zorder=1,
            )
            ax.add_patch(rect)
            ax.text(j + 0.5, i + 0.5, rating.capitalize() if rating else "",
                    ha="center", va="center", fontsize=8, color=text_color,
                    fontweight="bold", zorder=2)

        # Score cell
        score_color = _score_to_color(score)
        score_bg = (*_hex_to_rgb(score_color), 0.15)
        rect = mpatches.FancyBboxPatch(
            (n_cols - 1 + 0.02, i + 0.02), 0.96, 0.96,
            boxstyle="round,pad=0.02",
            facecolor=score_bg,
            edgecolor="#e0e0e0",
            linewidth=0.5,
            zorder=1,
        )
        ax.add_patch(rect)
        ax.text(n_cols - 1 + 0.5, i + 0.5, f"{score:.2f}",
                ha="center", va="center", fontsize=9, color=score_color,
                fontweight="bold", zorder=2)

    ax.set_title("Strategy Robustness: Options \u00d7 Scenarios",
                 fontsize=12, color=EP_DARK, fontweight="bold", pad=30, loc="center")

    plt.tight_layout(pad=1.5)
    fig.savefig(output_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_plots.py <project-dir> [output-dir]")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"Error: {project_dir} does not exist")
        sys.exit(1)

    output_dir = (
        Path(sys.argv[2]) if len(sys.argv) > 2
        else project_dir / "output" / "plots"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading project from {project_dir}")
    data = load_project(project_dir)
    print(f"  Forces: {len(data['forces'])}, "
          f"CUs: {len(data['critical_uncertainties'])}, "
          f"Scenarios: {len(data['scenarios'])}, "
          f"Options: {len(data['options'])}")

    print("\nGenerating figures...")
    plot_scenario_matrix(data, output_dir / "scenario_matrix.png")
    plot_force_landscape(data, output_dir / "force_landscape.png")
    plot_robustness_heatmap(data, output_dir / "robustness_heatmap.png")

    print(f"\nDone. Plots saved to {output_dir}")


if __name__ == "__main__":
    main()
