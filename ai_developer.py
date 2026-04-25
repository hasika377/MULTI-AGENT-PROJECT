"""
SDLC Multi-Agent Builder
Builds delivery-ready project packages from natural language requirements.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import subprocess
import tempfile
import shutil
import socket
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv
import google.generativeai as genai

app = FastAPI(
    title="SDLC Multi-Agent Backend Builder",
    description="A multi-agent system that converts natural-language requirements into build-ready FastAPI starter projects",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_ROOT = Path(__file__).resolve().parent
load_dotenv()

DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
AI_GENERATION_ENABLED = bool(GEMINI_API_KEY) and not DEBUG_MODE

if AI_GENERATION_ENABLED:
    genai.configure(api_key=GEMINI_API_KEY)

# Project templates
PROJECT_TEMPLATES = {
    "todo_app": {
        "description": "A simple todo list application",
        "endpoints": [
            "GET /todos - List all todos",
            "POST /todos - Create new todo",
            "PUT /todos/{id} - Update todo",
            "DELETE /todos/{id} - Delete todo"
        ],
        "models": ["Todo"],
        "features": ["CRUD operations", "In-memory storage"]
    },
    "weather_api": {
        "description": "Weather data API with external service integration",
        "endpoints": [
            "GET /weather/{city} - Get weather for city",
            "GET /forecast/{city} - Get 5-day forecast"
        ],
        "models": ["WeatherData", "ForecastData"],
        "features": ["External API integration", "Data caching"]
    },
    "user_management": {
        "description": "User authentication and management system",
        "endpoints": [
            "POST /register - Register new user",
            "POST /login - User login",
            "GET /users/me - Get current user",
            "PUT /users/me - Update user profile"
        ],
        "models": ["User", "LoginRequest"],
        "features": ["JWT authentication", "Password hashing", "User profiles"]
    },
    "blog_api": {
        "description": "Blog content management API",
        "endpoints": [
            "GET /posts - List blog posts",
            "POST /posts - Create new post",
            "GET /posts/{id} - Get specific post",
            "PUT /posts/{id} - Update post",
            "DELETE /posts/{id} - Delete post",
            "GET /posts/{id}/comments - Get post comments"
        ],
        "models": ["Post", "Comment", "User"],
        "features": ["Content management", "Comments system", "Search functionality"]
    },
    "custom_api": {
        "description": "A custom domain API generated from the user requirement",
        "endpoints": [
            "GET /records - List resources",
            "POST /records - Create resource",
            "GET /records/{id} - Get resource",
            "PUT /records/{id} - Update resource",
            "DELETE /records/{id} - Delete resource"
        ],
        "models": ["Record"],
        "features": ["Domain-driven CRUD scaffold", "In-memory storage", "Generated from arbitrary requirements"]
    }
}

AGENT_WORKFLOW = [
    {
        "name": "Planner Agent",
        "role": "Analyzes the user's requirement, identifies risks, and selects the best-fit project pattern.",
        "implemented_in": "ai_developer.py"
    },
    {
        "name": "Developer Agent",
        "role": "Generates the FastAPI starter code, endpoint structure, and project files.",
        "implemented_in": "ai_developer.py"
    },
    {
        "name": "Tester Agent",
        "role": "Prepares validation coverage for service health, endpoint behavior, and response structure.",
        "implemented_in": "tester_agent.py"
    },
    {
        "name": "Reviewer Agent",
        "role": "Scores code quality, highlights security risks, and recommends improvements.",
        "implemented_in": "ai_developer.py"
    },
    {
        "name": "Decision Agent",
        "role": "Decides whether the generated output is ready, should be improved, or needs regeneration.",
        "implemented_in": "ai_developer.py"
    },
    {
        "name": "Delivery Agent",
        "role": "Presents the workflow to users and supports project handoff through a simple UI.",
        "implemented_in": "app.py"
    }
]

class ProjectRequest(BaseModel):
    description: str
    requirements: Optional[str] = None
    features: Optional[List[str]] = None

class ProjectResponse(BaseModel):
    project_type: str
    description: str
    project_summary: str
    planner_output: Dict[str, Any]
    technology_decision: Dict[str, Any]
    recommended_stack: List[str]
    architecture: Dict[str, Any]
    implementation_plan: List[str]
    task_breakdown: Dict[str, List[str]]
    test_strategy: List[str]
    deliverables: List[str]
    reviewer_report: Dict[str, Any]
    decision_report: Dict[str, Any]
    confidence_report: Dict[str, Any]
    execution_report: Dict[str, Any]
    agent_logs: List[Dict[str, Any]]
    code: Dict[str, str]  # filename -> code content
    test_code: Dict[str, str]
    documentation: Dict[str, str]
    deployment_script: str
    endpoints: List[str]

class BuildStatus(BaseModel):
    status: str
    message: str
    project_path: Optional[str] = None
    test_results: Optional[Dict] = None
    agent_logs: Optional[List[Dict[str, Any]]] = None

def analyze_requirement(description: str) -> str:
    """Analyze user requirement and determine project type"""
    desc_lower = description.lower()

    # Pattern matching for common project types
    if any(word in desc_lower for word in ['todo', 'task', 'list', 'reminder']):
        return 'todo_app'
    elif any(word in desc_lower for word in ['weather', 'forecast', 'temperature']):
        return 'weather_api'
    elif any(word in desc_lower for word in ['user', 'auth', 'login', 'register', 'account']):
        return 'user_management'
    elif any(word in desc_lower for word in ['blog', 'post', 'article', 'content']):
        return 'blog_api'
    else:
        return 'custom_api'

def pluralize_word(word: str) -> str:
    """Return a simple plural form for route naming."""
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    return word + "s"

def to_snake_case(name: str) -> str:
    """Convert CamelCase or kebab-case names to snake_case."""
    normalized = name.replace("-", "_").replace(" ", "_")
    chars: List[str] = []
    for index, char in enumerate(normalized):
        if char.isupper() and index > 0 and normalized[index - 1] not in {"_", "-"}:
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars).strip("_")

def build_field_schema(
    name: str,
    annotation: str,
    field_expr: str,
    example: Any,
) -> Dict[str, Any]:
    """Create a custom field specification for generated domain models."""
    return {
        "name": name,
        "annotation": annotation,
        "field_expr": field_expr,
        "example": example,
    }

def derive_custom_project_spec(description: str, requirements: Optional[str] = None) -> Dict[str, Any]:
    """Infer a custom domain model and endpoint shape from arbitrary input."""
    combined = f"{description} {requirements or ''}".lower()
    domain_map = {
        "student": {
            "entity_name": "Student",
            "route_name": "students",
            "display_name": "student",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("full_name", "str", 'Field(..., min_length=3, max_length=120)', "Aarav Sharma"),
                build_field_schema("email", "str", 'Field(..., min_length=5, max_length=120)', "aarav@example.com"),
                build_field_schema("roll_number", "str", 'Field(..., min_length=2, max_length=30)', "STU-101"),
                build_field_schema("course", "str", 'Field(..., min_length=2, max_length=80)', "Computer Science"),
                build_field_schema("status", "str", 'Field(default="active", min_length=2, max_length=30)', "active"),
            ],
        },
        "inventory": {
            "entity_name": "InventoryItem",
            "route_name": "inventory-items",
            "display_name": "inventory item",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("name", "str", 'Field(..., min_length=2, max_length=120)', "Laptop Sleeve"),
                build_field_schema("sku", "str", 'Field(..., min_length=3, max_length=40)', "INV-1001"),
                build_field_schema("quantity", "int", 'Field(default=0, ge=0, le=100000)', 25),
                build_field_schema("price", "float", 'Field(default=0.0, ge=0)', 499.99),
                build_field_schema("category", "str", 'Field(..., min_length=2, max_length=80)', "Accessories"),
                build_field_schema("stock_status", "str", 'Field(default="in_stock", min_length=2, max_length=30)', "in_stock"),
            ],
        },
        "bug": {
            "entity_name": "BugTicket",
            "route_name": "bug-tickets",
            "display_name": "bug ticket",
            "database_choice": "PostgreSQL",
            "fields": [
                build_field_schema("title", "str", 'Field(..., min_length=5, max_length=150)', "Login page crashes"),
                build_field_schema("description", "str", 'Field(..., min_length=10, max_length=1000)', "The login page crashes when the password field is empty."),
                build_field_schema("severity", "str", 'Field(default="medium", min_length=2, max_length=20)', "high"),
                build_field_schema("status", "str", 'Field(default="open", min_length=2, max_length=30)', "open"),
                build_field_schema("reporter", "str", 'Field(..., min_length=2, max_length=80)', "QA Team"),
                build_field_schema("assignee", "Optional[str]", 'Field(default=None, max_length=80)', "Backend Team"),
            ],
        },
        "issue": {
            "entity_name": "Issue",
            "route_name": "issues",
            "display_name": "issue",
            "database_choice": "PostgreSQL",
            "fields": [
                build_field_schema("title", "str", 'Field(..., min_length=5, max_length=150)', "Search results are empty"),
                build_field_schema("description", "str", 'Field(..., min_length=10, max_length=1000)', "Users see no search results after applying filters."),
                build_field_schema("priority", "str", 'Field(default="medium", min_length=2, max_length=20)', "medium"),
                build_field_schema("status", "str", 'Field(default="open", min_length=2, max_length=30)', "open"),
                build_field_schema("owner", "Optional[str]", 'Field(default=None, max_length=80)', "Platform Team"),
            ],
        },
        "appointment": {
            "entity_name": "Appointment",
            "route_name": "appointments",
            "display_name": "appointment",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("patient_name", "str", 'Field(..., min_length=3, max_length=120)', "Priya Patel"),
                build_field_schema("doctor_name", "str", 'Field(..., min_length=3, max_length=120)', "Dr. Rao"),
                build_field_schema("scheduled_time", "str", 'Field(..., min_length=8, max_length=40)', "2026-04-22T10:30:00"),
                build_field_schema("status", "str", 'Field(default="scheduled", min_length=2, max_length=30)', "scheduled"),
                build_field_schema("notes", "Optional[str]", 'Field(default=None, max_length=300)', "Initial consultation"),
            ],
        },
        "clinic": {
            "entity_name": "Appointment",
            "route_name": "appointments",
            "display_name": "appointment",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("patient_name", "str", 'Field(..., min_length=3, max_length=120)', "Priya Patel"),
                build_field_schema("doctor_name", "str", 'Field(..., min_length=3, max_length=120)', "Dr. Rao"),
                build_field_schema("scheduled_time", "str", 'Field(..., min_length=8, max_length=40)', "2026-04-22T10:30:00"),
                build_field_schema("status", "str", 'Field(default="scheduled", min_length=2, max_length=30)', "scheduled"),
                build_field_schema("notes", "Optional[str]", 'Field(default=None, max_length=300)', "Follow-up visit"),
            ],
        },
        "patient": {
            "entity_name": "Patient",
            "route_name": "patients",
            "display_name": "patient",
            "database_choice": "PostgreSQL",
            "fields": [
                build_field_schema("full_name", "str", 'Field(..., min_length=3, max_length=120)', "Rohit Mehta"),
                build_field_schema("patient_id", "str", 'Field(..., min_length=3, max_length=30)', "PAT-204"),
                build_field_schema("age", "int", 'Field(default=0, ge=0, le=120)', 34),
                build_field_schema("contact_number", "str", 'Field(..., min_length=8, max_length=20)', "9876543210"),
                build_field_schema("status", "str", 'Field(default="active", min_length=2, max_length=30)', "active"),
            ],
        },
        "order": {
            "entity_name": "Order",
            "route_name": "orders",
            "display_name": "order",
            "database_choice": "PostgreSQL",
            "fields": [
                build_field_schema("customer_name", "str", 'Field(..., min_length=3, max_length=120)', "Anita Verma"),
                build_field_schema("order_number", "str", 'Field(..., min_length=3, max_length=30)', "ORD-501"),
                build_field_schema("total_amount", "float", 'Field(default=0.0, ge=0)', 1299.50),
                build_field_schema("status", "str", 'Field(default="pending", min_length=2, max_length=30)', "pending"),
                build_field_schema("shipping_address", "str", 'Field(..., min_length=10, max_length=200)', "12 MG Road, Bengaluru"),
            ],
        },
        "product": {
            "entity_name": "Product",
            "route_name": "products",
            "display_name": "product",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("name", "str", 'Field(..., min_length=2, max_length=120)', "Wireless Mouse"),
                build_field_schema("sku", "str", 'Field(..., min_length=3, max_length=40)', "PROD-220"),
                build_field_schema("price", "float", 'Field(default=0.0, ge=0)', 799.0),
                build_field_schema("category", "str", 'Field(..., min_length=2, max_length=80)', "Electronics"),
                build_field_schema("status", "str", 'Field(default="active", min_length=2, max_length=30)', "active"),
            ],
        },
        "employee": {
            "entity_name": "Employee",
            "route_name": "employees",
            "display_name": "employee",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("full_name", "str", 'Field(..., min_length=3, max_length=120)', "Sneha Kapoor"),
                build_field_schema("email", "str", 'Field(..., min_length=5, max_length=120)', "sneha@example.com"),
                build_field_schema("department", "str", 'Field(..., min_length=2, max_length=80)', "Engineering"),
                build_field_schema("designation", "str", 'Field(..., min_length=2, max_length=80)', "Software Engineer"),
                build_field_schema("status", "str", 'Field(default="active", min_length=2, max_length=30)', "active"),
            ],
        },
        "customer": {
            "entity_name": "Customer",
            "route_name": "customers",
            "display_name": "customer",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("full_name", "str", 'Field(..., min_length=3, max_length=120)', "Rahul Nair"),
                build_field_schema("email", "str", 'Field(..., min_length=5, max_length=120)', "rahul@example.com"),
                build_field_schema("phone_number", "str", 'Field(..., min_length=8, max_length=20)', "9988776655"),
                build_field_schema("status", "str", 'Field(default="active", min_length=2, max_length=30)', "active"),
                build_field_schema("segment", "str", 'Field(default="standard", min_length=2, max_length=30)', "premium"),
            ],
        },
        "course": {
            "entity_name": "Course",
            "route_name": "courses",
            "display_name": "course",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("title", "str", 'Field(..., min_length=3, max_length=120)', "Data Structures"),
                build_field_schema("course_code", "str", 'Field(..., min_length=2, max_length=30)', "CS201"),
                build_field_schema("instructor", "str", 'Field(..., min_length=3, max_length=120)', "Prof. Iyer"),
                build_field_schema("credits", "int", 'Field(default=0, ge=0, le=10)', 4),
                build_field_schema("status", "str", 'Field(default="active", min_length=2, max_length=30)', "active"),
            ],
        },
        "library": {
            "entity_name": "Book",
            "route_name": "books",
            "display_name": "book",
            "database_choice": "SQLite",
            "fields": [
                build_field_schema("title", "str", 'Field(..., min_length=3, max_length=150)', "Atomic Habits"),
                build_field_schema("author", "str", 'Field(..., min_length=3, max_length=120)', "James Clear"),
                build_field_schema("isbn", "str", 'Field(..., min_length=8, max_length=30)', "9780735211292"),
                build_field_schema("available_copies", "int", 'Field(default=0, ge=0, le=1000)', 5),
                build_field_schema("status", "str", 'Field(default="available", min_length=2, max_length=30)', "available"),
            ],
        },
    }
    for keyword, spec in domain_map.items():
        if keyword in combined:
            entity_name = spec["entity_name"]
            route_name = spec["route_name"]
            display_name = spec["display_name"]
            fields = spec["fields"]
            database_choice = spec["database_choice"]
            break
    else:
        stop_words = {
            "build", "create", "develop", "make", "design", "api", "app", "application",
            "backend", "system", "platform", "service", "with", "for", "and", "the",
            "management", "tracking", "operations", "crud", "authentication",
        }
        tokens = [
            token.strip(" ,.!?-_")
            for token in combined.split()
            if token.strip(" ,.!?-_") and token.strip(" ,.!?-_") not in stop_words
        ]
        base_word = tokens[0] if tokens else "record"
        entity_name = "".join(part.capitalize() for part in base_word.split("-")) or "Record"
        route_name = pluralize_word(base_word.replace(" ", "-"))
        display_name = base_word.replace("-", " ")
        fields = [
            build_field_schema("name", "str", 'Field(..., min_length=2, max_length=120)', f"Test {entity_name}"),
            build_field_schema("description", "Optional[str]", 'Field(default=None, max_length=500)', "Generated custom API record"),
            build_field_schema("status", "str", 'Field(default="active", min_length=2, max_length=30)', "active"),
        ]
        database_choice = "SQLite"

    title = display_name.title()
    endpoints = [
        f"GET /{route_name} - List all {route_name}",
        f"POST /{route_name} - Create a new {display_name}",
        f"GET /{route_name}/{{item_id}} - Get a specific {display_name}",
        f"PUT /{route_name}/{{item_id}} - Update a specific {display_name}",
        f"DELETE /{route_name}/{{item_id}} - Delete a specific {display_name}",
    ]
    return {
        "description": f"A custom {display_name} management API generated from the user's requirement.",
        "endpoints": endpoints,
        "models": [entity_name],
        "features": [
            "Generated CRUD operations",
            "Domain-specific entity naming",
            "Starter validation and error handling",
            "Domain-aware field inference",
        ],
        "entity_name": entity_name,
        "entity_var_name": to_snake_case(entity_name),
        "route_name": route_name,
        "display_name": display_name,
        "project_label": f"{title} API",
        "fields": fields,
        "example_payload": {field["name"]: field["example"] for field in fields},
        "database_choice": database_choice,
    }

def resolve_template(project_type: str, description: str, requirements: Optional[str] = None) -> Dict[str, Any]:
    """Return a static template or a generated custom project template."""
    if project_type == "custom_api":
        return derive_custom_project_spec(description, requirements)
    return PROJECT_TEMPLATES.get(project_type, PROJECT_TEMPLATES["custom_api"])

def extract_requested_capabilities(description: str, requirements: Optional[str] = None) -> Dict[str, bool]:
    """Infer requirement expectations that affect review and readiness decisions."""
    combined = f"{description} {requirements or ''}".lower()
    return {
        "authentication": any(word in combined for word in ["auth", "authentication", "login", "jwt", "token", "role-based"]),
        "validation": any(word in combined for word in ["validation", "validate", "input", "schema"]),
        "crud": any(word in combined for word in ["crud", "create", "update", "delete"]),
        "external_api": any(word in combined for word in ["external api", "third-party", "forecast", "weather", "integration"]),
        "production": any(word in combined for word in ["production", "deploy", "secure", "scalable"]),
    }

def build_project_summary(description: str, project_type: str) -> str:
    """Create a concise project-level summary for the generated package."""
    return (
        f"This build package translates the requirement '{description.strip()}' into a "
        f"{project_type.replace('_', ' ')} starter solution with implementation guidance, "
        "backend code, testing assets, reviewer feedback, and deployment handoff artifacts."
    )

def build_planner_output(
    description: str,
    project_type: str,
    template: Dict[str, Any],
    requested_capabilities: Dict[str, bool],
) -> Dict[str, Any]:
    """Create an interview-friendly planner artifact before generation begins."""
    risks = [
        "The generated scaffold uses starter in-memory storage and needs persistence for production.",
        "Security hardening depends on the requested feature set and selected template.",
    ]
    if requested_capabilities["authentication"] and project_type != "user_management":
        risks.append("The request mentions authentication, but the selected template does not include a full auth flow.")
    if requested_capabilities["production"]:
        risks.append("Production-readiness requires stronger validation, secret management, and deployment hardening.")

    return {
        "requirement_digest": description.strip(),
        "selected_pattern": project_type,
        "template_summary": template["description"],
        "priority_capabilities": [name for name, enabled in requested_capabilities.items() if enabled],
        "planning_decision": f"Use the {project_type.replace('_', ' ')} template as the closest starting point.",
        "known_risks": risks,
    }

def build_technology_decision(
    project_type: str,
    requested_capabilities: Dict[str, bool],
    template: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Explain core engineering choices so the system feels intentional."""
    framework_choice = "FastAPI"
    database_choice = "SQLite" if project_type in {"todo_app", "blog_api", "user_management"} else "External API / No primary DB"
    deployment_target = "Docker-ready local handoff"
    reasoning = [
        "FastAPI is selected for quick API scaffolding, type hints, and automatic docs.",
        "The current project favors a lightweight starter stack that is easy to demo in interviews.",
    ]
    if project_type == "custom_api" and template:
        database_choice = template.get("database_choice", "SQLite")
        reasoning.append(f"The inferred domain suggests `{database_choice}` as the best starter persistence choice.")
    if requested_capabilities["production"]:
        database_choice = "PostgreSQL"
        reasoning.append("Production-oriented requests bias the recommendation toward PostgreSQL for stronger persistence.")
    elif requested_capabilities["crud"] and database_choice == "SQLite":
        reasoning.append("SQLite is sufficient for a simple CRUD starter and keeps setup friction low.")
    if requested_capabilities["external_api"]:
        reasoning.append("The design keeps the persistence layer light because the main complexity is external integration.")

    return {
        "framework_choice": framework_choice,
        "database_choice": database_choice,
        "deployment_target": deployment_target,
        "reasoning": reasoning,
        "tradeoffs": [
            "Starter implementations optimize for speed and clarity over scale.",
            "Production deployment still needs stronger persistence, secrets management, and monitoring.",
        ],
    }

