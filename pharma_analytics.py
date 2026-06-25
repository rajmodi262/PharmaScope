# pharma_analytics.py
# ---------------------------------------------------------------------------
# EconoScope · US Biopharma Commercial Analytics module
#
# Built to mirror the day-to-day of a commercial-analytics consultant in life
# sciences: market sizing, brand-level forecasting, patent-cliff (LOE) erosion
# modelling, competitive landscaping, and an auto-generated consulting brief
# (Insights / Opportunities / Threats).
#
# The module is fully self-contained — it constructs a realistic, deterministic
# US biopharma reference market (seeded, reproducible) so the dashboard runs
# without external data or retraining. Swap `build_market()` for a live data
# feed (IQVIA / Evaluate / company 10-Ks) and the rest of the pipeline is
# unchanged.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY = True
except Exception:  # graceful fallback if plotly missing
    PLOTLY = False

# Blue-Matter-leaning palette (deep blue / cyan / violet to match app shell)
COLORS = ["#00d4ff", "#7b2ff7", "#10b981", "#f59e0b", "#ef4444",
          "#06b6d4", "#a78bfa", "#34d399", "#fbbf24", "#fb7185"]

HIST_YEARS = list(range(2019, 2025))     # 2019-2024 actuals
FCST_YEARS = list(range(2025, 2031))     # 2025-2030 forecast


# ---------------------------------------------------------------------------
# 1. REFERENCE MARKET  (deterministic, US net sales in $M)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def build_market() -> pd.DataFrame:
    """Real branded-Rx reference set.

    `Sales2024` = FY2024 **worldwide net sales** ($M) as reported in each
    company's FY2024 annual report / Form 10-K (the headline figures the
    companies themselves quote). `CAGR` is a forward growth assumption grounded
    in the brand's recent reported trajectory; `LOEYear` is the approximate US
    loss-of-exclusivity / key-patent-expiry year from public patent-cliff
    coverage. The FY2024 anchor is an actual; prior years (back-cast) and
    forward years are modelled.
    """
    rng = np.random.default_rng(42)
    # brand, company, therapy area, modality, FY2024 WW net sales ($M),
    # forward CAGR, approx US loss-of-exclusivity year, erosion type
    rows = [
        ("Keytruda",  "Merck",              "Oncology",           "Biologic",  29482,  0.10, 2028, "Biosimilar"),
        ("Ozempic",   "Novo Nordisk",       "Cardiometabolic",    "Biologic",  16700,  0.18, 2032, "Biosimilar"),
        ("Dupixent",  "Sanofi / Regeneron", "Immunology",         "Biologic",  14150,  0.16, 2031, "Biosimilar"),
        ("Biktarvy",  "Gilead",             "Infectious Disease", "Small mol", 13419,  0.08, 2033, "Generic"),
        ("Eliquis",   "BMS / Pfizer",       "Cardiometabolic",    "Small mol", 13335,  0.03, 2028, "Generic"),
        ("Skyrizi",   "AbbVie",             "Immunology",         "Biologic",  11718,  0.28, 2033, "Biosimilar"),
        ("Darzalex",  "Johnson & Johnson",  "Oncology",           "Biologic",  11670,  0.14, 2029, "Biosimilar"),
        ("Mounjaro",  "Eli Lilly",          "Cardiometabolic",    "Biologic",  11540,  0.40, 2036, "Biosimilar"),
        ("Stelara",   "Johnson & Johnson",  "Immunology",         "Biologic",  10361, -0.05, 2025, "Biosimilar"),
        ("Trikafta",  "Vertex",             "Rare Disease",       "Small mol", 10178,  0.10, 2037, "Generic"),
        ("Opdivo",    "BMS",                "Oncology",           "Biologic",   9304,  0.05, 2028, "Biosimilar"),
        ("Humira",    "AbbVie",             "Immunology",         "Biologic",   8993, -0.25, 2023, "Biosimilar"),
        ("Entresto",  "Novartis",           "Cardiometabolic",    "Small mol",  7816,  0.06, 2025, "Generic"),
        ("Tagrisso",  "AstraZeneca",        "Oncology",           "Small mol",  6576,  0.08, 2032, "Generic"),
        ("Comirnaty", "Pfizer / BioNTech",  "Vaccines",           "mRNA",       5353, -0.20, 2030, "None"),
        ("Verzenio",  "Eli Lilly",          "Oncology",           "Small mol",  5306,  0.18, 2030, "Generic"),
        ("Ibrance",   "Pfizer",             "Oncology",           "Small mol",  4374, -0.05, 2027, "Generic"),
        ("Imbruvica", "AbbVie / J&J",       "Oncology",           "Small mol",  3344, -0.12, 2032, "Generic"),
    ]
    df = pd.DataFrame(rows, columns=[
        "Brand", "Company", "TherapyArea", "Modality",
        "Sales2024", "CAGR", "LOEYear", "ErosionType"])

    # back-cast modelled history 2019-2024 from CAGR with light realistic noise
    for y in HIST_YEARS:
        factor = (1 + df["CAGR"]) ** (y - 2024)
        noise = rng.normal(1.0, 0.03, len(df))
        df[f"S{y}"] = (df["Sales2024"] * factor * noise).round(0)
    return df


