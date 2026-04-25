# SDLC Multi-Agent Backend Builder

This project is a multi-agent software development lifecycle assistant that converts a plain-English product idea into a delivery-ready project package. Instead of behaving like a normal chatbot, it simulates a lightweight engineering workflow: understanding the requirement, planning the solution, selecting a project pattern, generating backend code, producing test assets, reviewing quality and security, making a readiness decision, preparing documentation, and creating deployment artifacts.

The goal is to show a more interview-worthy use of AI than "ask a model for code." The value here is orchestration. Different agents handle different responsibilities so that a non-technical user, tester, or junior developer can move from idea to working backend scaffold faster and with more structure.

## Problem Statement

Traditional AI chatbots can generate code snippets quickly, but they do not reliably manage the full software development lifecycle. They often return unstructured answers, skip testing concerns, and leave non-technical users unsure how to convert an idea into a usable project.

This project solves that gap by building a multi-agent SDLC assistant that:

- accepts a natural-language software requirement,
- analyzes the request and maps it to a backend project type,
- creates a project summary and architecture blueprint,
- generates an implementation plan and task breakdown,
- generates a runnable FastAPI codebase,
- creates test scripts for validation,
- reviews the generated scaffold for code quality, security risk, and best practices,
- decides whether the output is production-ready or should be improved,
- reports a confidence score with explainable reasoning,
- generates handoff documentation,
- prepares deployment assets for handoff,
- exposes the entire workflow through APIs and a simple UI.

## Why This Project Is Different

- It is not just a chatbot response generator. It is a task-oriented SDLC pipeline.
- It is designed for role-based collaboration, not only for developers.
- It produces structured deliverables: plan, architecture, tasks, code, tests, reviewer feedback, decision output, confidence scoring, documentation, endpoints, and deployment script.
- It is easier to demonstrate in an interview because the output is concrete and inspectable.
- It shows system design thinking, not only prompt engineering.

## Interview Pitch

You can describe the project like this:

> I built a multi-agent SDLC assistant that helps a user go from requirement to a delivery-ready project package. Instead of giving only a chat answer, the system behaves like a small software team with separate responsibilities for planning, architecture, code generation, testing, documentation, and delivery. The output is not just code, but a structured implementation bundle.

## Current Agent Roles

### 1. Planner Agent

Implemented in `ai_developer.py`.

Responsibilities:

- receives the requirement,
- identifies the likely project type,
- chooses a template,
- surfaces key risks and capability expectations,
- returns planning artifacts before generation starts.

### 2. Developer Agent

Implemented in `ai_developer.py`.

Responsibilities:

- generates FastAPI code,
- creates the starter backend scaffold,
- supports a hardened second pass when the decision layer requests improvements.

### 3. Tester Agent

Implemented in `tester_agent.py`.

Responsibilities:

- validates the generated or running API,
- checks happy-path and error-path behavior,
- confirms response structure and service health.

### 4. Reviewer Agent

Implemented in `ai_developer.py`.

Responsibilities:

- checks code quality,
- flags security risks,
- highlights best-practice gaps,
- gives interview-friendly scoring and improvement notes.

### 5. Decision Agent

Implemented in `ai_developer.py`.

Responsibilities:

- evaluates whether the generated output is ready,
- decides whether to regenerate a hardened version,
- returns production-readiness and reasoning.

### 6. Delivery Agent

Implemented through `app.py` and deployment script generation.

Responsibilities:

- presents the workflow to the end user,
- allows non-technical interaction,
- packages the generated project for handoff.

### 7. Gemini Service Layer

Implemented in `main.py`.

Responsibilities:

- exposes a Gemini wrapper with caching and rate limiting,
- provides a reusable model access layer for AI-enabled workflows,
- supports experimentation beyond the builder pipeline.

## Architecture Overview

