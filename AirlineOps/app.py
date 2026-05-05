import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.data_loader import load_data
from src.preprocessing import (
    clean, kpis, delay_causes_summary, carrier_performance,
    top_delayed_routes, cancellation_breakdown, airport_disruptions,
    delay_by_day, delay_by_month, MONTH_LABELS,
)

# ── Config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AirlineOps Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme constants ─────────────────────────────────────────────────────────
BLUE   = "#4e8ef7"
TEAL   = "#00c9a7"
AMBER  = "#f5a623"
RED    = "#e74c3c"
PURPLE = "#9b59b6"
NAVY   = "#1a2540"
GRAY   = "#8896b3"
BG     = "#f0f2f8"
WHITE  = "#ffffff"
DARK   = "#1a2035"

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ─── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{ background: {NAVY} !important; }}
[data-testid="stSidebar"] > div:first-child {{ background: {NAVY}; padding: 0; }}

.sb-brand {{
    padding: 22px 20px 18px;
    font-size: 16px; font-weight: 700; color: white; letter-spacing: -0.2px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 14px;
}}
.sb-brand em {{ color: {BLUE}; font-style: normal; }}
.sb-section {{
    padding: 12px 20px 4px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.3px;
    text-transform: uppercase; color: rgba(200,218,240,0.75);
}}

