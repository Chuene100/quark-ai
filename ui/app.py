import streamlit as st
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Make sure Python can find our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agents.orchestractor import Orcherstrator
from agents.review_coordinator import ReviewCoordinator
from utils.cv_extractor import get_cv_summary

#--- Page config -----------------------------------------
st.set_page_config(
    page_title= "Quark AI",
    page_icon= "",
    layout= "wide",
    initial_sidebar_state= "expanded",
)

# ----- Custom CSS -----------------------------------------
st.markdown("""
<style>
    .main-title {
            front-size: 2rem; font-weight: 700;
            color: #1D9E75; margin-bottom: 0;
    }
    .sub-title {
            font-size: 0.9rem; color: #888; margin-botton: 2rem;
    }
    .metric-card {
            background: #f8f9fa; border-radius: 8px;
            padding: 1rem; text-align: center;
    }
    .phase-badge {
            display: inline-block; padding: 3px 10px;
            border-radius: 20px; font-size: 0.8rem; font-weight: 600;
    }
    .verdict-strong {color: #3D6D11; background: #EAF3DE; }
    .verdict-good   {color: #854F0B; background: #FAEEDA; }
    .verdict-partial{color: #185FA5; background: #E6F1FB; }
    .verdict-weak   {color: #A32D2D; background: #FCEBEB; }
    .output-box {
            background: #f8f9fa; border-left: 3px solid #1D9E75;
            padding: 1rem; border-radius: 0 8px 8px 0;
            white-space: pre-wrap; font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# -- Session state initialisation ----------------------------------------------------
def init_state():
    """
    Initial all session state variables.
    Called once at startup - if keys already exist, nothing changes.
    """
    defaults = {
        "orchestrator": None,
        "coordinator": None,
        "cv_path": None,
        "current_result": None,
        "review_state": None,
        "application": [],      # list of saved application dicts
        "page": "home",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_orchestrator() -> Orcherstrator:
    """
    Returns the Orchestrator, creating it once and caching in session state. 
    We don't recreate it on every rerun - that would be wasteful.
    """
    if st.session_state.orchestrator is None:
        st.session_state.orchestrator = Orcherstrator()
        st.session_state.coordinator = ReviewCoordinator(
            st.seesion_state.orchestrator
        )
    return st.session_state.orchestrator


# -- Sidebar -----------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("##  Quark AI")
        st.caption("Job Application system")
        st.divider()

        # CV upload - persists across pages
        st.markdown("### Your CV")
        uploaded = st.file_uploader(
            "Upload your CV (PDF)",
            type= ["pdf"],
            key= "cv_uploader"
        )

        if uploaded:
            # Save uploaded file to temp location
            cv_path = f"/temp/{uploaded.name}"
            with open(cv_path, "wb") as f:
                f.write(uploaded.getbuffer())

            # Only re-extract if it's a new file
            if st.session_state.cv_path != cv_path:
                with st.spinner("Reading CV..."):
                    st.session_state.cv_text = get_cv_summary(cv_path)
                    st.session_state.cv_path = cv_path

        if st.session_state.cv_text:
            st.success(
                f"CV loaded - {len(st.session_state.cv_text):,} chars"
            )
        else:
            st.warning("Uploaded your CV to begin")

        st.divider()

        # Navigation
        st.markdown("## Navigate")
        pages = {
            "home": "  Home",
            "new_app": "  New application",
            "cv_review": "  CV review",
            "inteview_prep": "  Interview prep",
            "tracker": "  Application tracker",
        }

        for page_key, label in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                st.session_state.page = page_key
                st.rerun()

        st.divider()
        st.caption(f"Application tracked: {len(st.session_state.applications)}")

        

# -- Page: Home -----------------------------------------------------------------
def page_home():
    st.markdown('<p class="main-title">  Quark AI </p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title"> AI agentic job application system - '
        'built by Chuene Mosomane </p>', unsafe_allow_html=True
    )

    # Starts row
    apps  = st.session_state_state.applications
    total = len(apps)
    interviews = sum(1 for a in apps if a.get("status") == "Interview")
    contracts = sum(1 for a in apps if a.get("status") == "Contract signed")
    rate = round((interviews / total) * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total applied", total)
    col2.metric("Interviews", interviews)
    col3.metric("Contracts", contracts)
    col4.metric("Conversation rate", f"{rate}%")

    st.divider()

    # Phase tracker
    st.markdown("### Interview readiness - 4 phases")

    phases = [
        ("I",   "CV editing",                   " Confident",   "normal"),
        ("II",  "Pitching & storytelling",      " In training", "normal"),
        ("III", "Technical interviews",         " Refining",    "normal"),
        ("IV",  "Management alignment",         " Upcoming",    "off"),
    ]

    cols = st.columns(4)
    for col, (num, name, status, _) in zip(cols, phases):
        with col:
            st.markdown(f"**Phases {num}**")
            st.markdown((f"*{name}*"))
            st.markdown(status)

    st.divider()


    # Quick actions
    st.markdown('### Quick actions')
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("  New Application", use_container_width=True):
            st.session_state.page = "new_app"
            st.rerun()

    with col2:
        if st.button(" Review my CV", use_container_width=True):
            st.session_state.page = "cv_review"
            st.rerun()

    with col3:
        if st.button("  Interview prep", use_container_width=True):
            st.session_state.page = "interview_prep"
            st.rerun()

    # Recent application
    if apps:
        st.divider()
        st.markdown("### Recent application")
        recent = sorted(
            apps,
            key=lambda x: x.get("date", ""),
            reverse=True
        )[:5]

        for app in recent:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**{app['title']}** - {app['company']}")
                col2.markdown(app.get("status", "Applied"))
                col3.markdown(app.get("date", "")[:10])


# -- Job input from (reused across pages) ------------------------------------------
def render_job_form(prefix: str = "") -> dict:
    """
    Renders a job input form and returns the form data.
    Used by multiple pages - the prefix avoids key collisions.

    Returns:
        dict with keys: method, url, title, company, description

    """
    method = st.radio(
        "How are you entering this role?",
        ["Paste job description", "Enter job URL"],
        key=f"{prefix}_method",
        horizontal=True,
    )

    result = {"method": method}

    if method == "Enter job URL":
        result['url'] = st.text_input(
            "Job posting URL",
            placeholder="https://www.pnet.co.za/jobs/...",
            key=f"{prefix}_url"
        )
        st.caption(
            "Note: LinkedIn and some boards require login."
            "If scraping fails, paste the JD below as a fallback."
        )
        result["description"] = st.text_area(
            "Paste JD her as a fallback (optional)",
            height=150,
            key=f"{prefix}_fallback",
        )
        result["title"] = ""
        result["company"] = ""
    
    else:
        col1, col2 = st.columns(2)
        result["title"] = col1.text_input(
            "Job title",
            placeholder="Senior Data Scientist",
            key=f"{prefix}_title",
        )
        result["company"] = col2.text_input(
            "Company",
            placeholder="Nedbank",
            key=f"{prefix}_company",

        )
        result["description"] = st.text_area(
            "Paste job description",
            height=200,
            placeholder="Paste the full job description here...",
            key=f"{prefix}_desc",
        )
        result["url"] = None

    return result

# --- Output renderer -----------------------------------------------------------------------
def render_output(result):
    """
    Renders the agent output based on task type.
    Each task type has its own display format.
    """
    task = result.task
    output = result.output

    if task == "cover_letter":
        st.markdown("### Generated cover letter")
        st.markdown(
            f'<div class="output-box">{output.get("letter", "")}</div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            label= " Download as .txt",
            data= output.get("letter", ""),
            file_name=f"cover_letter_{result.job.company.replace(' ', '_')}.txt",
            mime= "text/plain"
        )

    elif task == "networking":
        st.markdown('### LinkedIn DM')
        st.markdown(
            f'<div class="output-box">{output.get("linkedin_dm", "")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### Cold email")
        st.markdown(
            f'<div class="output-box">{output.get("cold_email", "")}</div>',
            unsafe_allow_html=True,
        )
        combined = (
            f"LINKEDIN DM:\n{output.get('linkedin_dm', '')}\n\n"
            f"COLD EMAIL: \n{output.get('cold_email', '')}"
        )
        st.download_button(
            label= " Download messages",
            data= combined,
            file_name= f"outreach_{result.job.company.replace(' ', '_')}.txt",
            mime= "text/plain"
        )

    elif task == "cv_review":
        verdict = output.get("verdict", "Unknown")
        confidence = output.get("confidence", 0)

        col1, col2 = st.columns(2)
        col1.metric("Verdict", verdict)
        col2.metric("Confidence", f"{int(confidence * 100)}")

        st.markdown("**Strengths**")
        st.success(output.get("strengths", ""))

        st.markdown("**Wesknesses")
        st.warning(output.get("weaknesses", []))

        keywords = output.get("priority_edits", [])
        if keywords:
            st.markdown("**Missing keywords to add**")
            st.code(", ".join(keywords))

        edits = output.get("priiority_edits", [])
        if edits:
            st.markdown("**Priority edits**")
            for edit in edits:
                priority = edit.get("priority", "Medium")
                color = (
                    "Red" if priority == "High"
                    else "Yellow" if priority == "Medium"
                    else "Green"
                )
                with st.expander(
                    f"{color} {priority} - {edit.get('section', '')}"
                ):
                    st.markdown(f"**Suggestion:** {edit.get('suggestion', '')}")
                    st.markdown(f"**Why:** {edit.get('reason', '')}")

    elif task == 'interview_prep':
        questions= output.get("questions", [])
        st.markdown(f"### {len(questions)} taiored questions")

        phase_names= {
            1: "Phase I - CV & Background",
            2: "Phase II - Pitch and Storytelling",
            3: "Phase III - Technical",
            4: "Phase IV - Management Ailignment"
        }

        # Group by phase
        by_phase = {}
        for q in questions:
            phase= q.get("phase", 1)
            by_phase.setdefault(phase, []).append(q)

        for phase_num in sorted(by_phase.keys()):
            st.markdown(f"**{phase_names.get(phase_num, f'Phase {phase_num}')}**")
            for q in by_phase[phase_num]:
                with st.expander(q.get("question", "")):
                    st.markdown("**Model answer:**")
                    st.info(q.get("model_answer", ""))
                    st.markdown(f"  *{q.get('tip', '')}*")



# -- Feedback loop UI ------------------------------------------------------------------------

def render_feedback_loop(result, task_key: str):
    """
    Renders the satisfaction + feedback UI after an agent output.
    Manages the review state in session state.

    Args:
        result: OrchestrationResult to review
        task_key" unique key for this task's session state
    """ 
    coordinator = st.session_state.coordinator

    # Initialise review state if this is a fresh result
    state_key = f"review_state_{task_key}"
    if (
        state_key not in st.session_state
        or st.session_state[state_key] is None
        or st.session_state[state_key].result != result
    ):
        st.session_state[state_key] = coordinator.start(result)

    state = st.session_state[state_key]

    if state.done:
        st.success(state.message)
        return
    
    st.divider()
    st.markdown("#### Are you satisfied with this output?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "  Yes, save this",
            key=f"satisfied_{task_key}",
            use_container_width=True,
        ):
            new_state = coordinator.handle(state, satisfied=True)
            st.session_state[state_key] = new_state
            st.rerun()

    with col2:
        if st.markdown("**No - I want changes:**"):
            feedback = st.text_area(
                "What should Quark AI improve?",
                placeholder=(
                    "e.g. Make it more direct."
                    "Emphasise the CERN work."
                    "Shorter opening paragraph"
            ),
            key=f"feedback_{task_key}",
            height=80,
        )
        if st.button(
            " Revise",
            key=f"revise_{task_key}",
            use_container_width=True,
        ):
            if not feedback.strip():
                st.warning("Please enter your feedback first.")
            else:
                with st.spinner("Quark AI is revising..."):
                    new_state = coordinator.handle(
                        state,
                        satisfied=True,
                        feedback=feedback,
                    )
                st.session_state[state_key] = new_state
                st.rerun()

    if state.iteration > 0:
        st.caption(
            f"Revision {state.iteration} of "
            f"{coordinator.MAX_ITERATIONS}"
        )


# -- Page: New Application ---------------------------------------------------

def page_new_application():
    st.markdown("##   New application ")
    st.caption("Generate cover letter and networking messages for a role")

    if not st.session_state.cv_text:
        st.warning("Please upload your CV in the sidebar first.")
        return
    
    job_data = render_job_form(prefix="new_app")

    col1, col2 = st.columns(2)
    task = col1.selectbox(
        "What do you need?",
        ["cover_letter", "networking"],
        format_func=lambda x: {
            "cover_letter": "Cover letter",
            "networking": "LinkedIn DM + cold email",
        }[x],
        key="new_app_task"
    )

    status = col2.selectbox(
        "Application status",
        ["Applied", "Interview", "Offer recieved", "Contract signed", "Rejected"],
        key="new_app_status",
    )

    if st.button(" Generate with Quark AI", type="primary"):
        orch = get_orchestrator()

        # Validate inputs
        if job_data["method"] == "Paste job description":
            if not all([
                job_data.get("title"),
                job_data.get("company"),
                job_data.get("description")
            ]):
                st.error("Please fill in title, company, and job description.")
                return
            
        else:
            if not job_data.get("url"):
                st.error("Please enter a job URL. ")
                return
            
        with st.spinner("Quark AI is generating..."):
            try:
                if job_data["method"] == "Enter job URL":
                    result = orch.run(
                        task=task,
                        cv_path=st.session_state.cv_path,
                        job_url=job_data["url"],
                        manual_description=job_data.get("description", ""),
                    )
                else:
                    result = orch.run(
                        task=task,
                        cv_path=st.session.cv_path,
                        manual_title=job_data["title"],
                        manual_company=job_data["company"],
                        manual_description=job_data["descsription"],
                    )

                st.session_state.current_result = result

                # Save to application tracker
                app_entry = {
                    "title": result.job.title,
                    "company": result.job.company,
                    "status": status,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": result.job.source,
                    "task": task,
                }
                st.session_state.application.append(app_entry)
            
            except Exception as e:
                st.error(f"Error: {e}")
                return 
            
            if result.needs_manual_id:
                st.warning(
                    "The URL returned limited content."
                    "Results are vased on what was scraped. "
                    "For better results, paste the full JD as a fallback"
                )

    # Render output if available
    if st.session_state.current_result:
        result = st.session_state.current_result
        st.divider()
        render_output(result)
        render_feedback_loop(result, task_key="new_app")


# --- Page: CV Review -------------------------------------------------------------------
def page_cv_review():
    st.markdown("##   CV review")
    st.caption("Analyse your CV against a specific job description")

    if not st.session_state.cv_text:
        st.warning("Please upload your CV in the sidebar first")
        return
    
    job_data = render_job_form(prefix="cv_review")

    if st.button("   Review my CV", type="primary"):
        orch = get_orchestrator()

        with st.spinner("Quark AI is analysis your CV..."):
            try:
                if job_data["method"] == "Enter job URL":
                    result = orch.run(
                        task="cv_review",
                        cv_path=st.session_state.cv_path,
                        job_url=job_data["url"],
                        manual_description=job_data.get("description", ""),
                    )
                else:
                    result = orch.run(
                        task="cv_review",
                        cv_path=st.session_state.cv_path,
                        manual_title=job_data["title"],
                        manual_company=job_data["company"],
                        manual_description=job_data["description"],
                    )
                st.session_state["cv_review_result"] = result

            except Exception as e:
                st.error(f"Error: {e}")
                return
            

    if st.session_state.get("cv_review_result"):
        st.divider()
        render_output(st.session_state["cv_review_result"])

## ------ Page: Interview prep ---------------------------------------------
def page_interview_prep():
    st.markdown("##   Interview prep")
    st.caption(
        "Phase-mapped questions and model answers tailored to your role"
    )

    if not st.session_state.cv_text:
        st.warning("Please upload your CV in the sidebar first.")
        return 
    
    job_data = render_job_form(prefix="interview")

    if st.button(" Generate prep questions", type="primary"):
        orch = get_orchestrator()

        with st.spinner("Quark AI is generating your interview prep..."):
            try:
                if job_data["method"] == "Enter job URL":
                    result = orch.run(
                        task="interview_prep",
                        cv_path=st.session_state.cv_path,
                        job_url=job_data["url"],
                        manual_description=job_data.get("description")
                    )

                else:
                    result = orch.run(
                        task="interview_prep",
                        cv_path=st.session_state.cv_path,
                        manual_title=job_data["title"],
                        manual_company=job_data["company"],
                        manual_description=job_data["description"]
                    )
                st.session_state["interview_result"] = result

            except Exception as e:
                st.error(f"Error: {e}")
                return
            
    if st.session_state.get("interview_result"):
        result = st.session_state["interview_result"]
        st.divider()
        render_output(result)
        render_feedback_loop(result, task_key="interview")

## --------Page: Application Tracker ---------------------------------------

def page_tracker():
    st.markdown("##   Application tracker")

    apps = st.session_state.applications

    if not apps:
        st.info(
            "No applications tracked yet."
            "Use 'New application' to start tracking"
        )
        return
    
    # Summary metrics
    total = len(apps)
    by_status = {}
    for a in apps:
        s = a.get("status", "Applied")
        by_status[s] = by_status.get(s, 0) + 1

    cols = st.columns(len(by_status) + 1)
    cols[0].metric("Total", total)

    for i, (status, count) in enumerate(by_status.items(), 1):
        cols[i].metric(status, count)

    st.divider()

    # Application table
    st.markdown("### All applications")

    # Manual status update
    for i, app in enumerate(apps):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            col1.markdown(f"**{app['title']}** - {app['company']}")
            col3.markdown(app.get("date", "")[:10])

            new_status = col2.selectbox(
                "Status",
                ["Applied", "Interview", "Offer received", "Contract signed", "Rejected"],
                index=["Applied", "Interview", "Offer received", "Contract signed", "Rejected"].index(
                    app.get("status", "Applied")
                ),
                key=f"status_{i}",
                label_visibility="collapsed"
            )

            # Update status if changed
            if new_status != app.get("status"):
                st.session_state.applications[i]["status"] = new_status
                st.rerun()

        st.divider()

    # Export
    if st.button("   Export tracker as JSON"):
        st.download_button(
            label="Download application.json",
            data=json.dumps(apps, indent=2),
            file_name="quark_ai_application.json",
            mime="application/json"
        )

# ------ Main router -----------------------------------------------------------
def main():
    init_state()
    render_sidebar()

    page = st.session_state.page

    if page == "home":
        page_home()
    elif page == "new_application":
        page_new_application()
    elif page == "cv_review":
        page_cv_review()
    elif page == "interview_prep":
        page_interview_prep()
    elif page == "tracker":
        page_tracker()


if __name__ == "__main__":
    main()

            