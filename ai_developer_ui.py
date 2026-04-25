"""
AI Development Assistant - Streamlit UI
Build FastAPI projects from natural language requirements
"""

import streamlit as st
import requests
import json
import time
from pathlib import Path

BUILD_TIMEOUT_SECONDS = 180
BUILD_AND_DEPLOY_TIMEOUT_SECONDS = 240

# Page Configuration
st.set_page_config(
    page_title="AI Development Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .project-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .code-block {
        background-color: #f1f1f1;
        padding: 1rem;
        border-radius: 0.3rem;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        margin: 0.5rem 0;
    }
    .success-msg {
        color: #28a745;
        font-weight: bold;
    }
    .error-msg {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8001"

# Initialize session state
if "project_data" not in st.session_state:
    st.session_state.project_data = None
if "build_status" not in st.session_state:
    st.session_state.build_status = None

# Sidebar
st.sidebar.title("🤖 AI Development Assistant")
st.sidebar.markdown("---")

# API Status Check
try:
    response = requests.get(f"{API_BASE_URL}/", timeout=5)
    if response.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Error")
except:
    st.sidebar.error("❌ Cannot Connect to API")
    st.sidebar.info("Start the AI Developer API:")
    st.sidebar.code("python ai_developer.py", language="bash")

st.sidebar.markdown("---")

# Available Templates
try:
    templates_response = requests.get(f"{API_BASE_URL}/templates", timeout=5)
    if templates_response.status_code == 200:
        templates = templates_response.json()
        st.sidebar.subheader("📋 Available Templates")
        for template, desc in templates.get("descriptions", {}).items():
            st.sidebar.markdown(f"**{template.replace('_', ' ').title()}**")
            st.sidebar.caption(desc)
            st.sidebar.markdown("")
except:
    pass

# Main Content
st.title("🤖 AI Development Assistant")
st.markdown("Build complete FastAPI projects from natural language requirements!")

# Project Input Section
st.header("🎯 Describe Your Project")

col1, col2 = st.columns([2, 1])

with col1:
    project_description = st.text_area(
        "What do you want to build?",
        placeholder="E.g., 'Build a todo list app with user authentication' or 'Create a weather API that shows forecasts'",
        height=100,
        help="Describe any project you want to build. The AI will analyze your requirements and generate complete FastAPI code."
    )

with col2:
    additional_requirements = st.text_area(
        "Additional Requirements (Optional)",
        placeholder="Any specific features, technologies, or constraints...",
        height=100,
        help="Add any specific requirements like authentication, database, external APIs, etc."
    )

# Build Options
st.markdown("---")
st.subheader("🔧 Build Options")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Build Project", type="primary", use_container_width=True):
        if not project_description.strip():
            st.error("Please describe what you want to build!")
        else:
            with st.spinner("🤖 Running AI planning, code generation, review, and runtime validation..."):
                try:
                    payload = {
                        "description": project_description,
                        "requirements": additional_requirements if additional_requirements.strip() else None
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/build",
                        json=payload,
                        timeout=BUILD_TIMEOUT_SECONDS
                    )

                    if response.status_code == 200:
                        st.session_state.project_data = response.json()
                        st.success("✅ Project generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to generate project: {response.text}")

                except requests.exceptions.Timeout:
                    st.error(
                        f"⏱️ Build timed out after {BUILD_TIMEOUT_SECONDS} seconds. "
                        "The AI-first pipeline can take longer because it plans, generates, and runs the project before returning."
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with col2:
    if st.button("🔨 Build & Deploy", use_container_width=True):
        if not project_description.strip():
            st.error("Please describe what you want to build!")
        else:
            with st.spinner("🤖 Building, validating, and packaging the project..."):
                try:
                    payload = {
                        "description": project_description,
                        "requirements": additional_requirements if additional_requirements.strip() else None
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/build-and-deploy",
                        json=payload,
                        timeout=BUILD_AND_DEPLOY_TIMEOUT_SECONDS
                    )

                    if response.status_code == 200:
                        st.session_state.build_status = response.json()
                        st.success("✅ Project built and deployed!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to build project: {response.text}")

                except requests.exceptions.Timeout:
                    st.error(
                        f"⏱️ Build & Deploy timed out after {BUILD_AND_DEPLOY_TIMEOUT_SECONDS} seconds. "
                        "Keep the backend running and try again once the AI build path settles."
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Display Generated Project
if st.session_state.project_data:
    st.markdown("---")
    st.header("📦 Generated Project")

    project_data = st.session_state.project_data

    # Project Info
    st.subheader(f"🏗️ {project_data['project_type'].replace('_', ' ').title()}")
    st.info(project_data['description'])

    confidence = project_data.get("confidence_report", {})
    decision = project_data.get("decision_report", {})
    reviewer = project_data.get("reviewer_report", {})
    execution = project_data.get("execution_report", {})
    agent_logs = project_data.get("agent_logs", [])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confidence", f"{confidence.get('confidence_score', 'N/A')}%")
    with col2:
        st.metric("Decision", decision.get("status", "N/A"))
    with col3:
        st.metric("Security", reviewer.get("security_risk", "N/A"))

    if project_data.get("planner_output"):
        st.subheader("Planner Output")
        st.json(project_data["planner_output"])

    if project_data.get("technology_decision"):
        st.subheader("Technology Decision")
        st.json(project_data["technology_decision"])

    st.subheader("Reviewer Report")
    st.write(f"Code Quality: {reviewer.get('code_quality_score', 'N/A')}/10")
    for item in reviewer.get("improvements", []):
        st.write(f"- {item}")

    st.subheader("Decision + Explainability")
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
    st.write(f"Runtime status: {execution.get('status', 'N/A')}")
    st.write(f"Service ready: {execution.get('service_ready', 'N/A')}")
    for check in execution.get("runtime_checks", []):
        icon = "PASS" if check.get("passed") else "FAIL"
        st.write(f"- {icon} {check.get('name')}: {check.get('details')}")
    if execution.get("generated_tests"):
        st.write(f"Generated tests passed: {execution['generated_tests'].get('passed', 'N/A')}")
        if execution["generated_tests"].get("output"):
            st.code(execution["generated_tests"]["output"], language="text")
        if execution["generated_tests"].get("error_output"):
            st.code(execution["generated_tests"]["error_output"], language="text")
    
    # Endpoints
    st.subheader("🔗 API Endpoints")
    for endpoint in project_data['endpoints']:
        st.code(endpoint, language="http")
    # Generated Code
    st.subheader("💻 Generated Code")

    tabs = st.tabs(["Main API", "Tests", "Deployment"])

    with tabs[0]:
        if "main.py" in project_data['code']:
            st.code(project_data['code']['main.py'], language="python")

    with tabs[1]:
        if project_data.get('test_code') and "test_api.py" in project_data['test_code']:
            st.code(project_data['test_code']['test_api.py'], language="python")

    with tabs[2]:
        st.code(project_data['deployment_script'], language="bash")

    # Download Options
    st.markdown("---")
    st.subheader("💾 Download Project")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Download main.py", use_container_width=True):
            st.download_button(
                label="Download",
                data=project_data['code']['main.py'],
                file_name="main.py",
                mime="text/plain"
            )

    with col2:
        if st.button("🧪 Download Tests", use_container_width=True):
            if project_data.get('test_code'):
                st.download_button(
                    label="Download",
                    data=project_data['test_code']['test_api.py'],
                    file_name="test_api.py",
                    mime="text/plain"
                )

    with col3:
        if st.button("🚀 Download Deploy Script", use_container_width=True):
            st.download_button(
                label="Download",
                data=project_data['deployment_script'],
                file_name="deploy.sh",
                mime="text/plain"
            )

# Build Status
if st.session_state.build_status:
    st.markdown("---")
    st.header("🔨 Build Status")

    status = st.session_state.build_status

    if status['status'] == 'success':
        st.success(f"✅ {status['message']}")
        if status.get('project_path'):
            st.info(f"📁 Project created at: {status['project_path']}")

        if status.get('test_results'):
            st.subheader("🧪 Test Results")
            st.json(status['test_results'])
        if status.get('agent_logs'):
            st.subheader("Agent Timeline")
            for log in status['agent_logs']:
                target = f" -> {log.get('to_agent')}" if log.get("to_agent") else ""
                st.write(f"[{log.get('agent', 'Agent')}{target}] {log.get('message', '')} ({log.get('status', 'unknown')})")
    else:
        st.error(f"❌ {status['message']}")

# Examples Section
st.markdown("---")
st.header("💡 Example Projects")

examples = [
    "Build a todo list app with CRUD operations",
    "Create a weather API that integrates with external services",
    "Build a user management system with authentication",
    "Create a blog API with posts and comments",
    "Build an e-commerce API with products and orders"
]

for example in examples:
    if st.button(f"🚀 {example}", key=example):
        st.session_state.example_text = example
        st.rerun()

if hasattr(st.session_state, 'example_text'):
    project_description = st.session_state.example_text
    st.info(f"Selected: {project_description}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using FastAPI + Streamlit")

# Instructions
with st.expander("📖 How to Use"):
    st.markdown("""
    ## Getting Started

    1. **Start the AI Developer API:**
       ```bash
       python ai_developer.py
       ```

    2. **Start this Streamlit UI:**
       ```bash
       streamlit run ai_developer_ui.py
       ```

    3. **Describe your project** in natural language

    4. **Click "Build Project"** to generate code

    5. **Download the files** and run them locally

    ## Supported Project Types

    - **Todo Apps** - Task management with CRUD
    - **Weather APIs** - Weather data and forecasts
    - **User Management** - Authentication and profiles
    - **Blog APIs** - Content management with comments

    ## Features

    - 🤖 **AI-Powered** - Analyzes natural language requirements
    - ⚡ **FastAPI** - Modern, fast web framework
    - 🧪 **Auto-Testing** - Generated test suites
    - 🚀 **Auto-Deployment** - Ready-to-run scripts
    - 📥 **Downloadable** - Get complete project files
    """)