# ---------------------------------------------------------------------------
# 2. FORECAST ENGINE  (pre-LOE growth + post-LOE erosion curve)
# ---------------------------------------------------------------------------
def erosion_factor(years_since_loe: int, erosion_type: str) -> float:
    """US erosion curves: biologics erode slower than small-molecule generics."""
    if years_since_loe < 0:
        return 1.0
    if erosion_type == "Generic":          # steep small-molecule cliff
        curve = [1.0, 0.45, 0.25, 0.18, 0.14, 0.12]
    elif erosion_type == "Biosimilar":     # gentler biologic erosion
        curve = [1.0, 0.80, 0.65, 0.55, 0.48, 0.43]
    else:                                   # protected (gene tx / vaccine)
        curve = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    i = min(years_since_loe, len(curve) - 1)
    return curve[i]


def forecast_brand(row: pd.Series) -> dict:
    """Return {year: sales} forecast 2025-2030 for one brand."""
    base = row["Sales2024"]
    out = {}
    for y in FCST_YEARS:
        pre = base * (1 + row["CAGR"]) ** (y - 2024)
        ef = erosion_factor(y - row["LOEYear"], row["ErosionType"])
        out[y] = max(pre * ef, 0)
    return out


@st.cache_data(show_spinner=False)
def build_forecast(df: pd.DataFrame) -> pd.DataFrame:
    fc = df.apply(forecast_brand, axis=1, result_type="expand")
    fc.columns = [f"F{y}" for y in FCST_YEARS]
    return pd.concat([df, fc], axis=1)


# ---------------------------------------------------------------------------
# 2b. LAUNCH ANALOG FORECASTER  (Bass diffusion uptake + erosion + rNPV)
# ---------------------------------------------------------------------------
def launch_forecast(peak: float, years_to_peak: int, launch_year: int,
                    loe_year: int, erosion_type: str,
                    horizon: int = 12, discount: float = 0.10,
                    p: float = 0.03, q: float = 0.45) -> dict:
    """Bass-diffusion launch uptake to `peak` ($M), eroded after LOE.

    Returns {year: sales} plus cumulative and risk-adjusted NPV. `p` (innovation)
    and `q` (imitation) are standard pharma launch-analog coefficients; the time
    axis is compressed so ~95% of peak is reached by `years_to_peak`.
    """
    grid = np.arange(0.01, 40, 0.01)
    F = (1 - np.exp(-(p + q) * grid)) / (1 + (q / p) * np.exp(-(p + q) * grid))
    t95 = grid[np.argmax(F >= 0.95)] or 1.0
    scale = t95 / max(years_to_peak, 1)

    series, npv = {}, 0.0
    for i in range(horizon + 1):
        yr = launch_year + i
        tau = i * scale
        frac = ((1 - np.exp(-(p + q) * tau)) /
                (1 + (q / p) * np.exp(-(p + q) * tau))) if tau > 0 else 0.0
        sales = max(peak * frac * erosion_factor(yr - loe_year, erosion_type), 0.0)
        series[yr] = sales
        npv += sales / ((1 + discount) ** i)
    return {"series": series, "cumulative": sum(series.values()), "npv": npv}


