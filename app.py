# -*- coding: utf-8 -*-
"""
Weather Intelligence Report
A professional Streamlit dashboard for daily weather data analysis.

Run with:
    streamlit run app.py
"""

import io
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Weather Intelligence Report",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM (CSS)
# ============================================================

INK = "#1D2A44"        # deep indigo-navy — headings, primary text
PAPER = "#F6F4EF"       # warm paper background
PANEL = "#FFFFFF"       # card background
LINE = "#E4E0D6"        # hairline borders
HEAT = "#C6752B"        # warm amber-clay — heat / max temperature
COLD = "#2E6E8E"        # station blue — cold / min temperature
RAIN = "#5B7A9D"        # muted rain blue
HUM = "#7A8B99"         # humidity slate
ALERT = "#B23A2E"       # brick red — extreme heat alert
MUTED = "#6B6455"       # secondary text

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

    html, body, [class*="css"]  {{
        font-family: 'IBM Plex Sans', sans-serif;
        color: {INK};
    }}

    .stApp {{
        background-color: {PAPER};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {INK};
        border-right: 1px solid {LINE};
    }}
    section[data-testid="stSidebar"] * {{
        color: #EAE6DA !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15);
    }}

    /* Streamlit's Markdown subheadings use h4–h6. Set every heading level
       explicitly so a dark Streamlit theme cannot make them disappear. */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Fraunces', serif;
        color: {INK} !important;
        font-weight: 500;
        letter-spacing: -0.01em;
    }}

    /* Keep prose readable even when the active Streamlit theme has a light
       foreground colour. Scope this to main content so the dark sidebar keeps
       its intentional light text. */
    [data-testid="stMain"] [data-testid="stMarkdownContainer"],
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stMain"] [data-testid="stCaptionContainer"] {{
        color: {INK} !important;
    }}

    .station-eyebrow {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        color: {MUTED};
        letter-spacing: 0.04em;
        margin-bottom: -0.6rem;
    }}

    .hero-title {{
        font-family: 'Fraunces', serif;
        font-size: 3rem;
        line-height: 1.05;
        color: {INK};
        margin: 0.2rem 0 0.4rem 0;
    }}

    .hero-sub {{
        color: {MUTED};
        font-size: 1.02rem;
        max-width: 620px;
        line-height: 1.5;
    }}

    .metric-card {{
        background-color: {PANEL};
        border: 1px solid {LINE};
        border-left: 4px solid var(--accent, {INK});
        border-radius: 4px;
        padding: 0.9rem 1.1rem 0.8rem 1.1rem;
        height: 100%;
    }}
    .metric-label {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: {MUTED};
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }}
    .metric-value {{
        font-family: 'Fraunces', serif;
        font-size: 1.9rem;
        color: {INK};
        margin-top: 0.15rem;
    }}
    .metric-delta {{
        font-size: 0.82rem;
        color: {MUTED};
        margin-top: 0.1rem;
    }}

    .insight-card {{
        background-color: {PANEL};
        border: 1px solid {LINE};
        border-radius: 4px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
    }}
    .insight-tag {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: {MUTED};
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}

    div[data-baseweb="tab-list"] {{
        border-bottom: 1px solid {LINE};
        gap: 1.6rem;
    }}
    button[data-baseweb="tab"] {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 500;
        color: {MUTED} !important;
    }}
    button[data-baseweb="tab"] p {{
        font-size: 0.92rem;
        color: {MUTED} !important;
    }}
    button[aria-selected="true"],
    button[aria-selected="true"] p {{
        color: {INK} !important;
    }}

    hr {{ border-color: {LINE}; }}

    .footer-note {{
        color: {MUTED};
        font-size: 0.8rem;
        border-top: 1px solid {LINE};
        padding-top: 0.8rem;
        margin-top: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(label, value, accent=INK, delta=None):
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{accent};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(tag, text):
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-tag">{tag}</div>
            <div style="margin-top:0.25rem; font-size:0.95rem; line-height:1.5;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


PLOTLY_LAYOUT = dict(
    font=dict(family="IBM Plex Sans, sans-serif", color=INK, size=13),
    plot_bgcolor=PANEL,
    paper_bgcolor=PANEL,
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(showgrid=False, linecolor=LINE, zeroline=False),
    yaxis=dict(gridcolor=LINE, zeroline=False),
)

# ============================================================
# DATA LOADING & CLEANING
# ============================================================

REQUIRED_COLS = ["Date", "Min Temperature", "Max Temperature", "Humidity"]


@st.cache_data(show_spinner=False)
def load_and_clean(file_bytes: bytes) -> tuple[pd.DataFrame, dict]:
    """Load raw CSV bytes, clean, engineer features, and return the dataframe
    plus a small report describing what was done (for transparency)."""

    raw = pd.read_csv(io.BytesIO(file_bytes))
    report = {"rows_in": len(raw), "issues": []}

    missing_required = [c for c in REQUIRED_COLS if c not in raw.columns]
    if missing_required:
        raise ValueError(
            f"The file is missing required column(s): {', '.join(missing_required)}. "
            f"Expected at least: {', '.join(REQUIRED_COLS)}."
        )

    df = raw.copy()

    # Dates
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    bad_dates = df["Date"].isna().sum()
    if bad_dates:
        report["issues"].append(f"{bad_dates} row(s) had an unreadable date and were dropped.")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

    # Numeric coercion
    numeric_cols = ["Min Temperature", "Max Temperature", "Humidity"]
    if "Rainfall" in df.columns:
        numeric_cols.append("Rainfall")

    for col in numeric_cols:
        before_na = df[col].isna().sum() if df[col].dtype != object else 0
        df[col] = pd.to_numeric(df[col], errors="coerce")
        after_na = df[col].isna().sum()
        coerced = after_na - before_na
        if coerced > 0:
            report["issues"].append(f"{coerced} non-numeric value(s) in '{col}' were coerced to blank.")

    missing_before = df[["Min Temperature", "Max Temperature", "Humidity"]].isna().sum()

    # Fix rows where Min > Max (sensor swap) by swapping them back
    swap_mask = df["Min Temperature"] > df["Max Temperature"]
    n_swapped = int(swap_mask.sum())
    if n_swapped:
        df.loc[swap_mask, ["Min Temperature", "Max Temperature"]] = df.loc[
            swap_mask, ["Max Temperature", "Min Temperature"]
        ].values
        report["issues"].append(
            f"{n_swapped} row(s) had Min Temperature greater than Max Temperature; values were swapped."
        )

    # Interpolate temperatures (gradual day-to-day change assumption)
    df[["Min Temperature", "Max Temperature"]] = df[["Min Temperature", "Max Temperature"]].interpolate(
        method="linear", limit_direction="both"
    )

    # Humidity: fill with median (robust to outliers)
    if df["Humidity"].isna().any():
        df["Humidity"] = df["Humidity"].fillna(df["Humidity"].median())

    if "Rainfall" in df.columns and df["Rainfall"].isna().any():
        df["Rainfall"] = df["Rainfall"].fillna(0.0)

    total_filled = int(missing_before.sum())
    if total_filled:
        report["issues"].append(
            f"{total_filled} missing temperature/humidity reading(s) were estimated via interpolation or median fill."
        )

    # Duplicate dates
    dup = df["Date"].duplicated().sum()
    if dup:
        report["issues"].append(f"{dup} duplicate date(s) found; kept the first occurrence.")
        df = df.drop_duplicates(subset="Date", keep="first")

    # Feature engineering
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month Name"] = df["Date"].dt.strftime("%B")
    df["Day of Week"] = df["Date"].dt.day_name()
    df["Week"] = df["Date"].dt.isocalendar().week
    df["Average Temperature"] = ((df["Min Temperature"] + df["Max Temperature"]) / 2).round(2)
    df["Temperature Range"] = (df["Max Temperature"] - df["Min Temperature"]).round(2)

    report["rows_out"] = len(df)
    return df, report


def month_order():
    return ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"]


# ============================================================
# SIDEBAR — DATA SOURCE & FILTERS
# ============================================================

st.sidebar.markdown("### 🌡️ Weather Intelligence")
st.sidebar.caption("Data source & filters")

uploaded = st.sidebar.file_uploader("Upload a weather CSV", type=["csv"])

default_path = "weather_data.csv"
file_bytes = None
source_label = None

if uploaded is not None:
    file_bytes = uploaded.getvalue()
    source_label = uploaded.name
else:
    try:
        with open(default_path, "rb") as f:
            file_bytes = f.read()
        source_label = default_path
    except FileNotFoundError:
        pass

if file_bytes is None:
    st.sidebar.warning("Upload a CSV with columns: Date, Min Temperature, Max Temperature, Humidity (Rainfall optional).")
    st.title("Weather Intelligence Report")
    st.info("👈 Upload a weather CSV in the sidebar to generate the report.")
    st.stop()

try:
    df, clean_report = load_and_clean(file_bytes)
except ValueError as e:
    st.error(str(e))
    st.stop()

if df.empty:
    st.error("No valid rows remained after cleaning. Please check the uploaded file.")
    st.stop()

has_rainfall = "Rainfall" in df.columns

st.sidebar.caption(f"Loaded: **{source_label}**  ·  {len(df)} daily records")

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

months_present = [m for m in month_order() if m in df["Month Name"].unique()]
selected_months = st.sidebar.multiselect("Months", months_present, default=months_present)

heat_threshold = st.sidebar.slider(
    "Heat-alert threshold (°C, Max Temperature)",
    min_value=float(np.floor(df["Max Temperature"].min())),
    max_value=float(np.ceil(df["Max Temperature"].max())),
    value=float(min(35.0, df["Max Temperature"].quantile(0.9))),
    step=0.5,
)

cold_threshold = st.sidebar.slider(
    "Cold-alert threshold (°C, Min Temperature)",
    min_value=float(np.floor(df["Min Temperature"].min())),
    max_value=float(np.ceil(df["Min Temperature"].max())),
    value=float(max(5.0, df["Min Temperature"].quantile(0.1))),
    step=0.5,
)

with st.sidebar.expander("Data cleaning log"):
    st.caption(f"{clean_report['rows_in']} rows read → {clean_report['rows_out']} rows used.")
    if clean_report["issues"]:
        for issue in clean_report["issues"]:
            st.caption(f"• {issue}")
    else:
        st.caption("No issues found — data was already clean.")

# Apply filters
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

mask = (
    (df["Date"].dt.date >= start_d)
    & (df["Date"].dt.date <= end_d)
    & (df["Month Name"].isin(selected_months))
)
fdf = df.loc[mask].copy()

if fdf.empty:
    st.warning("No data matches the current filters. Adjust the date range or month selection.")
    st.stop()

# ============================================================
# HERO
# ============================================================

years = sorted(fdf["Year"].unique())
year_label = f"{years[0]}" if len(years) == 1 else f"{years[0]}–{years[-1]}"

top_l, top_r = st.columns([2.4, 1])
with top_l:
    st.markdown(f'<div class="station-eyebrow">DAILY OBSERVATIONS · {year_label} · {len(fdf)} DAYS</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Weather Intelligence<br>Report</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-sub">A station-level read on temperature, humidity'
        + (', and rainfall' if has_rainfall else '')
        + f' across {len(fdf)} recorded days. Cleaned, interpolated, and broken down '
        f'by month, extremes, and trend.</div>',
        unsafe_allow_html=True,
    )
with top_r:
    spark = go.Figure()
    spark.add_trace(go.Scatter(
        x=fdf["Date"], y=fdf["Average Temperature"],
        mode="lines", line=dict(color=HEAT, width=2), fill="tozeroy",
        fillcolor="rgba(198,117,43,0.08)",
    ))
    spark.update_layout(
        **{
            **PLOTLY_LAYOUT,
            "margin": dict(l=0, r=0, t=10, b=0),
            "xaxis": dict(visible=False),
            "yaxis": dict(visible=False),
        },
        height=140,
        showlegend=False,
    )
    st.plotly_chart(spark, use_container_width=True, config={"displayModeBar": False})
    st.caption("Average daily temperature, full range shown above")

st.markdown("---")

# ============================================================
# KPI ROW
# ============================================================

avg_temp = fdf["Average Temperature"].mean()
avg_max = fdf["Max Temperature"].mean()
avg_min = fdf["Min Temperature"].mean()
avg_hum = fdf["Humidity"].mean()
hottest_row = fdf.loc[fdf["Max Temperature"].idxmax()]
coldest_row = fdf.loc[fdf["Min Temperature"].idxmin()]
hot_days = fdf[fdf["Max Temperature"] > heat_threshold]
cold_days = fdf[fdf["Min Temperature"] < cold_threshold]

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    metric_card("Avg. Temperature", f"{avg_temp:.1f}°C", accent=INK,
                delta=f"Range {fdf['Average Temperature'].min():.1f}–{fdf['Average Temperature'].max():.1f}°C")
with k2:
    metric_card("Hottest Day", f"{hottest_row['Max Temperature']:.1f}°C", accent=HEAT,
                delta=hottest_row["Date"].strftime("%d %b %Y"))
with k3:
    metric_card("Coldest Day", f"{coldest_row['Min Temperature']:.1f}°C", accent=COLD,
                delta=coldest_row["Date"].strftime("%d %b %Y"))
with k4:
    metric_card("Avg. Humidity", f"{avg_hum:.0f}%", accent=HUM,
                delta=f"{fdf['Humidity'].min():.0f}–{fdf['Humidity'].max():.0f}% range")
with k5:
    if has_rainfall:
        rain_total = fdf["Rainfall"].sum()
        rain_days = int((fdf["Rainfall"] > 0).sum())
        metric_card("Total Rainfall", f"{rain_total:.0f} mm", accent=RAIN,
                    delta=f"{rain_days} rainy day(s)")
    else:
        metric_card(f"Days > {heat_threshold:.0f}°C", f"{len(hot_days)}", accent=ALERT,
                    delta=f"{len(hot_days)/len(fdf)*100:.0f}% of period")

st.write("")

# ============================================================
# TABS
# ============================================================

tab_names = ["Overview", "Monthly Trends", "Extremes & Alerts", "Humidity & Rainfall", "Relationships", "Data Explorer"]
tabs = st.tabs(tab_names)

# ---------------- OVERVIEW ----------------
with tabs[0]:
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("#### Daily temperature — full record")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fdf["Date"], y=fdf["Max Temperature"], name="Max",
                                  line=dict(color=HEAT, width=1.6)))
        fig.add_trace(go.Scatter(x=fdf["Date"], y=fdf["Min Temperature"], name="Min",
                                  line=dict(color=COLD, width=1.6)))
        fig.add_trace(go.Scatter(x=fdf["Date"], y=fdf["Average Temperature"], name="Average",
                                  line=dict(color=INK, width=1.2, dash="dot")))
        fig.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="°C")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### 7-day rolling average")
        roll = fdf.set_index("Date")["Average Temperature"].rolling(7, min_periods=1).mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=roll.index, y=roll.values, line=dict(color=HEAT, width=2), fill="tozeroy",
                                   fillcolor="rgba(198,117,43,0.10)"))
        fig2.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="°C")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Key findings")
    ic1, ic2 = st.columns(2)
    with ic1:
        warmest_m = fdf.groupby("Month Name")["Average Temperature"].mean().idxmax()
        coolest_m = fdf.groupby("Month Name")["Average Temperature"].mean().idxmin()
        insight_card("Seasonal pattern",
                     f"<b>{warmest_m}</b> was the warmest month on average, while <b>{coolest_m}</b> was the coolest — "
                     f"a swing of {fdf.groupby('Month Name')['Average Temperature'].mean().max() - fdf.groupby('Month Name')['Average Temperature'].mean().min():.1f}°C between them.")
        insight_card("Volatility",
                     f"The average day-to-day temperature swing (max − min) is <b>{fdf['Temperature Range'].mean():.1f}°C</b>, "
                     f"peaking at {fdf['Temperature Range'].max():.1f}°C on {fdf.loc[fdf['Temperature Range'].idxmax(), 'Date'].strftime('%d %b')}.")
    with ic2:
        insight_card("Heat exposure",
                     f"<b>{len(hot_days)}</b> day(s) ({len(hot_days)/len(fdf)*100:.0f}% of the period) exceeded "
                     f"{heat_threshold:.0f}°C, concentrated mainly in "
                     f"{hot_days.groupby('Month Name').size().idxmax() if len(hot_days) else 'no particular month'}.")
        insight_card("Cold exposure",
                     f"<b>{len(cold_days)}</b> day(s) dropped below {cold_threshold:.0f}°C, "
                     f"concentrated mainly in {cold_days.groupby('Month Name').size().idxmax() if len(cold_days) else 'no particular month'}.")

