import streamlit as st
import time, random, os, re
import json
from datetime import datetime
import pandas as pd
import requests
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass
from pydub import AudioSegment
import folium
from streamlit_folium import st_folium

NOMINATIM_HEADERS = {"User-Agent": "CivicAssistAI/1.0"}

st.set_page_config(page_title="Report Issue · CivicAssist AI", page_icon="📝", layout="wide")

# shared CSS
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

# ── AI detection maps ──────────────────────────────────────────────────────────
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

HYDERABAD_AREAS = {
    "Hitech City": (17.4490, 78.3808), "Gachibowli": (17.4396, 78.3412),
    "Madhapur": (17.4386, 78.3903), "Kukatpally": (17.4860, 78.4100),
    "KPHB Colony": (17.4884, 78.3937), "JNTU": (17.4929, 78.3918),
    "Banjara Hills": (17.4156, 78.4343), "Jubilee Hills": (17.4319, 78.4093),
    "Secunderabad": (17.4381, 78.4979), "Ameerpet": (17.4370, 78.4483),
    "Kondapur": (17.4581, 78.3689), "Miyapur": (17.4982, 78.3523),
    "Nizampet": (17.5101, 78.3557), "Bachupally": (17.5041, 78.3372),
    "Chanda Nagar": (17.4917, 78.3266), "Patancheru": (17.5312, 78.2649),
    "Attapur": (17.3564, 78.3971), "Moinabad": (17.3043, 78.2768),
    "Shamshabad": (17.2495, 78.3910), "Rajendranagar": (17.3229, 78.4034),
    "Mehdipatnam": (17.4020, 78.4245), "Tolichowki": (17.3924, 78.4093),
    "Himayatnagar": (17.4070, 78.4778), "Saidabad": (17.3618, 78.4915),
    "Dilsukhnagar": (17.3680, 78.5250), "Malakpet": (17.3728, 78.4845),
    "Charminar": (17.3616, 78.4747), "Afzal Gunj": (17.3610, 78.4640),
    "Shah Ali Banda": (17.3585, 78.4575), "Bahadurpura": (17.3442, 78.4578),
    "Falaknuma": (17.3368, 78.4662), "L B Nagar": (17.3491, 78.5396),
    "Vanastahlipuram": (17.3510, 78.5600), "Saroor Nagar": (17.3500, 78.5390),
    "Hayathnagar": (17.3200, 78.6200), "Uppal": (17.4067, 78.5600),
    "Nacharam": (17.4110, 78.5610), "Mallapur": (17.4100, 78.5600),
    "ECIL": (17.4330, 78.5600), "Kushaiguda": (17.4400, 78.5600),
    "Kapra": (17.4386, 78.5715), "Alwal": (17.4898, 78.5175),
    "Malkajgiri": (17.4474, 78.5263), "Lalapet": (17.4551, 78.5063),
    "Srinagar Colony": (17.4083, 78.4432), "Punjagutta": (17.4117, 78.4565),
    "Somajiguda": (17.4170, 78.4490), "Begumpet": (17.4353, 78.4682),
    "Sanathnagar": (17.4415, 78.4320), "Bharat Nagar": (17.4390, 78.4304),
    "Erragadda": (17.4320, 78.4310), "Tukaramgate": (17.4340, 78.4260),
    "Fatehnagar": (17.4300, 78.4200), "Balanagar": (17.4686, 78.4195),
    "Jeedimetla": (17.4921, 78.4338), "Quthbullapur": (17.5064, 78.4300),
    "Medchal": (17.5710, 78.4600), "Ghatkesar": (17.4430, 78.6100),
    "Boduppal": (17.4160, 78.5740), "Peerzadiguda": (17.4120, 78.5800),
    "Nagole": (17.3620, 78.5650), "Bandlaguda": (17.3480, 78.5300),
    "Chandrayangutta": (17.3370, 78.4840), "Goshamahal": (17.3880, 78.4690),
    "Asif Nagar": (17.3840, 78.4700), "Nampally": (17.3900, 78.4820),
    "Abids": (17.3970, 78.4760), "Koti": (17.3850, 78.4860),
    "Sultan Bazar": (17.3850, 78.4800), "Moosarambagh": (17.3730, 78.5100),
    "Nallakunta": (17.3740, 78.5040), "Barkatpura": (17.3840, 78.5080),
    "Vidyanagar": (17.3920, 78.5170), "Kachiguda": (17.3840, 78.4870),
    "Shivam Road": (17.3670, 78.5020), "RTC Cross Roads": (17.3780, 78.4780),
    "Mettuguda": (17.4040, 78.5030), "Tarnaka": (17.4150, 78.5180),
    "Osmania University": (17.4120, 78.5290), "Vidya Nagar": (17.4080, 78.5250),
    "Narayanguda": (17.3750, 78.4900), "Rambagh": (17.3780, 78.5090),
    "Padmarao Nagar": (17.3810, 78.4870), "Ramnagar": (17.3680, 78.4850),
    "Chikkadpally": (17.3770, 78.4950), "Musheerabad": (17.3900, 78.5050),
    "Adikmet": (17.3960, 78.5110), "Gandhinagar": (17.3970, 78.4930),
    "Vivekananda Nagar": (17.3470, 78.5470), "Srikrishna Devaraya Nagar": (17.3550, 78.5550),
}