# ---------------------------------------------------------------------------
# 3. AUTO-GENERATED CONSULTING BRIEF  (Insights / Opportunities / Threats)
# ---------------------------------------------------------------------------
def generate_brief(df: pd.DataFrame) -> dict:
    insights, opps, threats = [], [], []

    if f"F{FCST_YEARS[-1]}" not in df.columns:   # ensure forecast present
        df = build_forecast(df)

    total_24 = df["Sales2024"].sum()
    total_30 = df[[f"F{y}" for y in FCST_YEARS]].iloc[:, -1].sum()
    cagr = (total_30 / total_24) ** (1 / 6) - 1
    insights.append(
        f"Tracked US market is **${total_24/1000:.1f}B** (2024) → **${total_30/1000:.1f}B** "
        f"(2030E), a **{cagr*100:+.1f}% CAGR** across {df['Brand'].nunique()} assets.")

    ta = (df.groupby("TherapyArea")["Sales2024"].sum() / total_24 * 100).sort_values(ascending=False)
    insights.append(
        f"**{ta.index[0]}** leads at **{ta.iloc[0]:.0f}%** of tracked value; "
        f"top-3 areas concentrate **{ta.iloc[:3].sum():.0f}%** — a focused commercial footprint.")

    # patent cliff exposure 2025-2030
    at_risk = df[(df["LOEYear"] >= 2025) & (df["LOEYear"] <= 2030)]
    risk_val = at_risk["Sales2024"].sum()
    threats.append(
        f"**${risk_val/1000:.1f}B** of 2024 sales ({risk_val/total_24*100:.0f}% of portfolio) face "
        f"loss-of-exclusivity by 2030 across **{len(at_risk)}** brands — a material patent cliff.")
    if not at_risk.empty:
        worst = at_risk.sort_values("Sales2024", ascending=False).iloc[0]
        threats.append(
            f"Largest single exposure: **{worst['Brand']}** ({worst['Company']}, "
            f"${worst['Sales2024']/1000:.1f}B) loses exclusivity in **{int(worst['LOEYear'])}** "
            f"to {worst['ErosionType'].lower()} competition.")

    # growth opportunities
    growth = df.sort_values("CAGR", ascending=False)
    g0 = growth.iloc[0]
    opps.append(
        f"**{g0['TherapyArea']}** momentum: **{g0['Brand']}** compounding at "
        f"**{g0['CAGR']*100:+.0f}%/yr** — prioritise share-of-voice and access investment.")
    # durable = still growing AND no loss-of-exclusivity before 2031
    durable = df[(df["CAGR"] > 0.05) & (df["LOEYear"] >= 2031)].sort_values("Sales2024", ascending=False)
    if not durable.empty:
        names = ", ".join(durable["Brand"].head(3))
        noun = "asset" if len(durable) == 1 else "assets"
        opps.append(
            f"**{len(durable)}** growing {noun} carry **no LOE before 2031** (e.g. {names}) — "
            f"durable, defensible revenue (${durable['Sales2024'].sum()/1000:.0f}B) to anchor the portfolio.")
    declining = df[df["CAGR"] < 0]
    if not declining.empty:
        threats.append(
            f"**{len(declining)}** assets already in decline (e.g. **{declining.iloc[0]['Brand']}**); "
            f"lifecycle-management or managed divestment should be evaluated.")

    return {"insights": insights, "opportunities": opps, "threats": threats}


