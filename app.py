import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.db_utils import get_all_complaints

st.set_page_config(
    page_title="CivicAssist AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

/* ── Root tokens ── */
:root {
  --navy:       #0A1628;
  --blue:       #1A56DB;
  --blue-light: #3B82F6;
  --sky:        #EFF6FF;
  --accent:     #06B6D4;
  --success:    #10B981;
  --warning:    #F59E0B;
  --danger:     #EF4444;
  --text:       #1E293B;
  --muted:      #64748B;
  --border:     #E2E8F0;
  --card-bg:    #FFFFFF;
  --radius:     12px;
  --shadow:     0 4px 24px rgba(10,22,40,.08);
  --shadow-lg:  0 8px 40px rgba(10,22,40,.14);
}

/* ── Base resets ── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text);
}
.main { background: #F8FAFC !important; }
.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--navy) !important;
  border-right: none !important;
}

section[data-testid="stSidebar"] * {
  color: #CBD5E1 !important;
}

section[data-testid="stSidebar"] .sidebar-logo {
  padding: 1.5rem 1rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,.1);
  margin-bottom: 1rem;
}

section[data-testid="stSidebar"] a {
  display: block;
  padding: .85rem 1rem;
  margin: .18rem 0;
  border-radius: 12px;
  color: #CBD5E1 !important;
  background: rgba(255,255,255,.04);
  text-decoration: none !important;
}

section[data-testid="stSidebar"] a:hover {
  color: #fff !important;
  background: rgba(255,255,255,.12);
}

section[data-testid="stSidebar"] a[aria-current="page"] {
  color: #fff !important;
  background: rgba(255,255,255,.16);
}
}
.page-nav-row {
  display: flex;
  flex-wrap: wrap;
  gap: .6rem;
  justify-content: center;
  margin: 1rem 0 1.6rem;
}
.page-nav-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 150px;
  padding: .9rem 1.2rem;
  border-radius: 999px;
  background: rgba(255,255,255,.95);
  color: #0A1628 !important;
  text-decoration: none !important;
  font-size: .95rem;
  font-weight: 600;
  border: 1px solid rgba(15,23,42,.08);
}
.page-nav-pill:hover {
  background: #fff;
}
.page-nav-pill.active {
  background: #e2e8f0;
  color: #0A1628 !important;
  border-color: rgba(15,23,42,.12);
}
/* active nav item highlight */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  font-size: .92rem;
  line-height: 1.4;
}

/* ── Cards ── */
.ca-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  padding: 1.5rem;
  transition: box-shadow .2s;
}
.ca-card:hover { box-shadow: var(--shadow-lg); }