# ---------------- MONTHLY TRENDS ----------------
with tabs[1]:
    monthly = (
        fdf.groupby("Month Name")
        .agg(
            Avg_Temp=("Average Temperature", "mean"),
            Max_Temp=("Max Temperature", "max"),
            Min_Temp=("Min Temperature", "min"),
            Avg_Humidity=("Humidity", "mean"),
            **({"Total_Rainfall": ("Rainfall", "sum")} if has_rainfall else {}),
        )
        .reindex([m for m in month_order() if m in fdf["Month Name"].unique()])
        .round(1)
        .reset_index()
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Average monthly temperature")
        fig = px.bar(monthly, x="Month Name", y="Avg_Temp", color="Avg_Temp",
                     color_continuous_scale=[COLD, "#EDD9B6", HEAT])
        fig.update_layout(**PLOTLY_LAYOUT, height=360, coloraxis_showscale=False, yaxis_title="°C")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("#### Monthly range (min–max)")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly["Month Name"], y=monthly["Max_Temp"] - monthly["Min_Temp"],
                              base=monthly["Min_Temp"], marker_color=HEAT, opacity=0.75, name="Range"))
        fig.update_layout(**PLOTLY_LAYOUT, height=360, yaxis_title="°C")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Monthly summary table")
    st.dataframe(monthly, use_container_width=True, hide_index=True)

    st.markdown("#### Day-of-week pattern")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = fdf.groupby("Day of Week")["Average Temperature"].mean().reindex(dow_order)
    fig = px.line(x=dow.index, y=dow.values, markers=True)
    fig.update_traces(line=dict(color=INK, width=2), marker=dict(color=HEAT, size=8))
    fig.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="", yaxis_title="Avg. °C")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Included mainly as a data-quality check — real weather has no weekly cycle, so a flat line here is expected.")