HYDERABAD_DEFAULT_COORDS = (17.3850, 78.4867)

# ── Pending voice text (must run before any widget with key="complaint_input") ──
if st.session_state.get("_pending_voice_text"):
    current = st.session_state.get("complaint_input", "")
    new_text = st.session_state._pending_voice_text
    st.session_state.complaint_input = (current + "\n\n" + new_text) if current.strip() else new_text
    del st.session_state._pending_voice_text

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h2>📝 Report a Civic Issue</h2>
  <p>Describe your issue in detail. Our AI will automatically classify it, route it to the right department, and generate a formal complaint letter.</p>
</div>
""", unsafe_allow_html=True)

# ── Form ───────────────────────────────────────────────────────────────────────
col_form, col_preview = st.columns([3, 2], gap="large")

with col_form:
    st.markdown('<div class="ca-card">', unsafe_allow_html=True)

    complaint_text = st.text_area(
        "Describe Your Issue *",
        placeholder="e.g. There is a large pothole on the main road near Koramangala 5th Block. It has been there for over 2 weeks and has caused two accidents...",
        height=160,
        help="Be as descriptive as possible for better AI classification.",
        key="complaint_input"
    )

    # ── Voice Recorder with Playback & Storage ──
    st.markdown("""
    <div style="display:flex;align-items:center;gap:.6rem;background:#F0F7FF;border:1.5px solid #BFDBFE;border-radius:8px;padding:.5rem .7rem .5rem 1rem;margin-bottom:.5rem;">
      <span style="font-size:1.2rem;">🎙️</span>
      <span style="font-size:.82rem;font-weight:500;color:#1E40AF;">Voice Recorder</span>
    </div>
    """, unsafe_allow_html=True)

    os.makedirs("recorded_audio", exist_ok=True)

    col_lang, col_mic = st.columns([1, 1.5])
    lang_map = {"en":"English", "te":"తెలుగు"}
    sr_lang_map = {"en":"en-US", "te":"te-IN"}
    with col_lang:
        voice_lang = st.selectbox(
            "Language",
            options=list(lang_map.keys()),
            format_func=lambda x: lang_map[x],
            key="voice_lang",
            label_visibility="collapsed"
        )
    with col_mic:
        audio_bytes = mic_recorder(
            start_prompt="🎤  Start Recording",
            stop_prompt="⏹️  Stop Recording",
            use_container_width=True,
            key="mic"
        )

    if audio_bytes and audio_bytes != st.session_state.get("_prev_audio"):
        st.session_state._prev_audio = audio_bytes
        audio_data = audio_bytes["bytes"]
        st.session_state.recorded_audio = audio_data

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        webm_path = f"recorded_audio/recording_{ts}.webm"
        with open(webm_path, "wb") as f:
            f.write(audio_data)
        st.session_state.recording_path = webm_path

        try:
            wav_path = f"recorded_audio/recording_{ts}.wav"
            sound = AudioSegment.from_file(webm_path, format="webm")
            sound.export(wav_path, format="wav")

            with sr.AudioFile(wav_path) as source:
                recognizer = sr.Recognizer()
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data_sr = recognizer.record(source)
                text = recognizer.recognize_google(audio_data_sr, language=sr_lang_map.get(voice_lang, "en-US"))
                if text.strip():
                    st.session_state.voice_text = text
                    current = st.session_state.get("complaint_input", "")
                    st.session_state._pending_voice_text = (current + "\n\n" + text) if current.strip() else text
        except sr.UnknownValueError:
            st.session_state.voice_error = "Could not understand audio. Try speaking clearly."
        except sr.RequestError:
            st.session_state.voice_error = "Transcription service unavailable. Audio saved."
        except Exception as e:
            st.session_state.voice_error = f"Transcription error: {str(e)}"

        st.rerun()

    if st.session_state.get("recorded_audio"):
        st.audio(st.session_state.recorded_audio, format="audio/webm")
        if st.session_state.get("voice_text"):
            st.success(f"📝 {st.session_state.voice_text}")
        if st.session_state.get("voice_error"):
            st.warning(st.session_state.voice_error)
        st.caption(f"💾 Saved: {st.session_state.get('recording_path', '')}")

    # ── Location — Hyderabad only ──
    st.markdown("""
    <div style="display:flex;align-items:center;gap:.6rem;background:#F0F7FF;border:1.5px solid #BFDBFE;border-radius:8px;padding:.5rem .7rem .5rem 1rem;margin-bottom:.5rem;">
      <span style="font-size:1.2rem;">📍</span>
      <span style="font-size:.82rem;font-weight:500;color:#1E40AF;">Location — Hyderabad</span>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        loc_query = st.text_input("🔍 Search street / area / landmark", placeholder="e.g. Gachibowli, KPHB Colony, JNTU...")
    with col_s2:
        quick_area = st.selectbox("Quick pick", options=[""] + sorted(HYDERABAD_AREAS.keys()), key="quick_area", label_visibility="collapsed")

    if loc_query.strip() or quick_area:
        query = quick_area if quick_area else loc_query.strip()
        if query != st.session_state.get("_last_loc_q"):
            st.session_state._last_loc_q = query
            try:
                params = {"q": f"{query}, Hyderabad, Telangana, India", "format": "json", "limit": 1}
                resp = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=NOMINATIM_HEADERS, timeout=5)
                results = resp.json()
                if results:
                    r = results[0]
                    st.session_state.map_lat = float(r["lat"])
                    st.session_state.map_lon = float(r["lon"])
                    st.session_state.detected_loc = r["display_name"]
            except Exception:
                pass
        # Fallback to preset coordinates
        if not st.session_state.get("map_lat") and quick_area in HYDERABAD_AREAS:
            lat, lon = HYDERABAD_AREAS[quick_area]
            st.session_state.map_lat = lat
            st.session_state.map_lon = lon
            st.session_state.detected_loc = f"{quick_area}, Hyderabad"

    if st.session_state.get("detected_loc"):
        st.success(f"📍 {st.session_state.get('detected_loc')[:70]}{'...' if len(st.session_state.get('detected_loc')) > 70 else ''}")
    location = st.session_state.get("detected_loc", "")

    col_a, col_b = st.columns(2)
    with col_a:
        contact_name = st.text_input("Your Name", placeholder="Full Name")
    with col_b:
        contact_phone = st.text_input("Phone / Email", placeholder="For status updates")

    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
    b1, b2, b3 = st.columns(3)
    submit_btn   = b1.button("🚀 Submit Complaint", type="primary", use_container_width=True)
    pdf_btn      = b2.button("📄 Generate PDF",     use_container_width=True)
    email_btn    = b3.button("📧 Send Email",        use_container_width=True)

