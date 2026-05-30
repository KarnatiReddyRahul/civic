import streamlit as st
import pandas as pd, numpy as np, random
from datetime import datetime, timedelta

st.set_page_config(page_title="Complaint History · CivicAssist AI", page_icon="📋", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
:root{--navy:#0A1628;--blue:#1A56DB;--text:#1E293B;--muted:#64748B;--border:#E2E8F0;--card-bg:#FFFFFF;--radius:12px;--shadow:0 4px 24px rgba(10,22,40,.08);}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;color:var(--text);}
.main{background:#F8FAFC!important;}.block-container{padding:2rem 2.5rem 3rem!important;max-width:1400px;}
section[data-testid="stSidebar"]{background:var(--navy)!important;}
section[data-testid="stSidebar"] *{color:#CBD5E1!important;}
.ca-card{background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);border:1px solid var(--border);padding:1.5rem;}
.badge{display:inline-block;padding:.22rem .7rem;border-radius:999px;font-size:.72rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;}
.badge-high{background:#FEE2E2;color:#B91C1C;}.badge-medium{background:#FEF3C7;color:#92400E;}.badge-low{background:#D1FAE5;color:#065F46;}
.badge-submitted{background:#E0E7FF;color:#3730A3;}.badge-assigned{background:#FEF9C3;color:#854D0E;}.badge-inprogress{background:#CFFAFE;color:#155E75;}.badge-resolved{background:#D1FAE5;color:#065F46;}
.page-header{background:linear-gradient(135deg,var(--navy) 0%,#1e3a6e 100%);border-radius:14px;padding:2rem 2.5rem;color:#fff;margin-bottom:2rem;}
.page-header h2{font-family:'Playfair Display',serif!important;font-size:1.8rem;margin:0 0 .4rem;color:#fff;}
.page-header p{opacity:.8;margin:0;font-size:.95rem;}
.stButton>button{border-radius:8px!important;font-weight:600!important;}
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

# ── Sample data ────────────────────────────────────────────────────────────────
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
            "Submitted": (base + timedelta(days=random.randint(0,90))).strftime("%d %b %Y"),
            "Description": f"Reported issue regarding {cat.lower()} at {random.choice(locs)}.",
        })
    return pd.DataFrame(rows)

df = get_data()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h2>📋 Complaint History</h2>
  <p>Search, filter, and track all submitted civic complaints. Click any row to view full details.</p>
</div>
""", unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns([3,2,2,2])
with f1:
    search = st.text_input("🔍 Search complaints", placeholder="Search by ID, category, location...")
with f2:
    status_filter = st.selectbox("Status", ["All"] + ["Submitted","Assigned","In Progress","Resolved"])
with f3:
    dept_filter   = st.selectbox("Department", ["All"] + sorted(df["Department"].unique().tolist()))
with f4:
    priority_filter = st.selectbox("Priority", ["All","High","Medium","Low"])

# Apply filters
fdf = df.copy()
if search:
    mask = fdf.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    fdf = fdf[mask]
if status_filter != "All":
    fdf = fdf[fdf["Status"] == status_filter]
if dept_filter != "All":
    fdf = fdf[fdf["Department"] == dept_filter]
if priority_filter != "All":
    fdf = fdf[fdf["Priority"] == priority_filter]

# ── Summary bar ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
  <div style="font-size:.9rem;color:#64748B;">Showing <strong style="color:#1E293B;">{len(fdf)}</strong> complaints</div>
  <div style="display:flex;gap:.5rem;font-size:.8rem;">
    <span class="badge badge-submitted">Submitted: {len(fdf[fdf['Status']=='Submitted'])}</span>
    <span class="badge badge-assigned">Assigned: {len(fdf[fdf['Status']=='Assigned'])}</span>
    <span class="badge badge-inprogress">In Progress: {len(fdf[fdf['Status']=='In Progress'])}</span>
    <span class="badge badge-resolved">Resolved: {len(fdf[fdf['Status']=='Resolved'])}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Pagination ─────────────────────────────────────────────────────────────────
PAGE_SIZE = 12
total_pages = max(1, (len(fdf) - 1) // PAGE_SIZE + 1)
if "history_page" not in st.session_state:
    st.session_state.history_page = 1
page = st.session_state.history_page
start = (page - 1) * PAGE_SIZE
page_df = fdf.iloc[start:start + PAGE_SIZE]

# ── Table ──────────────────────────────────────────────────────────────────────
def priority_badge(p):
    cls = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}.get(p,"")
    return f'<span class="badge {cls}">{p}</span>'

def status_badge(s):
    cls_map = {"Submitted":"badge-submitted","Assigned":"badge-assigned","In Progress":"badge-inprogress","Resolved":"badge-resolved"}
    return f'<span class="badge {cls_map.get(s,"")}">{s}</span>'

rows_html = ""
for _, row in page_df.iterrows():
    rows_html += f"""
    <tr style="border-bottom:1px solid #F1F5F9;transition:background .15s;" onmouseover="this.style.background='#F8FAFC'" onmouseout="this.style.background=''">
      <td style="padding:.75rem 1rem;font-weight:600;color:#1A56DB;">{row['Complaint ID']}</td>
      <td style="padding:.75rem 1rem;">{row['Category']}</td>
      <td style="padding:.75rem 1rem;color:#64748B;">🏢 {row['Department']}</td>
      <td style="padding:.75rem 1rem;">📍 {row['Location']}</td>
      <td style="padding:.75rem 1rem;">{priority_badge(row['Priority'])}</td>
      <td style="padding:.75rem 1rem;">{status_badge(row['Status'])}</td>
      <td style="padding:.75rem 1rem;color:#64748B;">{row['Submitted']}</td>
    </tr>"""

st.markdown(f"""
<div class="ca-card" style="padding:0;overflow:hidden;margin-bottom:1rem;">
<table style="width:100%;border-collapse:collapse;font-size:.87rem;">
  <thead>
    <tr style="background:#F8FAFC;border-bottom:2px solid #E2E8F0;">
      {''.join(f'<th style="padding:.8rem 1rem;text-align:left;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:#64748B;font-weight:700;">{h}</th>' for h in ['Complaint ID','Category','Department','Location','Priority','Status','Date'])}
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── Pagination controls ────────────────────────────────────────────────────────
pc1, pc2, pc3 = st.columns([1,2,1])
with pc1:
    if st.button("← Previous", disabled=(page == 1)):
        st.session_state.history_page = max(1, page - 1)
        st.rerun()
with pc2:
    st.markdown(f"""<div style="text-align:center;font-size:.85rem;color:#64748B;padding:.5rem;">
    Page <strong>{page}</strong> of <strong>{total_pages}</strong> · {len(fdf)} total results</div>""", unsafe_allow_html=True)
with pc3:
    if st.button("Next →", disabled=(page == total_pages)):
        st.session_state.history_page = min(total_pages, page + 1)
        st.rerun()

# ── Detail popup ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("**🔎 View Complaint Detail**")
selected_id = st.selectbox("Select Complaint ID", ["— Select —"] + page_df["Complaint ID"].tolist())

if selected_id != "— Select —":
    row = df[df["Complaint ID"] == selected_id].iloc[0]
    p_cls = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}[row['Priority']]
    s_cls = {"Submitted":"badge-submitted","Assigned":"badge-assigned","In Progress":"badge-inprogress","Resolved":"badge-resolved"}[row['Status']]
    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown(f"""
        <div class="ca-card">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
            <div style="font-size:1rem;font-weight:700;">{row['Complaint ID']}</div>
            <div style="display:flex;gap:.4rem;"><span class="badge {p_cls}">{row['Priority']}</span> <span class="badge {s_cls}">{row['Status']}</span></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-bottom:1rem;">
            <div><div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#94A3B8;margin-bottom:.2rem;">CATEGORY</div><div style="font-weight:600;">{row['Category']}</div></div>
            <div><div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#94A3B8;margin-bottom:.2rem;">DEPARTMENT</div><div style="font-weight:600;color:#1A56DB;">{row['Department']}</div></div>
            <div><div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#94A3B8;margin-bottom:.2rem;">LOCATION</div><div style="font-weight:600;">📍 {row['Location']}</div></div>
            <div><div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#94A3B8;margin-bottom:.2rem;">SUBMITTED</div><div style="font-weight:600;">{row['Submitted']}</div></div>
          </div>
          <div><div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#94A3B8;margin-bottom:.3rem;">DESCRIPTION</div>
          <div style="background:#F8FAFC;border-radius:8px;padding:.8rem;font-size:.9rem;color:#374151;">{row['Description']}</div></div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        timeline_steps = {"Submitted":1,"Assigned":2,"In Progress":3,"Resolved":4}
        current = timeline_steps.get(row["Status"],1)
        steps = [("📤","Submitted"),("👤","Assigned"),("🔧","In Progress"),("✅","Resolved")]
        tl_html = '<div class="ca-card"><div style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#64748B;margin-bottom:1rem;">PROGRESS TIMELINE</div>'
        for i,(icon,label) in enumerate(steps):
            done = i < current
            active = i == current - 1
            color = "#10B981" if done else ("#1A56DB" if active else "#E2E8F0")
            tl_html += f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.7rem;"><div style="width:28px;height:28px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;font-size:.75rem;flex-shrink:0;">{icon if done else ""}</div><div style="font-size:.85rem;font-weight:{"600" if done else "400"};color:{"#1E293B" if done else "#94A3B8"};">{label}</div></div>'
        tl_html += '</div>'
        st.markdown(tl_html, unsafe_allow_html=True)
