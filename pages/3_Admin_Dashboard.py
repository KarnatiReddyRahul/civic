import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from backend.db_helper import (
    get_all_complaints,
    update_complaint_status
)

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

# ── Sample data / backend fetch ─────────────────────────────────────────────────
@st.cache_data(ttl=5)
def get_data():
    complaints = get_all_complaints()

    rows = []

    for c in complaints:

        rows.append({
            "Complaint ID": c.complaint_id,
            "Category": c.issue_category,
            "Department": c.department,
            "Location": c.location,
            "Priority": c.priority,
            "Status": c.status,
            "Date": pd.to_datetime(c.created_at),
            "Submitted": str(c.created_at)[:10],
            "Resolve Days": None,
            "Description": c.complaint_text
        })

    return pd.DataFrame(rows)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h2>📊 Admin Dashboard</h2>
  <p>Real-time analytics, department performance metrics, and complaint intelligence for city administrators.</p>
</div>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
df = get_data()

if df.empty:
    st.warning("No complaints found.")
    st.stop()

# ── KPI Cards ──────────────────────────────────────────────────────────────────
total = len(df)
resolved = len(df[df["Status"]=="Resolved"])
avg_resolve = df[df["Status"]=="Resolved"]["Resolve Days"].mean() if resolved > 0 else 0
high = len(df[df["Priority"]=="High"])

def stat_card(col, icon, label, value, delta, color):
    col.markdown(f"""<div class="stat-card"><div class="accent-bar" style="background:{color};"></div>
    <div class="label">{label}</div><div class="value">{value}</div><div class="delta">{delta}</div><div class="icon">{icon}</div></div>""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
stat_card(c1,"📋","Total Complaints",    total,    "↑ 18 this month",       "#1A56DB")
resolution_rate = 0

if total > 0:
    resolution_rate = round((resolved / total) * 100)

stat_card(
    c2,
    "✅",
    "Resolution Rate",
    f"{resolution_rate}%",
    "↑ 4% from last month",
    "#10B981"
)
stat_card(c3,"⏱️","Avg Resolve Time",   f"{avg_resolve:.1f}d","↓ 2.3 days improvement", "#F59E0B")
stat_card(c4,"🚨","High Priority Open",  high,     "Requires attention",     "#EF4444")

st.markdown("<br>", unsafe_allow_html=True)

st.subheader("🛠 Complaint Status Management")

st.dataframe(
    df[[
        "Complaint ID",
        "Category",
        "Department",
        "Location",
        "Priority",
        "Status"
    ]],
    use_container_width=True
)

complaint_id = st.selectbox(
    "Select Complaint ID",
    df["Complaint ID"].tolist()
)
selected_row = df[
    df["Complaint ID"] == complaint_id
]
if not selected_row.empty:

    st.info(
        f"📍 Location: {selected_row.iloc[0]['Location']}"
    )

    st.info(
        f"🏢 Department: {selected_row.iloc[0]['Department']}"
    )

    st.info(
        f"⚡ Priority: {selected_row.iloc[0]['Priority']}"
    )
new_status = st.selectbox(
    "Update Status",
    [
        "Submitted",
        "Assigned",
        "In Progress",
        "Resolved",
        "Rejected"
    ]
)

if st.button("✅ Update Status"):

    complaint = update_complaint_status(
        complaint_id,
        new_status
    )

    if complaint:

        st.success(
            f"Complaint {complaint_id} updated successfully!"
        )

        st.cache_data.clear()

        st.rerun()

    else:

        st.error(
            "Complaint not found"
        )

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
    st.plotly_chart(fig, width='stretch', config={"displayModeBar":False})

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
    st.plotly_chart(fig2, width='stretch', config={"displayModeBar":False})

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
    # Hyderabad location coordinates
    loc_coords = {
        "Miyapur": (17.4948, 78.3915),
        "Miyapur Metro Station": (17.4960, 78.3919),
        "Gachibowli": (17.4401, 78.3489),
        "Kukatpally": (17.4849, 78.4138),
        "Hitech City": (17.4435, 78.3772),
        "Madhapur": (17.4486, 78.3908),
        "Ameerpet": (17.4375, 78.4483),
        "Secunderabad": (17.4399, 78.4983),
        "LB Nagar": (17.3457, 78.5520),
        "Uppal": (17.4058, 78.5591),
        "Banjara Hills": (17.4126, 78.4482),
        "Jubilee Hills": (17.4326, 78.4071),
    }
    
    selected_location = selected_row.iloc[0]["Location"]

    if selected_location in loc_coords:
        lat, lon = loc_coords[selected_location]

        map_df = pd.DataFrame({
            "Location": [selected_location],
            "lat": [lat],
            "lon": [lon]
        })

        fig3 = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            hover_name="Location",
            zoom=14,
            height=350,
            mapbox_style="carto-positron"
        )
        fig3.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=False,
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig3, width='stretch', config={"displayModeBar": False})
    else:
        st.info(f"Map coordinates not available for {selected_location}")