```text
User Requirement
    |
    v
SDLC Multi-Agent Builder
    |
    +--> Planner Agent
    |
    +--> Developer Agent
    |
    +--> Tester Agent
    |
    +--> Reviewer Agent
    |
    +--> Decision Agent
    |
    +--> Delivery Agent
    |
    v
Delivery-Ready Project Package
```

For a more detailed breakdown, see [ARCHITECTURE.md](/C:/Users/hasik/Downloads/internship_tasks/multi%20agent%20project/ARCHITECTURE.md).

## Key Features

- Natural-language project input
- Template-driven FastAPI generation
- Architecture and implementation planning
- Team-style task breakdown generation
- Multi-agent workflow presentation
- Automated test generation
- Visible agent timeline and inter-agent communication logs
- Runtime execution of generated APIs with pass/fail reporting
- Reviewer scoring for code quality and security
- Readiness decision layer with auto-hardening
- Confidence score with explainability
- Generated documentation and handoff notes
- Deployment script generation
- Streamlit UI for easy demonstration
- Gemini wrapper with caching and rate limiting

## Supported Project Types

- Todo application
- Weather API
- User management system
- Blog API

These are starter templates today, but the architecture is designed to expand into richer project planning and execution flows.

## Project Structure

```text
ai_developer.py      Multi-agent backend builder API
app.py               Streamlit demo interface
main.py              Gemini API wrapper with caching and rate limiting
tester_agent.py      Automated API validation agent
ARCHITECTURE.md      Technical architecture and workflow explanation
PROBLEM_STATEMENT.md Interview-ready project framing
QUICK_START.md       Setup instructions
requirements.txt     Python dependencies
```

## How To Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
DEBUG=True
```

Use `DEBUG=True` if you want to test without consuming API quota.

### 3. Start the SDLC builder API

```bash
python ai_developer.py
```

Runs on `http://localhost:8001`.

### 4. Start the demo UI

```bash
streamlit run app.py
```

Runs on `http://localhost:8501`.

### 5. Optional: start the Gemini wrapper

```bash
python main.py
```

Runs on `http://localhost:8000`.

## Security Scanning

This project includes lightweight security scanning support with:

- `bandit` for Python source-code security checks
- `pip-audit` for dependency vulnerability checks

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the scans manually:

```bash
bandit -r . -x ./venv,./__pycache__
pip-audit
```

Or use the helper scripts:

```bash
security_scan.bat
```

```bash
./security_scan.sh
```

This is a practical interview-friendly setup that shows both code-level and dependency-level security awareness without requiring enterprise tooling.

## Main API Endpoints

### SDLC Builder API

- `GET /` - project overview and available endpoints
- `GET /templates` - list available starter templates
- `GET /agents` - list active agent responsibilities
- `GET /workflow` - view lifecycle stages and project value
- `POST /build` - generate a full project package including reviewer, decision, and confidence reports
- `POST /build-and-deploy` - create a temporary build directory

### Gemini Wrapper API

- `GET /health`
- `POST /chat`
- `POST /chat-stream`
- `GET /stats`

## Suggested Demo Flow For Interview

1. Open the Streamlit app.
2. Enter a requirement like: `Build a student management API with authentication and CRUD`.
3. Show how the system classifies the request and generates architecture, plan, tasks, and code artifacts.
4. Highlight the reviewer report, readiness decision, and confidence score.
5. Open the generated endpoints, documentation, and test script.
6. Explain that the tester agent validates quality, the reviewer critiques the scaffold, and the decision layer determines whether to improve it.

## Future Improvements

- Add a requirement analyst agent for ambiguity detection
- Add a documentation agent for API docs and README generation
- Add a DevOps agent for Docker and CI/CD pipelines
- Add persistent project memory and iteration history
- Add support for more frameworks beyond FastAPI

## Best One-Line Description

This is a multi-agent SDLC assistant that transforms product requirements into delivery-ready project packages instead of returning generic chatbot answers.
