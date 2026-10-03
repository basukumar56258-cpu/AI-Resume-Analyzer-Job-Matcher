from html import escape

import streamlit as st
from parsers.pdf_parser import extract_pdf_text
from parsers.docx_parser import extract_docx_text
from services.skill_extractor import extract_skills
from services.ats_scorer import calculate_ats_score
from services.matcher import match_resume_to_job
from services.recommendation import generate_recommendations

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root {
        --ink: #18243b; --muted: #738098; --paper: #f4f6fb; --line: #e4e9f2;
        --navy: #111f3d; --blue: #3478f6; --violet: #8051e8; --green: #19ae76;
        --orange: #f3a13b; --red: #e9656a;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', 'Segoe UI', sans-serif; color: var(--ink); }
    [data-testid="stAppViewContainer"] { background: var(--paper); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] { max-width: 1480px; padding: 0 28px 40px; }
    [data-testid="stSidebar"] { min-width: 242px; max-width: 242px; background: var(--navy); }
    [data-testid="stSidebar"] * { color: #edf2ff; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: #1a2c50; border: 1px dashed #617293; border-radius: 8px;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: #397bfa; border: 0; border-radius: 5px; color: #fff;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * { color: #fff; }
    .sidebar-brand { display: flex; align-items: center; gap: 10px; margin: 8px 0 34px; }
    .brand-icon { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 9px; background: #315cbd; color: white; font-size: 20px; }
    .brand-copy strong, .brand-copy small { display: block; }
    .brand-copy strong { font: 700 13px 'Space Grotesk', sans-serif; }
    .brand-copy small { color: #aab8d1; font-size: 10px; margin-top: 2px; }
    .nav-caption, .upload-caption { color: #92a3c0 !important; font-size: 9px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: 0 0 10px; }
    .side-nav { display: grid; gap: 5px; margin-bottom: 30px; }
    .side-nav a { display: flex; align-items: center; gap: 11px; padding: 10px 12px; border-radius: 6px; color: #d5dff1; text-decoration: none; font-size: 12px; }
    .side-nav a:first-child { background: #243d70; box-shadow: inset 0 0 0 1px #31538f; color: #fff; }
    .nav-icon { display: inline-grid; place-items: center; width: 18px; color: #b4c8ef; font-size: 14px; }
    .sidebar-upload { border-top: 1px solid #2c3c5d; padding-top: 20px; }
    .sidebar-note { color: #9babc5; font-size: 10px; line-height: 1.5; margin-top: 10px; }
    .topbar { display: flex; align-items: center; justify-content: space-between; min-height: 54px; border-bottom: 1px solid var(--line); margin-bottom: 14px; }
    .topbar-note { display: flex; align-items: center; gap: 9px; color: #65738a; font-size: 11px; }
    .topbar-spark { color: #7052df; font-size: 15px; }
    .privacy-pill { display: inline-flex; align-items: center; gap: 7px; padding: 6px 10px; border: 1px solid #dbe4f1; border-radius: 20px; background: #fff; color: #57677f; font-size: 10px; font-weight: 600; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); }
    .hero {
        display: flex; align-items: center; justify-content: space-between; min-height: 206px;
        overflow: hidden; padding: 25px 34px; margin-bottom: 14px; border-radius: 8px;
        background: linear-gradient(108deg, #d9efff 0%, #e6eaff 60%, #e9d9ff 100%);
    }
    .hero-copy { position: relative; z-index: 1; max-width: 53%; }
    .hero-kicker { color: #536a92; font-size: 9px; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .hero h1 { color: #17233b; font: 700 30px/1.12 'Space Grotesk', 'Segoe UI', sans-serif; margin: 8px 0 7px; letter-spacing: 0; }
    .hero p { color: #4c5b75; font-size: 11px; line-height: 1.55; margin: 0; max-width: 410px; }
    .hero-actions { display: flex; gap: 8px; margin-top: 12px; }
    .hero-button { display: inline-flex; align-items: center; gap: 6px; padding: 8px 12px; border-radius: 6px; font-size: 10px; font-weight: 700; text-decoration: none; }
    .hero-button.primary { background: #1769f8; color: #fff; box-shadow: 0 3px 8px #1769f833; }
    .hero-button.secondary { border: 1px solid #cdd8e9; background: #fff; color: #243653; }
    .hero-art { position: relative; width: 42%; max-width: 390px; height: 160px; flex: 0 0 42%; }
    .doc-card { position: absolute; top: 19px; display: flex; flex-direction: column; gap: 8px; width: 112px; height: 128px; padding: 12px; border-radius: 9px; background: #fff; box-shadow: 0 10px 24px #364b7a24; transform: rotate(-6deg); }
    .doc-card.job { right: 2px; transform: rotate(6deg); }
    .doc-title { display: flex; align-items: center; gap: 6px; color: #293856; font-size: 9px; font-weight: 700; }
    .doc-avatar { width: 21px; height: 21px; border-radius: 6px; background: #dceaff; color: #397bfa; text-align: center; line-height: 21px; font-size: 13px; }
    .doc-line { height: 5px; border-radius: 5px; background: #e5eaf3; }
    .doc-line.short { width: 64%; }
    .doc-line.blue { width: 80%; background: #bdd4ff; }
    .ai-orbit { position: absolute; left: 50%; top: 50%; width: 74px; height: 74px; border: 2px dotted #5578ff; border-left-color: transparent; border-bottom-color: transparent; border-radius: 50%; transform: translate(-50%, -50%) rotate(20deg); }
    .ai-tile { position: absolute; left: 50%; top: 50%; display: grid; place-items: center; width: 43px; height: 43px; border-radius: 12px; background: linear-gradient(145deg, #19b991, #3877fa); box-shadow: 0 7px 16px #516cbd42; color: #fff; font: 700 14px 'Space Grotesk', sans-serif; transform: translate(-50%, -50%) rotate(-7deg); }
    .metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 11px; margin-bottom: 14px; }
    .metric-card { position: relative; min-height: 86px; padding: 13px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .metric-card.blue { background: linear-gradient(130deg, #fff, #eef6ff); }
    .metric-card.violet { background: linear-gradient(130deg, #fff, #f4efff); }
    .metric-card.orange { background: linear-gradient(130deg, #fff, #fff5e5); }
    .metric-card.red { background: linear-gradient(130deg, #fff, #fff0f0); }
    .metric-icon { display: grid; place-items: center; float: left; width: 34px; height: 34px; margin-right: 10px; border-radius: 50%; font-size: 15px; }
    .blue .metric-icon { background: #dceaff; color: #3478f6; }
    .violet .metric-icon { background: #e9ddff; color: #8051e8; }
    .orange .metric-icon { background: #ffe9c8; color: #df8a20; }
    .red .metric-icon { background: #ffdddd; color: #dc555a; }
    .metric-label { color: #526078; font-size: 10px; font-weight: 700; }
    .metric-value { color: #17233b; font: 700 23px/1.25 'Space Grotesk', sans-serif; }
    .metric-foot { color: #8390a5; font-size: 9px; }
    .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr .88fr; gap: 11px; align-items: stretch; }
    .panel { min-width: 0; padding: 15px 16px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 13px; }
    .panel-heading h2 { color: #1b2942; font: 700 14px 'Space Grotesk', sans-serif; margin: 0; }
    .panel-icon { display: grid; place-items: center; width: 28px; height: 28px; border-radius: 7px; background: #e7efff; color: #397bfa; font-size: 14px; flex: 0 0 28px; }
    .panel-icon.purple { background: #f0e9ff; color: #8051e8; }
    .panel-icon.green { background: #e2f8ef; color: #159b68; }
    .resume-overview { display: flex; align-items: center; gap: 13px; min-height: 108px; }
    .score-ring { display: grid; place-items: center; width: 86px; height: 86px; flex: 0 0 86px; border-radius: 50%; background: conic-gradient(#22bd88 calc(var(--score) * 1%), #e9eef5 0); }
    .score-inner { display: grid; place-content: center; width: 67px; height: 67px; border-radius: 50%; background: #fff; text-align: center; }
    .score-inner strong { color: #202e48; font: 700 18px 'Space Grotesk', sans-serif; }
    .score-inner small { color: #8490a4; font-size: 8px; }
    .resume-file strong { display: block; overflow-wrap: anywhere; color: #263550; font-size: 10px; }
    .resume-file small { display: block; color: #8994a7; font-size: 9px; line-height: 1.5; margin-top: 4px; }
    .panel-rule { height: 1px; background: #e9edf4; margin: 12px 0; }
    .panel-subtitle { color: #65738b; font-size: 9px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 8px; }
    .skill-list { display: flex; flex-wrap: wrap; gap: 5px; }
    .skill-tag { padding: 4px 7px; border-radius: 4px; background: #eff4fb; color: #475a77; font-size: 9px; }
    .match-score { padding: 9px 10px; border-radius: 6px; background: #eef9f4; margin-bottom: 10px; }
    .match-score-row { display: flex; justify-content: space-between; align-items: center; color: #54627a; font-size: 9px; }
    .match-score-row strong { color: #14885d; font: 700 19px 'Space Grotesk', sans-serif; }
    .match-track { height: 5px; overflow: hidden; margin-top: 7px; border-radius: 5px; background: #dce9e4; }
    .match-track span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #20bd82, #64d3a0); }
    .skill-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
    .skill-column-label { color: #6e7c93; font-size: 9px; font-weight: 700; margin-bottom: 6px; }
    .skill-column-label.missing { color: #c84f57; }
    .skill-list.compact { gap: 4px; }
    .skill-list.compact .skill-tag { padding: 4px 6px; font-size: 8px; }
    .skill-tag.missing { color: #ad4a50; background: #fff0f0; }
    .recommend-list { display: grid; gap: 7px; }
    .recommend-item { display: flex; align-items: flex-start; gap: 8px; padding: 8px; border-radius: 5px; background: #f5f2ff; color: #4b4b68; font-size: 9px; line-height: 1.45; }
    .recommend-number { display: grid; place-items: center; width: 17px; height: 17px; flex: 0 0 17px; border-radius: 50%; background: #8051e8; color: #fff; font-size: 8px; font-weight: 700; }
    .dashboard-lower { margin-top: 11px; }
    .analysis-list { display: grid; gap: 7px; }
    .analysis-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 3px 0; color: #33415b; font-size: 10px; }
    .analysis-state { display: inline-flex; align-items: center; gap: 5px; color: #14885d; font-size: 9px; white-space: nowrap; }
    .analysis-state.missing { color: #d34e59; }
    .analysis-state.neutral { color: #77849a; }
    .quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
    .quick-action { display: grid; place-items: center; gap: 5px; min-height: 54px; padding: 8px; border-radius: 6px; color: #fff; text-align: center; text-decoration: none; font-size: 9px; font-weight: 700; }
    .quick-action span { font-size: 16px; }
    .quick-action.blue { background: #3478f6; }
    .quick-action.violet { background: #7950e8; }
    .quick-action.green { background: #12b87a; }
    .quick-action.orange { background: #ee9b23; }
    .assistant-tag { padding: 4px 6px; border-radius: 4px; background: #edf5ff; color: #4771af; font-size: 8px; font-weight: 700; letter-spacing: .06em; }
    .assistant-bubble { padding: 10px; border-radius: 7px 7px 7px 2px; background: #eaf3ff; color: #41516a; font-size: 10px; line-height: 1.5; margin-bottom: 8px; }
    .assistant-answer { padding: 9px 10px; border: 1px solid #e6eaf1; border-radius: 7px; color: #384761; font-size: 9px; line-height: 1.5; margin-bottom: 8px; }
    .assistant-caption { color: #8994a7; font-size: 8px; letter-spacing: .08em; margin: 6px 0; }
    .assistant-panel [data-testid="stVerticalBlockBorderWrapper"] { border: 0; padding: 0; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--line); border-radius: 8px; background: #fff; }
    [data-testid="stVerticalBlockBorderWrapper"] > div { border-radius: inherit; }
    .assistant-panel [data-testid="stButton"] button { min-height: 29px; border: 1px solid #e2e8f2; border-radius: 5px; background: #fff; color: #53627b; font-size: 8px; }
    .assistant-panel [data-testid="stButton"] button:hover { border-color: #9bb8ec; color: #2b60ba; }
    .assistant-panel [data-testid="stTextInput"] input { font-size: 9px; }
    .empty-note { display: grid; place-items: center; min-height: 105px; padding: 15px; border: 1px dashed #dbe3ef; border-radius: 6px; color: #8692a7; font-size: 10px; text-align: center; }
    .job-input-label { color: #738098; font-size: 9px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 9px 0 5px; }
    [data-testid="stForm"] { margin-bottom: 14px; padding: 6px 12px 9px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    [data-testid="stTextArea"] textarea { background: #fff; border: 0; color: var(--ink); font-size: 12px; line-height: 1.5; }
    [data-testid="stTextArea"] textarea:focus { box-shadow: none; }
    .stTextArea [data-testid="InputInstructions"] { display: none; }
    [data-testid="stFormSubmitButton"] button {
        min-height: 40px; border: 0; border-radius: 6px; background: #3478f6;
        color: #fff; font-size: 10px; font-weight: 700; white-space: nowrap;
    }
    [data-testid="stFormSubmitButton"] button:hover { background: #245ed0; color: #fff; }
    @media (max-width: 900px) {
        [data-testid="stSidebar"] { min-width: 180px; max-width: 180px; }
    }
    @media (max-width: 700px) {
        [data-testid="stSidebar"] { min-width: 0; max-width: 100%; }
        [data-testid="stMainBlockContainer"] { padding: 0 14px 28px; }
        .topbar { min-height: 46px; }
        .hero { min-height: 175px; padding: 19px; }
        .hero-copy { max-width: 65%; }
        .hero h1 { font-size: 23px; }
        .hero p { font-size: 9px; }
        .hero-art { width: 32%; height: 125px; flex-basis: 32%; }
        .doc-card { width: 70px; height: 100px; padding: 8px; gap: 6px; }
        .doc-title { font-size: 7px; }
        .ai-orbit { width: 48px; height: 48px; }
        .ai-tile { width: 31px; height: 31px; font-size: 10px; }
        .metric-grid { grid-template-columns: 1fr 1fr; gap: 7px; }
        .metric-card { min-height: 78px; padding: 10px; }
        .metric-icon { width: 28px; height: 28px; margin-right: 7px; }
        .metric-value { font-size: 20px; }
        .dashboard-grid { grid-template-columns: 1fr; }
        .dashboard-grid .panel:last-child { grid-column: auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><span class="brand-icon">✦</span>'
        '<span class="brand-copy"><strong>AI Resume Analyzer</strong>'
        '<small>&amp; Job Matcher</small></span></div>'
        '<p class="nav-caption">WORKSPACE</p>'
        '<nav class="side-nav">'
        '<a href="#dashboard"><span class="nav-icon">⌂</span>Dashboard</a>'
        '<a href="#resume-upload"><span class="nav-icon">▤</span>Analyze Resume</a>'
        '<a href="#job-match"><span class="nav-icon">◎</span>Job Matcher</a>'
        '<a href="#assistant"><span class="nav-icon">▢</span>Resume Assistant</a>'
        '<a href="#recommendations"><span class="nav-icon">✧</span>Recommendations</a>'
        '</nav>'
        '<div id="resume-upload" class="sidebar-upload"><p class="upload-caption">RESUME FILE</p></div>',
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("Resume file", type=["pdf", "docx"], label_visibility="collapsed")
    st.markdown('<p class="sidebar-note">PDF or DOCX · Up to 200 MB</p>', unsafe_allow_html=True)

resume_text = ""
if uploaded:
    if uploaded.name.lower().endswith(".pdf"):
        resume_text = extract_pdf_text(uploaded)
    else:
        resume_text = extract_docx_text(uploaded)

skills = extract_skills(resume_text) if resume_text else []
job_description = ""
job_skills = []
result = None
score = None
recommendations = []

st.markdown(
    '<div id="dashboard" class="topbar"><div class="topbar-note">'
    '<span class="topbar-spark">✦</span> Smarter resumes. Better opportunities.</div>'
    '<span class="privacy-pill"><span class="status-dot"></span>Local workspace</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero"><div class="hero-copy"><div class="hero-kicker">YOUR CAREER WORKSPACE</div>'
    '<h1>AI Resume Analyzer &amp;<br>Job Matcher</h1>'
    '<p>Upload your resume and job description to see your match, skill gaps, and practical next steps.</p>'
    '<div class="hero-actions"><a class="hero-button primary" href="#resume-upload">⇧ Upload Resume</a>'
    '<a class="hero-button secondary" href="#job-match">◎ Match with Job</a></div>'
    '</div><div class="hero-art"><div class="doc-card resume"><div class="doc-title"><span class="doc-avatar">●</span> RESUME</div>'
    '<div class="doc-line blue"></div><div class="doc-line"></div><div class="doc-line short"></div>'
    '<div class="doc-line"></div><div class="doc-line short"></div></div><div class="ai-orbit"></div>'
    '<div class="ai-tile">AI</div><div class="doc-card job"><div class="doc-title"><span class="doc-avatar">▣</span> JOB</div>'
    '<div class="doc-line blue"></div><div class="doc-line short"></div><div class="doc-line"></div>'
    '<div class="doc-line short"></div><div class="doc-line"></div></div></div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div id="job-match" class="job-input-label">TARGET JOB DESCRIPTION</div>', unsafe_allow_html=True)
with st.form("job_match_form", border=False):
    description_column, action_column = st.columns([5, 1], vertical_alignment="bottom")
    with description_column:
        st.text_area(
            "Job description",
            height=82,
            label_visibility="collapsed",
            placeholder="Paste the job description here...",
            key="job_description",
        )
    with action_column:
        st.form_submit_button("Match with Job", use_container_width=True)

job_description = st.session_state.get("job_description", "")

if job_description.strip():
    job_skills = extract_skills(job_description)
if resume_text and job_description.strip():
    result = match_resume_to_job(resume_text, job_description)
    score = calculate_ats_score(resume_text, job_description)
    recommendations = generate_recommendations(result)

missing_count = len(result["missing_skills"]) if result else "—"
metric_data = [
    ("green", "◉", "ATS Score", f"{score}%" if score is not None else "—", "Resume + role alignment" if score is not None else "Waiting for both inputs"),
    ("violet", "◎", "Job Skills", str(len(job_skills)) if job_description.strip() else "—", "Requirements detected" if job_description.strip() else "No role added yet"),
    ("orange", "▤", "Skills Found", str(len(skills)) if resume_text else "—", "In your resume" if resume_text else "No resume uploaded"),
    ("red", "△", "Skill Gaps", str(missing_count), "To address" if result else "Waiting for match"),
]
metric_cards = "".join(
    f'<div class="metric-card {tone}"><span class="metric-icon">{icon}</span>'
    f'<div class="metric-label">{label}</div><div class="metric-value">{value}</div>'
    f'<div class="metric-foot">{foot}</div></div>'
    for tone, icon, label, value, foot in metric_data
)
st.markdown(f'<div class="metric-grid">{metric_cards}</div>', unsafe_allow_html=True)

if resume_text:
    score_value = score if score is not None else 0
    score_label = f"{score}%" if score is not None else "—"
    score_caption = "ATS Score" if score is not None else "Add job description"
    resume_body = (
        f'<div class="resume-overview"><div class="score-ring" style="--score:{score_value}">'
        f'<div class="score-inner"><strong>{score_label}</strong><small>{score_caption}</small></div></div>'
        f'<div class="resume-file"><strong>{escape(uploaded.name)}</strong>'
        f'<small>{len(resume_text.split())} words · {len(skills)} skills detected</small></div></div>'
        '<div class="panel-rule"></div><div class="panel-subtitle">Extracted skills</div>'
    )
    if skills:
        resume_body += '<div class="skill-list">' + "".join(
            f'<span class="skill-tag">{escape(skill)}</span>' for skill in skills
        ) + '</div>'
    else:
        resume_body += '<div class="empty-note">No supported skills detected in this resume.</div>'
else:
    resume_body = '<div class="empty-note">Your uploaded resume analysis will appear here.</div>'

if result:
    matched_skills = result["matched_skills"]
    missing_skills = result["missing_skills"]
    matched_markup = "".join(f'<span class="skill-tag">{escape(skill)}</span>' for skill in matched_skills) or '<span class="skill-tag">None yet</span>'
    missing_markup = "".join(f'<span class="skill-tag missing">{escape(skill)}</span>' for skill in missing_skills) or '<span class="skill-tag">None</span>'
    match_body = (
        f'<div class="match-score"><div class="match-score-row"><span>Match score</span><strong>{score}%</strong></div>'
        f'<div class="match-track"><span style="width:{score}%"></span></div></div>'
        '<div class="skill-columns"><div><div class="skill-column-label">Matched</div>'
        f'<div class="skill-list compact">{matched_markup}</div></div>'
        '<div><div class="skill-column-label missing">Missing</div>'
        f'<div class="skill-list compact">{missing_markup}</div></div></div>'
    )
else:
    match_body = '<div class="empty-note">Add both a resume and target role to see your skill match.</div>'

if recommendations:
    recommendation_body = '<div class="recommend-list">' + "".join(
        f'<div class="recommend-item"><span class="recommend-number">{index}</span>'
        f'<span>{escape(item)}</span></div>'
        for index, item in enumerate(recommendations, start=1)
    ) + '</div>'
else:
    recommendation_body = '<div class="empty-note">Role-specific recommendations appear after a match.</div>'

skill_rows = []
for skill in (job_skills or skills)[:5]:
    if result and skill in result["matched_skills"]:
        state, state_class = "✓ Matched", ""
    elif result:
        state, state_class = "× Missing", " missing"
    else:
        state, state_class = "In resume", " neutral"
    skill_rows.append(
        f'<div class="analysis-row"><span>{escape(skill)}</span>'
        f'<span class="analysis-state{state_class}">{state}</span></div>'
    )
skill_analysis_body = "".join(skill_rows) or '<div class="empty-note">Add a resume or role to see skill signals.</div>'
if len(job_skills or skills) > 5:
    skill_analysis_body += f'<div class="assistant-caption">+ {len(job_skills or skills) - 5} more skills</div>'

resume_column, match_column, assistant_column = st.columns([1, 1, .88], gap="small")
with resume_column:
    st.markdown(
        '<section class="panel"><div class="panel-heading"><h2>Resume Analysis</h2>'
        f'<span class="panel-icon">▤</span></div>{resume_body}</section>',
        unsafe_allow_html=True,
    )
with match_column:
    st.markdown(
        '<section class="panel"><div class="panel-heading"><h2>Job Matching</h2>'
        f'<span class="panel-icon purple">◎</span></div>{match_body}</section>',
        unsafe_allow_html=True,
    )

def answer_assistant(question: str) -> str:
    if not result:
        return "Upload a resume and add a target role before asking about your match."
    normalized = question.casefold()
    if any(term in normalized for term in ("missing", "gap", "focus", "add", "learn")):
        missing = result["missing_skills"]
        return "Skills to focus on: " + ", ".join(missing) if missing else "No job-required skill gaps were detected."
    if any(term in normalized for term in ("match", "overlap", "strong")):
        matched = result["matched_skills"]
        return f"Your resume matches {len(matched)} of {len(result['job_skills'])} detected job skills: " + (", ".join(matched) or "none yet") + "."
    if recommendations:
        return recommendations[0]
    return "Your resume covers the detected skills for this role. Keep achievements specific and measurable."

with assistant_column:
    st.markdown('<div id="assistant"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div class="panel-heading"><h2>Resume Assistant</h2>'
            '<span class="assistant-tag">LOCAL</span></div>'
            '<div class="assistant-bubble">Hi, I can help you review this resume-to-role match.</div>',
            unsafe_allow_html=True,
        )
        last_answer = st.session_state.get("assistant_answer", "")
        if last_answer:
            st.markdown(f'<div class="assistant-answer">{escape(last_answer)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="assistant-caption">SUGGESTED QUESTIONS</div>', unsafe_allow_html=True)
        assistant_questions = ["Which skills match?", "What skills are missing?", "How can I improve?"]
        for index, question in enumerate(assistant_questions):
            if st.button(question, key=f"assistant_suggestion_{index}", use_container_width=True):
                st.session_state["assistant_answer"] = answer_assistant(question)
                st.rerun()
        with st.form("assistant_question_form", border=False):
            assistant_query = st.text_input(
                "Ask about your match",
                placeholder="Ask about your match...",
                label_visibility="collapsed",
            )
            assistant_submitted = st.form_submit_button("Ask", use_container_width=True)
        if assistant_submitted and assistant_query.strip():
            st.session_state["assistant_answer"] = answer_assistant(assistant_query.strip())
            st.rerun()

skills_column, recommendations_column, actions_column = st.columns([1, 1, .88], gap="small")
with skills_column:
    st.markdown(
        '<section class="panel"><div class="panel-heading"><h2>Skills Analysis</h2>'
        '<span class="panel-icon">▥</span></div>'
        f'<div class="analysis-list">{skill_analysis_body}</div></section>',
        unsafe_allow_html=True,
    )
with recommendations_column:
    st.markdown(
        '<section id="recommendations" class="panel"><div class="panel-heading"><h2>AI Recommendations</h2>'
        '<span class="panel-icon green">✧</span></div>'
        f'{recommendation_body}</section>',
        unsafe_allow_html=True,
    )
with actions_column:
    st.markdown(
        '<section class="panel"><div class="panel-heading"><h2>Quick Actions</h2>'
        '<span class="panel-icon purple">↗</span></div><div class="quick-grid">'
        '<a class="quick-action blue" href="#resume-upload"><span>⇧</span>Upload Resume</a>'
        '<a class="quick-action violet" href="#job-match"><span>◎</span>Match with Job</a>'
        '<a class="quick-action green" href="#assistant"><span>▢</span>Open Assistant</a>'
        '<a class="quick-action orange" href="#recommendations"><span>◷</span>View Tips</a>'
        '</div></section>',
        unsafe_allow_html=True,
    )
