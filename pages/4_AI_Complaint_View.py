import streamlit as st
import requests
import time
from datetime import datetime

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
.letter-card{background:#FDFCF7;border:1px solid #D4C5A9;border-radius:14px;padding:2.5rem 3rem;font-family:'Lora',serif!important;line-height:1.9;color:#1E293B;position:relative;}
.letter-card::before{content:'OFFICIAL COMPLAINT';position:absolute;top:1rem;right:1.5rem;font-size:.65rem;font-weight:700;letter-spacing:.12em;color:#94A3B8;opacity:.5;}
.letter-watermark{position:absolute;bottom:2rem;right:2rem;opacity:.06;font-size:4rem;}
.stamp{display:inline-block;border:3px solid #1A56DB;border-radius:4px;padding:.3rem .8rem;color:#1A56DB;font-size:.75rem;font-weight:700;letter-spacing:.08em;transform:rotate(-3deg);opacity:.7;}
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

# ── Demo input or use a pre-loaded example ────────────────────────────────────
@st.cache_data(ttl=10)
def load_complaints():

    try:

        response = requests.get(
            "http://127.0.0.1:8000/api/complaints/"
        )

        if response.status_code == 200:
            return response.json()

        return []

    except:
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
    if "pothole" in t or "road" in t: return "The Executive Engineer, Roads & Transport Department, BBMP", "High", "Pothole / Road Damage"
    if "light" in t: return "The Assistant Executive Engineer, Electricity Department, BBMP", "Medium", "Broken Streetlight"
    if "garbage" in t or "waste" in t or "dump" in t: return "The Health Officer, Sanitation Department, BBMP", "High", "Garbage / Waste Dump"
    if "water" in t or "leak" in t: return "The Assistant Engineer, Water Works Department, BWSSB", "High", "Water Leakage"
    if "drain" in t: return "The Assistant Executive Engineer, Drainage Department, BBMP", "Medium", "Drainage Issue"
    return "The Commissioner, Bruhat Bengaluru Mahanagara Palike (BBMP)", "Medium", "General Civic Issue"

def generate_letter(text, location, name, complaint_id, today):
    addressee, priority, category = get_dept_and_priority(text)
    return f"""
{today}

To,
{addressee},
Bengaluru Municipal Corporation,
Bengaluru, Karnataka — 560001.

Subject: **Formal Complaint Regarding {category} at {location} — Urgent Action Requested**

Respected Sir/Madam,

I, **{name}**, a resident of Bengaluru and a law-abiding citizen, wish to draw your kind attention to a pressing civic issue that has been adversely affecting daily life in the community at **{location}**.

The issue pertains to: **{text[:200]}{'...' if len(text)>200 else ''}**

This problem has been persisting for a considerable period of time and, despite being a matter of significant public concern, has not been adequately addressed. The situation poses risks to public safety, health, and the general well-being of residents in the area. It has caused inconvenience to commuters, pedestrians, and families — including senior citizens and children.

I humbly request your immediate intervention and corrective action in accordance with the provisions of the Bruhat Bengaluru Mahanagara Palike Act, 2020, and the Karnataka Municipal Corporations Act, 1976. The issue has been assigned **{priority} Priority** by the CivicAssist AI system (Complaint ID: **{complaint_id}**).

I request that:
1. An inspection team be deputed at the earliest to assess the ground situation.
2. Necessary repair / remedial work be initiated on a priority basis.
3. A status update be provided to the undersigned within **7 working days**.

Kindly treat this as urgent and acknowledge receipt of this complaint.

Thanking you in anticipation of your prompt action.

Yours sincerely,
**{name}**
Contact: Registered via CivicAssist AI Portal
Complaint ID: **{complaint_id}**
Date: {today}

---
*Generated by CivicAssist AI — India's AI-Powered Citizen Services Platform*
*This is an official complaint letter. Kindly route to the appropriate authority.*
"""

# ── Main output ────────────────────────────────────────────────────────────────
if "generated_letter" not in st.session_state:
    st.session_state.generated_letter = None
    st.session_state.generated_cid    = None

if selected_complaint:

    st.session_state.generated_letter = (
        selected_complaint["generated_letter"]
    )

    st.session_state.generated_cid = (
        selected_complaint["complaint_id"]
    )

if st.session_state.generated_letter:
    letter = st.session_state.generated_letter
    cid    = st.session_state.generated_cid
    priority = selected_complaint["priority"]
    category = selected_complaint["issue_category"]
    addressee = selected_complaint["department"]
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
      <span class="meta-pill">🏢 {addressee.split(',')[0]}</span>
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
            time.sleep(1)
        st.markdown('<div class="notif-success">📄 PDF ready — <strong>civicassist_complaint_{}.pdf</strong> downloaded.</div>'.format(cid), unsafe_allow_html=True)
    if email_btn:
        with st.spinner("📧 Dispatching to government email..."):
            time.sleep(1.5)
        st.markdown(f'<div class="notif-success">📧 Email dispatched to <strong>{selected_complaint["department_email"]}</strong>. Reference: <strong>{cid}</strong></div>', unsafe_allow_html=True)
    if new_btn:
        st.session_state.generated_letter = None
        st.rerun()

    # Dispatch status
    st.markdown("""
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
          <span style="color:#F59E0B;">●</span><span style="font-size:.82rem;">Email — Pending</span>
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

# ── How it works ───────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="font-size:1rem;font-weight:700;color:#1E293B;margin-bottom:.8rem;">⚙️ How CivicAssist AI Works</div>', unsafe_allow_html=True)

steps = [
    ("1","🗣️","Citizen Describes Issue","Plain language input — text or voice"),
    ("2","🧠","AI Classifies","NLP detects category, priority, and relevant department"),
    ("3","📝","Letter Generated","Formal, legally-framed complaint letter created instantly"),
    ("4","📧","Auto-Dispatched","Email sent directly to concerned government department"),
    ("5","🔔","Track Progress","Real-time status updates via SMS and portal"),
]
cols = st.columns(5)
for col, (num, icon, title, desc) in zip(cols, steps):
    col.markdown(f"""
    <div class="ca-card" style="text-align:center;padding:1.2rem .8rem;">
      <div style="font-size:1.6rem;margin-bottom:.4rem;">{icon}</div>
      <div style="background:#EFF6FF;color:#1A56DB;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;margin:0 auto .5rem;">{num}</div>
      <div style="font-weight:600;font-size:.85rem;margin-bottom:.25rem;">{title}</div>
      <div style="font-size:.75rem;color:#64748B;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
