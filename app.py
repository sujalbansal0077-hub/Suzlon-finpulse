# SUZLON FINPULSE — 10-year financial intelligence dashboard
# Install: pip install streamlit pandas plotly
# Run: streamlit run app.py
# Data basis: consolidated financial highlights from Suzlon annual reports/results.
# Important: FY23 and FY26 reported PAT are materially affected by tax/exceptional items.

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Suzlon FINPULSE", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --bg:#08110f; --panel:#111d1a; --panel2:#14231f; --line:#243a32; --lime:#c7f36b; --mint:#66e0b4; --text:#eef6f0; --muted:#9aafa4; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 80% 0%, #18352b 0%, #08110f 42%); color:var(--text); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#101c18,#09110f); border-right:1px solid #263a32; }
[data-testid="stSidebar"] * { color:#e9f2eb; }
.block-container { padding-top:1.4rem; padding-bottom:3rem; max-width:1500px; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
h1 { color:#f4f9f3; font-size:2.55rem !important; }
h2 { color:#e8f7eb; }
.hero { padding:30px 34px; border:1px solid #315044; border-radius:22px; background:linear-gradient(115deg,rgba(24,57,44,.96),rgba(14,27,24,.9) 68%,rgba(40,61,38,.65)); position:relative; overflow:hidden; }
.hero:after { content:'✳'; position:absolute; right:32px; top:-50px; font-size:190px; color:rgba(199,243,107,.09); transform:rotate(12deg); }
.eyebrow { color:var(--mint); font-size:.78rem; font-weight:700; letter-spacing:.17em; text-transform:uppercase; }
.hero-title { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:2.5rem; line-height:1.12; color:var(--lime); margin:.45rem 0 .7rem; }
.hero-sub { color:#c0d1c6; font-size:1.02rem; max-width:780px; }
.pill { display:inline-block; border:1px solid #466454; border-radius:100px; padding:6px 11px; margin:12px 7px 0 0; color:#d8e9dd; font-size:.78rem; background:#14251e; }
.kpi { background:linear-gradient(145deg,#15241f,#0e1916); border:1px solid #2a4036; border-radius:17px; padding:18px 19px 16px; min-height:128px; box-shadow:0 10px 26px rgba(0,0,0,.12); }
.kpi-label { color:#9db4a6; font-size:.76rem; letter-spacing:.12em; text-transform:uppercase; font-weight:700; }
.kpi-value { font-family:'Space Grotesk',sans-serif; color:#f5faf3; font-size:1.85rem; font-weight:700; margin:.38rem 0 .25rem; }
.kpi-foot { color:#9fb7a9; font-size:.78rem; }
.section-head { margin-top:1.1rem; margin-bottom:.2rem; font-size:1.4rem; font-weight:700; color:#e8f6e9; }
.section-sub { color:#9eb2a6; font-size:.9rem; margin-bottom:1rem; }
.note { border:1px solid #64522a; border-left:4px solid #e5b85c; border-radius:10px; padding:12px 15px; background:rgba(71,52,17,.3); color:#f0d9a1; font-size:.86rem; }
.good { border:1px solid #2a5e4a; border-left:4px solid #66e0b4; border-radius:10px; padding:12px 15px; background:rgba(17,69,49,.22); color:#c4f1dc; font-size:.88rem; }
div[data-testid="stMetric"] { background:#111e19; border:1px solid #2a4036; padding:14px 16px; border-radius:14px; }
div[data-testid="stMetricLabel"] { color:#a7bbae; }
div[data-testid="stMetricValue"] { color:#f1f7ef; }
.stTabs [data-baseweb="tab-list"] { gap:8px; border-bottom:1px solid #294037; }
.stTabs [data-baseweb="tab"] { background:#112019; border-radius:10px 10px 0 0; color:#b6c8bc; padding:10px 16px; }
.stTabs [aria-selected="true"] { background:#263e30 !important; color:#d4fa83 !important; }
.stButton>button { border-radius:10px; border:1px solid #4b6c54; background:#c7f36b; color:#102015; font-weight:700; }
[data-testid="stDataFrame"] { border:1px solid #2a4036; border-radius:12px; overflow:hidden; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Verified-source dataset ----------
DATA = [
    ["FY2017",2017,12714.00,2499.00,852.00,"https://newsroom.suzlon.com/wp-content/uploads/2025/05/Annual-Report-FY20.pdf","FY2019-20 Annual Report, historical consolidated highlights; rounded values"],
    ["FY2018",2018,8074.61,1003.00,-384.00,"https://newsroom.suzlon.com/wp-content/uploads/2025/05/Annual-Report-FY20.pdf","FY2019-20 Annual Report, historical consolidated highlights; FY18 revenue restated/rounded per report"],
    ["FY2019",2019,4978.46,-9.00,-1537.00,"https://newsroom.suzlon.com/wp-content/uploads/2025/05/Annual-Report-FY20.pdf","FY2019-20 Annual Report, historical consolidated highlights"],
    ["FY2020",2020,2933.00,-860.00,-2692.00,"https://newsroom.suzlon.com/wp-content/uploads/2025/05/Annual-Report-FY20.pdf","FY2019-20 Annual Report, consolidated financial highlights"],
    ["FY2021",2021,3295.00,534.00,104.00,"https://www.suzlon.com/microsites/2023-24/pdf/Suzlon-AR-2023-24.pdf","FY2023-24 Annual Report, consolidated historical financial highlights"],
    ["FY2022",2022,6520.00,889.00,-177.00,"https://www.suzlon.com/microsites/2023-24/pdf/Suzlon-AR-2023-24.pdf","FY2023-24 Annual Report, consolidated historical financial highlights"],
    ["FY2023",2023,5947.00,832.00,2887.00,"https://www.suzlon.com/microsites/2023-24/pdf/Suzlon-AR-2023-24.pdf","FY2023-24 Annual Report, consolidated historical financial highlights"],
    ["FY2024",2024,6497.00,1029.00,660.00,"https://www.suzlon.com/NewPdf/Convened_Meeting/Suzlon-AR-2024-25_C2C-For-website-upload.pdf","FY2024-25 Annual Report, consolidated FY24 comparative"],
    ["FY2025",2025,10851.32,1857.23,2071.63,"https://www.suzlon.com/NewPdf/Convened_Meeting/Suzlon-AR-2024-25_C2C-For-website-upload.pdf","FY2024-25 Annual Report, audited consolidated results"],
    ["FY2026",2026,16679.00,3022.00,3163.00,"https://www.suzlon.com/pdf/green-business/Q4FY26_Results_Release_FINAL.pdf","FY2025-26 annual results release, consolidated; PAT includes deferred tax impact"],
]
df = pd.DataFrame(DATA, columns=["FY","Year","Revenue","EBITDA","PAT","Source","Source_note"])
df["EBITDA Margin %"] = df["EBITDA"] / df["Revenue"] * 100
df["PAT Margin %"] = df["PAT"] / df["Revenue"] * 100
df["Revenue YoY %"] = df["Revenue"].pct_change() * 100
df["EBITDA YoY %"] = df["EBITDA"].pct_change() * 100

# Detailed financial statements: audited consolidated values transcribed from official reports.
# FY2026 detail is deliberately blank until the annual report statement lines are reconciled.
BS_CF_SOURCE_FY20_21 = "https://www.suzlon.com/pdf/new-pdf/Annual-Report-2020-2021.pdf"
BS_CF_SOURCE_FY22_23 = "https://newsroom.suzlon.com/wp-content/uploads/2025/05/Suzlon-01-09-2023.pdf"
BS_CF_SOURCE_FY24_25 = "https://www.suzlon.com/NewPdf/Convened_Meeting/Suzlon-AR-2024-25_C2C-For-website-upload.pdf"
BS_CF_DATA = [
    # FY, year, total assets, current assets, current liabilities, total borrowings (current + non-current), cash & cash equivalents, total equity, CFO, CFI, CFF, source, note
    ["FY2020",2020,6530.35,4643.55,16545.17,9685.62,57.59,-11041.84,-929.04,-32.46,969.24,BS_CF_SOURCE_FY20_21,"FY2020 comparative in FY2020-21 audited consolidated statements"],
    ["FY2021",2021,6601.09,4797.92,3813.78,6202.54,262.50,-3400.71,530.50,-23.73,-326.60,BS_CF_SOURCE_FY20_21,"FY2020-21 audited consolidated statements"],
    ["FY2022",2022,6474.86,5019.11,4234.40,6390.56,437.38,-3561.81,1301.90,-18.43,-1044.95,BS_CF_SOURCE_FY22_23,"FY2022 comparative in FY2022-23 audited consolidated statements; values in ₹ crore"],
    ["FY2023",2023,5523.38,4142.18,2700.79,1904.88,367.31,1099.14,466.66,84.91,-684.49,BS_CF_SOURCE_FY22_23,"FY2022-23 audited consolidated statements"],
    ["FY2024",2024,7179.02,5287.69,3008.85,109.95,249.57,3920.31,79.53,-151.55,131.63,BS_CF_SOURCE_FY24_25,"FY2024 comparative in FY2024-25 audited consolidated statements"],
    ["FY2025",2025,12959.59,9251.71,5914.64,283.33,901.07,6105.72,1091.96,-751.74,343.01,BS_CF_SOURCE_FY24_25,"FY2024-25 audited consolidated statements"],
    ["FY2026",2026,float("nan"),float("nan"),float("nan"),float("nan"),float("nan"),float("nan"),float("nan"),float("nan"),float("nan"),"https://www.suzlon.com/investors/financial-reports/","FY2025-26 annual statement detail not yet reconciled in this dashboard; intentionally blank, not zero"],
]
bs = pd.DataFrame(BS_CF_DATA, columns=["FY","Year","Total assets","Current assets","Current liabilities","Total borrowings","Cash and cash equivalents","Total equity","Operating cash flow","Investing cash flow","Financing cash flow","Source","Source_note"])
bs["Net debt/(cash)"] = bs["Total borrowings"] - bs["Cash and cash equivalents"]
bs["Working capital"] = bs["Current assets"] - bs["Current liabilities"]
bs["Current ratio"] = bs["Current assets"] / bs["Current liabilities"]
bs["Debt/equity"] = bs["Total borrowings"] / bs["Total equity"].where(bs["Total equity"] > 0)
bs["Operating cash flow / revenue %"] = bs["Operating cash flow"] / bs["FY"].map(df.set_index("FY")["Revenue"]) * 100
bs["Operating cash flow / EBITDA %"] = bs["Operating cash flow"] / bs["FY"].map(df.set_index("FY")["EBITDA"]).where(bs["FY"].map(df.set_index("FY")["EBITDA"]) > 0) * 100

# Latest quarterly pulse, kept separate from the audited annual time series.
# Source: Suzlon official Q2 FY27 press release, 29 October 2026.
Q2_FY27 = {"Revenue": 4869, "EBITDA": 720, "EBITDA Margin %": 14.8, "PAT": 394,
           "Revenue YoY %": 26.0, "Source": "https://www.suzlon.com/media/press/press-releases/suzlon-q2-revenue-grows-26-yo-y-on-record-deliveries/"}

def inr_cr(x):
    return f"₹{x:,.0f} Cr"

def fmt_pct(x):
    return "—" if pd.isna(x) else f"{x:+.1f}%"

# ---------- Sidebar controls ----------
with st.sidebar:
    st.markdown("## 🌿 FINPULSE")
    st.caption("SUZLON ENERGY · FINANCIAL INTELLIGENCE")
    st.markdown("---")
    page = st.radio("WORKSPACE", ["Dean Brief","Executive Cockpit","10-Year Performance","Profitability & Health","Balance Sheet & Cash Flow","Forecast Studio","Source Register"], index=0)
    st.markdown("---")
    st.markdown("### View controls")
    start_fy, end_fy = st.select_slider("Financial-year window", options=df["FY"].tolist(), value=("FY2017","FY2026"))
    metric = st.selectbox("Primary chart metric", ["Revenue","EBITDA","PAT"], index=0)
    st.markdown("---")
    st.caption("DATA POLICY")
    st.caption("Consolidated financial highlights · ₹ crore · annual reports / audited results")
    st.caption("Figures are reported values, not stock-price recommendations.")

view = df[(df["FY"] >= start_fy) & (df["FY"] <= end_fy)].copy()
latest = df.iloc[-1]
prior = df.iloc[-2]
cagr = ((latest["Revenue"] / df.iloc[0]["Revenue"]) ** (1/9) - 1) * 100

# ---------- Reusable chart ----------
def chart_layout(fig, height=360):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#dbe9df", size=12),
        margin=dict(l=12,r=18,t=35,b=10), legend=dict(orientation="h",y=1.12,x=0),
        hoverlabel=dict(bgcolor="#15251e",font_color="#f1f7ef"),
        xaxis=dict(showgrid=False,zeroline=False,linecolor="#31463b"),
        yaxis=dict(gridcolor="rgba(148,177,157,.14)",zerolinecolor="#486152",linecolor="#31463b"),
    )
    return fig

def line_chart(frame, cols, labels=None, title=None):
    fig = go.Figure()
    for i,col in enumerate(cols):
        fig.add_trace(go.Scatter(x=frame["FY"],y=frame[col],mode="lines+markers",name=(labels[i] if labels else col),
            line=dict(width=3),marker=dict(size=7),connectgaps=False))
    fig.update_layout(title=title)
    return chart_layout(fig)

def kpi(label, value, foot):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>', unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown(f"""
<div class="hero">
  <div class="eyebrow">Renewable energy · Financial intelligence · 10-year lens</div>
  <div class="hero-title">SUZLON<br>FINPULSE</div>
  <div class="hero-sub">A live-feeling financial command centre for exploring Suzlon Energy’s reported financial trajectory — from the difficult years to its recent scale-up.</div>
  <span class="pill">FY2017–FY2026</span><span class="pill">Consolidated reporting</span><span class="pill">Interactive analytics</span><span class="pill">Source-linked figures</span>
</div>
""", unsafe_allow_html=True)
st.write("")

st.markdown('<div class="note">Reading note: reported PAT in FY2023 and FY2026 is materially influenced by tax/exceptional items. Read profit alongside EBITDA, margins and the annual-report notes; reported PAT alone does not describe underlying operating performance.</div>', unsafe_allow_html=True)
st.write("")

if page == "Dean Brief":
    st.markdown('<div class="section-head">Dean presentation brief</div><div class="section-sub">A concise, evidence-led storyline for presenting the dashboard and its limitations.</div>', unsafe_allow_html=True)
    st.markdown('<div class="good"><b>Core message:</b> Suzlon has moved from a stressed financial position in FY20 toward a materially larger and more profitable operating business by FY26. The next test is whether growth converts into sustainable cash generation and disciplined execution.</div>', unsafe_allow_html=True)
    st.write("")
    q1,q2,q3,q4=st.columns(4)
    with q1: kpi("FY26 Revenue", inr_cr(latest["Revenue"]), f"{latest['Revenue YoY %']:+.1f}% YoY")
    with q2: kpi("FY26 EBITDA", inr_cr(latest["EBITDA"]), f"{latest['EBITDA Margin %']:.1f}% EBITDA margin")
    with q3: kpi("FY27 Q2 Revenue", inr_cr(Q2_FY27["Revenue"]), "+26% YoY, company-reported")
    with q4: kpi("FY27 Q2 EBITDA", inr_cr(Q2_FY27["EBITDA"]), f"{Q2_FY27['EBITDA Margin %']:.1f}% margin")
    st.markdown('<div class="section-head">Three points to communicate</div>', unsafe_allow_html=True)
    x,y,z=st.columns(3)
    with x:
        st.markdown('<div class="kpi"><div class="kpi-label">01 · Scale</div><div class="kpi-value">5.7×</div><div class="kpi-foot">FY26 revenue is approximately 5.7 times FY20 revenue.</div></div>', unsafe_allow_html=True)
    with y:
        st.markdown('<div class="kpi"><div class="kpi-label">02 · Operations</div><div class="kpi-value">18.1%</div><div class="kpi-foot">FY26 EBITDA margin, calculated from reported headline values.</div></div>', unsafe_allow_html=True)
    with z:
        st.markdown('<div class="kpi"><div class="kpi-label">03 · Quality of earnings</div><div class="kpi-value">Cash matters</div><div class="kpi-foot">PAT is affected by deferred-tax items; validate cash flow and working capital before judging quality.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">Latest operating pulse · Q2 FY27</div><div class="section-sub">Quarterly numbers are shown separately and are not mixed into the FY17–FY26 annual series.</div>', unsafe_allow_html=True)
    qleft,qright=st.columns([1,1.2])
    with qleft:
        st.metric("Revenue", inr_cr(Q2_FY27["Revenue"]), "+26% YoY")
        st.metric("EBITDA", inr_cr(Q2_FY27["EBITDA"]), "14.8% margin")
        st.metric("Reported PAT", inr_cr(Q2_FY27["PAT"]), "Q2 FY27")
    with qright:
        qdf=pd.DataFrame({"Metric":["Revenue","EBITDA","PAT"],"Q2 FY27 (₹ Cr)":[4869,720,394],"Q2 FY26 comparable (₹ Cr)":[3866,721,389]})
        qdf["YoY change %"]=(qdf["Q2 FY27 (₹ Cr)"]/qdf["Q2 FY26 comparable (₹ Cr)"]-1)*100
        fig=go.Figure()
        fig.add_trace(go.Bar(x=qdf["Metric"],y=qdf["Q2 FY27 (₹ Cr)"],name="Q2 FY27",marker_color="#c7f36b"))
        fig.add_trace(go.Bar(x=qdf["Metric"],y=qdf["Q2 FY26 comparable (₹ Cr)"],name="Q2 FY26 comparable",marker_color="#66e0b4"))
        fig.update_layout(title="Q2 comparison (₹ crore)",barmode="group")
        st.plotly_chart(chart_layout(fig,320),width="stretch")
        st.caption("Q2 FY26 comparable PAT excludes the ₹891 Cr deferred-tax asset creation, as described in Suzlon’s Q2 FY27 release. Do not compare it with unadjusted reported Q2 FY26 PAT.")
    st.markdown('<div class="section-head">Questions the dashboard should lead to</div>', unsafe_allow_html=True)
    st.markdown("""
    1. **Can revenue growth sustain?** Track deliveries, order-book conversion and execution capacity.
    2. **Is operating performance converting into cash?** Review operating cash flow, receivables, inventory and contract assets.
    3. **How much of PAT is recurring?** Separate operating performance from deferred-tax recognition and exceptional items.
    4. **What is the balance-sheet position?** Use the latest audited consolidated statements for net cash/debt, liquidity and interest burden.
    """)
    st.markdown('<div class="note">Scope note for the presentation: this prototype currently verifies a 10-year headline series for revenue, EBITDA and PAT, plus the latest Q2 FY27 snapshot. It does not yet claim a fully reconciled 10-year balance sheet, cash-flow statement or ratio model.</div>', unsafe_allow_html=True)
    st.link_button("Open official Q2 FY27 results release", Q2_FY27["Source"])
    st.link_button("Open Suzlon official Financial Reports hub", "https://www.suzlon.com/investors/financial-reports/")

elif page == "Executive Cockpit":
    st.markdown('<div class="section-head">Executive cockpit</div><div class="section-sub">A concise view of the latest reported year, plus the long-term shift in scale.</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]: kpi("FY26 Revenue", inr_cr(latest["Revenue"]), f"{latest['Revenue YoY %']:+.1f}% vs FY25")
    with cols[1]: kpi("FY26 EBITDA", inr_cr(latest["EBITDA"]), f"Margin {latest['EBITDA Margin %']:.1f}%")
    with cols[2]: kpi("FY26 Reported PAT", inr_cr(latest["PAT"]), "Includes deferred-tax impact")
    with cols[3]: kpi("10Y Revenue CAGR", f"{cagr:.1f}%", "FY17 to FY26")

    left,right = st.columns([1.55,1])
    with left:
        st.markdown('<div class="section-head">Revenue and operating earnings</div>',unsafe_allow_html=True)
        st.plotly_chart(line_chart(view,["Revenue","EBITDA"],["Revenue (₹ Cr)","EBITDA (₹ Cr)"]),width="stretch")
    with right:
        st.markdown('<div class="section-head">Reported profit after tax</div>',unsafe_allow_html=True)
        fig=go.Figure(go.Bar(x=view["FY"],y=view["PAT"],marker_color=["#66e0b4" if x>=0 else "#e97878" for x in view["PAT"]],name="PAT"))
        fig.add_hline(y=0,line_color="#8aa394",line_width=1)
        fig.update_layout(title="PAT (₹ crore)",showlegend=False)
        st.plotly_chart(chart_layout(fig),width="stretch")
    st.markdown('<div class="section-head">What the numbers suggest</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="kpi"><div class="kpi-label">Scale-up</div><div class="kpi-value">5.7×</div><div class="kpi-foot">Revenue FY26 compared with FY20 (approx.).</div></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="kpi"><div class="kpi-label">Operating turnaround</div><div class="kpi-value">18.1%</div><div class="kpi-foot">FY26 EBITDA margin based on reported headline values.</div></div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="kpi"><div class="kpi-label">Interpret carefully</div><div class="kpi-value">PAT ≠ cash</div><div class="kpi-foot">Tax credits and exceptional items can create sharp PAT swings.</div></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="good">Analyst lens: FY26 headline revenue and EBITDA reached new highs in this 10-year series. For a complete investment-quality view, add cash-flow, working-capital, debt and note-level analysis before drawing conclusions.</div>',unsafe_allow_html=True)

elif page == "10-Year Performance":
    st.markdown('<div class="section-head">10-year performance explorer</div><div class="section-sub">Choose the metric in the sidebar; zoom, hover and compare year-by-year values.</div>',unsafe_allow_html=True)
    left,right=st.columns([1.5,1])
    with left:
        fig=go.Figure()
        colors=["#c7f36b" if v>=0 else "#e97878" for v in view[metric]]
        fig.add_trace(go.Bar(x=view["FY"],y=view[metric],marker_color=colors,name=metric))
        fig.add_hline(y=0,line_color="#8ba597")
        fig.update_layout(title=f"{metric} by financial year (₹ crore)",showlegend=False)
        st.plotly_chart(chart_layout(fig,420),width="stretch")
    with right:
        st.plotly_chart(line_chart(view,["EBITDA Margin %","PAT Margin %"],["EBITDA margin %","PAT margin %"],"Profitability margins"),width="stretch")
        st.metric("Latest-year revenue growth",fmt_pct(latest["Revenue YoY %"]))
        st.metric("Latest-year EBITDA growth",fmt_pct(latest["EBITDA YoY %"]))
    st.markdown("#### Historical data table")
    display=view[["FY","Revenue","EBITDA","PAT","EBITDA Margin %","PAT Margin %","Revenue YoY %"]].copy()
    display.columns=["Financial year","Revenue (₹ Cr)","EBITDA (₹ Cr)","PAT (₹ Cr)","EBITDA margin %","PAT margin %","Revenue YoY %"]
    st.dataframe(display.style.format({"Revenue (₹ Cr)":"{:,.2f}","EBITDA (₹ Cr)":"{:,.2f}","PAT (₹ Cr)":"{:,.2f}","EBITDA margin %":"{:.1f}%","PAT margin %":"{:.1f}%","Revenue YoY %":"{:+.1f}%"}),width="stretch",hide_index=True)
    st.download_button("⬇ Download displayed data (CSV)",display.to_csv(index=False).encode("utf-8"),file_name="suzlon_finpulse_selected_years.csv",mime="text/csv")

elif page == "Profitability & Health":
    st.markdown('<div class="section-head">Profitability & health monitor</div><div class="section-sub">Margins, profit volatility and the gap between operating performance and reported PAT.</div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.plotly_chart(line_chart(view,["EBITDA Margin %","PAT Margin %"],["EBITDA margin %","PAT margin %"],"Margin trend"),width="stretch")
    with b:
        fig=go.Figure()
        fig.add_trace(go.Bar(x=view["FY"],y=view["EBITDA"],name="EBITDA",marker_color="#66e0b4"))
        fig.add_trace(go.Scatter(x=view["FY"],y=view["PAT"],name="PAT",mode="lines+markers",line=dict(color="#c7f36b",width=3)))
        fig.add_hline(y=0,line_color="#8ba597")
        fig.update_layout(title="EBITDA vs PAT (₹ crore)",barmode="group")
        st.plotly_chart(chart_layout(fig),width="stretch")
    st.markdown("#### Analyst checks")
    st.markdown("""
    - **Operating profitability:** EBITDA and EBITDA margin are useful for tracking core operating performance before interest, tax and depreciation.
    - **PAT quality:** large gaps between EBITDA trends and PAT can reflect financing, exceptional items, deferred-tax recognition or accounting changes.
    - **Comparability:** this view uses the consolidated headline series published in Suzlon annual reports/results. Historical restatements and definition changes should be checked in the source report.
    - **Not shown as verified here:** current ratio, debt/equity, interest coverage and operating cash conversion are intentionally omitted because this 10-year summary dataset does not contain all audited balance-sheet and cash-flow line items.
    """)
    st.dataframe(view[["FY","Revenue","EBITDA","PAT","EBITDA Margin %","PAT Margin %"]].rename(columns={"FY":"Financial year","Revenue":"Revenue (₹ Cr)","EBITDA":"EBITDA (₹ Cr)","PAT":"PAT (₹ Cr)"}).style.format({"Revenue (₹ Cr)":"{:,.2f}","EBITDA (₹ Cr)":"{:,.2f}","PAT (₹ Cr)":"{:,.2f}","EBITDA Margin %":"{:.1f}%","PAT Margin %":"{:.1f}%"}),width="stretch",hide_index=True)

elif page == "Balance Sheet & Cash Flow":
    st.markdown('<div class="section-head">Balance sheet, debt & cash-flow monitor</div><div class="section-sub">Audited consolidated statement lines with formula-based ratios. Figures are in ₹ crore unless stated otherwise.</div>',unsafe_allow_html=True)
    st.markdown('<div class="note"><b>Coverage note:</b> detailed statement values below are reconciled for FY2020–FY2025. FY2026 detail is deliberately blank until the annual report line items are checked and reconciled. No missing values are treated as zero. FY2017–FY2019 detailed statement data is not included in this module yet.</div>',unsafe_allow_html=True)
    bsv = bs[bs["FY"].isin(view["FY"])].copy()
    valid = bsv.dropna(subset=["Total assets"])
    if valid.empty:
        st.warning("Select a year from FY2020–FY2025 in the sidebar to view reconciled balance-sheet and cash-flow data.")
    else:
        latest_bs = valid.iloc[-1]
        k1,k2,k3,k4 = st.columns(4)
        with k1: st.metric("Latest total assets", inr_cr(latest_bs["Total assets"]))
        with k2: st.metric("Total borrowings", inr_cr(latest_bs["Total borrowings"]))
        with k3: st.metric("Net debt / (cash)", inr_cr(latest_bs["Net debt/(cash)"]), "Borrowings less cash equivalents")
        with k4: st.metric("Current ratio", f'{latest_bs["Current ratio"]:.2f}×' if pd.notna(latest_bs["Current ratio"]) else "—")

        tab1,tab2,tab3,tab4 = st.tabs(["Balance sheet", "Debt & liquidity", "Cash flow", "Ratios & definitions"])
        with tab1:
            left,right=st.columns(2)
            with left:
                fig=go.Figure()
                fig.add_trace(go.Bar(x=valid["FY"],y=valid["Total assets"],name="Total assets",marker_color="#c7f36b"))
                fig.add_trace(go.Bar(x=valid["FY"],y=valid["Total equity"],name="Total equity",marker_color="#66e0b4"))
                fig.update_layout(title="Assets and equity (₹ crore)",barmode="group")
                st.plotly_chart(chart_layout(fig,350),width="stretch")
            with right:
                fig=go.Figure()
                fig.add_trace(go.Bar(x=valid["FY"],y=valid["Current assets"],name="Current assets",marker_color="#66e0b4"))
                fig.add_trace(go.Bar(x=valid["FY"],y=valid["Current liabilities"],name="Current liabilities",marker_color="#e5b85c"))
                fig.update_layout(title="Current assets vs current liabilities (₹ crore)",barmode="group")
                st.plotly_chart(chart_layout(fig,350),width="stretch")
            show=valid[["FY","Total assets","Current assets","Current liabilities","Total equity"]].copy()
            st.dataframe(show.style.format({c:"{:,.2f}" for c in show.columns if c!="FY"}),width="stretch",hide_index=True)
        with tab2:
            left,right=st.columns(2)
            with left:
                fig=go.Figure()
                fig.add_trace(go.Bar(x=valid["FY"],y=valid["Total borrowings"],name="Total borrowings",marker_color="#e5b85c"))
                fig.add_trace(go.Scatter(x=valid["FY"],y=valid["Net debt/(cash)"],name="Net debt/(cash)",mode="lines+markers",line=dict(color="#c7f36b",width=3)))
                fig.add_hline(y=0,line_color="#8ba597")
                fig.update_layout(title="Borrowings and net debt/(cash) (₹ crore)")
                st.plotly_chart(chart_layout(fig,350),width="stretch")
            with right:
                fig=go.Figure()
                fig.add_trace(go.Scatter(x=valid["FY"],y=valid["Current ratio"],mode="lines+markers",name="Current ratio",line=dict(color="#66e0b4",width=3)))
                fig.add_hline(y=1,line_dash="dash",line_color="#e5b85c",annotation_text="1.0× reference")
                fig.update_layout(title="Current ratio (times)")
                st.plotly_chart(chart_layout(fig,350),width="stretch")
            show=valid[["FY","Total borrowings","Cash and cash equivalents","Net debt/(cash)","Working capital","Current ratio","Debt/equity"]].copy()
            show.columns=["FY","Borrowings (₹ Cr)","Cash equivalents (₹ Cr)","Net debt/(cash) (₹ Cr)","Working capital (₹ Cr)","Current ratio (x)","Debt/equity (x)"]
            st.dataframe(show.style.format({c:"{:,.2f}" for c in show.columns if c!="FY"}),width="stretch",hide_index=True)
        with tab3:
            fig=go.Figure()
            for col,label,color in [("Operating cash flow","Operating cash flow","#c7f36b"),("Investing cash flow","Investing cash flow","#66e0b4"),("Financing cash flow","Financing cash flow","#e5b85c")]:
                fig.add_trace(go.Bar(x=valid["FY"],y=valid[col],name=label,marker_color=color))
            fig.add_hline(y=0,line_color="#8ba597")
            fig.update_layout(title="Cash flow by activity (₹ crore)",barmode="group")
            st.plotly_chart(chart_layout(fig,390),width="stretch")
            cf=valid[["FY","Operating cash flow","Investing cash flow","Financing cash flow","Operating cash flow / revenue %","Operating cash flow / EBITDA %"]].copy()
            cf.columns=["FY","Operating cash flow (₹ Cr)","Investing cash flow (₹ Cr)","Financing cash flow (₹ Cr)","Operating cash flow / revenue %","Operating cash flow / EBITDA %"]
            st.dataframe(cf.style.format({c:"{:,.2f}" for c in cf.columns if c!="FY"}),width="stretch",hide_index=True)
            st.caption("Operating cash flow is the reported net cash from operating activities, after the direct-tax line. Investing/financing flows are reported net totals; their composition can include acquisitions, investments, equity issues and borrowing movements.")
        with tab4:
            st.subheader("Suzlon financial ratios — historical analysis")
            ratio_view = valid.copy()

            # Latest-year KPI cards based on reconciled annual statement data
            ratio_latest = ratio_view.iloc[-1]
            r1, r2, r3, r4 = st.columns(4)
            r1.metric(
                "Current ratio",
                f'{ratio_latest["Current ratio"]:.2f}×'
                if pd.notna(ratio_latest["Current ratio"]) else "N/A"
            )
            r2.metric(
                "Debt / equity",
                f'{ratio_latest["Debt/equity"]:.2f}×'
                if pd.notna(ratio_latest["Debt/equity"]) else "N/A"
            )
            r3.metric(
                "Working capital",
                inr_cr(ratio_latest["Working capital"])
                if pd.notna(ratio_latest["Working capital"]) else "N/A"
            )
            r4.metric(
                "Operating cash flow",
                inr_cr(ratio_latest["Operating cash flow"])
                if pd.notna(ratio_latest["Operating cash flow"]) else "N/A"
            )

            st.markdown("#### Liquidity and leverage trends")
            left_ratio, right_ratio = st.columns(2)
            with left_ratio:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=ratio_view["FY"], y=ratio_view["Current ratio"],
                    name="Current ratio", mode="lines+markers",
                    line=dict(color="#c7f36b", width=3)
                ))
                fig.update_layout(title="Current ratio (×)", yaxis_title="Times")
                st.plotly_chart(chart_layout(fig, 340), width="stretch")
            with right_ratio:
                debt_plot = ratio_view.dropna(subset=["Debt/equity"])
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=debt_plot["FY"], y=debt_plot["Debt/equity"],
                    name="Debt / equity", marker_color="#66e0b4"
                ))
                fig.update_layout(title="Debt-to-equity (×)", yaxis_title="Times")
                st.plotly_chart(chart_layout(fig, 340), width="stretch")

            st.markdown("#### Cash flow and working capital")
            left_cash, right_cash = st.columns(2)
            with left_cash:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=ratio_view["FY"], y=ratio_view["Operating cash flow"],
                    name="Operating cash flow", marker_color="#66e0b4"
                ))
                fig.add_hline(y=0, line_color="#8ba597")
                fig.update_layout(title="Operating cash flow (₹ crore)", yaxis_title="₹ crore")
                st.plotly_chart(chart_layout(fig, 340), width="stretch")
            with right_cash:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=ratio_view["FY"], y=ratio_view["Working capital"],
                    name="Working capital", marker_color="#c7f36b"
                ))
                fig.add_hline(y=0, line_color="#8ba597")
                fig.update_layout(title="Working capital (₹ crore)", yaxis_title="₹ crore")
                st.plotly_chart(chart_layout(fig, 340), width="stretch")

            st.markdown("#### Company ratios — year-by-year")
            ratio_table = ratio_view[[
                "FY", "Current ratio", "Working capital", "Debt/equity",
                "Net debt/(cash)", "Operating cash flow",
                "Operating cash flow / revenue %",
                "Operating cash flow / EBITDA %"
            ]].copy()
            ratio_table.columns = [
                "Financial year", "Current ratio (×)", "Working capital (₹ Cr)",
                "Debt / equity (×)", "Net debt / (cash) (₹ Cr)",
                "Operating cash flow (₹ Cr)", "Operating cash flow / revenue (%)",
                "Operating cash flow / EBITDA (%)"
            ]
            st.dataframe(
                ratio_table.style.format({
                    "Current ratio (×)": "{:.2f}",
                    "Working capital (₹ Cr)": "₹{:,.2f}",
                    "Debt / equity (×)": "{:.2f}",
                    "Net debt / (cash) (₹ Cr)": "₹{:,.2f}",
                    "Operating cash flow (₹ Cr)": "₹{:,.2f}",
                    "Operating cash flow / revenue (%)": "{:.2f}%",
                    "Operating cash flow / EBITDA (%)": "{:.2f}%"
                }, na_rep="N/A"),
                width="stretch", hide_index=True
            )
            st.download_button(
                "⬇ Download company ratios (CSV)",
                ratio_table.to_csv(index=False).encode("utf-8"),
                file_name="suzlon_company_ratios.csv",
                mime="text/csv"
            )

            with st.expander("Ratio definitions and interpretation"):
                st.markdown("""
                - **Current ratio** = current assets ÷ current liabilities.
                - **Working capital** = current assets − current liabilities.
                - **Debt/equity** = total borrowings ÷ positive total equity; unavailable when equity is zero or negative.
                - **Net debt/(cash)** = total borrowings − cash and cash equivalents.
                - **Operating cash flow / revenue** = net operating cash flow ÷ revenue × 100.
                - **Operating cash flow / EBITDA** = net operating cash flow ÷ EBITDA × 100, shown only when EBITDA is positive.

                **Interpretation caution:** Suzlon’s historical equity and current-liability structure changed materially during the turnaround. Compare ratios with the audited statement notes and business context; no single ratio should be used alone to judge solvency.
                """)
        source_view=valid[["FY","Source_note","Source"]].copy()
        source_view.columns=["Financial year","Source / reconciliation note","Official annual report"]
        st.markdown("#### Source register — detailed statements")
        st.dataframe(source_view,width="stretch",hide_index=True,column_config={"Official annual report":st.column_config.LinkColumn("Official annual report",display_text="Open audited report ↗")})
        download_cols=["FY","Year","Total assets","Current assets","Current liabilities","Total borrowings","Cash and cash equivalents","Total equity","Net debt/(cash)","Working capital","Current ratio","Debt/equity","Operating cash flow","Investing cash flow","Financing cash flow","Operating cash flow / revenue %","Operating cash flow / EBITDA %","Source","Source_note"]
        st.download_button("⬇ Download balance sheet, cash-flow & ratios (CSV)",bs[download_cols].to_csv(index=False).encode("utf-8"),file_name="suzlon_finpulse_balance_cashflow_ratios.csv",mime="text/csv")

elif page == "Forecast Studio":
    st.markdown('<div class="section-head">Forecast studio</div><div class="section-sub">An interactive assumption-based scenario tool — not company guidance or an official forecast.</div>',unsafe_allow_html=True)
    st.markdown('<div class="note">Forecasts are illustrative scenarios only. They are calculated from your assumptions and must not be presented as Suzlon guidance or verified future results.</div>',unsafe_allow_html=True)
    x,y,z=st.columns(3)
    with x: growth=st.slider("Annual revenue growth assumption",min_value=-10,max_value=35,value=12,step=1)
    with y: margin=st.slider("Target EBITDA margin (%)",min_value=0.0,max_value=25.0,value=float(latest["EBITDA Margin %"]),step=0.5)
    with z: horizon=st.slider("Projection horizon (years)",min_value=1,max_value=5,value=3)
    base=st.number_input("Starting revenue (₹ crore)",min_value=100.0,max_value=100000.0,value=float(latest["Revenue"]),step=250.0)
    forecast=[]
    for yr in range(1,horizon+1):
        rev=base*((1+growth/100)**yr)
        forecast.append({"Period":f"FY{2026+yr} scenario","Revenue (₹ Cr)":rev,"EBITDA (₹ Cr)":rev*margin/100,"Assumed EBITDA margin %":margin})
    fdf=pd.DataFrame(forecast)
    c1,c2=st.columns([1.3,1])
    with c1:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=["FY2026"]+fdf["Period"].tolist(),y=[base]+fdf["Revenue (₹ Cr)"].tolist(),mode="lines+markers",line=dict(color="#c7f36b",width=4),name="Scenario revenue"))
        fig.update_layout(title="Assumption-based revenue path")
        st.plotly_chart(chart_layout(fig,360),width="stretch")
    with c2:
        st.metric("Revenue at horizon",inr_cr(fdf.iloc[-1]["Revenue (₹ Cr)"]))
        st.metric("EBITDA at horizon",inr_cr(fdf.iloc[-1]["EBITDA (₹ Cr)"]))
        st.dataframe(fdf.style.format({"Revenue (₹ Cr)":"{:,.1f}","EBITDA (₹ Cr)":"{:,.1f}","Assumed EBITDA margin %":"{:.1f}%"}),width="stretch",hide_index=True)
    st.download_button("⬇ Download scenario (CSV)",fdf.to_csv(index=False).encode("utf-8"),file_name="suzlon_finpulse_scenario.csv",mime="text/csv")

else:
    st.markdown('<div class="section-head">Source register & verification</div><div class="section-sub">Every annual observation is linked to the company report/result source used for this dashboard.</div>',unsafe_allow_html=True)
    sources=view[["FY","Source_note","Source"]].copy()
    sources.columns=["Financial year","Data/source note","Official report / results link"]
    st.dataframe(sources,width="stretch",hide_index=True,column_config={"Official report / results link":st.column_config.LinkColumn("Official report / results link",display_text="Open source ↗")})
    st.markdown("#### Data methodology")
    st.markdown("""
    - **Entity/basis:** Suzlon Energy / Suzlon Group consolidated headline financials.
    - **Unit:** ₹ crore. Figures are transcribed from published annual-report highlights and annual results releases.
    - **FY24–FY25:** FY24 comparative and FY25 audited consolidated figures are referenced to the FY2024–25 annual report.
    - **FY26:** revenue, EBITDA and PAT are from Suzlon’s FY2025–26 annual results release; reported PAT includes deferred-tax impact.
    - **Important:** early-year annual report highlights can reflect restatements and accounting-standard changes. Use the linked original report and notes for formal submission or investment decisions.
    - **Scope limitation:** this version intentionally focuses on a comparable 10-year headline series. It does not pretend that detailed 10-year cash flow, debt, liquidity or balance-sheet ratios are verified when those statement lines have not been reconciled here.
    """)
    st.markdown("**Latest quarterly context:** Q2 FY27 release (29 October 2026), shown separately from annual figures.")
    st.link_button("Open official Q2 FY27 results release", Q2_FY27["Source"])
    st.link_button("Open Suzlon official Financial Reports hub","https://www.suzlon.com/investors/financial-reports/")
    st.download_button("⬇ Download full 10-year dataset (CSV)",df.to_csv(index=False).encode("utf-8"),file_name="suzlon_finpulse_10y_data.csv",mime="text/csv")

st.markdown("---")
st.markdown('<div style="color:#81988b;font-size:.78rem">SUZLON FINPULSE · Student financial analytics prototype · Figures in ₹ crore · Sources linked in Source Register · Not investment advice.</div>',unsafe_allow_html=True)