# ---------------- EXTREMES & ALERTS ----------------
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        insight_card("🔥 Hottest day", f"<b>{hottest_row['Date'].strftime('%d %B %Y')}</b> reached "
                     f"<b>{hottest_row['Max Temperature']:.1f}°C</b>.")
        insight_card("❄️ Coldest day", f"<b>{coldest_row['Date'].strftime('%d %B %Y')}</b> fell to "
                     f"<b>{coldest_row['Min Temperature']:.1f}°C</b>.")
    with c2:
        hot_by_month = hot_days.groupby("Month Name").size().reindex(
            [m for m in month_order() if m in fdf["Month Name"].unique()], fill_value=0
        )
        cold_by_month = cold_days.groupby("Month Name").size().reindex(
            [m for m in month_order() if m in fdf["Month Name"].unique()], fill_value=0
        )
        top_hot_month = hot_by_month.idxmax() if hot_by_month.max() > 0 else "—"
        top_cold_month = cold_by_month.idxmax() if cold_by_month.max() > 0 else "—"
        insight_card(f"Days above {heat_threshold:.0f}°C", f"<b>{len(hot_days)}</b> total, most in <b>{top_hot_month}</b>.")
        insight_card(f"Days below {cold_threshold:.0f}°C", f"<b>{len(cold_days)}</b> total, most in <b>{top_cold_month}</b>.")

    st.markdown("#### Heat & cold alert days by month")
    alert_df = pd.DataFrame({
        "Month Name": hot_by_month.index,
        f"Above {heat_threshold:.0f}°C": hot_by_month.values,
        f"Below {cold_threshold:.0f}°C": -cold_by_month.values,
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(x=alert_df["Month Name"], y=alert_df[f"Above {heat_threshold:.0f}°C"],
                          marker_color=ALERT, name=f"Above {heat_threshold:.0f}°C"))
    fig.add_trace(go.Bar(x=alert_df["Month Name"], y=alert_df[f"Below {cold_threshold:.0f}°C"],
                          marker_color=COLD, name=f"Below {cold_threshold:.0f}°C"))
    fig.update_layout(**PLOTLY_LAYOUT, height=360, barmode="relative", yaxis_title="Days (± count)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Top 10 hottest & coldest days")
    c3, c4 = st.columns(2)
    with c3:
        top_hot = fdf.nlargest(10, "Max Temperature")[["Date", "Max Temperature"]].reset_index(drop=True)
        top_hot["Date"] = top_hot["Date"].dt.strftime("%d %b %Y")
        st.dataframe(top_hot, use_container_width=True, hide_index=True)
    with c4:
        top_cold = fdf.nsmallest(10, "Min Temperature")[["Date", "Min Temperature"]].reset_index(drop=True)
        top_cold["Date"] = top_cold["Date"].dt.strftime("%d %b %Y")
        st.dataframe(top_cold, use_container_width=True, hide_index=True)

# ---------------- HUMIDITY & RAINFALL ----------------
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Humidity over time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fdf["Date"], y=fdf["Humidity"], line=dict(color=HUM, width=1.5),
                                  fill="tozeroy", fillcolor="rgba(122,139,153,0.12)"))
        fig.update_layout(**PLOTLY_LAYOUT, height=340, yaxis_title="%")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("#### Humidity distribution")
        fig = px.histogram(fdf, x="Humidity", nbins=25, color_discrete_sequence=[HUM])
        fig.update_layout(**PLOTLY_LAYOUT, height=340, yaxis_title="Days")
        st.plotly_chart(fig, use_container_width=True)

    if has_rainfall:
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("#### Rainfall by month")
            rain_monthly = fdf.groupby("Month Name")["Rainfall"].sum().reindex(
                [m for m in month_order() if m in fdf["Month Name"].unique()]
            )
            fig = px.bar(x=rain_monthly.index, y=rain_monthly.values, color_discrete_sequence=[RAIN])
            fig.update_layout(**PLOTLY_LAYOUT, height=340, yaxis_title="mm")
            st.plotly_chart(fig, use_container_width=True)
        with c4:
            st.markdown("#### Daily rainfall")
            fig = px.bar(fdf, x="Date", y="Rainfall", color_discrete_sequence=[RAIN])
            fig.update_layout(**PLOTLY_LAYOUT, height=340, yaxis_title="mm")
            st.plotly_chart(fig, use_container_width=True)

        wettest = fdf.loc[fdf["Rainfall"].idxmax()]
        insight_card("Wettest day", f"<b>{wettest['Date'].strftime('%d %B %Y')}</b> recorded "
                     f"<b>{wettest['Rainfall']:.1f} mm</b> of rainfall — the highest in the period.")
        dry_streak = (fdf["Rainfall"] == 0).astype(int).groupby(
            (fdf["Rainfall"] != 0).astype(int).cumsum()
        ).cumsum().max()
        insight_card("Longest dry streak", f"<b>{int(dry_streak)} consecutive day(s)</b> without rainfall.")
    else:
        st.info("No rainfall column detected in this dataset — rainfall analysis is skipped.")