/* ── Stat cards ── */
.stat-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  padding: 1.4rem 1.6rem;
  position: relative;
  overflow: hidden;
}
.stat-card .accent-bar {
  position: absolute; top: 0; left: 0;
  width: 4px; height: 100%;
  border-radius: 4px 0 0 4px;
}
.stat-card .label {
  font-size: .78rem; font-weight: 600;
  letter-spacing: .06em; text-transform: uppercase;
  color: var(--muted); margin-bottom: .3rem;
}
.stat-card .value {
  font-size: 2rem; font-weight: 700; color: var(--text); line-height: 1;
}
.stat-card .delta {
  font-size: .8rem; margin-top: .4rem; color: var(--muted);
}
.stat-card .icon {
  position: absolute; right: 1.2rem; top: 1.2rem;
  font-size: 1.8rem; opacity: .18;
}

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: .22rem .7rem;
  border-radius: 999px;
  font-size: .72rem; font-weight: 600;
  letter-spacing: .04em; text-transform: uppercase;
}
.badge-high   { background: #FEE2E2; color: #B91C1C; }
.badge-medium { background: #FEF3C7; color: #92400E; }
.badge-low    { background: #D1FAE5; color: #065F46; }
.badge-submitted  { background: #E0E7FF; color: #3730A3; }
.badge-assigned   { background: #FEF9C3; color: #854D0E; }
.badge-inprogress { background: #CFFAFE; color: #155E75; }
.badge-resolved   { background: #D1FAE5; color: #065F46; }

/* ── Progress steps ── */
.steps { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
.step  {
  display: flex; align-items: center; gap: .4rem;
  font-size: .8rem; font-weight: 500;
}
.step-dot {
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .65rem; font-weight: 700;
}
.step-dot.done  { background: var(--success); color: #fff; }
.step-dot.active{ background: var(--blue); color: #fff; }
.step-dot.idle  { background: var(--border); color: var(--muted); }
.step-line { flex: 1; height: 2px; background: var(--border); min-width: 20px; }
.step-line.done { background: var(--success); }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, var(--navy) 0%, #1e3a6e 60%, #1A56DB 100%);
  border-radius: 16px;
  padding: 3rem 3.5rem;
  color: #fff;
  position: relative;
  overflow: hidden;
  margin-bottom: 2rem;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero h1 {
  font-family: 'Playfair Display', serif !important;
  font-size: 2.4rem; font-weight: 700;
  margin: 0 0 .6rem; color: #fff;
}
.hero p { font-size: 1.05rem; opacity: .85; max-width: 560px; margin: 0; }
.hero-badge {
  display: inline-flex; align-items: center; gap: .4rem;
  background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 999px;
  padding: .3rem 1rem;
  font-size: .78rem; font-weight: 600;
  letter-spacing: .06em; text-transform: uppercase;
  color: #fff; margin-bottom: 1rem;
}

/* ── Section headers ── */
.section-header {
  display: flex; align-items: center; gap: .5rem;
  font-size: 1.1rem; font-weight: 700; color: var(--text);
  margin-bottom: 1rem;
}
.section-header::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

/* ── Table overrides ── */
[data-testid="stDataFrame"] { border-radius: var(--radius) !important; overflow: hidden; }

/* ── Buttons ── */
.stButton > button {
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stButton > button[kind="primary"] {
  background: var(--blue) !important;
  border-color: var(--blue) !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  border-radius: 8px !important;
  border-color: var(--border) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── Footer ── */
.ca-footer {
  margin-top: 4rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  text-align: center;
  font-size: .8rem;
  color: var(--muted);
}

/* ── Complaint letter card ── */
.letter-card {
  background: #FAFBFF;
  border: 1px solid #C7D7F9;
  border-radius: var(--radius);
  padding: 2rem 2.5rem;
  font-family: 'DM Sans', sans-serif;
  line-height: 1.8;
  font-size: .95rem;
}

/* ── Notification ── */
.notif-success {
  background: #ECFDF5; border: 1px solid #6EE7B7;
  border-radius: 8px; padding: .8rem 1.2rem;
  color: #065F46; font-weight: 500; font-size: .9rem;
}
.notif-error {
  background: #FEF2F2; border: 1px solid #FCA5A5;
  border-radius: 8px; padding: .8rem 1.2rem;
  color: #991B1B; font-weight: 500; font-size: .9rem;
}

/* ── Map placeholder ── */
.map-placeholder {
  background: linear-gradient(135deg, #e0e7ff 0%, #bfdbfe 100%);
  border-radius: var(--radius);
  height: 320px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: var(--blue); font-size: 1rem; font-weight: 600;
  gap: .5rem;
}

/* ── Metric delta override ── */
[data-testid="stMetricDelta"] { font-size: .78rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div style="display:flex;align-items:center;gap:.7rem;">
        <span style="font-size:2rem;">🏛️</span>
        <div>
          <div style="font-size:1.1rem;font-weight:700;color:#fff;font-family:'Playfair Display',serif;">CivicAssist AI</div>
          <div style="font-size:.72rem;color:#94A3B8;letter-spacing:.05em;text-transform:uppercase;">Citizen Services Platform</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Navigation**")
    st.page_link("app.py",            label="🏠  Home Dashboard",         )
    st.page_link("pages/1_Report_Issue.py",       label="📝  Report an Issue"       )
    st.page_link("pages/2_Complaint_History.py",  label="📋  Complaint History"     )
    st.page_link("pages/3_Admin_Dashboard.py",    label="📊  Admin Dashboard"       )
    st.page_link("pages/4_AI_Complaint_View.py",  label="🤖  AI Complaint View"     )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:.78rem;color:#64748B;padding:.5rem 0;">
      <div style="margin-bottom:.4rem;">🔒 Secure Government Portal</div>
      <div>v2.4.1 · © 2025 CivicAssist</div>
    </div>
    """, unsafe_allow_html=True)

# ── Shared data (cached) ───────────────────────────────────────────────────────


@st.cache_data(ttl=10)
def fetch_complaints():
    try:
        complaints = get_all_complaints()

        rows = []
        for c in complaints:
            created_at = c.get("created_at", "")
            submitted = str(created_at)[:10] if created_at else ""
            rows.append({
                "Complaint ID": c.get("complaint_id", "N/A"),
                "Category": c.get("issue_category", "Unknown"),
                "Department": c.get("department", "Unknown"),
                "Location": c.get("location", "Unknown"),
                "Priority": c.get("priority", "Medium"),
                "Status": c.get("status", "Submitted"),
                "Submitted": submitted,
                "Date": pd.to_datetime(created_at, errors="coerce"),
                "Citizen": c.get("citizen_name", ""),
                "Description": c.get("complaint_text", ""),
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df["Submitted"] = pd.to_datetime(df["Submitted"], errors="coerce").dt.strftime("%d %b %Y")
            df["_date"] = pd.to_datetime(df["Submitted"], format="%d %b %Y", errors="coerce")
        df = df.sort_values("_date", ascending=False)
        return df
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return pd.DataFrame()


df = fetch_complaints()
if df.empty:
    st.warning("No complaints available.")
    st.stop()

# ── HOME DASHBOARD ─────────────────────────────────────────────────────────────
# Hero
st.markdown("""
<div class="hero">
  <div class="hero-badge">🚀 AI-Powered · Real-Time · Civic Intelligence</div>
  <h1>CivicAssist AI</h1>
  <p>India's most intelligent citizen service platform — report civic issues, track resolutions, and hold departments accountable with the power of AI.</p>
</div>
""", unsafe_allow_html=True)


# Stats
total     = len(df)
resolved  = len(df[df["Status"] == "Resolved"])
pending   = len(df[df["Status"].isin(["Submitted","Assigned","In Progress"])])
high_pri  = len(df[df["Priority"] == "High"])

c1, c2, c3, c4 = st.columns(4)
def stat_card(col, icon, label, value, delta, color):
    col.markdown(f"""
    <div class="stat-card">
      <div class="accent-bar" style="background:{color};"></div>
      <div class="label">{label}</div>
      <div class="value">{value}</div>
      <div class="delta">{delta}</div>
      <div class="icon">{icon}</div>
    </div>
    """, unsafe_allow_html=True)

stat_card(c1, "📋", "Total Complaints",    total,    "↑ 18 this week",      "#1A56DB")
stat_card(c2, "✅", "Resolved Complaints", resolved, f"↑ {resolved*100//total}% resolution rate", "#10B981")
stat_card(c3, "⏳", "Pending Complaints",  pending,  "↓ 5 from last week",  "#F59E0B")
stat_card(c4, "🚨", "High Priority",       high_pri, "Needs immediate action","#EF4444")

st.markdown("<br>", unsafe_allow_html=True)

# Charts row
left, right = st.columns([3, 2])

with left:
    st.markdown('<div class="section-header">📈 Complaint Trends (Last 90 Days)</div>', unsafe_allow_html=True)
    df["_date"] = pd.to_datetime(df["Submitted"], format="%d %b %Y")
    trend = df.groupby("_date").size().reset_index(name="count")
    trend = trend.sort_values("_date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["_date"], y=trend["count"],
        mode="lines", fill="tozeroy",
        line=dict(color="#1A56DB", width=2.5),
        fillcolor="rgba(26,86,219,.1)",
        name="Complaints"
    ))
    fig.update_layout(
        margin=dict(l=0,r=0,t=10,b=0), height=240,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        font=dict(family="DM Sans", size=11),
        showlegend=False,
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

with right:
    st.markdown('<div class="section-header">🏢 By Department</div>', unsafe_allow_html=True)
    dept_counts = df["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Count"]
    fig2 = px.pie(dept_counts, values="Count", names="Department",
                  color_discrete_sequence=px.colors.sequential.Blues_r,
                  hole=.45)
    fig2.update_layout(
        margin=dict(l=0,r=0,t=0,b=0), height=240,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", size=10),
        legend=dict(font_size=10, orientation="v"),
        showlegend=True,
    )
    fig2.update_traces(textinfo="percent", textfont_size=10)
    st.plotly_chart(fig2, width='stretch', config={"displayModeBar": False})

# Recent complaints table
st.markdown('<div class="section-header">🗒️ Recent Complaints</div>', unsafe_allow_html=True)

def priority_badge(p):
    cls = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}.get(p,"")
    return f'<span class="badge {cls}">{p}</span>'

def status_badge(s):
    cls = {"Submitted":"badge-submitted","Assigned":"badge-assigned","In Progress":"badge-inprogress","Resolved":"badge-resolved"}.get(s,"")
    return f'<span class="badge {cls}">{s}</span>'

recent = df.head(8)[["Complaint ID","Category","Location","Priority","Status","Submitted"]]
# render as styled HTML table
rows_html = ""
for _, row in recent.iterrows():
    rows_html += f"""
    <tr>
      <td style="font-weight:600;color:#1A56DB;">{row['Complaint ID']}</td>
      <td>{row['Category']}</td>
      <td>📍 {row['Location']}</td>
      <td>{priority_badge(row['Priority'])}</td>
      <td>{status_badge(row['Status'])}</td>
      <td style="color:#64748B;">{row['Submitted']}</td>
    </tr>"""

st.markdown(f"""
<div class="ca-card" style="padding:0;overflow:hidden;">
<table style="width:100%;border-collapse:collapse;font-size:.87rem;">
  <thead>
    <tr style="background:#F8FAFC;border-bottom:1px solid #E2E8F0;">
      <th style="padding:.8rem 1rem;text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#64748B;font-weight:600;">ID</th>
      <th style="padding:.8rem 1rem;text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#64748B;font-weight:600;">Category</th>
      <th style="padding:.8rem 1rem;text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#64748B;font-weight:600;">Location</th>
      <th style="padding:.8rem 1rem;text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#64748B;font-weight:600;">Priority</th>
      <th style="padding:.8rem 1rem;text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#64748B;font-weight:600;">Status</th>
      <th style="padding:.8rem 1rem;text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#64748B;font-weight:600;">Date</th>
    </tr>
  </thead>
  <tbody>
    {"".join('<tr style="border-bottom:1px solid #F1F5F9;">' + row + '</tr>' for row in rows_html.split('</tr>') if '<tr' in row)}
  </tbody>
</table>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="ca-footer">
  🏛️ CivicAssist AI · Empowering Citizens, Improving Cities · Built for India's Digital Governance Future<br>
  <span style="opacity:.6;">Data refreshed every 15 minutes · Powered by AI</span>
</div>
""", unsafe_allow_html=True)