[data-testid="stSidebar"] [role="radiogroup"] {{ gap: 2px; padding: 0 8px; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{
    padding: 9px 14px !important; border-radius: 8px !important;
    color: #a8bdd8 !important; font-size: 14px !important; width: 100%; cursor: pointer !important;
}}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.07) !important; color: white !important;
}}
[data-testid="stSidebar"] [aria-checked="true"] {{
    background: rgba(78,142,247,0.22) !important; color: white !important; font-weight: 500 !important;
}}
[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stMarkdownContainer"] p {{
    color: inherit !important; font-size: 14px !important; font-weight: inherit !important;
    text-transform: none !important; letter-spacing: normal !important; padding: 0 !important; margin: 0 !important;
}}
[data-testid="stSidebar"] label:not([role="radio"]) {{ color: #c8d8ee !important; font-size: 13px !important; font-weight: 500 !important; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.07) !important; margin: 14px 0 !important; }}

/* ─── Main ─────────────────────────────────────────────────────────────── */
.stApp {{ background: {BG}; }}
.block-container {{ padding: 1.4rem 1.8rem 3rem !important; max-width: 100% !important; }}

/* ─── KPI card: make plotly chart containers look like cards ────────────── */
[data-testid="stPlotlyChart"] > div {{
    border-radius: 14px !important;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 4px 20px rgba(0,0,0,0.04);
}}

/* ─── Page header ──────────────────────────────────────────────────────── */
.pg-title {{ font-size: 20px; font-weight: 700; color: {DARK}; margin: 0 0 2px; }}
.pg-sub {{ font-size: 13px; color: #5a6a85; margin: 0 0 20px; }}

/* ─── Ranking card ─────────────────────────────────────────────────────── */
.rank-card {{
    background: {WHITE}; border-radius: 14px; padding: 20px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 4px 20px rgba(0,0,0,0.04); height: 100%;
}}
.rank-title {{ font-size: 14px; font-weight: 600; color: {DARK}; margin-bottom: 3px; }}
.rank-sub {{ font-size: 12px; color: #5a6a85; margin-bottom: 14px; }}
.rank-row {{
    display: flex; align-items: center; padding: 8px 0;
    border-bottom: 1px solid #f0f2fa; gap: 12px;
}}
.rank-row:last-child {{ border-bottom: none; padding-bottom: 0; }}
.rank-badge {{
    width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; flex-shrink: 0;
}}
.top1 {{ background: {BLUE}; color: white; }}
.top2 {{ background: #7aa8fa; color: white; }}
.top3 {{ background: #a8c4fc; color: white; }}
.topn {{ background: #eef1fb; color: #4a5568; }}
.rank-name {{
    flex: 1; font-size: 13px; color: {DARK}; font-weight: 500;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.rank-val {{ font-size: 13px; font-weight: 600; color: {DARK}; flex-shrink: 0; }}

/* ─── Main content widget labels ("Rank by", slider, selectbox…) ──────── */
.block-container [data-testid="stWidgetLabel"] p,
.block-container [data-testid="stWidgetLabel"] span,
.block-container [data-testid="stText"] p,
.block-container label:not([data-baseweb]) {{ color: #374151 !important; font-size: 13px !important; font-weight: 500 !important; }}

/* ─── Segmented control ────────────────────────────────────────────────── */
[data-testid="stSegmentedControl"] {{
    background: #e8ecf5 !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: none !important;
}}
[data-testid="stSegmentedControl"] button {{
    background: transparent !important;
    color: #374151 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border: none !important;
    border-radius: 7px !important;
}}
[data-testid="stSegmentedControl"] button:hover {{
    background: rgba(255,255,255,0.55) !important;
    color: #1f2937 !important;
}}
[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[data-active="true"],
[data-testid="stSegmentedControl"] button[tabindex="0"] {{
    background: {WHITE} !important;
    color: {BLUE} !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}}

/* ─── Main content radio buttons ──────────────────────────────────────── */
.block-container [role="radiogroup"] label {{ color: #1f2937 !important; }}

/* ─── Hide chrome ──────────────────────────────────────────────────────── */
#MainMenu, footer {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────
raw = load_data()
df  = clean(raw)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-brand">✈️ <em>Airline</em>Ops</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-section">Navigation</div>', unsafe_allow_html=True)

    page = st.radio("", [
        "Overview", "Delay Analysis", "Carrier Performance",
        "Routes", "Airports", "Time Patterns",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="sb-section">Filters</div>', unsafe_allow_html=True)

    all_airlines = sorted(df["Airline"].dropna().astype(str).unique().tolist())
    selected_airlines = st.multiselect(
        "Airlines", options=all_airlines, default=all_airlines, placeholder="Select airlines..."
    )
    months = sorted(df["Month"].dropna().unique().tolist())
    selected_months = st.multiselect(
        "Months", options=months, default=months,
        format_func=lambda m: MONTH_LABELS.get(m, str(m)),
        placeholder="All months",
    )

    st.markdown("---")
    st.markdown(
        f'<div style="color:rgba(168,189,216,0.4);font-size:11px;padding:0 20px;line-height:1.7">'
        f'US Domestic Flights · 2019<br>Source: Kaggle</div>',
        unsafe_allow_html=True,
    )

# ── Guard ──────────────────────────────────────────────────────────────────
if not selected_airlines or not selected_months:
    st.warning("Select at least one airline and one month.")
    st.stop()

mask     = df["Airline"].astype(str).isin(selected_airlines) & df["Month"].isin(selected_months)
filtered = df[mask]

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Helpers ────────────────────────────────────────────────────────────────
_TICK = dict(size=13, color="#1f2937")
_AXIS_BASE = dict(tickfont=_TICK, title=None)


def _merge_axis(user_axis: dict) -> dict:
    """Merge user axis dict on top of _AXIS_BASE so tickfont is always set."""
    merged = {**_AXIS_BASE, **user_axis}
    if "tickfont" not in user_axis:
        merged["tickfont"] = _TICK
    return merged


def cl(**kw):
    """Merged Plotly layout dict.
    • Converts title strings → dict with dark font (never overwritten).
    • Auto-injects tickfont into every xaxis / yaxis / yaxis2 passed in kw.
    • Adds sensible axis defaults to xaxis/yaxis even when caller omits them.
    """
    # ── title string → styled dict ──────────────────────────────────────────
    if "title" in kw and isinstance(kw["title"], str):
        kw["title"] = dict(
            text=kw["title"],
            font=dict(size=15, color="#111827"),
            x=0, xanchor="left", pad=dict(l=4),
        )

    # ── auto-inject tickfont into every axis key ────────────────────────────
    for ax in ("xaxis", "yaxis", "yaxis2", "yaxis3"):
        if ax in kw:
            kw[ax] = _merge_axis(kw[ax])

    # ── base layout ─────────────────────────────────────────────────────────
    base = dict(
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(family="Inter, system-ui, sans-serif", color="#1f2937", size=13),
        margin=dict(l=10, r=10, t=48, b=10),
        hoverlabel=dict(bgcolor=WHITE, bordercolor="#d1d5db", font_size=13),
        # Default axes — overridden when caller provides their own
        xaxis=_merge_axis({}),
        yaxis=_merge_axis({}),
    )
    base.update(kw)
    return base


def no_bar():
    return dict(displayModeBar=False)


def pg(title, sub):
    st.markdown(f'<div class="pg-title">{title}</div><div class="pg-sub">{sub}</div>', unsafe_allow_html=True)


def ranking_card(title, sub, items):
    """items = list of (name_str, value_str)"""
    rows = []
    for i, (name, val) in enumerate(items, 1):
        cls = {1: "top1", 2: "top2", 3: "top3"}.get(i, "topn")
        rows.append(
            f'<div class="rank-row">'
            f'<div class="rank-badge {cls}">{i}</div>'
            f'<div class="rank-name" title="{name}">{name}</div>'
            f'<div class="rank-val">{val}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="rank-card"><div class="rank-title">{title}</div>'
        f'<div class="rank-sub">{sub}</div>{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def kpi_card(label, value_str, sub_str, spark_y, color=BLUE):
    """
    Self-contained Plotly figure acting as a KPI card with sparkline.
    h=155, t=95, b=5 → plot area = 55px → 1 paper unit = 55px
    Annotation y positions place text in the top margin area.
    """
    n   = len(spark_y)
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(n)), y=spark_y, mode="lines", fill="tozeroy",
        line=dict(color=color, width=2.5, shape="spline", smoothing=1.2),
        fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.13)",
        hoverinfo="skip",
    ))
    fig.update_layout(
        height=155,
        margin=dict(l=16, r=16, t=95, b=5),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        showlegend=False,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        annotations=[
            dict(x=0, y=2.38, xref="paper", yref="paper", xanchor="left", yanchor="middle",
                 text=f'<span style="color:#374151;font-size:13px;font-weight:600">{label}</span>',
                 showarrow=False),
            dict(x=0, y=1.90, xref="paper", yref="paper", xanchor="left", yanchor="middle",
                 text=f'<b style="color:#111827;font-size:26px;letter-spacing:-0.5px">{value_str}</b>',
                 showarrow=False),
            dict(x=0, y=1.44, xref="paper", yref="paper", xanchor="left", yanchor="middle",
                 text=f'<span style="color:#4b5563;font-size:12px">{sub_str}</span>',
                 showarrow=False),
        ],
    )
    return fig


def get_monthly(df):
    mom    = delay_by_month(df)
    ontime = df.groupby("Month")["OnTime"].mean().reset_index()
    cancel = df.groupby("Month")["Cancelled"].mean().reset_index()
    return mom.merge(ontime, on="Month").merge(cancel, on="Month")

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    stats   = kpis(filtered)
    monthly = get_monthly(filtered).sort_values("Month")

    pg("Operations Overview",
       f"{stats['total_flights']:,} flights · {len(selected_airlines)} carrier(s) · "
       f"{len(selected_months)} month(s)")

    # ── KPI cards ────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4, gap="small")
    spark_kw = dict(use_container_width=True, config=no_bar())

    with k1:
        st.plotly_chart(kpi_card(
            "Total Flights", f"{stats['total_flights']:,}",
            "2019 US Domestic",
            monthly["Flights"].tolist(), BLUE,
        ), **spark_kw)

    with k2:
        st.plotly_chart(kpi_card(
            "On-Time Rate", f"{stats['on_time_rate']:.1f}%",
            "Arrival delay ≤ 0 min",
            (monthly["OnTime"] * 100).tolist(), TEAL,
        ), **spark_kw)

    with k3:
        st.plotly_chart(kpi_card(
            "Cancellation Rate", f"{stats['cancel_rate']:.2f}%",
            "Flights cancelled",
            (monthly["Cancelled"] * 100).tolist(), AMBER,
        ), **spark_kw)

    with k4:
        st.plotly_chart(kpi_card(
            "Avg Delay (delayed)", f"{stats['avg_delay']:.0f} min",
            "When ArrDelay > 0",
            monthly["AvgDelay"].tolist(), RED,
        ), **spark_kw)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Monthly trend + Rankings ──────────────────────────────────────────────
    chart_col, rank_col = st.columns([3, 1], gap="medium")

    with chart_col:
        mon = monthly.copy()
        mon["MonthName"] = mon["Month"].map(MONTH_LABELS)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=mon["MonthName"], y=mon["AvgDelay"],
            name="Avg Arrival Delay (min)",
            marker_color=BLUE, marker_opacity=0.85,
            hovertemplate="%{x}: <b>%{y:.1f} min</b><extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=mon["MonthName"], y=mon["Flights"],
            name="Total Flights", yaxis="y2",
            line=dict(color=TEAL, width=2.5, shape="spline", smoothing=1),
            marker=dict(size=7, color=TEAL),
            hovertemplate="%{x}: <b>%{y:,} flights</b><extra></extra>",
        ))
        fig.update_layout(**cl(
            title="Monthly Avg Delay (min)  ·  Total Flights per Month",
            height=360,
            margin=dict(l=10, r=10, t=48, b=56),
            legend=dict(
                orientation="h", y=-0.18, x=0.5, xanchor="center",
                font=dict(size=13, color="#1f2937"),
                bgcolor="rgba(0,0,0,0)",
                itemsizing="constant",
            ),
            yaxis=dict(
                title=None, gridcolor="#eef0f6",
                zeroline=False, tickfont=dict(size=13, color="#374151"),
                ticksuffix=" min",
            ),
            yaxis2=dict(
                title=None, overlaying="y", side="right",
                gridcolor=None, zeroline=False,
                tickfont=dict(size=13, color="#0e9488"),
                tickformat=",",
            ),
            xaxis=dict(gridcolor="#eef0f6", tickfont=dict(size=13, color="#374151")),
        ))
        st.plotly_chart(fig, use_container_width=True, config=no_bar())

    with rank_col:
        cp   = carrier_performance(filtered)
        top7 = cp.nsmallest(7, "AvgArrDelay")
        items = [
            (r["Airline"][:22] + ("…" if len(r["Airline"]) > 22 else ""), f"{r['AvgArrDelay']:.1f} min")
            for _, r in top7.iterrows()
        ]
        ranking_card("Airline Rankings", "By avg arrival delay — lower is better", items)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Delay cause bar ───────────────────────────────────────────────────────
    causes = delay_causes_summary(filtered)
    fig2 = px.bar(
        causes, x="Cause", y="Minutes",
        color="Cause",
        color_discrete_sequence=[BLUE, TEAL, AMBER, RED, PURPLE],
        text_auto=".3s",
        title="Total Delay Minutes by Cause",
    )
    fig2.update_layout(**cl(
        showlegend=False, height=280, margin=dict(l=10, r=10, t=48, b=40),
        yaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                   tickfont=dict(size=13, color="#374151")),
        xaxis=dict(title=None, tickfont=dict(size=13, color="#1f2937")),
    ))
    fig2.update_traces(textfont=dict(size=13, color="#1f2937"))
    st.plotly_chart(fig2, use_container_width=True, config=no_bar())

# ══════════════════════════════════════════════════════════════════════════════
# DELAY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Delay Analysis":
    pg("Delay Analysis", "Breakdown of delay causes and cancellation reasons")

    causes  = delay_causes_summary(filtered)
    cancels = cancellation_breakdown(filtered)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        fig = px.pie(
            causes, names="Cause", values="Minutes",
            title="Delay Minutes by Cause",
            color_discrete_sequence=[BLUE, TEAL, AMBER, RED, PURPLE],
            hole=0.48,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          textfont=dict(size=13, color="white"))
        fig.update_layout(**cl(showlegend=False, height=360, margin=dict(l=10, r=10, t=44, b=10)))
        st.plotly_chart(fig, use_container_width=True, config=no_bar())

    with col2:
        fig2 = px.bar(
            causes, x="Minutes", y="Cause", orientation="h",
            title="Delay Minutes by Cause — Horizontal Breakdown",
            color="Cause",
            color_discrete_sequence=[BLUE, TEAL, AMBER, RED, PURPLE],
            text_auto=".3s",
        )
        fig2.update_traces(textfont=dict(size=13, color="#1f2937"))
        fig2.update_layout(**cl(
            showlegend=False, height=360, margin=dict(l=10, r=90, t=44, b=10),
            yaxis=dict(title=None, autorange="reversed",
                       tickfont=dict(size=13, color="#1f2937")),
            xaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                       tickfont=dict(size=12, color="#374151")),
        ))
        st.plotly_chart(fig2, use_container_width=True, config=no_bar())

    if not cancels.empty:
        fig3 = px.bar(
            cancels, x="Reason", y="Flights",
            title="Cancellations by Reason",
            color="Reason",
            color_discrete_sequence=[BLUE, AMBER, RED, TEAL],
            text_auto=True,
        )
        fig3.update_traces(textfont=dict(size=13, color="#1f2937"))
        fig3.update_layout(**cl(
            showlegend=False, height=280, margin=dict(l=10, r=10, t=44, b=10),
            yaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                       tickfont=dict(size=13, color="#374151")),
            xaxis=dict(title=None, tickfont=dict(size=13, color="#1f2937")),
        ))
        st.plotly_chart(fig3, use_container_width=True, config=no_bar())

# ══════════════════════════════════════════════════════════════════════════════
# CARRIER PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Carrier Performance":
    pg("Carrier Performance", "On-time rate, average delay, and cancellations by airline")

    cp   = carrier_performance(filtered)
    view = st.segmented_control("Rank by", ["On-Time Rate", "Avg Arrival Delay", "Cancellation Rate"], default="On-Time Rate") or "On-Time Rate"

    sort_map = {
        "On-Time Rate":      ("OnTimeRate",       False, "RdYlGn",   "%"),
        "Avg Arrival Delay": ("AvgArrDelay",       True,  "RdYlGn_r", " min"),
        "Cancellation Rate": ("CancellationRate",  True,  "RdYlGn_r", "%"),
    }
    col, asc, cscale, unit = sort_map[view]
    cp_sorted = cp.sort_values(col, ascending=asc)

    fig = px.bar(
        cp_sorted, x=col, y="Airline", orientation="h",
        color=col, color_continuous_scale=cscale,
        text=col, title=f"Carriers by {view}",
    )
    fig.update_traces(texttemplate=f"%{{x:.1f}}{unit}", textposition="outside",
                      textfont=dict(size=13, color="#1f2937"))
    fig.update_layout(**cl(
        coloraxis_showscale=False, showlegend=False,
        height=max(340, len(cp_sorted) * 42),
        margin=dict(l=10, r=90, t=44, b=10),
        yaxis=dict(title=None, tickfont=dict(size=13, color="#1f2937")),
        xaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                   tickfont=dict(size=13, color="#374151")),
    ))
    st.plotly_chart(fig, use_container_width=True, config=no_bar())

    st.dataframe(
        cp.rename(columns={
            "OnTimeRate": "On-Time %", "AvgArrDelay": "Avg Delay (min)", "CancellationRate": "Cancel %",
        })[["Airline", "Flights", "On-Time %", "Avg Delay (min)", "Cancel %"]]
        .sort_values("On-Time %", ascending=False),
        use_container_width=True, hide_index=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Routes":
    pg("Route Analysis", "Most disruption-prone city-pair routes (min. 50 flights)")

    n_routes = st.slider("Top N routes", 10, 50, 20, 5)
    routes   = top_delayed_routes(filtered, n=n_routes)

    fig = px.bar(
        routes, x="AvgDelay", y="Route", orientation="h",
        color="AvgDelay",
        color_continuous_scale=["#fde8e8", RED],
        text_auto=".1f",
        title=f"Top {n_routes} Routes by Avg Arrival Delay",
        hover_data={"Flights": True, "CancellationRate": True},
    )
    fig.update_traces(textfont=dict(size=13, color="#1f2937"))
    fig.update_layout(**cl(
        coloraxis_showscale=False,
        height=max(380, n_routes * 30),
        margin=dict(l=10, r=60, t=44, b=10),
        yaxis=dict(title=None, autorange="reversed",
                   tickfont=dict(size=12, color="#1f2937")),
        xaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                   tickfont=dict(size=13, color="#374151"),
                   ticksuffix=" min"),
    ))
    st.plotly_chart(fig, use_container_width=True, config=no_bar())

    st.dataframe(
        routes.rename(columns={"AvgDelay": "Avg Delay (min)", "CancellationRate": "Cancel %"}),
        use_container_width=True, hide_index=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# AIRPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Airports":
    pg("Airport Disruptions", "Departure airports ranked by average departure delay (min. 100 flights)")

    airports = airport_disruptions(filtered, n=20)

    fig = px.bar(
        airports, x="AvgDepDelay", y="Org_Airport", orientation="h",
        color="AvgDepDelay",
        color_continuous_scale=["#fff3e0", AMBER],
        text_auto=".1f",
        title="Top 20 Airports by Avg Departure Delay",
        hover_data={"Origin": True, "Flights": True, "CancellationRate": True},
    )
    fig.update_traces(textfont=dict(size=13, color="#1f2937"))
    fig.update_layout(**cl(
        coloraxis_showscale=False, height=600,
        margin=dict(l=10, r=60, t=44, b=10),
        yaxis=dict(title=None, autorange="reversed",
                   tickfont=dict(size=12, color="#1f2937")),
        xaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                   tickfont=dict(size=13, color="#374151"),
                   ticksuffix=" min"),
    ))
    st.plotly_chart(fig, use_container_width=True, config=no_bar())

    st.dataframe(
        airports.rename(columns={
            "Org_Airport": "Airport", "AvgDepDelay": "Avg Dep Delay (min)", "CancellationRate": "Cancel %",
        })[["Origin", "Airport", "Flights", "Avg Dep Delay (min)", "Cancel %"]],
        use_container_width=True, hide_index=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# TIME PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Time Patterns":
    pg("Time Patterns", "When do delays and disruptions peak?")

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        dow = delay_by_day(filtered)
        fig = px.bar(
            dow, x="Day", y="AvgDelay",
            color="AvgDelay",
            color_continuous_scale=["#e8f0fe", BLUE],
            text_auto=".1f",
            title="Avg Arrival Delay by Day of Week",
            category_orders={"Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
        )
        fig.update_traces(textfont=dict(size=13, color="#1f2937"))
        fig.update_layout(**cl(
            coloraxis_showscale=False, height=320, margin=dict(l=10, r=10, t=44, b=10),
            yaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                       tickfont=dict(size=13, color="#374151"), ticksuffix=" min"),
            xaxis=dict(title=None, tickfont=dict(size=13, color="#1f2937")),
        ))
        st.plotly_chart(fig, use_container_width=True, config=no_bar())

    with col2:
        mom = delay_by_month(filtered)
        fig2 = px.line(
            mom, x="MonthName", y="AvgDelay",
            title="Avg Arrival Delay by Month (min)", markers=True,
            category_orders={"MonthName": list(MONTH_LABELS.values())},
        )
        fig2.update_traces(line_color=RED, line_width=2.5, marker_size=7, marker_color=RED)
        fig2.update_layout(**cl(
            height=320, margin=dict(l=10, r=10, t=44, b=10),
            yaxis=dict(title=None, gridcolor="#eef0f6", zeroline=False,
                       tickfont=dict(size=13, color="#374151"), ticksuffix=" min"),
            xaxis=dict(title=None, gridcolor="#eef0f6",
                       tickfont=dict(size=13, color="#1f2937")),
        ))
        st.plotly_chart(fig2, use_container_width=True, config=no_bar())

    # Heatmap: day × month
    heat = (
        filtered.groupby(["Month", "DayOfWeek"])["ArrDelay"]
        .mean().reset_index()
    )
    heat["MonthName"] = heat["Month"].map(MONTH_LABELS)
    heat["DayName"]   = heat["DayOfWeek"].map({1:"Mon",2:"Tue",3:"Wed",4:"Thu",5:"Fri",6:"Sat",7:"Sun"})

    pivot = heat.pivot(index="DayName", columns="MonthName", values="ArrDelay")
    day_order   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    month_order = [MONTH_LABELS[m] for m in sorted(MONTH_LABELS)]
    pivot = pivot.reindex(
        index=[d for d in day_order if d in pivot.index],
        columns=[m for m in month_order if m in pivot.columns],
    )

    fig3 = px.imshow(
        pivot, color_continuous_scale="RdYlGn_r",
        title="Avg Arrival Delay Heatmap — Day × Month",
        aspect="auto", text_auto=".0f",
    )
    fig3.update_traces(textfont=dict(size=12, color="#1f2937"))
    fig3.update_layout(**cl(
        height=340, margin=dict(l=10, r=10, t=44, b=10),
        coloraxis_colorbar=dict(title="min", thickness=12, len=0.8),
        xaxis=dict(title=None, tickfont=dict(size=13, color="#1f2937")),
        yaxis=dict(title=None, tickfont=dict(size=13, color="#1f2937")),
    ))
    st.plotly_chart(fig3, use_container_width=True, config=no_bar())