# ---------------- RELATIONSHIPS ----------------
with tabs[4]:
    st.markdown("#### Humidity vs. temperature")
    try:
        fig = px.scatter(fdf, x="Average Temperature", y="Humidity", color="Month Name",
                          color_discrete_sequence=px.colors.qualitative.Prism,
                          trendline="ols")
    except Exception:
        fig = px.scatter(fdf, x="Average Temperature", y="Humidity", color="Month Name",
                          color_discrete_sequence=px.colors.qualitative.Prism)
    fig.update_layout(**PLOTLY_LAYOUT, height=420)
    st.plotly_chart(fig, use_container_width=True)

    corr_cols = ["Min Temperature", "Max Temperature", "Average Temperature", "Humidity", "Temperature Range"]
    if has_rainfall:
        corr_cols.append("Rainfall")
    corr = fdf[corr_cols].corr().round(2)

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("#### Correlation matrix")
        fig = px.imshow(corr, text_auto=True, color_continuous_scale=[COLD, "#F6F4EF", HEAT],
                         zmin=-1, zmax=1, aspect="auto")
        fig.update_layout(**PLOTLY_LAYOUT, height=420, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        temp_hum_corr = corr.loc["Average Temperature", "Humidity"]
        direction = "inverse" if temp_hum_corr < 0 else "positive"
        insight_card("Temperature ↔ humidity",
                     f"Correlation of <b>{temp_hum_corr:.2f}</b> — a {direction} relationship. "
                     f"{'Warmer days tend to be less humid.' if temp_hum_corr < 0 else 'Warmer days tend to be more humid.'}")
        if has_rainfall:
            temp_rain_corr = corr.loc["Average Temperature", "Rainfall"]
            insight_card("Temperature ↔ rainfall",
                         f"Correlation of <b>{temp_rain_corr:.2f}</b> between average temperature and rainfall.")
        insight_card("Reading this matrix",
                     "Values close to +1 or −1 indicate a strong relationship; values near 0 indicate the two "
                     "variables move independently of each other.")

# ---------------- DATA EXPLORER ----------------
with tabs[5]:
    st.markdown("#### Filtered dataset")
    show_cols = ["Date", "Min Temperature", "Max Temperature", "Average Temperature",
                 "Temperature Range", "Humidity"] + (["Rainfall"] if has_rainfall else []) + ["Month Name", "Day of Week"]
    display_df = fdf[show_cols].copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

    st.markdown("#### Summary statistics")
    st.dataframe(fdf[corr_cols].describe().round(2), use_container_width=True)

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        data=csv_bytes,
        file_name=f"weather_cleaned_{start_d}_{end_d}.csv",
        mime="text/csv",
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f'<div class="footer-note">Weather Intelligence Report · generated {datetime.now().strftime("%d %B %Y, %H:%M")} '
    f'· source: {source_label} · {len(fdf)} of {len(df)} total records shown after filtering</div>',
    unsafe_allow_html=True,
)
