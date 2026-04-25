# Architecture: SDLC Multi-Agent Backend Builder

## System Goal

The system is designed to demonstrate how multiple AI-inspired agents can collaborate across the software development lifecycle instead of acting like a single chatbot. The current implementation focuses on backend project generation, validation, review, decision-making, and delivery.

## Core Idea

Rather than answering with unstructured code snippets, the platform turns a requirement into a packaged engineering output:

- requirement understanding,
- project type identification,
- backend code generation,
- test generation,
- visible agent communication,
- runtime execution and validation,
- reviewer scoring,
- readiness decision-making,
- deployment handoff.

## High-Level Flow

```text
User
 |
 v
Streamlit UI / API Client
 |
 v
SDLC Builder API
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
 +--> Deployment Artifact Generation
 |
 v
Structured Output Package
```

## Implemented Components

### 1. `ai_developer.py`

Primary orchestration layer for the builder workflow.

Responsibilities:

- receives project descriptions,
- maps them to one of the supported project templates,
- generates FastAPI starter code,
- generates basic test code,
- reviews the generated scaffold for quality and security,
- makes a readiness decision with explainable confidence,
- generates deployment script,
- exposes the result through API endpoints.

### 2. `tester_agent.py`

Validation layer for the generated or running API.

Responsibilities:

- health-check testing,
- endpoint validation,
- response structure validation,
- basic negative-path testing.

### 3. `app.py`

Presentation and delivery layer.

Responsibilities:

- allows a non-technical or junior user to interact with the system,
- collects project requirements,
- displays generated code and deployment output,
- helps demonstrate the workflow clearly in an interview.

### 4. `main.py`

Gemini integration layer.

Responsibilities:

- wraps the Gemini API behind FastAPI,
- adds caching,
- adds simple rate limiting,
- supports experimentation with LLM-backed services.

## Agent Mapping

The current project can be explained as a multi-agent system with these practical roles:

| Agent | Current Implementation | Responsibility |
|------|-------------------------|----------------|
| Planner Agent | `ai_developer.py` | Converts user requirement into a matched project pattern and planning brief |
| Developer Agent | `ai_developer.py` | Generates the project scaffold and applies a hardening pass when needed |
| Tester Agent | `tester_agent.py` | Validates generated or running service |
| Reviewer Agent | `ai_developer.py` | Scores code quality, security, and best-practice gaps |
| Decision Agent | `ai_developer.py` | Determines readiness and whether regeneration is needed |
| Delivery Agent | `app.py` | Makes the system usable and demo-friendly |
| Model Service Agent | `main.py` | Provides reusable model access infrastructure |

## Request Lifecycle

### Build Flow

```text
1. User submits requirement
2. Planner agent analyzes keywords, intent, and expected capabilities
3. System selects a matching project template
4. Developer agent produces FastAPI starter files
5. Tester agent creates validation scripts
6. Reviewer agent scores quality and risk
7. Decision agent determines whether to harden the scaffold
8. Deployment script is prepared
9. Results are returned to the UI
```

### Validation Flow

```text
1. Tester agent calls service endpoints
2. It checks status codes and response structure
3. It validates both successful and failing cases
4. It reports pass/fail summary
```

## Why This Architecture Matters

This architecture is stronger than a generic chatbot demo because:

- it separates responsibilities,
- it produces structured outputs,
- it supports demonstration of workflow thinking,
- it includes a self-critique and readiness gate,
- it shows how AI can assist engineering processes, not only chat,
- it is easy to extend with additional specialist agents.

## Extension Roadmap

The project can be expanded into a richer SDLC platform with:

- a Business Analyst agent for requirement clarification,
- an Architect agent for project breakdown and technology choices,
- a Documentation agent for README and API docs,
- a DevOps agent for Docker, CI/CD, and deployment manifests.

## Interview-Friendly Summary

You can present this architecture in one sentence:

> The system models a lightweight software team where separate agents handle planning, generation, validation, review, decision-making, and delivery so that users receive build-ready engineering artifacts instead of only AI chat responses.