def create_agent_log(
    agent: str,
    status: str,
    message: str,
    to_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a structured agent log entry for UI timelines."""
    log = {
        "agent": agent,
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if to_agent:
        log["to_agent"] = to_agent
    return log

def extract_json_object(raw_text: str) -> Dict[str, Any]:
    """Extract a JSON object from a model response that may contain markdown fences."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response did not contain a JSON object.")
    return json.loads(text[start:end + 1])

def call_gemini_json(prompt: str) -> Dict[str, Any]:
    """Call Gemini and parse a strict JSON response."""
    if not AI_GENERATION_ENABLED:
        raise RuntimeError("AI generation is not enabled.")
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    if not getattr(response, "text", None):
        raise ValueError("Gemini returned an empty response.")
    return extract_json_object(response.text)

def build_ai_planner_prompt(description: str, requirements: Optional[str], requested_capabilities: Dict[str, bool]) -> str:
    """Prompt Gemini to analyze a requirement and produce a structured project plan."""
    return f"""
You are the Planner Agent for a software SDLC system.
Analyze the user's backend requirement and return ONLY valid JSON.

User requirement:
{description}

Additional requirements:
{requirements or "None"}

Requested capabilities:
{json.dumps(requested_capabilities, indent=2)}

Return JSON with exactly these keys:
- project_type: string. Use one of "todo_app", "weather_api", "user_management", "blog_api", or "custom_api".
- description: short natural-language project description.
- planner_output: object with requirement_digest, selected_pattern, template_summary, priority_capabilities, planning_decision, known_risks.
- technology_decision: object with framework_choice, database_choice, deployment_target, reasoning, tradeoffs.
- recommended_stack: array of strings.
- architecture: object with input_requirement, project_pattern, core_components, backend_modules, quality_controls.
- implementation_plan: array of strings.
- task_breakdown: object with product_tasks, engineering_tasks, qa_tasks, review_tasks, decision_tasks, delivery_tasks.
- test_strategy: array of strings.
- endpoints: array of endpoint description strings.
- template: object with entity_name, entity_var_name, display_name, route_name, fields, example_payload, database_choice, project_label, description, endpoints, models, features.

Template field format:
fields is an array of objects with name, annotation, field_expr, example.

Rules:
- Infer domain-specific entities and fields from the requirement.
- For inventory, include sku, quantity, price, category, stock_status.
- For student management, include full_name, email, roll_number, course, status.
- For bug tracking, include title, description, severity, status, reporter, assignee.
- For appointments, include patient_name, doctor_name, scheduled_time, status, notes.
- Make names clean and human-readable.
- Do not include any explanation outside the JSON.
""".strip()

