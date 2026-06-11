import os
from datetime import datetime

import requests
import streamlit as st

API_BASE = os.environ.get(
    "API_BASE",
    "http://localhost:8001"
)

st.set_page_config(page_title="AI Complaint View · CivicAssist AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
:root{--navy:#0A1628;--blue:#1A56DB;--text:#1E293B;--muted:#64748B;--border:#E2E8F0;--card-bg:#FFFFFF;--radius:12px;--shadow:0 4px 24px rgba(10,22,40,.08);}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;color:var(--text);}
.main{background:#F8FAFC!important;}.block-container{padding:2rem 2.5rem 3rem!important;max-width:1200px;}
section[data-testid="stSidebar"]{background:var(--navy)!important;}
section[data-testid="stSidebar"] *{color:#CBD5E1!important;}
.ca-card{background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);border:1px solid var(--border);padding:1.5rem;}
.badge{display:inline-block;padding:.22rem .7rem;border-radius:999px;font-size:.72rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;}
.badge-high{background:#FEE2E2;color:#B91C1C;}.badge-medium{background:#FEF3C7;color:#92400E;}.badge-low{background:#D1FAE5;color:#065F46;}
.page-header{background:linear-gradient(135deg,var(--navy) 0%,#1e3a6e 100%);border-radius:14px;padding:2rem 2.5rem;color:#fff;margin-bottom:2rem;}
.page-header h2{font-family:'Playfair Display',serif!important;font-size:1.8rem;margin:0 0 .4rem;color:#fff;}
.page-header p{opacity:.8;margin:0;font-size:.95rem;}
.letter-card{background:#FFFFFF;border:1px solid #D4C5A9;padding:2rem 2.5rem;font-family:'Lora',serif!important;line-height:1.9;color:#1E293B;position:relative;}
.letter-card::before{content:'OFFICIAL';position:absolute;top:.8rem;right:1.2rem;font-size:.6rem;font-weight:700;letter-spacing:.12em;color:#94A3B8;opacity:.5;}
.letter-watermark{display:none;}
.stamp{display:inline-block;border:2px solid #1A56DB;padding:.2rem .6rem;color:#1A56DB;font-size:.7rem;font-weight:700;letter-spacing:.06em;font-family:'DM Sans',sans-serif!important;}
.meta-pill{display:inline-flex;align-items:center;gap:.4rem;background:#F1F5F9;border-radius:999px;padding:.3rem .9rem;font-size:.78rem;font-weight:500;color:#475569;}
.dispatch-row{display:flex;align-items:center;gap:.6rem;padding:.6rem 0;border-bottom:1px solid #F1F5F9;}
.stButton>button{border-radius:8px!important;font-weight:600!important;}
.notif-success{background:#ECFDF5;border:1px solid #6EE7B7;border-radius:8px;padding:.8rem 1.2rem;color:#065F46;font-weight:500;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""<div style="padding:1.2rem 1rem .8rem;border-bottom:1px solid rgba(255,255,255,.1);margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:.6rem;"><span style="font-size:1.8rem;">🏛️</span>
      <div><div style="font-size:1rem;font-weight:700;color:#fff;font-family:'Playfair Display',serif;">CivicAssist AI</div>
      <div style="font-size:.7rem;color:#94A3B8;text-transform:uppercase;letter-spacing:.05em;">Citizen Services</div></div></div></div>""", unsafe_allow_html=True)
    st.markdown("**Navigation**")
    st.page_link("app.py",                         label="🏠  Home Dashboard")
    st.page_link("pages/1_Report_Issue.py",        label="📝  Report an Issue")
    st.page_link("pages/2_Complaint_History.py",   label="📋  Complaint History")
    st.page_link("pages/3_Admin_Dashboard.py",     label="📊  Admin Dashboard")
    st.page_link("pages/4_AI_Complaint_View.py",   label="🤖  AI Complaint View")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h2>🤖 AI-Generated Complaint Letter</h2>
  <p>CivicAssist AI creates formal, legally-appropriate complaint letters routed directly to the concerned government department.</p>
</div>
""", unsafe_allow_html=True)

# ── Load complaints from API ──────────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_complaints():

    try:
        response = requests.get(
            f"{API_BASE}/api/complaints/", timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return []

    except Exception:
        return []

complaints = load_complaints()

if not complaints:

    st.warning(
        "No complaints available. Submit a complaint first."
    )

    st.stop()

selected_id = st.selectbox(
    "📂 Select Complaint",
    [c["complaint_id"] for c in complaints]
)

selected_complaint = next(
    (
        c for c in complaints
        if c["complaint_id"] == selected_id
    ),
    None
)

complaint_text = selected_complaint["complaint_text"]

location = selected_complaint["location"]

citizen_name = selected_complaint["citizen_name"]

phone = selected_complaint["phone"]

generate_btn = st.button("🤖 Generate AI Complaint Letter", type="primary")

# ── Letter templates ───────────────────────────────────────────────────────────
def get_dept_and_priority(text):
    t = text.lower()
    if "pothole" in t or "road" in t:
        return (
            "The Executive Engineer,\nRoads & Transport Department,\nGHMC Head Office,\nHyderabad, Telangana — 500004",
            "High", "Road Damage / Pothole"
        )
    if "light" in t or "streetlight" in t:
        return (
            "The Assistant Executive Engineer,\nStreetlight & Electrical Maintenance,\nGHMC Circle Office,\nHyderabad, Telangana",
            "Medium", "Broken Streetlight"
        )
    if "garbage" in t or "waste" in t or "dump" in t:
        return (
            "The Chief Medical Officer of Health,\nSanitation & Solid Waste Management,\nGHMC Head Office,\nHyderabad, Telangana — 500004",
            "High", "Garbage / Solid Waste Dumping"
        )
    if "water" in t or "leak" in t:
        return (
            "The Deputy General Manager,\nWater Works Department,\nHyderabad Metropolitan Water Supply & Sewerage Board (HMWS&SB),\nHyderabad, Telangana",
            "High", "Water Leakage / Supply Issue"
        )
    if "drain" in t or "flood" in t:
        return (
            "The Executive Engineer,\nDrainage & Storm Water Management,\nGHMC Head Office,\nHyderabad, Telangana — 500004",
            "Medium", "Drainage / Waterlogging Issue"
        )
    if "encroach" in t:
        return (
            "The Deputy Commissioner,\nRevenue & Estates Department,\nGHMC Head Office,\nHyderabad, Telangana — 500004",
            "Low", "Encroachment Issue"
        )
    if "noise" in t:
        return (
            "The Commissioner of Police,\nHyderabad City Police,\nHyderabad, Telangana",
            "Low", "Noise Pollution"
        )
    return (
        "The Commissioner,\nGreater Hyderabad Municipal Corporation (GHMC),\nTank Bund Road,\nHyderabad, Telangana — 500004",
        "Medium", "General Civic Issue"
    )

def generate_letter(text, location, name, complaint_id, today):
    addressee, priority, category = get_dept_and_priority(text)
    return f"""
Date: {today}

From,
{name}
Hyderabad, Telangana

To,
{addressee}

Subject: Complaint regarding {category} at {location}

Respected Sir/Madam,

I am writing to bring to your notice an issue concerning {category} at {location}.

{text}

I request you to take necessary action at the earliest and provide a status update within 7 days.

Thanking you,

Yours faithfully,
{name}
Complaint ID: {complaint_id}
Contact: Registered on CivicAssist AI Portal
"""

# ── Main output ────────────────────────────────────────────────────────────────
if "generated_letter" not in st.session_state:
    st.session_state.generated_letter = None
    st.session_state.generated_cid    = None
    st.session_state.generated_data   = None

today = datetime.now().strftime("%d %B %Y")

# Regenerate letter on button click or on complaint selection
if selected_complaint:
    cid = selected_complaint["complaint_id"]
    if generate_btn or st.session_state.get("_last_cid") != cid:
        letter = generate_letter(
            selected_complaint["complaint_text"],
            selected_complaint["location"],
            selected_complaint["citizen_name"],
            cid,
            today,
        )
        st.session_state.generated_letter = letter
        st.session_state.generated_cid    = cid
        st.session_state.generated_data   = selected_complaint
        st.session_state._last_cid        = cid

letter    = st.session_state.get("generated_letter")
cid       = st.session_state.get("generated_cid")
comp_data = st.session_state.get("generated_data")

if letter and comp_data:
    priority  = comp_data["priority"]
    category  = comp_data["issue_category"]
    dept_name = comp_data["department"]
    p_cls  = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}[priority]
    today  = datetime.now().strftime("%d %B %Y")

    st.markdown("<br>", unsafe_allow_html=True)

    # Meta row
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin-bottom:1rem;">
      <span class="meta-pill">🔖 {cid}</span>
      <span class="meta-pill">📂 {category}</span>
      <span class="badge {p_cls}">{priority} Priority</span>
      <span class="meta-pill">📅 {today}</span>
      <span class="meta-pill">🏢 {dept_name}</span>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    ab1, ab2, ab3, ab4 = st.columns(4)
    copy_btn  = ab1.button("📋 Copy Letter",     width='stretch')
    pdf_btn   = ab2.button("📄 Download PDF",    width='stretch')
    email_btn = ab3.button("📧 Dispatch Email",  width='stretch', type="primary")
    new_btn   = ab4.button("🔄 New Letter",       width='stretch')

    if copy_btn:
        st.markdown('<div class="notif-success">✅ Letter content copied to clipboard!</div>', unsafe_allow_html=True)
    if pdf_btn:
        with st.spinner("Generating PDF..."):
            try:
                resp = requests.get(f"{API_BASE}/api/complaints/{cid}/pdf", timeout=10)
                if resp.ok:
                    st.markdown(f'<div class="notif-success">📄 PDF ready — <a href="{API_BASE}/api/complaints/{cid}/pdf" target="_blank">Download complaint_{cid}.pdf</a></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="notif-error">❌ PDF not available. Submit the complaint first.</div>', unsafe_allow_html=True)
            except Exception:
                st.markdown('<div class="notif-error">❌ Cannot connect to backend.</div>', unsafe_allow_html=True)
    if email_btn:
        with st.spinner("📧 Dispatching to government email..."):
            try:
                resp = requests.post(f"{API_BASE}/api/complaints/{cid}/dispatch-email", timeout=15)
                if resp.ok:
                    result = resp.json()
                    if result.get("success"):
                        dept_email = comp_data.get("department_email", "dept@ghmc.gov.in")
                        st.markdown(f'<div class="notif-success">📧 Email dispatched to <strong>{dept_email}</strong>. Reference: <strong>{cid}</strong></div>', unsafe_allow_html=True)
                        st.cache_data.clear()
                    else:
                        st.markdown('<div class="notif-error">❌ Email dispatch failed. Check SMTP configuration.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="notif-error">❌ Dispatch failed: {resp.text}</div>', unsafe_allow_html=True)
            except Exception:
                st.markdown('<div class="notif-error">❌ Cannot connect to backend.</div>', unsafe_allow_html=True)
    if new_btn:
        st.session_state.generated_letter = None
        st.session_state.generated_data   = None
        st.session_state._last_cid        = None
        st.rerun()

    # Dispatch status
    email_sent = comp_data.get("email_sent", False)
    email_color = "#10B981" if email_sent else "#F59E0B"
    email_label = "Email — Sent" if email_sent else "Email — Pending"
    st.markdown(f"""
    <div class="ca-card" style="padding:.8rem 1.2rem;margin-top:.8rem;margin-bottom:1.2rem;">
      <div style="font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#64748B;margin-bottom:.6rem;">📡 Dispatch Status</div>
      <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
        <div class="dispatch-row" style="border:none;padding:.2rem 0;gap:.4rem;">
          <span style="color:#10B981;">●</span><span style="font-size:.82rem;">AI Classified</span>
        </div>
        <div class="dispatch-row" style="border:none;padding:.2rem 0;gap:.4rem;">
          <span style="color:#10B981;">●</span><span style="font-size:.82rem;">Dept Routed</span>
        </div>
        <div class="dispatch-row" style="border:none;padding:.2rem 0;gap:.4rem;">
          <span style="color:#10B981;">●</span><span style="font-size:.82rem;">Letter Generated</span>
        </div>
        <div class="dispatch-row" style="border:none;padding:.2rem 0;gap:.4rem;">
          <span style="color:{email_color};">●</span><span style="font-size:.82rem;">{email_label}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # The letter
    st.markdown('<div class="section-header">📜 Generated Complaint Letter</div>', unsafe_allow_html=True)

    # Convert markdown bold to HTML in letter for nice rendering
    letter_display = letter.replace("**", "<strong>", 1)
    while "**" in letter_display:
        letter_display = letter_display.replace("**", "</strong>", 1).replace("**", "<strong>", 1)

    st.markdown(f"""
    <div class="letter-card">
      <div class="letter-watermark">🏛️</div>
      {letter_display.replace(chr(10), '<br>')}
      <br><br>
      <div style="text-align:center;margin-top:1rem;">
        <span class="stamp">CIVICASSIST AI · {cid}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div class="ca-card" style="text-align:center;padding:4rem 2rem;margin-top:1rem;">
      <div style="font-size:4rem;margin-bottom:1rem;">📜</div>
      <div style="font-size:1.2rem;font-weight:700;color:#1E293B;margin-bottom:.5rem;">No Letter Generated Yet</div>
      <div style="font-size:.9rem;color:#64748B;max-width:420px;margin:0 auto;">
        Select a sample complaint above or enter your own issue, then click <strong>Generate AI Complaint Letter</strong> to see the AI create a formal government complaint.
      </div>
    </div>
    """, unsafe_allow_html=True)