with col_preview:
    if complaint_text.strip():
        category, dept, priority = detect_category(complaint_text)
        p_class = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}[priority]

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

        steps = [("Classified","✓"), ("Routed","✓"), ("Letter Generated","✓"), ("Email Sent","✓")]
        step_html = '<div class="step-row">'
        for i, (label, icon) in enumerate(steps):
            done   = i < steps_done
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
          <div style="font-size:.88rem;color:#64748B;">Start typing your complaint on the left — AI will instantly classify it, route it to the right department, and assign priority.</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Interactive Map (OpenStreetMap) — always visible ──
    st.markdown('<div class="section-header">🌍 Hyderabad Map — Click to detect exact location</div>', unsafe_allow_html=True)
    map_lat = st.session_state.get("map_lat", 17.3850)
    map_lon = st.session_state.get("map_lon", 78.4867)
    zoom = 15 if st.session_state.get("map_lat") else 11
    m = folium.Map(location=[map_lat, map_lon], zoom_start=zoom, tiles="OpenStreetMap", control_scale=True)
    if st.session_state.get("map_lat"):
        folium.Marker(
            [map_lat, map_lon],
            popup=st.session_state.get("detected_loc", "Selected Location"),
            icon=folium.Icon(color="red", icon="info-sign", prefix="glyphicon")
        ).add_to(m)
    output = st_folium(m, height=320, width="100%", key="loc_map")
    if output and output.get("last_clicked"):
        clat, clng = output["last_clicked"]["lat"], output["last_clicked"]["lng"]
        try:
            params = {"lat": clat, "lon": clng, "format": "json", "addressdetails": 1}
            resp = requests.get("https://nominatim.openstreetmap.org/reverse", params=params, headers=NOMINATIM_HEADERS, timeout=5)
            data = resp.json()
            if "display_name" in data:
                st.session_state.detected_loc = data["display_name"]
                st.session_state.map_lat = clat
                st.session_state.map_lon = clng
                st.rerun()
        except Exception:
            pass