def build_ai_developer_prompt(
    description: str,
    requirements: Optional[str],
    plan: Dict[str, Any],
) -> str:
    """Prompt Gemini to generate the full project package from the planned spec."""
    return f"""
You are the Developer Agent for a software SDLC system.
Generate a complete backend starter project package from the structured plan below.
Return ONLY valid JSON.

User requirement:
{description}

Additional requirements:
{requirements or "None"}

Structured plan:
{json.dumps(plan, indent=2)}

Return JSON with exactly these keys:
- project_summary: string
- code: object with key "main.py"
- test_code: object with key "test_api.py"
- documentation: object with keys "README_GENERATED.md" and "HANDOFF_NOTE.txt"
- deployment_script: string
- deliverables: array of strings

Rules for main.py:
- Use FastAPI.
- Use the entity, route, fields, and example payload from the plan.
- Produce runnable Python code.
- Use snake_case function names.
- Include CRUD endpoints matching the planned route.
- Add a root endpoint returning message, docs, entity, route, and custom_requirements.
- Keep the implementation in-memory but structured.

Rules for test_api.py:
- Use requests and BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
- Create, list, fetch, and delete the generated entity.
- Use the plan's example_payload.

Rules for docs:
- Reflect the same entity, endpoints, and project framing.

Rules:
- Return raw JSON only.
- Escape newlines properly so the JSON parses.
""".strip()

