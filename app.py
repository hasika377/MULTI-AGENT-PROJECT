"""
Streamlit frontend for the SDLC Multi-Agent Builder.
Displays a full project package, not just generated code.
"""

import streamlit as st
import requests

BUILD_TIMEOUT_SECONDS = 180


st.set_page_config(
    page_title="SDLC Multi-Agent Builder",
    page_icon=":computer:",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.sidebar.title("Configuration")
API_URL = "http://localhost:8001"

try:
    health_response = requests.get(f"{API_URL}/", timeout=5)
    if health_response.status_code == 200:
        st.sidebar.success("API is online")
    else:
        st.sidebar.error("API returned an error")
except requests.exceptions.ConnectionError:
    st.sidebar.error("Cannot connect to developer API")
    st.sidebar.info("Start it with: `python ai_developer.py`")
except Exception as exc:
    st.sidebar.error(f"Connection error: {exc}")

st.sidebar.divider()
st.sidebar.subheader("How It Works")
st.sidebar.markdown(
    """
1. Start the backend with `python ai_developer.py`
2. Describe the software requirement in plain English
3. Click `Build Project`
4. Review the generated code, tests, and deployment assets
    """
)

st.sidebar.divider()
st.sidebar.subheader("Agent Flow")
st.sidebar.markdown(
    """
- `Planner Agent`: understands the request and selects the project pattern
- `Developer Agent`: creates the architecture, plan, and backend starter
- `Tester Agent`: prepares validation assets
- `Reviewer Agent`: scores quality and flags security gaps
- `Decision Agent`: decides if the package is ready or should be improved
- `Delivery Agent`: presents the output for handoff
"""
)


if "project_data" not in st.session_state:
    st.session_state.project_data = None


st.title("SDLC Multi-Agent Backend Builder")
st.caption("Turn a software requirement into a delivery-ready project package with plan, architecture, code, tests, and deployment assets.")

example_prompts = [
    "Build a student management API with authentication and CRUD operations",
    "Create a student grade prediction API",
    "Build a bug tracking backend for testers and developers",
    "Create a blog API with posts, comments, and role-based access",
]

selected_example = st.selectbox(
    "Quick examples",
    [""] + example_prompts,
    help="Pick an example to quickly populate the project description.",
)

default_description = selected_example if selected_example else ""

project_description = st.text_area(
    "What do you want to build? *",
    value=default_description,
    height=140,
    placeholder="Example: Build a chatbot system with FastAPI, message history, and user support features.",
)

additional_requirements = st.text_area(
    "Additional requirements",
    height=120,
    placeholder="Example: add authentication, request validation, sample tests, or deployment notes.",
)

col1, col2 = st.columns([1, 1])

with col1:
    build_clicked = st.button("Build Project", type="primary", use_container_width=True)

with col2:
    clear_clicked = st.button("Clear Output", use_container_width=True)

if clear_clicked:
    st.session_state.project_data = None
    st.rerun()

if build_clicked:
    if not project_description.strip():
        st.error("Enter a project description first.")
    else:
        payload = {
            "description": project_description,
            "requirements": additional_requirements.strip() or None,
        }

        try:
            with st.spinner("Building project package with AI planning, generation, review, and runtime checks..."):
                response = requests.post(f"{API_URL}/build", json=payload, timeout=BUILD_TIMEOUT_SECONDS)

            if response.status_code == 200:
                st.session_state.project_data = response.json()
                st.success("Project package generated successfully.")
            else:
                try:
                    detail = response.json()
                except Exception:
                    detail = response.text
                st.error(f"Build failed: {detail}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the developer API. Start it with `python ai_developer.py`.")
        except requests.exceptions.Timeout:
            st.error(
                f"The build request timed out after {BUILD_TIMEOUT_SECONDS} seconds. "
                "AI planning plus runtime execution can take longer on the first run, so keep the backend running and try again."
            )
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")


project_data = st.session_state.project_data

if project_data:
    st.divider()
    st.subheader("Generated Project")

    st.write(f"Project type: `{project_data['project_type']}`")
    st.write(project_data["description"])
    st.write(project_data.get("project_summary", ""))
    st.info(
        "This output is framed as an SDLC workflow result: planning, scaffold generation, validation assets, reviewer scoring, readiness decision, confidence reasoning, documentation, and deployment handoff."
    )

    confidence = project_data.get("confidence_report", {})
    decision = project_data.get("decision_report", {})
    reviewer = project_data.get("reviewer_report", {})
    execution = project_data.get("execution_report", {})
    agent_logs = project_data.get("agent_logs", [])

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Confidence Score", f"{confidence.get('confidence_score', 'N/A')}%")
    with metric_col2:
        st.metric("Decision", decision.get("status", "N/A"))
    with metric_col3:
        st.metric("Security Risk", reviewer.get("security_risk", "N/A"))

    st.subheader("Planner Output")
    planner_output = project_data.get("planner_output", {})
    if planner_output:
        st.json(planner_output)

    st.subheader("Technology Decision")
    technology_decision = project_data.get("technology_decision", {})
    if technology_decision:
        st.json(technology_decision)

    st.subheader("Recommended Stack")
    st.write(", ".join(project_data.get("recommended_stack", [])))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Implementation Plan")
        for step in project_data.get("implementation_plan", []):
            st.write(f"- {step}")

    with col2:
        st.subheader("Deliverables")
        for item in project_data.get("deliverables", []):
            st.write(f"- {item}")

    st.subheader("Architecture Blueprint")
    architecture = project_data.get("architecture", {})
    if architecture:
        st.json(architecture)

    st.subheader("Task Breakdown")
    task_breakdown = project_data.get("task_breakdown", {})
    for section, tasks in task_breakdown.items():
        st.markdown(f"**{section.replace('_', ' ').title()}**")
        for task in tasks:
            st.write(f"- {task}")

    st.subheader("Test Strategy")
    for item in project_data.get("test_strategy", []):
        st.write(f"- {item}")

    insight_col1, insight_col2 = st.columns(2)
    with insight_col1:
        st.subheader("Reviewer Report")
        st.write(f"Code Quality: `{reviewer.get('code_quality_score', 'N/A')}/10`")
        st.write(f"Security Risk: `{reviewer.get('security_risk', 'N/A')}`")
        for item in reviewer.get("improvements", []):
            st.write(f"- {item}")

    with insight_col2:
        st.subheader("Decision And Explainability")
        st.write(f"Decision: `{decision.get('status', 'N/A')}`")
        st.write(decision.get("summary", ""))
        for item in decision.get("reason", []):
            st.write(f"- {item}")
        for item in confidence.get("reasons", []):
            st.write(f"- {item}")

    st.subheader("Agent Timeline")
    if agent_logs:
        for log in agent_logs:
            target = f" -> {log.get('to_agent')}" if log.get("to_agent") else ""
            st.write(f"[{log.get('agent', 'Agent')}{target}] {log.get('message', '')} ({log.get('status', 'unknown')})")

    st.subheader("Execution Report")
    st.write(f"Runtime status: `{execution.get('status', 'N/A')}`")
    st.write(f"Service ready: `{execution.get('service_ready', 'N/A')}`")
    for check in execution.get("runtime_checks", []):
        icon = "PASS" if check.get("passed") else "FAIL"
        st.write(f"- `{icon}` {check.get('name')}: {check.get('details')}")
    generated_tests = execution.get("generated_tests", {})
    if generated_tests:
        st.write(f"Generated tests passed: `{generated_tests.get('passed', 'N/A')}`")
        if generated_tests.get("output"):
            st.code(generated_tests.get("output", ""), language="text")
        if generated_tests.get("error_output"):
            st.code(generated_tests.get("error_output", ""), language="text")

    tabs = st.tabs(["Code", "Tests", "Documentation", "Deployment"])

    with tabs[0]:
        code_files = project_data.get("code", {})
        for filename, content in code_files.items():
            st.markdown(f"**{filename}**")
            st.code(content, language="python")

    with tabs[1]:
        test_files = project_data.get("test_code", {})
        if test_files:
            for filename, content in test_files.items():
                st.markdown(f"**{filename}**")
                st.code(content, language="python")
        else:
            st.info("No tests were generated.")

    with tabs[2]:
        docs = project_data.get("documentation", {})
        if docs:
            for filename, content in docs.items():
                st.markdown(f"**{filename}**")
                st.code(content, language="markdown")
        else:
            st.info("No documentation was generated.")

    with tabs[3]:
        st.code(project_data.get("deployment_script", ""), language="bash")

    main_code = project_data.get("code", {}).get("main.py")
    if main_code:
        st.download_button(
            label="Download main.py",
            data=main_code,
            file_name="main.py",
            mime="text/x-python",
        )