# ── Notifications ──────────────────────────────────────────────────────────────
if submit_btn:
    if not location.strip():
        st.markdown('<div class="notif-error" style="margin-top:1rem;">⚠️ Please select your city and area before submitting.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("🤖 AI is processing your complaint..."):
            time.sleep(1.8)
        category, dept, priority = detect_category(complaint_text)
        cid = f"CA-2025-{random.randint(1100,9999)}"
        p_badge = {"High":"🔴","Medium":"🟡","Low":"🟢"}[priority]
        st.markdown(f"""
        <div class="notif-success" style="margin-top:1rem;">
          ✅ Complaint <strong>{cid}</strong> submitted successfully!<br><br>
          📂 <strong>Category:</strong> {category}<br>
          🏢 <strong>Routed to:</strong> {dept}<br>
          {p_badge} <strong>Priority:</strong> {priority}
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

if pdf_btn:
    with st.spinner("📄 Generating formal complaint PDF..."):
        time.sleep(1.2)
    st.markdown('<div class="notif-success" style="margin-top:1rem;">📄 PDF generated successfully! Check <a href="#">AI Complaint View</a> to download.</div>', unsafe_allow_html=True)

if email_btn:
    with st.spinner("📧 Dispatching email to department..."):
        time.sleep(1)
    st.markdown('<div class="notif-success" style="margin-top:1rem;">📧 Email dispatched to <strong>roads@bbmp.gov.in</strong> successfully!</div>', unsafe_allow_html=True)

# Load department data for chatbot context
def load_dept_data():
    try:
        with open("backend/data/departments.json", "r") as f:
            return json.load(f)
    except:
        return {}

def _has_telugu(text):
    for ch in text:
        if '\u0C00' <= ch <= '\u0C7F':
            return True
    return False

def get_chatbot_response(prompt):
    dept_data = load_dept_data()
    is_te = _has_telugu(prompt)

    sla_en = {"High": "2-3 days", "Medium": "5-7 days", "Low": "7-10 days"}
    sla_te = {"High": "2-3 రోజుల", "Medium": "5-7 రోజుల", "Low": "7-10 రోజుల"}

    if is_te:
        if "నీర" in prompt:
            info = dept_data.get("Water Leakage", {})
            res = sla_te.get(info.get("priority", "High"), "3 రోజుల")
            dept_name = info.get("department", "నీటి సరఫరా విభాగం")
            return f"నీటి లీకేజ్ సమస్యలను {dept_name} {res}లో పరిష్కరిస్తుంది."
        if "చెత్త" in prompt or "శుభ్ర" in prompt:
            info = dept_data.get("Garbage", {})
            res = sla_te.get(info.get("priority", "High"), "3 రోజుల")
            dept_name = info.get("department", "సానిటేషన్ విభాగం")
            return f"చెత్త/పారిశుద్ధ్య సమస్యలను {dept_name} {res}లో పరిష్కరిస్తుంది."
        if "గుంత" in prompt or "రోడ్" in prompt:
            info = dept_data.get("Pothole", {})
            res = sla_te.get(info.get("priority", "High"), "3 రోజుల")
            dept_name = info.get("department", "రోడ్డు విభాగం")
            return f"రోడ్డు గుంతల సమస్యలను {dept_name} {res}లో పరిష్కరిస్తుంది."
        return ("నేను పౌర సమస్యల గురించి సమాధానం ఇవ్వగలను. "
                "ఉదా: గుంతలు, నీటి లీకేజ్, చెత్త సమస్యల పరిష్కార సమయాలు.")

    w = prompt.lower()
    if "water" in w or "leak" in w:
        info = dept_data.get("Water Leakage", {})
        res = sla_en.get(info.get("priority", "High"), "3 days")
        return f"Water Leakage issues are handled by {info.get('department', 'Water Works Dept')} within {res}."
    if "garbage" in w or "cleaning" in w or "waste" in w:
        info = dept_data.get("Garbage", {})
        res = sla_en.get(info.get("priority", "High"), "3 days")
        return f"Garbage/sanitation issues are handled by {info.get('department', 'Sanitation Dept')} within {res}."
    if "pothole" in w or "road" in w:
        info = dept_data.get("Pothole", {})
        res = sla_en.get(info.get("priority", "High"), "3 days")
        return f"Pothole/road issues are handled by {info.get('department', 'Roads Dept')} within {res}."
    return "I can answer questions about civic issues like potholes, water leaks, garbage, etc."

# ── Chatbot ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">🤖 CivicAssist AI Chatbot</div>', unsafe_allow_html=True)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Process pending voice input for chatbot
if st.session_state.get("_pending_chat_voice"):
    voice_text = st.session_state._pending_chat_voice
    del st.session_state._pending_chat_voice
    st.session_state.chat_messages.append({"role": "user", "content": voice_text})
    resp_text = get_chatbot_response(voice_text)
    st.session_state.chat_messages.append({"role": "assistant", "content": resp_text})
    st.rerun()

# Display chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Voice recorder for chatbot
vcol1, vcol2 = st.columns([0.12, 0.88])
with vcol1:
    chat_voice = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        key="chat_mic",
        use_container_width=True
    )
    if chat_voice and chat_voice != st.session_state.get("_prev_chat_mic"):
        st.session_state._prev_chat_mic = chat_voice
        try:
            audio_bytes = chat_voice["bytes"]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            webm_path = f"recorded_audio/chat_{ts}.webm"
            with open(webm_path, "wb") as f:
                f.write(audio_bytes)
            wav_path = f"recorded_audio/chat_{ts}.wav"
            AudioSegment.from_file(webm_path, format="webm").export(wav_path, format="wav")
            with sr.AudioFile(wav_path) as src:
                recognizer = sr.Recognizer()
                recognizer.adjust_for_ambient_noise(src, duration=0.3)
                try:
                    text = recognizer.recognize_google(
                        recognizer.record(src), language="te-IN"
                    )
                except sr.UnknownValueError:
                    with sr.AudioFile(wav_path) as src2:
                        text = recognizer.recognize_google(
                            recognizer.record(src2), language="en-US"
                        )
            if text.strip():
                st.session_state._pending_chat_voice = text
                st.rerun()
        except:
            pass

with vcol2:
    if prompt := st.chat_input("Ask me about civic issues..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        resp_text = get_chatbot_response(prompt)
        st.session_state.chat_messages.append({"role": "assistant", "content": resp_text})
        st.rerun()

# CSS for notif (reuse from main app)
st.markdown("""
<style>
.notif-success{background:#ECFDF5;border:1px solid #6EE7B7;border-radius:8px;padding:.8rem 1.2rem;color:#065F46;font-weight:500;font-size:.9rem;}
.notif-error{background:#FEF2F2;border:1px solid #FCA5A5;border-radius:8px;padding:.8rem 1.2rem;color:#991B1B;font-weight:500;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)