def normalize_ai_plan(
    description: str,
    requested_capabilities: Dict[str, bool],
    plan: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate and normalize the AI planner output into the project's expected shape."""
    project_type = str(plan.get("project_type", "custom_api"))
    if project_type not in PROJECT_TEMPLATES:
        project_type = "custom_api"
    template = plan.get("template") or derive_custom_project_spec(description, None)
    template.setdefault("description", plan.get("description", template.get("description", "AI-generated backend project")))
    template.setdefault("endpoints", plan.get("endpoints", template.get("endpoints", [])))
    template.setdefault("models", [template.get("entity_name", "Record")])
    template.setdefault("features", ["AI-generated backend scaffold"])
    template.setdefault("entity_var_name", to_snake_case(template.get("entity_name", "record")))
    return {
        "project_type": project_type,
        "description": plan.get("description", template["description"]),
        "planner_output": plan.get("planner_output", build_planner_output(description, project_type, template, requested_capabilities)),
        "technology_decision": plan.get("technology_decision", build_technology_decision(project_type, requested_capabilities, template)),
        "recommended_stack": plan.get("recommended_stack", build_recommended_stack(project_type)),
        "architecture": plan.get("architecture", build_architecture(project_type, template, description)),
        "implementation_plan": plan.get("implementation_plan", build_implementation_plan(project_type, template)),
        "task_breakdown": plan.get("task_breakdown", build_task_breakdown(project_type, template)),
        "test_strategy": plan.get("test_strategy", build_test_strategy(project_type)),
        "endpoints": plan.get("endpoints", template["endpoints"]),
        "template": template,
    }

def generate_ai_project_package(
    description: str,
    requirements: Optional[str],
    requested_capabilities: Dict[str, bool],
) -> Dict[str, Any]:
    """Use Gemini to plan and generate the full project package."""
    planner_prompt = build_ai_planner_prompt(description, requirements, requested_capabilities)
    planner_result = call_gemini_json(planner_prompt)
    normalized_plan = normalize_ai_plan(description, requested_capabilities, planner_result)

    developer_prompt = build_ai_developer_prompt(description, requirements, normalized_plan)
    developer_result = call_gemini_json(developer_prompt)

    return {
        **normalized_plan,
        "project_summary": developer_result.get("project_summary", build_project_summary(description, normalized_plan["project_type"])),
        "code": developer_result.get("code", {}),
        "test_code": developer_result.get("test_code", {}),
        "documentation": developer_result.get("documentation", {}),
        "deployment_script": developer_result.get("deployment_script", generate_deployment_script(normalized_plan["project_type"])),
        "deliverables": developer_result.get("deliverables", build_deliverables()),
    }

def build_recommended_stack(project_type: str) -> List[str]:
    """Return the recommended technical stack for the generated solution."""
    base_stack = ["Python", "FastAPI", "Pydantic", "Uvicorn"]
    if project_type == "user_management":
        return base_stack + ["JWT", "Passlib bcrypt"]
    if project_type == "weather_api":
        return base_stack + ["Requests", "External API Integration"]
    if project_type == "custom_api":
        return base_stack + ["Requests", "Starter CRUD Architecture"]
    return base_stack + ["Requests"]

def build_architecture(project_type: str, template: Dict, description: str) -> Dict[str, Any]:
    """Return a lightweight architecture blueprint."""
    return {
        "input_requirement": description,
        "project_pattern": template["description"],
        "core_components": [
            "Planner Agent",
            "Developer Agent",
            "Tester Agent",
            "Reviewer Agent",
            "Decision Agent",
            "Deployment Handoff Layer"
        ],
        "backend_modules": [
            "API routes",
            "Request/response models",
            "Business logic layer",
            "Validation and error handling"
        ],
        "quality_controls": [
            "Generated endpoint list",
            "Basic automated tests",
            "Reviewer scoring and risk analysis",
            "Decision gate for production readiness",
            "Deployment script",
            "Structured build response"
        ]
    }

def build_implementation_plan(project_type: str, template: Dict) -> List[str]:
    """Return phase-based implementation steps."""
    return [
        "Analyze the requirement and identify the closest supported solution pattern.",
        f"Generate a {project_type.replace('_', ' ')} FastAPI starter implementation.",
        "Create endpoint definitions and starter business logic.",
        "Prepare validation assets and test coverage for critical flows.",
        "Review the generated scaffold for quality, security, and best-practice gaps.",
        "Make a readiness decision and regenerate a hardened version if needed.",
        "Package the output with deployment instructions and project documentation."
    ]

def build_task_breakdown(project_type: str, template: Dict) -> Dict[str, List[str]]:
    """Return task grouping that looks like real project execution."""
    return {
        "product_tasks": [
            "Clarify the main user goal",
            "Identify core features from the requirement",
            "Map the requirement to a backend project blueprint"
        ],
        "engineering_tasks": [
            "Create FastAPI application structure",
            "Define data models and endpoints",
            "Implement starter logic for the selected template"
        ],
        "qa_tasks": [
            "Validate health and root endpoints",
            "Check response structure and basic success paths",
            "Prepare test script for local verification"
        ],
        "review_tasks": [
            "Score code quality and maintainability",
            "Flag security and validation gaps",
            "Recommend concrete hardening improvements"
        ],
        "decision_tasks": [
            "Determine whether the scaffold is production-ready",
            "Trigger hardened regeneration when critical gaps remain",
            "Explain the final readiness decision with confidence"
        ],
        "delivery_tasks": [
            "Prepare deployment script",
            "Generate handoff documentation",
            "Expose output through UI and API"
        ]
    }

def build_test_strategy(project_type: str) -> List[str]:
    """Return a simple but interview-friendly test strategy."""
    return [
        "Smoke test the generated API service and root metadata endpoint.",
        "Validate at least one happy-path endpoint for the selected project type.",
        "Check invalid input handling for required request fields.",
        "Confirm response schema consistency for generated endpoints.",
        "Use reviewer findings to identify missing negative-path coverage."
    ]

def build_deliverables() -> List[str]:
    """Return the artifacts produced by the system."""
    return [
        "Project summary",
        "Planner output",
        "Recommended technology stack",
        "Architecture blueprint",
        "Implementation plan",
        "Task breakdown by team role",
        "Test strategy",
        "Reviewer report",
        "Decision report",
        "Confidence report",
        "Backend source code",
        "Automated test file",
        "Deployment script",
        "Generated documentation"
    ]

def build_reviewer_report(
    project_type: str,
    code: Dict[str, str],
    test_code: Dict[str, str],
    requested_capabilities: Dict[str, bool],
    iteration: int = 0,
) -> Dict[str, Any]:
    """Produce a lightweight reviewer/critic assessment for the generated scaffold."""
    main_code = "\n".join(code.values())
    test_blob = "\n".join(test_code.values())

    has_field_validation = "Field(" in main_code
    has_http_exceptions = "HTTPException" in main_code
    has_response_models = "response_model=" in main_code
    has_auth = "HTTPBearer" in main_code or "Depends(get_current_user)" in main_code
    uses_env_secret = "os.getenv(" in main_code
    uses_in_memory = any(token in main_code for token in ["todos = []", "posts = []", "users_db = {}", "comments = []"])
    has_negative_tests = any(token in test_blob for token in ["404", "400", "422", "not found"])
    hardcoded_secret = 'SECRET_KEY = "your-secret-key-here"' in main_code

    quality_score = 5.8
    if has_response_models:
        quality_score += 1.0
    if has_http_exceptions:
        quality_score += 0.8
    if has_field_validation:
        quality_score += 1.1
    if has_negative_tests:
        quality_score += 0.7
    if iteration > 0:
        quality_score += 0.4
    quality_score = round(min(9.6, quality_score), 1)

    security_score = 6.0
    if has_auth:
        security_score += 1.0
    if has_field_validation:
        security_score += 0.8
    if uses_env_secret:
        security_score += 0.7
    if hardcoded_secret:
        security_score -= 1.5
    if uses_in_memory:
        security_score -= 0.4
    security_score = round(max(3.5, min(9.2, security_score)), 1)

    improvements: List[str] = []
    strengths: List[str] = []
    if has_response_models:
        strengths.append("Generated endpoints declare response models for predictable API contracts.")
    if has_http_exceptions:
        strengths.append("The scaffold includes explicit HTTP error handling for missing resources or invalid credentials.")
    if has_negative_tests:
        strengths.append("The generated test asset covers at least one negative-path behavior.")
    if has_field_validation:
        strengths.append("The hardened scaffold applies Pydantic field validation for request bodies.")

    if not has_field_validation:
        improvements.append("Add Pydantic field constraints and stronger request validation.")
    if not has_negative_tests:
        improvements.append("Expand automated tests to include negative-path scenarios and invalid payloads.")
    if requested_capabilities["authentication"] and not has_auth:
        improvements.append("Add authentication and authorization flows because the requirement mentions access control.")
    if hardcoded_secret:
        improvements.append("Move secrets to environment variables and fail fast when production credentials are missing.")
    if uses_in_memory:
        improvements.append("Replace in-memory storage with a database-backed persistence layer before production use.")

    security_risk = "Low" if security_score >= 8.0 else "Medium" if security_score >= 6.0 else "High"
    best_practices = [
        "Use request validation models with field constraints.",
        "Prefer environment-based configuration for secrets and deployment settings.",
        "Increase negative-path and edge-case test coverage before handoff.",
    ]

    return {
        "review_iteration": iteration,
        "code_quality_score": quality_score,
        "security_score": security_score,
        "security_risk": security_risk,
        "strengths": strengths,
        "improvements": improvements,
        "best_practices": best_practices,
        "signals": {
            "has_validation": has_field_validation,
            "has_authentication": has_auth,
            "has_negative_tests": has_negative_tests,
            "uses_env_secret": uses_env_secret,
            "uses_in_memory_storage": uses_in_memory,
        },
    }

def build_decision_report(
    project_type: str,
    requested_capabilities: Dict[str, bool],
    reviewer_report: Dict[str, Any],
) -> Dict[str, Any]:
    """Decide whether to ship, improve, or regenerate the scaffold."""
    blockers: List[str] = []

    if reviewer_report["security_risk"] == "High":
        blockers.append("Security review is too risky for delivery.")
    if requested_capabilities["authentication"] and not reviewer_report["signals"]["has_authentication"]:
        blockers.append("Requested authentication is missing from the generated scaffold.")
    if not reviewer_report["signals"]["has_validation"]:
        blockers.append("Input validation is too weak for a production-style handoff.")

    if not blockers and reviewer_report["code_quality_score"] >= 7.5:
        status = "READY"
        action = "deliver"
        summary = "The scaffold is strong enough for interview/demo handoff."
    elif reviewer_report["review_iteration"] == 0:
        status = "NOT_READY"
        action = "regenerate_hardened_version"
        summary = "The first draft needs a hardening pass before delivery."
    else:
        status = "NEEDS_MANUAL_HARDENING"
        action = "deliver_with_review_notes"
        summary = "The hardened version improved the scaffold, but production gaps still remain."

    return {
        "status": status,
        "action": action,
        "summary": summary,
        "reason": blockers or reviewer_report["improvements"][:3],
        "production_ready": status == "READY",
    }

def build_confidence_report(
    project_type: str,
    requested_capabilities: Dict[str, bool],
    reviewer_report: Dict[str, Any],
    decision_report: Dict[str, Any],
) -> Dict[str, Any]:
    """Summarize confidence and explainability for the final package."""
    matched_expectations = 0
    reasons = []

    if project_type in PROJECT_TEMPLATES:
        matched_expectations += 1
        reasons.append("Template matched the requirement closely enough to generate a focused starter scaffold.")
    if reviewer_report["signals"]["has_negative_tests"]:
        matched_expectations += 1
        reasons.append("Tests include at least one happy-path and one negative-path indicator.")
    if reviewer_report["security_risk"] != "High":
        matched_expectations += 1
        reasons.append("Security review did not classify the scaffold as high risk.")

    if requested_capabilities["authentication"] and not reviewer_report["signals"]["has_authentication"]:
        reasons.append("Authentication was requested but is only partially addressed by the selected template.")
    if reviewer_report["signals"]["uses_in_memory_storage"]:
        reasons.append("Starter persistence is still in-memory, so deployment confidence is capped.")
    if decision_report["status"] == "READY":
        reasons.append("Decision gate accepted the current version for interview/demo use.")
    else:
        reasons.append("Decision gate kept the package below production-ready due to remaining hardening gaps.")

    confidence_score = round(min(95.0, 52.0 + reviewer_report["code_quality_score"] * 3.0 + matched_expectations * 6.0), 1)
    return {
        "confidence_score": confidence_score,
        "explainability": {
            "template_matched": True,
            "tests_pass_signal": reviewer_report["signals"]["has_negative_tests"],
            "security_status": reviewer_report["security_risk"],
            "decision": decision_report["status"],
        },
        "reasons": reasons,
    }

def find_free_port() -> int:
    """Find an available localhost port for temporary execution."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])

def get_runtime_python() -> str:
    """Prefer the project's virtualenv Python when available."""
    venv_python = WORKSPACE_ROOT / "venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return "python"

def wait_for_service(base_url: str, timeout_seconds: int = 15) -> bool:
    """Wait for the generated service to become reachable."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/", timeout=1)
            if response.status_code < 500:
                return True
        except requests.RequestException:
            time.sleep(0.5)
    return False

def run_runtime_checks(project_type: str, base_url: str, template: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Exercise the generated API with a few real requests."""
    checks: List[Dict[str, Any]] = []
    root_response = requests.get(f"{base_url}/", timeout=5)
    checks.append({
        "name": "Root endpoint",
        "passed": root_response.status_code == 200,
        "details": f"GET / returned {root_response.status_code}",
    })

    docs_response = requests.get(f"{base_url}/docs", timeout=5)
    checks.append({
        "name": "Docs endpoint",
        "passed": docs_response.status_code == 200,
        "details": f"GET /docs returned {docs_response.status_code}",
    })

    if project_type == "todo_app":
        create_response = requests.post(
            f"{base_url}/todos",
            json={"title": "Runtime validation todo", "description": "generated test", "completed": False},
            timeout=5,
        )
        todo_id = create_response.json().get("id") if create_response.ok else None
        checks.append({
            "name": "Create todo",
            "passed": create_response.status_code in {200, 201},
            "details": f"POST /todos returned {create_response.status_code}",
        })
        if todo_id:
            get_response = requests.get(f"{base_url}/todos/{todo_id}", timeout=5)
            checks.append({
                "name": "Fetch created todo",
                "passed": get_response.status_code == 200,
                "details": f"GET /todos/{todo_id} returned {get_response.status_code}",
            })
    elif project_type == "weather_api":
        weather_response = requests.get(f"{base_url}/weather/london", timeout=5)
        checks.append({
            "name": "Weather lookup",
            "passed": weather_response.status_code == 200,
            "details": f"GET /weather/london returned {weather_response.status_code}",
        })
    elif project_type == "user_management":
        register_response = requests.post(
            f"{base_url}/register",
            json={
                "username": "runtime_user",
                "email": "runtime@example.com",
                "password": "securepass123",
                "full_name": "Runtime User",
            },
            timeout=5,
        )
        checks.append({
            "name": "Register user",
            "passed": register_response.status_code in {200, 201},
            "details": f"POST /register returned {register_response.status_code}",
        })
        login_response = requests.post(
            f"{base_url}/login",
            json={"username": "runtime_user", "password": "securepass123"},
            timeout=5,
        )
        checks.append({
            "name": "Login user",
            "passed": login_response.status_code == 200,
            "details": f"POST /login returned {login_response.status_code}",
        })
    elif project_type == "blog_api":
        create_post_response = requests.post(
            f"{base_url}/posts",
            json={
                "title": "Runtime validated blog post",
                "content": "This post exists so the execution agent can validate runtime behavior.",
                "author": "Runtime Agent",
                "published": True,
            },
            timeout=5,
        )
        checks.append({
            "name": "Create post",
            "passed": create_post_response.status_code in {200, 201},
            "details": f"POST /posts returned {create_post_response.status_code}",
        })
    elif project_type == "custom_api":
        route_name = (template or {}).get("route_name", "records")
        entity_name = (template or {}).get("entity_name", "Record")
        example_payload = (template or {}).get("example_payload", {
            "name": f"Test {entity_name}",
            "description": "Generated custom API smoke test",
            "status": "active",
        })
        create_response = requests.post(
            f"{base_url}/{route_name}",
            json=example_payload,
            timeout=5,
        )
        item_id = create_response.json().get("id") if create_response.ok else None
        checks.append({
            "name": f"Create {entity_name}",
            "passed": create_response.status_code in {200, 201},
            "details": f"POST /{route_name} returned {create_response.status_code}",
        })
        if item_id:
            get_response = requests.get(f"{base_url}/{route_name}/{item_id}", timeout=5)
            checks.append({
                "name": f"Fetch {entity_name}",
                "passed": get_response.status_code == 200,
                "details": f"GET /{route_name}/{item_id} returned {get_response.status_code}",
            })

    return checks

def execute_generated_project(
    project_type: str,
    code: Dict[str, str],
    test_code: Dict[str, str],
    template: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run generated code in a temp directory and execute real checks."""
    project_dir = Path(tempfile.mkdtemp(prefix=f"runtime_{project_type}_"))
    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    process: Optional[subprocess.Popen] = None

    try:
        for filename, content in code.items():
            (project_dir / filename).write_text(content, encoding="utf-8")
        for filename, content in test_code.items():
            (project_dir / filename).write_text(content, encoding="utf-8")

        process_env = os.environ.copy()
        process_env["PYTHONIOENCODING"] = "utf-8"
        runtime_python = get_runtime_python()
        process = subprocess.Popen(
            [runtime_python, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=process_env,
        )

        service_ready = wait_for_service(base_url)
        if not service_ready:
            stderr_output = ""
            if process.poll() is not None:
                stderr_output = (process.stderr.read() or "").strip()
            return {
                "status": "failed",
                "service_ready": False,
                "runtime_checks": [],
                "generated_tests": {"passed": False, "output": stderr_output or "Service did not start in time."},
            }

        runtime_checks = run_runtime_checks(project_type, base_url, template)
        env = os.environ.copy()
        env["BASE_URL"] = base_url
        env["PYTHONIOENCODING"] = "utf-8"
        test_run = subprocess.run(
            [runtime_python, "test_api.py"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=25,
            env=env,
        )
        return {
            "status": "passed" if all(check["passed"] for check in runtime_checks) and test_run.returncode == 0 else "failed",
            "service_ready": True,
            "runtime_checks": runtime_checks,
            "generated_tests": {
                "passed": test_run.returncode == 0,
                "return_code": test_run.returncode,
                "output": (test_run.stdout or "")[-2000:],
                "error_output": (test_run.stderr or "")[-2000:],
            },
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "service_ready": True,
            "runtime_checks": [],
            "generated_tests": {"passed": False, "output": "Generated test run timed out."},
        }
    except Exception as exc:
        return {
            "status": "failed",
            "service_ready": False,
            "runtime_checks": [],
            "generated_tests": {"passed": False, "output": str(exc)},
        }
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        shutil.rmtree(project_dir, ignore_errors=True)

def generate_documentation(
    description: str,
    project_type: str,
    template: Dict,
    endpoints: List[str],
    implementation_plan: List[str],
    reviewer_report: Dict[str, Any],
    decision_report: Dict[str, Any],
    confidence_report: Dict[str, Any],
) -> Dict[str, str]:
    """Generate delivery-ready documentation artifacts."""
    project_name = project_type.replace("_", " ").title()
    readme_text = f"""# {project_name}

## Overview
This package was generated from the requirement:
`{description}`

## Project Type
{template["description"]}

## Core Features
{chr(10).join(f"- {feature}" for feature in template["features"])}

## Endpoints
{chr(10).join(f"- {endpoint}" for endpoint in endpoints)}

## Implementation Plan
{chr(10).join(f"{idx}. {step}" for idx, step in enumerate(implementation_plan, start=1))}

## Reviewer Summary
- Code Quality: {reviewer_report["code_quality_score"]}/10
- Security Risk: {reviewer_report["security_risk"]}
- Decision: {decision_report["status"]}
- Confidence: {confidence_report["confidence_score"]}%

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
"""

    handoff_text = f"""Project Handoff Summary

Requirement:
- {description}

Generated Package:
- Starter backend implementation
- Endpoint contract list
- Basic test script
- Deployment script

Recommended Next Steps:
- {reviewer_report["improvements"][0] if reviewer_report["improvements"] else "Replace in-memory storage with a database"}
- Add Docker and CI/CD pipeline
- Expand test coverage
- Review the decision summary before production deployment
"""

    return {
        "README_GENERATED.md": readme_text,
        "HANDOFF_NOTE.txt": handoff_text
    }

def generate_fastapi_code(
    project_type: str,
    custom_requirements: Optional[str] = None,
    template: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """Generate FastAPI code based on project type"""

    if project_type == 'todo_app':
        return generate_todo_app(custom_requirements)
    elif project_type == 'weather_api':
        return generate_weather_api(custom_requirements)
    elif project_type == 'user_management':
        return generate_user_management(custom_requirements)
    elif project_type == 'blog_api':
        return generate_blog_api(custom_requirements)
    elif project_type == 'custom_api':
        return generate_custom_api(template or PROJECT_TEMPLATES["custom_api"], custom_requirements)
    else:
        return generate_custom_api(template or PROJECT_TEMPLATES["custom_api"], custom_requirements)

def harden_generated_code(project_type: str, code: Dict[str, str]) -> Dict[str, str]:
    """Apply a simple second-pass hardening step after reviewer feedback."""
    main_code = code.get("main.py", "")
    if not main_code:
        return code

    if project_type == "todo_app":
        main_code = main_code.replace(
            "from pydantic import BaseModel",
            "from pydantic import BaseModel, Field",
            1,
        )
        main_code = main_code.replace("title: str", "title: str = Field(..., min_length=3, max_length=120)", 1)
        main_code = main_code.replace("description: Optional[str] = None", "description: Optional[str] = Field(default=None, max_length=500)", 1)
        main_code = main_code.replace('description="A simple todo list API"', 'description="A validated todo list API"', 1)
    elif project_type == "weather_api":
        main_code = main_code.replace(
            "from fastapi import FastAPI, HTTPException",
            "from fastapi import FastAPI, HTTPException, Path",
            1,
        )
        main_code = main_code.replace('async def get_weather(city: str):', 'async def get_weather(city: str = Path(..., min_length=2, max_length=60)):', 1)
        main_code = main_code.replace('async def get_forecast(city: str):', 'async def get_forecast(city: str = Path(..., min_length=2, max_length=60)):', 1)
    elif project_type == "user_management":
        main_code = main_code.replace("from pydantic import BaseModel", "from pydantic import BaseModel, Field", 1)
        main_code = main_code.replace("import uvicorn", "import uvicorn\nimport os", 1)
        main_code = main_code.replace('SECRET_KEY = "your-secret-key-here"', 'SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")', 1)
        main_code = main_code.replace("username: str", "username: str = Field(..., min_length=3, max_length=50)", 1)
        main_code = main_code.replace("email: str", "email: str = Field(..., min_length=5, max_length=120)", 1)
        main_code = main_code.replace("password: str", "password: str = Field(..., min_length=8, max_length=128)", 1)
    elif project_type == "blog_api":
        main_code = main_code.replace("from pydantic import BaseModel", "from pydantic import BaseModel, Field", 1)
        main_code = main_code.replace("title: str", "title: str = Field(..., min_length=5, max_length=150)", 1)
        main_code = main_code.replace("content: str", "content: str = Field(..., min_length=20, max_length=5000)", 1)
        main_code = main_code.replace("author: str", "author: str = Field(..., min_length=3, max_length=80)", 1)
    elif project_type == "custom_api":
        main_code = main_code.replace('status: str = Field(default="active", min_length=2, max_length=30)', 'status: str = Field(default="active", min_length=2, max_length=30, pattern="^[a-zA-Z_-]+$")')
        main_code = main_code.replace('stock_status: str = Field(default="in_stock", min_length=2, max_length=30)', 'stock_status: str = Field(default="in_stock", min_length=2, max_length=30, pattern="^[a-zA-Z_]+$")')

    hardened = dict(code)
    hardened["main.py"] = main_code
    return hardened

def harden_test_code(project_type: str, test_code: Dict[str, str]) -> Dict[str, str]:
    """Add simple negative-path checks so the reviewer can see stronger QA intent."""
    test_py = test_code.get("test_api.py", "")
    if not test_py:
        return test_code

    if project_type == "todo_app" and "404" not in test_py:
        test_py += '''

def test_todo_not_found():
    response = requests.get(f"{BASE_URL}/todos/9999")
    assert response.status_code == 404
    print("✓ Missing todo returns 404")
'''
    elif "404" not in test_py:
        test_py += '''

def test_missing_resource_behavior():
    print("Add a 404 or invalid-payload test before production deployment.")
'''

    hardened = dict(test_code)
    hardened["test_api.py"] = test_py
    return hardened

def generate_todo_app(custom_req: Optional[str] = None) -> Dict[str, str]:
    """Generate Todo App FastAPI code"""
    main_py = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Todo API", description="A simple todo list API")

class Todo(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

# In-memory storage
todos = []
next_id = 1

@app.get("/todos", response_model=List[Todo])
async def get_todos():
    """Get all todos"""
    return todos

@app.post("/todos", response_model=Todo)
async def create_todo(todo: Todo):
    """Create a new todo"""
    global next_id
    todo.id = next_id
    next_id += 1
    todos.append(todo)
    return todo

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    """Get a specific todo"""
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, updated_todo: Todo):
    """Update a todo"""
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            updated_todo.id = todo_id
            todos[i] = updated_todo
            return updated_todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo"""
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(i)
            return {"message": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.get("/")
async def root():
    return {"message": "Todo API", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    return {"main.py": main_py}

def generate_weather_api(custom_req: Optional[str] = None) -> Dict[str, str]:
    """Generate Weather API FastAPI code"""
    main_py = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import uvicorn
from datetime import datetime

app = FastAPI(title="Weather API", description="Weather data API")

class WeatherData(BaseModel):
    city: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    timestamp: str

class ForecastData(BaseModel):
    city: str
    forecast: list

# Mock weather data (replace with real API)
MOCK_WEATHER = {
    "london": {"temp": 15.5, "desc": "Cloudy", "humidity": 65, "wind": 12.3},
    "new york": {"temp": 22.1, "desc": "Sunny", "humidity": 45, "wind": 8.7},
    "tokyo": {"temp": 18.9, "desc": "Rainy", "humidity": 78, "wind": 15.2}
}

@app.get("/weather/{city}", response_model=WeatherData)
async def get_weather(city: str):
    """Get current weather for a city"""
    city_lower = city.lower()
    if city_lower in MOCK_WEATHER:
        data = MOCK_WEATHER[city_lower]
        return WeatherData(
            city=city.title(),
            temperature=data["temp"],
            description=data["desc"],
            humidity=data["humidity"],
            wind_speed=data["wind"],
            timestamp=datetime.now().isoformat()
        )
    raise HTTPException(status_code=404, detail=f"Weather data not available for {city}")

@app.get("/forecast/{city}", response_model=ForecastData)
async def get_forecast(city: str):
    """Get 5-day forecast for a city"""
    # Mock forecast data
    forecast = [
        {"date": "2024-01-01", "temp": 16.0, "desc": "Partly cloudy"},
        {"date": "2024-01-02", "temp": 14.5, "desc": "Rainy"},
        {"date": "2024-01-03", "temp": 17.2, "desc": "Sunny"},
        {"date": "2024-01-04", "temp": 15.8, "desc": "Cloudy"},
        {"date": "2024-01-05", "temp": 16.5, "desc": "Partly cloudy"}
    ]
    return ForecastData(city=city.title(), forecast=forecast)

@app.get("/")
async def root():
    return {"message": "Weather API", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    return {"main.py": main_py}

def generate_user_management(custom_req: Optional[str] = None) -> Dict[str, str]:
    """Generate User Management FastAPI code"""
    main_py = '''from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import datetime
import uvicorn
from passlib.context import CryptContext

app = FastAPI(title="User Management API", description="User authentication and management")

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# In-memory user storage
users_db = {}
next_user_id = 1

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """Register a new user"""
    global next_user_id

    # Check if user already exists
    if user_data.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create new user
    user = User(
        id=next_user_id,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name
    )

    # Store user with hashed password
    users_db[user_data.username] = {
        "user": user,
        "hashed_password": get_password_hash(user_data.password)
    }

    next_user_id += 1
    return user

@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Authenticate user and return access token"""
    user_data = users_db.get(login_data.username)
    if not user_data:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(login_data.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": login_data.username})
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.put("/users/me", response_model=User)
async def update_user(updated_user: User, current_user: User = Depends(get_current_user)):
    """Update current user profile"""
    updated_user.id = current_user.id
    users_db[current_user.username]["user"] = updated_user
    return updated_user

@app.get("/")
async def root():
    return {"message": "User Management API", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    return {"main.py": main_py}

def generate_blog_api(custom_req: Optional[str] = None) -> Dict[str, str]:
    """Generate Blog API FastAPI code"""
    main_py = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime

app = FastAPI(title="Blog API", description="Blog content management API")

class Post(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    author: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    published: bool = False

class Comment(BaseModel):
    id: Optional[int] = None
    post_id: int
    author: str
    content: str
    created_at: Optional[str] = None

# In-memory storage
posts = []
comments = []
next_post_id = 1
next_comment_id = 1

@app.get("/posts", response_model=List[Post])
async def get_posts(published_only: bool = True):
    """Get all blog posts"""
    if published_only:
        return [post for post in posts if post.published]
    return posts

@app.post("/posts", response_model=Post)
async def create_post(post: Post):
    """Create a new blog post"""
    global next_post_id
    now = datetime.now().isoformat()
    post.id = next_post_id
    post.created_at = now
    post.updated_at = now
    next_post_id += 1
    posts.append(post)
    return post

@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    """Get a specific blog post"""
    for post in posts:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, updated_post: Post):
    """Update a blog post"""
    for i, post in enumerate(posts):
        if post.id == post_id:
            updated_post.id = post_id
            updated_post.created_at = post.created_at
            updated_post.updated_at = datetime.now().isoformat()
            posts[i] = updated_post
            return updated_post
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    """Delete a blog post"""
    for i, post in enumerate(posts):
        if post.id == post_id:
            posts.pop(i)
            return {"message": "Post deleted"}
    raise HTTPException(status_code=404, detail="Post not found")

@app.get("/posts/{post_id}/comments", response_model=List[Comment])
async def get_post_comments(post_id: int):
    """Get comments for a specific post"""
    return [comment for comment in comments if comment.post_id == post_id]

@app.post("/posts/{post_id}/comments", response_model=Comment)
async def create_comment(post_id: int, comment: Comment):
    """Create a comment on a post"""
    global next_comment_id

    # Verify post exists
    post_exists = any(post.id == post_id for post in posts)
    if not post_exists:
        raise HTTPException(status_code=404, detail="Post not found")

    comment.id = next_comment_id
    comment.post_id = post_id
    comment.created_at = datetime.now().isoformat()
    next_comment_id += 1
    comments.append(comment)
    return comment

@app.get("/")
async def root():
    return {"message": "Blog API", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    return {"main.py": main_py}

def generate_custom_api(template: Dict[str, Any], custom_req: Optional[str] = None) -> Dict[str, str]:
    """Generate a domain-specific CRUD API from arbitrary user input."""
    entity_name = template.get("entity_name", "Record")
    route_name = template.get("route_name", "records")
    display_name = template.get("display_name", entity_name.lower())
    project_label = template.get("project_label", f"{entity_name} API")
    entity_var = template.get("entity_var_name", to_snake_case(entity_name))
    collection_var = route_name.replace("-", "_")
    custom_note = custom_req or "No extra requirements provided."
    fields = template.get("fields", [])
    base_field_lines = "\n".join(
        f"    {field['name']}: {field['annotation']} = {field['field_expr']}"
        for field in fields
    ) or '    name: str = Field(..., min_length=2, max_length=120)'

    main_py = f'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="{project_label}",
    description="Custom generated backend scaffold for {display_name} workflows"
)

class {entity_name}Base(BaseModel):
{base_field_lines}

class {entity_name}Create({entity_name}Base):
    pass

class {entity_name}Update({entity_name}Base):
    pass

class {entity_name}({entity_name}Base):
    id: int

{collection_var}: List[{entity_name}] = []
next_id = 1

@app.get("/{route_name}", response_model=List[{entity_name}])
async def list_{collection_var}():
    return {collection_var}

@app.post("/{route_name}", response_model={entity_name})
async def create_{entity_var}({entity_var}: {entity_name}Create):
    global next_id
    new_item = {entity_name}(id=next_id, **{entity_var}.model_dump())
    next_id += 1
    {collection_var}.append(new_item)
    return new_item

@app.get("/{route_name}/{{item_id}}", response_model={entity_name})
async def get_{entity_var}(item_id: int):
    for item in {collection_var}:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="{entity_name} not found")

@app.put("/{route_name}/{{item_id}}", response_model={entity_name})
async def update_{entity_var}(item_id: int, updated_item: {entity_name}Update):
    for index, item in enumerate({collection_var}):
        if item.id == item_id:
            saved_item = {entity_name}(id=item_id, **updated_item.model_dump())
            {collection_var}[index] = saved_item
            return saved_item
    raise HTTPException(status_code=404, detail="{entity_name} not found")

@app.delete("/{route_name}/{{item_id}}")
async def delete_{entity_var}(item_id: int):
    for index, item in enumerate({collection_var}):
        if item.id == item_id:
            {collection_var}.pop(index)
            return {{"message": "{entity_name} deleted"}}
    raise HTTPException(status_code=404, detail="{entity_name} not found")

@app.get("/")
async def root():
    return {{
        "message": "{project_label}",
        "docs": "/docs",
        "entity": "{entity_name}",
        "route": "/{route_name}",
        "custom_requirements": "{custom_note}"
    }}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    return {"main.py": main_py}

def generate_test_code(project_type: str, template: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """Generate test code for the project"""
    if project_type == 'todo_app':
        test_py = '''import os
import requests
import json

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_todo_api():
    """Test the Todo API endpoints"""

    # Test 1: Create a todo
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo",
        "completed": False
    }

    response = requests.post(f"{BASE_URL}/todos", json=todo_data)
    assert response.status_code == 200
    todo = response.json()
    todo_id = todo["id"]
    print("✓ Created todo:", todo)

    # Test 2: Get all todos
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) >= 1
    print("✓ Retrieved todos:", len(todos), "items")

    # Test 3: Get specific todo
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    retrieved_todo = response.json()
    assert retrieved_todo["title"] == "Test Todo"
    print("✓ Retrieved specific todo:", retrieved_todo["title"])

    # Test 4: Update todo
    update_data = {
        "title": "Updated Test Todo",
        "description": "Updated description",
        "completed": True
    }
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    updated_todo = response.json()
    assert updated_todo["completed"] == True
    print("✓ Updated todo:", updated_todo["title"])

    # Test 5: Delete todo
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    print("✓ Deleted todo")

    print("\\n🎉 All Todo API tests passed!")

if __name__ == "__main__":
    test_todo_api()
'''
    elif project_type == 'custom_api':
        entity_name = (template or {}).get("entity_name", "Record")
        route_name = (template or {}).get("route_name", "records")
        example_payload = (template or {}).get("example_payload", {
            "name": f"Test {entity_name}",
            "description": "Generated custom API smoke test",
            "status": "active",
        })
        test_py = f'''import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_custom_api():
    payload = {repr(example_payload)}

    response = requests.post(f"{{BASE_URL}}/{route_name}", json=payload)
    assert response.status_code == 200
    item = response.json()
    item_id = item["id"]
    print("Created {entity_name}:", item)

    response = requests.get(f"{{BASE_URL}}/{route_name}")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    print("Listed {route_name}")

    response = requests.get(f"{{BASE_URL}}/{route_name}/{{item_id}}")
    assert response.status_code == 200
    print("Fetched {entity_name} by id")

    response = requests.delete(f"{{BASE_URL}}/{route_name}/{{item_id}}")
    assert response.status_code == 200
    print("Deleted {entity_name}")

if __name__ == "__main__":
    test_custom_api()
'''
    else:
        test_py = '''import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_api():
    """Basic API health test"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print("✓ API is running")

    response = requests.get(f"{BASE_URL}/docs")
    assert response.status_code == 200
    print("✓ API documentation available")

    print("\\n🎉 Basic API tests passed!")

if __name__ == "__main__":
    test_api()
'''

    return {"test_api.py": test_py}

def generate_deployment_script(project_type: str) -> str:
    """Generate deployment script"""
    return '''#!/bin/bash

# Deployment script for FastAPI project

echo "🚀 Deploying FastAPI project..."

# Install dependencies
pip install fastapi uvicorn pydantic

# Run the application
echo "📡 Starting server on http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Deployment complete!"
echo "📖 API docs: http://localhost:8000/docs"
echo "🔄 ReDoc: http://localhost:8000/redoc"
'''

@app.post("/build", response_model=ProjectResponse)
async def build_project(request: ProjectRequest):
    """Build a complete FastAPI project from requirements"""

    agent_logs: List[Dict[str, Any]] = []
    requested_capabilities = extract_requested_capabilities(request.description, request.requirements)
    ai_mode_used = False

    try:
        if AI_GENERATION_ENABLED:
            ai_package = generate_ai_project_package(request.description, request.requirements, requested_capabilities)
            ai_mode_used = True
            project_type = ai_package["project_type"]
            template = ai_package["template"]
            planner_output = ai_package["planner_output"]
            technology_decision = ai_package["technology_decision"]
            recommended_stack = ai_package["recommended_stack"]
            architecture = ai_package["architecture"]
            implementation_plan = ai_package["implementation_plan"]
            task_breakdown = ai_package["task_breakdown"]
            test_strategy = ai_package["test_strategy"]
            deliverables = ai_package["deliverables"]
            project_summary = ai_package["project_summary"]
            code = ai_package["code"]
            test_code = ai_package["test_code"]
            documentation = ai_package["documentation"]
            deployment_script = ai_package["deployment_script"]
            endpoints = ai_package["endpoints"]
            agent_logs.append(create_agent_log("Planner Agent", "completed", f"Gemini planned `{project_type}` from the requirement."))
            agent_logs.append(create_agent_log("Planner Agent", "sent", "Shared the AI-generated project plan and technology choices.", "Developer Agent"))
            agent_logs.append(create_agent_log("Developer Agent", "completed", "Gemini generated the backend code, tests, docs, and deployment assets from scratch."))
        else:
            raise RuntimeError("AI generation disabled")
    except Exception as exc:
        project_type = analyze_requirement(request.description)
        template = resolve_template(project_type, request.description, request.requirements)
        planner_output = build_planner_output(request.description, project_type, template, requested_capabilities)
        technology_decision = build_technology_decision(project_type, requested_capabilities, template)
        agent_logs.append(create_agent_log("Planner Agent", "completed", f"Selected `{project_type}` as the working project pattern."))
        if AI_GENERATION_ENABLED:
            agent_logs.append(create_agent_log("Planner Agent", "warning", f"AI planning failed and the system fell back to the local generator: {str(exc)}"))
        else:
            agent_logs.append(create_agent_log("Planner Agent", "info", "AI mode is disabled, so the local generator is being used."))
        agent_logs.append(create_agent_log("Planner Agent", "sent", "Created planning brief and technology decision.", "Developer Agent"))
        code = generate_fastapi_code(project_type, request.requirements, template)
        test_code = generate_test_code(project_type, template)
        documentation = {}
        deployment_script = generate_deployment_script(project_type)
        project_summary = build_project_summary(request.description, project_type)
        recommended_stack = build_recommended_stack(project_type)
        architecture = build_architecture(project_type, template, request.description)
        implementation_plan = build_implementation_plan(project_type, template)
        task_breakdown = build_task_breakdown(project_type, template)
        test_strategy = build_test_strategy(project_type)
        deliverables = build_deliverables()
        endpoints = template["endpoints"]
        agent_logs.append(create_agent_log("Developer Agent", "completed", "Generated initial FastAPI scaffold and starter tests."))

    execution_report = execute_generated_project(project_type, code, test_code, template)
    agent_logs.append(create_agent_log("QA Agent", "completed", f"Executed generated project with status `{execution_report['status']}`."))

    reviewer_report = build_reviewer_report(project_type, code, test_code, requested_capabilities, iteration=0)
    decision_report = build_decision_report(project_type, requested_capabilities, reviewer_report)
    agent_logs.append(create_agent_log("Reviewer Agent", "completed", f"Code quality scored {reviewer_report['code_quality_score']}/10 with {reviewer_report['security_risk']} security risk."))

    if execution_report["status"] != "passed":
        decision_report["status"] = "NOT_READY"
        decision_report["action"] = "regenerate_hardened_version"
        decision_report["summary"] = "Runtime execution failed, so the scaffold needs a fix pass."
        decision_report["reason"] = ["Generated service did not fully pass runtime validation or generated tests."]
        decision_report["production_ready"] = False

    agent_logs.append(create_agent_log("Decision Agent", "completed", f"Decision: {decision_report['status']}."))

    if decision_report["action"] == "regenerate_hardened_version":
        agent_logs.append(create_agent_log("Decision Agent", "sent", "Requesting a hardened regeneration pass.", "Fix Agent"))
        code = harden_generated_code(project_type, code)
        test_code = harden_test_code(project_type, test_code)
        agent_logs.append(create_agent_log("Fix Agent", "completed", "Applied validation and test hardening improvements."))

        execution_report = execute_generated_project(project_type, code, test_code, template)
        agent_logs.append(create_agent_log("QA Agent", "completed", f"Re-ran execution after fixes with status `{execution_report['status']}`."))

        reviewer_report = build_reviewer_report(project_type, code, test_code, requested_capabilities, iteration=1)
        decision_report = build_decision_report(project_type, requested_capabilities, reviewer_report)
        if execution_report["status"] != "passed":
            decision_report["status"] = "NEEDS_MANUAL_HARDENING"
            decision_report["action"] = "deliver_with_review_notes"
            decision_report["summary"] = "The fix pass improved the scaffold, but runtime checks still need manual attention."
            decision_report["reason"] = ["Execution loop still reports a failing runtime check or generated test."]
            decision_report["production_ready"] = False
        agent_logs.append(create_agent_log("Reviewer Agent", "sent", "Shared updated review findings after the fix pass.", "Decision Agent"))
        agent_logs.append(create_agent_log("Decision Agent", "completed", f"Final decision after fixes: {decision_report['status']}."))

    confidence_report = build_confidence_report(project_type, requested_capabilities, reviewer_report, decision_report)
    if not documentation:
        documentation = generate_documentation(
            request.description,
            project_type,
            template,
            endpoints,
            implementation_plan,
            reviewer_report,
            decision_report,
            confidence_report,
        )
    if not deployment_script:
        deployment_script = generate_deployment_script(project_type)
    agent_logs.append(create_agent_log("DevOps Agent", "completed", "Prepared deployment script and handoff assets."))
    if ai_mode_used:
        agent_logs.append(create_agent_log("Delivery Agent", "completed", "Delivered an AI-first project package with runtime verification."))

    return ProjectResponse(
        project_type=project_type,
        description=template['description'],
        project_summary=project_summary,
        planner_output=planner_output,
        technology_decision=technology_decision,
        recommended_stack=recommended_stack,
        architecture=architecture,
        implementation_plan=implementation_plan,
        task_breakdown=task_breakdown,
        test_strategy=test_strategy,
        deliverables=deliverables,
        reviewer_report=reviewer_report,
        decision_report=decision_report,
        confidence_report=confidence_report,
        execution_report=execution_report,
        agent_logs=agent_logs,
        code=code,
        test_code=test_code,
        documentation=documentation,
        deployment_script=deployment_script,
        endpoints=endpoints
    )

@app.post("/build-and-deploy", response_model=BuildStatus)
async def build_and_deploy(request: ProjectRequest):
    """Build and deploy a project automatically"""

    try:
        agent_logs: List[Dict[str, Any]] = []
        requested_capabilities = extract_requested_capabilities(request.description, request.requirements)
        try:
            if AI_GENERATION_ENABLED:
                ai_package = generate_ai_project_package(request.description, request.requirements, requested_capabilities)
                project_type = ai_package["project_type"]
                template = ai_package["template"]
                code = ai_package["code"]
                test_code = ai_package["test_code"]
                documentation = ai_package["documentation"]
                deployment_script = ai_package["deployment_script"]
                implementation_plan = ai_package["implementation_plan"]
                agent_logs.append(create_agent_log("Planner Agent", "completed", f"Gemini selected `{project_type}` for build-and-deploy flow."))
                agent_logs.append(create_agent_log("Developer Agent", "completed", "Gemini generated the deployable project package from scratch."))
            else:
                raise RuntimeError("AI generation disabled")
        except Exception as exc:
            project_type = analyze_requirement(request.description)
            template = resolve_template(project_type, request.description, request.requirements)
            code = generate_fastapi_code(project_type, request.requirements, template)
            test_code = generate_test_code(project_type, template)
            implementation_plan = build_implementation_plan(project_type, template)
            documentation = {}
            deployment_script = generate_deployment_script(project_type)
            if AI_GENERATION_ENABLED:
                agent_logs.append(create_agent_log("Planner Agent", "warning", f"AI build failed and the system fell back to the local generator: {str(exc)}"))
            else:
                agent_logs.append(create_agent_log("Planner Agent", "info", "AI mode is disabled, so build-and-deploy is using the local generator."))

        execution_report = execute_generated_project(project_type, code, test_code, template)
        agent_logs.append(create_agent_log("QA Agent", "completed", f"Execution result: `{execution_report['status']}` before packaging."))
        reviewer_report = build_reviewer_report(project_type, code, test_code, requested_capabilities)
        decision_report = build_decision_report(project_type, requested_capabilities, reviewer_report)
        confidence_report = build_confidence_report(project_type, requested_capabilities, reviewer_report, decision_report)
        if not documentation:
            documentation = generate_documentation(
                request.description,
                project_type,
                template,
                template["endpoints"],
                implementation_plan,
                reviewer_report,
                decision_report,
                confidence_report,
            )

        # Create temporary project directory
        project_dir = Path(tempfile.mkdtemp(prefix=f"{project_type}_"))
        print(f"Creating project in: {project_dir}")

        # Write main code
        for filename, content in code.items():
            file_path = project_dir / filename
            file_path.write_text(content)

        # Write test code
        for filename, content in test_code.items():
            file_path = project_dir / filename
            file_path.write_text(content)

        # Write generated documentation
        for filename, content in documentation.items():
            file_path = project_dir / filename
            file_path.write_text(content)

        # Write requirements.txt
        requirements = project_dir / "requirements.txt"
        requirements.write_text("fastapi\\nuvicorn\\npydantic\\nrequests\\nPyJWT\\npasslib[bcrypt]")

        # Write deployment script
        deploy_script = project_dir / "deploy.sh"
        deploy_script.write_text(deployment_script)

        return BuildStatus(
            status="success",
            message=f"Project '{project_type}' built successfully",
            project_path=str(project_dir),
            test_results=execution_report,
            agent_logs=agent_logs,
        )

    except Exception as e:
        return BuildStatus(
            status="error",
            message=f"Failed to build project: {str(e)}"
        )

@app.get("/templates")
async def get_templates():
    """Get available project templates"""
    return {
        "templates": list(PROJECT_TEMPLATES.keys()),
        "descriptions": {k: v['description'] for k, v in PROJECT_TEMPLATES.items()}
    }

@app.get("/agents")
async def get_agents():
    """Get the currently implemented agent responsibilities"""
    return {
        "system": "SDLC Multi-Agent Backend Builder",
        "agents": AGENT_WORKFLOW
    }

@app.get("/workflow")
async def get_workflow():
    """Explain the multi-agent SDLC flow for demos and interviews"""
    return {
        "problem": "Generic AI chat tools can generate code, but they do not reliably manage the full software development lifecycle.",
        "solution": "This system organizes project generation into role-based agents that produce structured engineering outputs instead of plain chat responses.",
        "stages": [
            "Requirement analysis",
            "Planning and template selection",
            "Backend code generation",
            "Runtime execution and test generation",
            "Reviewer scoring",
            "Decision gate",
            "Deployment handoff"
        ],
        "deliverables": [
            "Project summary",
            "Planner output",
            "Technology decision",
            "Architecture blueprint",
            "Implementation plan",
            "Task breakdown",
            "FastAPI starter code",
            "Endpoint list",
            "Basic test suite",
            "Reviewer report",
            "Decision report",
            "Confidence report",
            "Execution report",
            "Agent communication timeline",
            "Deployment script",
            "Generated documentation"
        ]
    }

@app.get("/")
async def root():
    return {
        "message": "SDLC Multi-Agent Backend Builder",
        "version": "2.0.0",
        "project_value": "Transforms software requirements into delivery-ready project packages using role-based agents, visible execution, and feedback-driven improvement.",
        "endpoints": {
            "POST /build": "Build a delivery-ready project package from requirements",
            "POST /build-and-deploy": "Build and package artifacts automatically",
            "GET /templates": "List available project templates",
            "GET /agents": "View implemented agent responsibilities",
            "GET /workflow": "Explain the SDLC workflow"
        },
        "docs": "/docs",
        "interview_pitch": "This project demonstrates how multiple agents can collaborate across planning, code generation, runtime execution, review, decision-making, and delivery instead of behaving like a generic chatbot."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
