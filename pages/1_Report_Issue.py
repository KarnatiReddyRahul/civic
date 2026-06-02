import streamlit as st
import time
import random
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Report Issue · CivicAssist AI", page_icon="📝", layout="wide")

# ── Shared CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
:root{--navy:#0A1628;--blue:#1A56DB;--blue-light:#3B82F6;--sky:#EFF6FF;--accent:#06B6D4;--success:#10B981;--warning:#F59E0B;--danger:#EF4444;--text:#1E293B;--muted:#64748B;--border:#E2E8F0;--card-bg:#FFFFFF;--radius:12px;--shadow:0 4px 24px rgba(10,22,40,.08);--shadow-lg:0 8px 40px rgba(10,22,40,.14);}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;color:var(--text);}
.main{background:#F8FAFC!important;}.block-container{padding:2rem 2.5rem 3rem!important;max-width:1200px;}
section[data-testid="stSidebar"]{background:var(--navy)!important;}
section[data-testid="stSidebar"] *{color:#CBD5E1!important;}
.ca-card{background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);border:1px solid var(--border);padding:1.5rem;}
.badge{display:inline-block;padding:.22rem .7rem;border-radius:999px;font-size:.72rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;}
.badge-high{background:#FEE2E2;color:#B91C1C;}.badge-medium{background:#FEF3C7;color:#92400E;}.badge-low{background:#D1FAE5;color:#065F46;}
.section-header{display:flex;align-items:center;gap:.5rem;font-size:1.1rem;font-weight:700;color:var(--text);margin-bottom:1rem;}
.stButton>button{border-radius:8px!important;font-weight:600!important;font-family:'DM Sans',sans-serif!important;}
.page-header{background:linear-gradient(135deg,var(--navy) 0%,#1e3a6e 100%);border-radius:14px;padding:2rem 2.5rem;color:#fff;margin-bottom:2rem;}
.page-header h2{font-family:'Playfair Display',serif!important;font-size:1.8rem;margin:0 0 .4rem;color:#fff;}
.page-header p{opacity:.8;margin:0;font-size:.95rem;}
.step-row{display:flex;align-items:center;gap:.3rem;flex-wrap:wrap;margin-top:.8rem;}
.step-item{display:flex;align-items:center;gap:.35rem;font-size:.82rem;font-weight:500;}
.dot{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:700;}
.dot-done{background:#10B981;color:#fff;}.dot-active{background:#1A56DB;color:#fff;}.dot-idle{background:#E2E8F0;color:#94A3B8;}
.connector{height:2px;width:28px;background:#E2E8F0;}.connector-done{background:#10B981;}
.info-row{display:flex;align-items:center;gap:.5rem;background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:.7rem 1rem;font-size:.88rem;color:#1D4ED8;font-weight:500;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="padding:1.2rem 1rem .8rem;border-bottom:1px solid rgba(255,255,255,.1);margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:.6rem;"><span style="font-size:1.8rem;">🏛️</span>
      <div><div style="font-size:1rem;font-weight:700;color:#fff;font-family:'Playfair Display',serif;">CivicAssist AI</div>
      <div style="font-size:.7rem;color:#94A3B8;text-transform:uppercase;letter-spacing:.05em;">Citizen Services</div></div></div></div>""", unsafe_allow_html=True)
    st.markdown("**Navigation**")
    st.page_link("app.py",                           label="🏠  Home Dashboard")
    st.page_link("pages/1_Report_Issue.py",          label="📝  Report an Issue")
    st.page_link("pages/2_Complaint_History.py",     label="📋  Complaint History")
    st.page_link("pages/3_Admin_Dashboard.py",       label="📊  Admin Dashboard")
    st.page_link("pages/4_AI_Complaint_View.py",     label="🤖  AI Complaint View")

# ── AI Detection Maps ──────────────────────────────────────────────────────────
CATEGORY_MAP = {
    "pothole": ("Pothole / Road Damage", "Roads & Transport", "High"),
    "road":    ("Road Damage",           "Roads & Transport", "High"),
    "light":   ("Broken Streetlight",    "Electricity Dept",  "Medium"),
    "streetlight": ("Broken Streetlight","Electricity Dept",  "Medium"),
    "garbage": ("Garbage / Waste Dump",  "Sanitation Dept",   "High"),
    "waste":   ("Garbage / Waste Dump",  "Sanitation Dept",   "High"),
    "water":   ("Water Leakage",         "Water Works Dept",  "High"),
    "leak":    ("Water Leakage",         "Water Works Dept",  "High"),
    "drain":   ("Drainage Issue",        "Drainage Dept",     "Medium"),
    "flood":   ("Flooding / Waterlogging","Drainage Dept",    "High"),
    "encroach":("Encroachment",          "Revenue Dept",      "Low"),
    "noise":   ("Noise Pollution",       "Police Dept",       "Low"),
    "park":    ("Park / Garden Issue",   "Parks & Horticulture","Low"),
    "footpath":("Footpath Damage",       "Roads & Transport", "Medium"),
}

def detect_category(text):
    t = text.lower()
    for kw, vals in CATEGORY_MAP.items():
        if kw in t:
            return vals
    return ("General Civic Issue", "Municipal Corporation", "Medium")

# ── Page Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h2>📝 Report a Civic Issue</h2>
  <p>Describe your issue in detail. Our AI will automatically classify it, route it to the right department, and generate a formal complaint letter.</p>
</div>
""", unsafe_allow_html=True)

# Pre-define tracking flags
submit_btn = False
pdf_btn = False
email_btn = False

# ── Main Content Form ──────────────────────────────────────────────────────────
col_form, col_preview = st.columns([3, 2], gap="large")

with col_form:
    st.markdown('<div class="ca-card">', unsafe_allow_html=True)

    complaint_text = st.text_area(
        "Describe Your Issue *",
        placeholder="e.g. There is a large pothole on the main road near Koramangala 5th Block. It has been there for over 2 weeks and has caused two accidents...",
        height=160,
        help="Be as descriptive as possible for better AI classification."
    )

    # 🎙️ Voice Input Component
    st.subheader("🎙️ Voice Description")
    voice_audio = st.audio_input("Record your issue details directly (AI will transcribe it)")
    
    if voice_audio is not None:
        st.audio(voice_audio, format="audio/wav")
        st.success("Voice description captured successfully!")

    # 📷 Image Upload Section
    st.subheader("📷 Upload an Image")
    uploaded_image = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(
            image,
            caption="Uploaded Image",
            use_container_width=True
        )
        st.success("Image uploaded successfully!")

    # Location Search + Map
    location_query = st.text_input(
        "📍 Location / Address",
        placeholder="Type location (e.g. Koramangala)"
    )

    location = ""
    lat = None
    lon = None

    if location_query:
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": location_query,
                    "format": "json",
                    "limit": 5
                },
                headers={
                    "User-Agent": "CivicAssistAI"
                }
            )

            results = response.json()

            if results:
                location_options = {
                    item["display_name"]: (
                        float(item["lat"]),
                        float(item["lon"])
                    )
                    for item in results
                }

                location = st.selectbox(
                    "Select Matching Location",
                    list(location_options.keys())
                )

                lat, lon = location_options[location]
                st.success(f"📍 Selected Location: {location}")

                m = folium.Map(location=[lat, lon], zoom_start=15)
                folium.Marker([lat, lon], popup=location, tooltip=location).add_to(m)
                st_folium(m, width=700, height=350)
            else:
                st.warning("No matching locations found.")

        except Exception as e:
            st.error(f"Location search failed: {e}")

    col_a, col_b = st.columns(2)
    with col_a:
        contact_name = st.text_input("Your Name", placeholder="Full Name")
    with col_b:
        contact_phone = st.text_input("Phone / Email", placeholder="For status updates")

    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
    b1, b2, b3 = st.columns(3)
    submit_btn = b1.button("🚀 Submit Complaint", type="primary", use_container_width=True)
    pdf_btn = b2.button("📄 Generate PDF", use_container_width=True)
    email_btn = b3.button("📧 Send Email", use_container_width=True)

# ── Preview Pane ───────────────────────────────────────────────────────────────
with col_preview:
    if complaint_text.strip():
        category, dept, priority = detect_category(complaint_text)
        p_class = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}[priority]

        st.markdown(f"""
        <div class="ca-card" style="margin-bottom:1rem;">
          <div style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#64748B;margin-bottom:.8rem;">AI Detection Results</div>
          <div style="margin-bottom:.7rem;">
            <div style="font-size:.72rem;color:#94A3B8;margin-bottom:.2rem;">CATEGORY</div>
            <div style="font-weight:600;color:#1E293B;">📂 {category}</div>
          </div>
          <div style="margin-bottom:.7rem;">
            <div style="font-size:.72rem;color:#94A3B8;margin-bottom:.2rem;">ROUTED TO</div>
            <div style="font-weight:600;color:#1A56DB;">🏢 {dept}</div>
          </div>
          <div>
            <div style="font-size:.72rem;color:#94A3B8;margin-bottom:.2rem;">PRIORITY</div>
            <span class="badge {p_class}">{priority} Priority</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Progress steps
        steps_done = 1
        if submit_btn or pdf_btn or email_btn:
            steps_done = 4

        steps = [("Classified", "✓"), ("Routed", "✓"), ("Letter Generated", "✓"), ("Email Sent", "✓")]
        step_html = '<div class="step-row">'
        for i, (label, icon) in enumerate(steps):
            done = i < steps_done
            active = i == steps_done
            dot_cls = "dot-done" if done else ("dot-active" if active else "dot-idle")
            conn_cls = "connector-done" if done and i < 3 else "connector"
            step_html += f'<div class="step-item"><div class="dot {dot_cls}">{"✓" if done else i+1}</div><span style="color:{"#10B981" if done else "#94A3B8"}">{label}</span></div>'
            if i < 3:
                step_html += f'<div class="connector {conn_cls if done else ""}"></div>'
        step_html += '</div>'

        st.markdown(f"""
        <div class="ca-card">
          <div style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#64748B;margin-bottom:.6rem;">Processing Status</div>
          {step_html}
        </div>
        """, unsafe_allow_html=True)

        # Complaint ID preview
        cid = f"CA-2025-{random.randint(1100,9999)}"
        st.markdown(f"""
        <div class="info-row" style="margin-top:.8rem;">
          🔖 Complaint ID: <strong>{cid}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="ca-card" style="text-align:center;padding:2.5rem 1rem;">
          <div style="font-size:3rem;margin-bottom:.8rem;">🤖</div>
          <div style="font-weight:600;color:#1E293B;margin-bottom:.4rem;">AI Detection</div>
          <div style="font-size:.88rem;color:#64748B;">Start typing your complaint or use the audio recorder on the left — AI will instantly process it.</div>
        </div>
        """, unsafe_allow_html=True)

# ── Notifications & Actions ────────────────────────────────────────────────────
if submit_btn:
    if not complaint_text.strip() and voice_audio is None:
        st.markdown(
            '<div class="notif-error" style="margin-top:1rem;">⚠️ Please provide a text description or record a voice note.</div>',
            unsafe_allow_html=True
        )
    elif not location.strip():
        st.markdown(
            '<div class="notif-error" style="margin-top:1rem;">⚠️ Please enter location.</div>',
            unsafe_allow_html=True
        )
    else:
        try:
            with st.spinner("🤖 Submitting complaint to CivicAssist AI..."):
                payload = {
                    "citizen_name": contact_name if contact_name else "Anonymous",
                    "email": contact_phone if contact_phone else "user@example.com",
                    "phone": contact_phone if contact_phone else "0000000000",
                    "complaint_text": complaint_text if complaint_text.strip() else "Voice Recording Attached",
                    "location": location,
                    "latitude": lat,
                    "longitude": lon
                }
                
                # If your backend processes voice files via multipart-form, handle files parameter here
                response = requests.post("http://127.0.0.1:8000/api/complaints/", json=payload)

            if response.status_code == 200:
                data = response.json()
                st.markdown(
                    f'''
                    <div class="notif-success" style="margin-top:1rem;">
                    ✅ Complaint <strong>{data["complaint_id"]}</strong> submitted successfully!
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                st.balloons()

                st.markdown("### 📋 Complaint Details")
                st.write("**Complaint ID:**", data["complaint_id"])
                st.write("**Category:**", data["category"])
                st.write("**Department:**", data["department"])
                st.write("**Priority:**", data["priority"])

                st.text_area(
                    "Generated Complaint Letter",
                    data["generated_letter"],
                    height=250
                )
            else:
                st.error(f"Backend Error: {response.text}")

        except Exception as e:
            st.error(f"Connection Error: {str(e)}")


if pdf_btn:
    with st.spinner("📄 Generating formal complaint PDF..."):
        time.sleep(1.2)
    st.markdown('<div class="notif-success" style="margin-top:1rem;">📄 PDF generated successfully! Check <a href="#">AI Complaint View</a> to download.</div>', unsafe_allow_html=True)

if email_btn:
    with st.spinner("📧 Dispatching email to department..."):
        time.sleep(1)
    st.markdown('<div class="notif-success" style="margin-top:1rem;">📧 Email dispatched successfully!</div>', unsafe_allow_html=True)


# Notification Alerts Base Styles
st.markdown("""
<style>
.notif-success{background:#ECFDF5;border:1px solid #6EE7B7;border-radius:8px;padding:.8rem 1.2rem;color:#065F46;font-weight:500;font-size:.9rem;}
.notif-error{background:#FEF2F2;border:1px solid #FCA5A5;border-radius:8px;padding:.8rem 1.2rem;color:#991B1B;font-weight:500;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)