# ---------------------------------------------------------------------------
# 4. RENDER
# ---------------------------------------------------------------------------
def _metric_card(label, value, sub=""):
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div style="color:#94a3b8;font-size:12px;margin-top:4px;">{sub}</div>
        </div>""", unsafe_allow_html=True)


def render_pharma_tab():
    df = build_market()
    fdf = build_forecast(df)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💊 US Biopharma Commercial Analytics</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Market sizing · brand forecasting · patent-cliff erosion · '
        'competitive landscape · auto-generated consulting brief — anchored on FY2024 reported '
        'net sales ($M) from company 10-Ks.</div>',
        unsafe_allow_html=True)

    # ---- controls
    areas = ["All therapy areas"] + sorted(df["TherapyArea"].unique())
    c1, c2 = st.columns([2, 2])
    with c1:
        sel = st.selectbox("🔬 Therapy area lens", areas)
    with c2:
        view = st.radio("View", ["Market & Forecast", "Patent Cliff",
                                  "Competitive Landscape", "Launch Forecaster"],
                        horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    sub = df if sel == "All therapy areas" else df[df["TherapyArea"] == sel]
    fsub = fdf if sel == "All therapy areas" else fdf[fdf["TherapyArea"] == sel]

    # ---- KPI row
    total_24 = sub["Sales2024"].sum()
    total_30 = fsub[f"F{FCST_YEARS[-1]}"].sum()
    cagr = (total_30 / total_24) ** (1 / 6) - 1 if total_24 else 0
    risk = sub[(sub["LOEYear"] >= 2025) & (sub["LOEYear"] <= 2030)]["Sales2024"].sum()
    k1, k2, k3, k4 = st.columns(4)
    with k1: _metric_card("2024 Market (US)", f"${total_24/1000:.1f}B", "tracked net sales")
    with k2: _metric_card("2030E Market", f"${total_30/1000:.1f}B", "model forecast")
    with k3: _metric_card("Forecast CAGR", f"{cagr*100:+.1f}%", "2024 → 2030")
    with k4: _metric_card("Sales at LOE risk", f"${risk/1000:.1f}B", "exclusivity loss by 2030")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- VIEW 1: market & forecast
    if view == "Market & Forecast":
        hist = [sub[f"S{y}"].sum() for y in HIST_YEARS]
        fc = [fsub[f"F{y}"].sum() for y in FCST_YEARS]
        if PLOTLY:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=HIST_YEARS, y=[v/1000 for v in hist],
                          mode="lines+markers", name="History (FY24 actual)",
                          line=dict(color="#00d4ff", width=3)))
            allx = [HIST_YEARS[-1]] + FCST_YEARS
            ally = [hist[-1]] + fc
            fig.add_trace(go.Scatter(x=allx, y=[v/1000 for v in ally],
                          mode="lines+markers", name="Forecast",
                          line=dict(color="#7b2ff7", width=3, dash="dash")))
            # uncertainty band ±12%
            fig.add_trace(go.Scatter(
                x=allx + allx[::-1],
                y=[v*1.12/1000 for v in ally] + [v*0.88/1000 for v in ally][::-1],
                fill="toself", fillcolor="rgba(123,47,247,0.12)",
                line=dict(color="rgba(0,0,0,0)"), name="±12% band", hoverinfo="skip"))
            fig.update_layout(
                template="plotly_dark", height=420,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=40, b=10),
                title="Market trajectory — US net sales ($B)",
                yaxis_title="$B", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)

            # therapy-area treemap of 2024 value
            if sel == "All therapy areas":
                tdf = df.copy()
                fig2 = px.treemap(tdf, path=["TherapyArea", "Brand"], values="Sales2024",
                                  color="CAGR", color_continuous_scale="RdYlGn",
                                  title="2024 market value by therapy area & brand (color = growth)")
                fig2.update_layout(template="plotly_dark", height=420,
                                   paper_bgcolor="rgba(0,0,0,0)",
                                   margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.line_chart(pd.DataFrame({"Actual ($B)": [v/1000 for v in hist]}, index=HIST_YEARS))

    # ---- VIEW 2: patent cliff
    elif view == "Patent Cliff":
        st.markdown('<div class="section-title">⏳ Patent-Cliff / Loss-of-Exclusivity Exposure</div>',
                    unsafe_allow_html=True)
        risk_by_year = (sub[sub["LOEYear"].between(2025, 2030)]
                        .groupby("LOEYear")["Sales2024"].sum().reindex(FCST_YEARS, fill_value=0))
        if PLOTLY:
            fig = go.Figure(go.Bar(
                x=[str(y) for y in FCST_YEARS], y=[v/1000 for v in risk_by_year.values],
                marker_color=["#ef4444" if v > 0 else "#334155" for v in risk_by_year.values],
                text=[f"${v/1000:.1f}B" if v else "" for v in risk_by_year.values],
                textposition="outside"))
            fig.update_layout(template="plotly_dark", height=380,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(l=10, r=10, t=40, b=10),
                              title="2024 sales reaching LOE, by year ($B at risk)",
                              yaxis_title="$B")
            st.plotly_chart(fig, use_container_width=True)
        cliff = sub[sub["LOEYear"].between(2025, 2030)][
            ["Brand", "Company", "TherapyArea", "Sales2024", "LOEYear", "ErosionType"]
        ].sort_values("LOEYear")
        cliff = cliff.rename(columns={"Sales2024": "US Sales 2024 ($M)", "LOEYear": "LOE Year"})
        st.dataframe(cliff, use_container_width=True, hide_index=True)

    # ---- VIEW 3: competitive landscape
    elif view == "Competitive Landscape":
        st.markdown('<div class="section-title">🏁 Competitive Landscape</div>',
                    unsafe_allow_html=True)
        if PLOTLY:
            plot = sub.copy()
            plot["GrowthPct"] = plot["CAGR"] * 100
            fig = px.scatter(
                plot, x="GrowthPct", y="Sales2024", size="Sales2024", color="TherapyArea",
                hover_name="Brand", size_max=60,
                labels={"GrowthPct": "Pre-LOE growth (%/yr)", "Sales2024": "US sales 2024 ($M)"},
                color_discrete_sequence=COLORS,
                title="Share-of-market vs growth (bubble = US sales)")
            fig.add_vline(x=0, line_dash="dot", line_color="#64748b")
            fig.update_layout(template="plotly_dark", height=460,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        comp = (sub.groupby("Company")
                .agg(Brands=("Brand", "count"), Sales=("Sales2024", "sum"),
                     AvgGrowth=("CAGR", "mean")).reset_index()
                .sort_values("Sales", ascending=False))
        comp["Share %"] = (comp["Sales"] / df["Sales2024"].sum() * 100).round(1)
        comp["Sales"] = comp["Sales"].map(lambda v: f"${v/1000:.1f}B")
        comp["AvgGrowth"] = (comp["AvgGrowth"] * 100).round(1).map(lambda v: f"{v:+.1f}%")
        st.dataframe(comp.rename(columns={"AvgGrowth": "Avg Growth"}),
                     use_container_width=True, hide_index=True)

    # ---- VIEW 4: launch analog forecaster
    else:
        st.markdown('<div class="section-title">🚀 Launch Analog Forecaster '
                    '(Bass diffusion + rNPV)</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-subtitle">Model a pipeline asset\'s uptake to peak, '
                    'patent-cliff erosion, and risk-adjusted NPV — the core launch deliverable.</div>',
                    unsafe_allow_html=True)
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            peak = st.slider("Expected peak sales ($M/yr)", 200, 20000, 4000, step=100)
            ttp = st.slider("Years to peak", 2, 8, 5)
        with lc2:
            launch_yr = st.slider("Launch year", 2026, 2032, 2027)
            loe_yr = st.slider("Loss-of-exclusivity year", 2030, 2045, 2039)
        with lc3:
            etype = st.selectbox("Post-LOE erosion", ["Biosimilar", "Generic", "None"])
            disc = st.slider("Discount rate (%)", 6, 14, 10) / 100

        lf = launch_forecast(peak, ttp, launch_yr, loe_yr, etype, discount=disc)
        years = list(lf["series"].keys())
        vals = list(lf["series"].values())
        peak_reached = max(vals)
        m1, m2, m3 = st.columns(3)
        with m1: _metric_card("Peak annual sales", f"${peak_reached/1000:.2f}B", f"reached ~{launch_yr+ttp}")
        with m2: _metric_card("Cumulative (12y)", f"${lf['cumulative']/1000:.1f}B", "undiscounted")
        with m3: _metric_card("Risk-adjusted NPV", f"${lf['npv']/1000:.1f}B", f"@ {disc*100:.0f}% discount")
        if PLOTLY:
            colors = ["#10b981" if y < loe_yr else "#ef4444" for y in years]
            fig = go.Figure(go.Bar(x=[str(y) for y in years], y=[v/1000 for v in vals],
                                   marker_color=colors,
                                   text=[f"{v/1000:.1f}" for v in vals], textposition="outside"))
            fig.update_layout(template="plotly_dark", height=400,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(l=10, r=10, t=40, b=10),
                              title=f"Modelled launch trajectory ($B) — green pre-LOE, "
                                    f"red post-LOE ({loe_yr})",
                              yaxis_title="$B")
            st.plotly_chart(fig, use_container_width=True)

    # ---- CONSULTING BRIEF (always shown)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Auto-Generated Consulting Brief</div>',
                unsafe_allow_html=True)
    brief = generate_brief(df)
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown("#### 🔎 Key Insights")
        for x in brief["insights"]:
            st.markdown(f"- {x}")
    with b2:
        st.markdown("#### 🚀 Opportunities")
        for x in brief["opportunities"]:
            st.markdown(f"- {x}")
    with b3:
        st.markdown("#### ⚠️ Threats")
        for x in brief["threats"]:
            st.markdown(f"- {x}")

    # ---- downloadable consultant deliverables
    export = fdf[["Brand", "Company", "TherapyArea", "Modality", "Sales2024",
                  "CAGR", "LOEYear", "ErosionType"] + [f"F{y}" for y in FCST_YEARS]]
    brief_md = "# US Biopharma Commercial Analytics — Consulting Brief\n\n"
    for title, key in [("Key Insights", "insights"), ("Opportunities", "opportunities"),
                       ("Threats", "threats")]:
        brief_md += f"## {title}\n" + "".join(f"- {x}\n" for x in brief[key]) + "\n"
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("⬇️ Download forecast (CSV)",
                           export.to_csv(index=False).encode("utf-8"),
                           "biopharma_forecast.csv", "text/csv", use_container_width=True)
    with d2:
        st.download_button("⬇️ Download consulting brief (Markdown)",
                           brief_md.encode("utf-8"),
                           "biopharma_brief.md", "text/markdown", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("FY2024 net sales are **actuals from company annual reports / 10-Ks** "
               "(worldwide net sales, $M). Prior-year history, forward forecast, LOE years and "
               "erosion curves are modelled. Swap `build_market()` for an IQVIA / Evaluate feed "
               "for US-specific, audited figures.")
