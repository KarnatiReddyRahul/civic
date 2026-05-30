import streamlit as st
import pandas as pd, numpy as np, random, plotly.express as px, plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Admin Dashboard · CivicAssist AI", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
:root{--navy:#0A1628;--blue:#1A56DB;--text:#1E293B;--muted:#64748B;--border:#E2E8F0;--card-bg:#FFFFFF;--radius:12px;--shadow:0 4px 24px rgba(10,22,40,.08);}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;color:var(--text);}
.main{background:#F8FAFC!important;}.block-container{padding:2rem 2.5rem 3rem!important;max-width:1400px;}
section[data-testid="stSidebar"]{background:var(--navy)!important;}
section[data-testid="stSidebar"] *{color:#CBD5E1!important;}
.ca-card{background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);border:1px solid var(--border);padding:1.5rem;}
.stat-card{background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);border:1px solid var(--border);padding:1.4rem 1.6rem;position:relative;overflow:hidden;}
.stat-card .accent-bar{position:absolute;top:0;left:0;width:4px;height:100%;border-radius:4px 0 0 4px;}
.stat-card .label{font-size:.78rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:.3rem;}
.stat-card .value{font-size:2rem;font-weight:700;color:var(--text);line-height:1;}
.stat-card .delta{font-size:.8rem;margin-top:.4rem;color:var(--muted);}
.stat-card .icon{position:absolute;right:1.2rem;top:1.2rem;font-size:1.8rem;opacity:.18;}
.section-header{display:flex;align-items:center;gap:.5rem;font-size:1.05rem;font-weight:700;color:var(--text);margin-bottom:.8rem;}
.page-header{background:linear-gradient(135deg,var(--navy) 0%,#1e3a6e 100%);border-radius:14px;padding:2rem 2.5rem;color:#fff;margin-bottom:2rem;}
.page-header h2{font-family:'Playfair Display',serif!important;font-size:1.8rem;margin:0 0 .4rem;color:#fff;}
.page-header p{opacity:.8;margin:0;font-size:.95rem;}
.perf-row{display:flex;align-items:center;gap:.8rem;padding:.6rem 0;border-bottom:1px solid #F1F5F9;}
.perf-bar{height:8px;border-radius:4px;transition:width .3s;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""<div style="padding:1.2rem 1rem .8rem;border-bottom:1px solid rgba(255,255,255,.1);margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:.6rem;"><span style="font-size:1.8rem;">🏛️</span>
      <div><div style="font-size:1rem;font-weight:700;color:#fff;font-family:'Playfair Display',serif;">CivicAssist AI</div>
      <div style="font-size:.7rem;color:#94A3B8;text-transform:uppercase;letter-spacing:.05em;">Citizen Services</div></div></div></div>""", unsafe_allow_html=True)
    st.markdown("**Navigation**")
    st.page_link("app.py",                          label="🏠  Home Dashboard")
    st.page_link("pages/1_Report_Issue.py",         label="📝  Report an Issue")
    st.page_link("pages/2_Complaint_History.py",    label="📋  Complaint History")
    st.page_link("pages/3_Admin_Dashboard.py",      label="📊  Admin Dashboard")
    st.page_link("pages/4_AI_Complaint_View.py",    label="🤖  AI Complaint View")

@st.cache_data
def get_data():
    random.seed(42); np.random.seed(42)
    cats = ["Pothole","Broken Streetlight","Garbage Dump","Water Leakage","Drainage Issue","Road Damage","Encroachment","Noise Pollution"]
    depts = {"Pothole":"Roads & Transport","Broken Streetlight":"Electricity Dept","Garbage Dump":"Sanitation","Water Leakage":"Water Works","Drainage Issue":"Drainage Dept","Road Damage":"Roads & Transport","Encroachment":"Revenue Dept","Noise Pollution":"Police Dept"}
    statuses = ["Submitted","Assigned","In Progress","Resolved"]
    priorities = ["High","Medium","Low"]
    locs = ["Koramangala","Indiranagar","Whitefield","HSR Layout","Jayanagar","Malleswaram","Hebbal","Electronic City","BTM Layout","Marathahalli"]
    rows = []
    base = datetime.now() - timedelta(days=90)
    for i in range(120):
        cat = random.choice(cats)
        rows.append({
            "Complaint ID": f"CA-2025-{1000+i:04d}",
            "Category": cat,
            "Department": depts[cat],
            "Location": random.choice(locs),
            "Priority": random.choices(priorities, weights=[25,50,25])[0],
            "Status": random.choices(statuses, weights=[15,20,30,35])[0],
            "Date": base + timedelta(days=random.randint(0,90)),
            "Resolve Days": random.randint(1,30),
        })
    return pd.DataFrame(rows)

df = get_data()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h2>📊 Admin Dashboard</h2>
  <p>Real-time analytics, department performance metrics, and complaint intelligence for city administrators.</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
total = len(df)
resolved = len(df[df["Status"]=="Resolved"])
avg_resolve = df[df["Status"]=="Resolved"]["Resolve Days"].mean()
high = len(df[df["Priority"]=="High"])

def stat_card(col, icon, label, value, delta, color):
    col.markdown(f"""<div class="stat-card"><div class="accent-bar" style="background:{color};"></div>
    <div class="label">{label}</div><div class="value">{value}</div><div class="delta">{delta}</div><div class="icon">{icon}</div></div>""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
stat_card(c1,"📋","Total Complaints",    total,    "↑ 18 this month",       "#1A56DB")
stat_card(c2,"✅","Resolution Rate",     f"{resolved*100//total}%","↑ 4% from last month",  "#10B981")
stat_card(c3,"⏱️","Avg Resolve Time",   f"{avg_resolve:.1f}d","↓ 2.3 days improvement", "#F59E0B")
stat_card(c4,"🚨","High Priority Open",  high,     "Requires attention",     "#EF4444")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ───────────────────────────────────────────────────────────────
ch1, ch2 = st.columns([3,2])

with ch1:
    st.markdown('<div class="section-header">📈 Weekly Complaint Trends</div>', unsafe_allow_html=True)
    df["Week"] = df["Date"].dt.to_period("W").dt.start_time
    weekly = df.groupby(["Week","Priority"]).size().reset_index(name="Count")
    fig = px.bar(weekly, x="Week", y="Count", color="Priority",
                 color_discrete_map={"High":"#EF4444","Medium":"#F59E0B","Low":"#10B981"},
                 barmode="stack")
    fig.update_layout(
        margin=dict(l=0,r=0,t=10,b=0), height=260,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, title=""),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="DM Sans", size=11),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with ch2:
    st.markdown('<div class="section-header">🏆 Top Issue Categories</div>', unsafe_allow_html=True)
    cat_counts = df["Category"].value_counts().head(6).reset_index()
    cat_counts.columns = ["Category","Count"]
    fig2 = go.Figure(go.Bar(
        x=cat_counts["Count"], y=cat_counts["Category"],
        orientation='h',
        marker_color=["#1A56DB","#3B82F6","#60A5FA","#93C5FD","#BFDBFE","#DBEAFE"],
        text=cat_counts["Count"], textposition="outside",
    ))
    fig2.update_layout(
        margin=dict(l=0,r=40,t=10,b=0), height=260,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        font=dict(family="DM Sans", size=11),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

# ── Charts Row 2 ───────────────────────────────────────────────────────────────
ch3, ch4 = st.columns([2,3])

with ch3:
    st.markdown('<div class="section-header">🏢 Department Performance</div>', unsafe_allow_html=True)
    dept_perf = df.groupby("Department").apply(
        lambda x: round(len(x[x["Status"]=="Resolved"])/len(x)*100,1)
    ).reset_index()
    dept_perf.columns = ["Department","Resolution %"]
    dept_perf = dept_perf.sort_values("Resolution %", ascending=False)

    st.markdown('<div class="ca-card" style="padding:1rem;">', unsafe_allow_html=True)
    for _, row in dept_perf.iterrows():
        pct = row["Resolution %"]
        color = "#10B981" if pct >= 60 else ("#F59E0B" if pct >= 40 else "#EF4444")
        st.markdown(f"""
        <div class="perf-row">
          <div style="flex:1;font-size:.82rem;font-weight:500;color:#1E293B;">{row['Department']}</div>
          <div style="width:80px;">
            <div style="background:#F1F5F9;border-radius:4px;height:8px;overflow:hidden;">
              <div class="perf-bar" style="width:{pct}%;background:{color};"></div>
            </div>
          </div>
          <div style="width:36px;text-align:right;font-size:.78rem;font-weight:600;color:{color};">{pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with ch4:
    st.markdown('<div class="section-header">📍 Complaint Hotspot Map</div>', unsafe_allow_html=True)
    # Bangalore coordinates for demo
    loc_coords = {
        "Koramangala":  (12.9352, 77.6245),
        "Indiranagar":  (12.9784, 77.6408),
        "Whitefield":   (12.9698, 77.7500),
        "HSR Layout":   (12.9116, 77.6389),
        "Jayanagar":    (12.9308, 77.5838),
        "Malleswaram":  (13.0035, 77.5700),
        "Hebbal":       (13.0350, 77.5970),
        "Electronic City":(12.8450, 77.6601),
        "BTM Layout":   (12.9166, 77.6101),
        "Marathahalli": (12.9591, 77.6974),
    }
    map_df = df.groupby("Location").size().reset_index(name="Count")
    map_df["lat"] = map_df["Location"].map(lambda x: loc_coords.get(x,(12.97,77.59))[0]) + np.random.normal(0,.005,len(map_df))
    map_df["lon"] = map_df["Location"].map(lambda x: loc_coords.get(x,(12.97,77.59))[1]) + np.random.normal(0,.005,len(map_df))

    fig3 = px.scatter_mapbox(
        map_df, lat="lat", lon="lon", size="Count",
        color="Count", color_continuous_scale="Blues",
        hover_name="Location", hover_data={"Count":True,"lat":False,"lon":False},
        zoom=11, height=280,
        mapbox_style="carto-positron",
        size_max=35,
    )
    fig3.update_layout(
        margin=dict(l=0,r=0,t=0,b=0),
        coloraxis_showscale=False,
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

# ── Heatmap ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔥 Complaint Heatmap — Category × Location</div>', unsafe_allow_html=True)

heat = df.groupby(["Category","Location"]).size().reset_index(name="Count")
heat_pivot = heat.pivot(index="Category", columns="Location", values="Count").fillna(0)

fig4 = go.Figure(go.Heatmap(
    z=heat_pivot.values,
    x=heat_pivot.columns.tolist(),
    y=heat_pivot.index.tolist(),
    colorscale="Blues",
    text=heat_pivot.values.astype(int),
    texttemplate="%{text}",
    textfont={"size":10},
    showscale=True,
    colorbar=dict(thickness=12, len=1),
))
fig4.update_layout(
    margin=dict(l=0,r=0,t=10,b=0), height=300,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(tickfont=dict(size=10)),
    yaxis=dict(tickfont=dict(size=10)),
    font=dict(family="DM Sans", size=11),
)
st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})

# ── Recent activity feed ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">⚡ Recent Activity</div>', unsafe_allow_html=True)
activities = [
    ("✅","CA-2025-1048 resolved by Roads & Transport Dept","2 min ago","#10B981"),
    ("📋","New complaint CA-2025-1119 submitted — Pothole, Whitefield","8 min ago","#1A56DB"),
    ("🔧","CA-2025-1031 status updated to In Progress","15 min ago","#F59E0B"),
    ("🚨","High priority complaint CA-2025-1052 escalated","28 min ago","#EF4444"),
    ("📧","Automated email dispatched to Water Works Dept","45 min ago","#06B6D4"),
]
act_html = '<div class="ca-card" style="padding:0;overflow:hidden;">'
for icon, msg, time_ago, color in activities:
    act_html += f"""<div style="display:flex;align-items:center;gap:1rem;padding:.9rem 1.2rem;border-bottom:1px solid #F1F5F9;">
    <div style="width:32px;height:32px;border-radius:50%;background:{color}15;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">{icon}</div>
    <div style="flex:1;font-size:.87rem;">{msg}</div>
    <div style="font-size:.75rem;color:#94A3B8;white-space:nowrap;">{time_ago}</div>
    </div>"""
act_html += '</div>'
st.markdown(act_html, unsafe_allow_html=True)
