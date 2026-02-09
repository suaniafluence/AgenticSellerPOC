"""FastAPI web application for monitoring and configuring the sales agent system."""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.models import (
    LLMProvider, LLMConfig, SystemConfig, MCPConnection, MCPConnectionType,
    AgentPrompt, ProspectInput, ProspectResponse, SessionSummary, SessionDetail,
    BlackboardState, APIResponse, ConfigUpdateRequest, LLM_MODELS, AgentLog
)
from config import config, Config
from memory import get_memory_store, set_memory_store, JSONFileStore, InMemoryStore
from orchestrator import SalesOrchestrator, set_agent_log_callback
from state import create_initial_state, add_message


# Global state
_orchestrator: Optional[SalesOrchestrator] = None
_agent_logs: List[Dict[str, Any]] = []
_system_config: Optional[SystemConfig] = None
_prompts_cache: Dict[str, str] = {}


def get_orchestrator() -> SalesOrchestrator:
    """Get or create the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        set_agent_log_callback(add_agent_log)
        _orchestrator = SalesOrchestrator()
    return _orchestrator


def get_system_config() -> SystemConfig:
    """Get or create system configuration."""
    global _system_config
    if _system_config is None:
        # Initialize from environment/config
        provider = LLMProvider.OPENAI
        if "claude" in config.default_llm_model.lower():
            provider = LLMProvider.ANTHROPIC

        _system_config = SystemConfig(
            llm=LLMConfig(
                provider=provider,
                model=config.default_llm_model,
                temperature=config.temperature,
            ),
            max_iterations=config.max_iterations,
            mcp_connections={
                MCPConnectionType.HUBSPOT.value: MCPConnection(
                    type=MCPConnectionType.HUBSPOT,
                    enabled=bool(config.hubspot_api_key),
                    api_key=config.hubspot_api_key[:4] + "..." if config.hubspot_api_key else None,
                ),
                MCPConnectionType.GMAIL.value: MCPConnection(
                    type=MCPConnectionType.GMAIL,
                    enabled=False,
                ),
                MCPConnectionType.GOOGLE_DRIVE.value: MCPConnection(
                    type=MCPConnectionType.GOOGLE_DRIVE,
                    enabled=False,
                ),
                MCPConnectionType.WEB.value: MCPConnection(
                    type=MCPConnectionType.WEB,
                    enabled=True,  # Web access is usually available
                ),
                MCPConnectionType.LINKEDIN.value: MCPConnection(
                    type=MCPConnectionType.LINKEDIN,
                    enabled=False,
                ),
            }
        )
    return _system_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Starting IAfluence Agent Monitor...")

    # Initialize file-based memory store
    data_path = Path(__file__).parent.parent / "data"
    data_path.mkdir(exist_ok=True)
    set_memory_store(JSONFileStore(str(data_path)))

    # Load prompts
    load_agent_prompts()

    print("✅ Agent Monitor ready!")

    yield

    # Shutdown
    print("👋 Shutting down Agent Monitor...")


# Create FastAPI app
app = FastAPI(
    title="IAfluence Agent Monitor",
    description="Interface de monitoring et configuration du système d'agents commerciaux",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
templates_path = Path(__file__).parent / "templates"
static_path = Path(__file__).parent / "static"
templates_path.mkdir(exist_ok=True)
static_path.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ============================================================================
# Helper Functions
# ============================================================================

def load_agent_prompts():
    """Load agent prompts from files."""
    global _prompts_cache
    agents_dir = Path(__file__).parent.parent / "agents"
    prompts_dir = Path(__file__).parent.parent / "data" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    agent_files = {
        "classifier": "classifier.py",
        "seller": "seller.py",
        "negotiator": "negotiator.py",
        "supervisor": "supervisor.py",
        "crm": "crm.py",
    }

    # Default prompts for agents that don't have a get_system_prompt method
    default_prompts = {
        "crm": (
            "Agent CRM IAfluence.\n"
            "Enregistre les conversations, suit les opportunités, "
            "met à jour les informations de contact et crée des tâches de suivi.\n"
            "Synchronise les données avec le CRM (HubSpot) et génère les actions post-conversation."
        ),
    }

    for agent_name, filename in agent_files.items():
        # Check for custom prompt first
        custom_prompt_file = prompts_dir / f"{agent_name}_prompt.txt"
        if custom_prompt_file.exists():
            _prompts_cache[agent_name] = custom_prompt_file.read_text(encoding="utf-8")
        else:
            # Extract from source file
            agent_file = agents_dir / filename
            if agent_file.exists():
                content = agent_file.read_text(encoding="utf-8")
                # Extract system prompt from get_system_prompt method
                if 'def get_system_prompt' in content:
                    start = content.find('return """', content.find('def get_system_prompt'))
                    if start != -1:
                        start += len('return """')
                        end = content.find('"""', start)
                        if end != -1:
                            _prompts_cache[agent_name] = content[start:end].strip()
                            continue

            # Use default prompt if extraction failed
            if agent_name not in _prompts_cache and agent_name in default_prompts:
                _prompts_cache[agent_name] = default_prompts[agent_name]


def save_agent_prompt(agent_name: str, prompt: str):
    """Save a custom agent prompt."""
    prompts_dir = Path(__file__).parent.parent / "data" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = prompts_dir / f"{agent_name}_prompt.txt"
    prompt_file.write_text(prompt)
    _prompts_cache[agent_name] = prompt


def add_agent_log(session_id: str, agent_name: str, action: str,
                  input_state: Dict, output_state: Dict, duration_ms: float = None):
    """Add a log entry for agent activity."""
    global _agent_logs
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "agent_name": agent_name,
        "action": action,
        "input_state": {k: v for k, v in input_state.items() if k != "messages"},
        "output_state": {k: v for k, v in output_state.items() if k != "messages"},
        "duration_ms": duration_ms,
    }
    _agent_logs.append(log_entry)

    # Keep only last 1000 logs
    if len(_agent_logs) > 1000:
        _agent_logs = _agent_logs[-1000:]


# ============================================================================
# Web Interface Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


# ============================================================================
# Monitoring API Routes
# ============================================================================

@app.get("/api/sessions", response_model=List[SessionSummary])
async def get_sessions():
    """Get all sessions."""
    memory = get_memory_store()
    sessions = []

    # Get sessions from memory store
    if hasattr(memory, 'sessions'):
        for session_id, data in memory.sessions.items():
            state = data.get("state", {})
            sessions.append(SessionSummary(
                session_id=session_id,
                created_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
                lead_type=state.get("lead_type"),
                lead_score=state.get("lead_score", 0),
                qualified=state.get("qualified", False),
                converted=state.get("converted", False),
                escalated=state.get("escalated", False),
                closed=state.get("closed", False),
                message_count=len(state.get("messages", [])),
                agents_used=list(set([m.get("metadata", {}).get("agent", "")
                                      for m in state.get("messages", [])
                                      if m.get("metadata", {}).get("agent")])),
            ))

    return sorted(sessions, key=lambda x: x.updated_at, reverse=True)


@app.get("/api/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    """Get detailed session information."""
    memory = get_memory_store()
    state = memory.load_session(session_id)

    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetail(
        session_id=session_id,
        created_at=datetime.now(),  # Would need to track this properly
        updated_at=datetime.now(),
        lead_type=state.get("lead_type"),
        lead_score=state.get("lead_score", 0),
        qualified=state.get("qualified", False),
        converted=state.get("converted", False),
        escalated=state.get("escalated", False),
        closed=state.get("closed", False),
        message_count=len(state.get("messages", [])),
        messages=state.get("messages", []),
        lead_info=state.get("lead_info", {}),
        offers_made=state.get("offers_made", []),
        current_offer=state.get("current_offer"),
        objections=state.get("objections", []),
        key_insights=state.get("key_insights", []),
    )


@app.get("/api/logs")
async def get_logs(
    session_id: Optional[str] = None,
    agent: Optional[str] = None,
    limit: int = 100
):
    """Get agent activity logs."""
    logs = _agent_logs.copy()

    if session_id:
        logs = [l for l in logs if l["session_id"] == session_id]
    if agent:
        logs = [l for l in logs if l["agent_name"] == agent]

    return logs[-limit:]


@app.get("/api/blackboard", response_model=BlackboardState)
async def get_blackboard():
    """Get current blackboard/memory state."""
    memory = get_memory_store()

    sessions_summary = {}
    total_score = 0
    conversions = 0
    active = 0

    if hasattr(memory, 'sessions'):
        for session_id, data in memory.sessions.items():
            state = data.get("state", {})
            score = state.get("lead_score", 0)
            total_score += score

            if state.get("converted"):
                conversions += 1
            if not state.get("closed"):
                active += 1

            sessions_summary[session_id] = SessionSummary(
                session_id=session_id,
                created_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
                lead_type=state.get("lead_type"),
                lead_score=score,
                qualified=state.get("qualified", False),
                converted=state.get("converted", False),
                escalated=state.get("escalated", False),
                closed=state.get("closed", False),
                message_count=len(state.get("messages", [])),
            )

    insights = memory.get_insights() if hasattr(memory, 'get_insights') else []
    total_sessions = len(sessions_summary)

    return BlackboardState(
        sessions=sessions_summary,
        insights=insights,
        total_sessions=total_sessions,
        active_sessions=active,
        total_conversions=conversions,
        avg_lead_score=total_score / total_sessions if total_sessions > 0 else 0,
    )


# ============================================================================
# Prompt Management API Routes
# ============================================================================

@app.get("/api/prompts")
async def get_prompts():
    """Get all agent prompts."""
    return [
        {"agent_name": name, "prompt": prompt, "last_modified": None}
        for name, prompt in _prompts_cache.items()
    ]


@app.get("/api/prompts/{agent_name}")
async def get_prompt(agent_name: str):
    """Get a specific agent's prompt."""
    if agent_name not in _prompts_cache:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "agent_name": agent_name,
        "prompt": _prompts_cache[agent_name],
    }


@app.put("/api/prompts/{agent_name}")
async def update_prompt(agent_name: str, request: Request):
    """Update an agent's prompt."""
    data = await request.json()
    prompt = data.get("prompt", "")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    save_agent_prompt(agent_name, prompt)

    return APIResponse(
        success=True,
        message=f"Prompt for {agent_name} updated successfully",
    )


# ============================================================================
# Configuration API Routes
# ============================================================================

@app.get("/api/config")
async def get_config():
    """Get current system configuration."""
    cfg = get_system_config()
    return {
        "llm": {
            "provider": cfg.llm.provider,
            "model": cfg.llm.model,
            "temperature": cfg.llm.temperature,
        },
        "mcp_connections": {k: v.model_dump() for k, v in cfg.mcp_connections.items()},
        "max_iterations": cfg.max_iterations,
    }


@app.get("/api/config/llm-models")
async def get_llm_models():
    """Get available LLM models."""
    return {provider.value: models for provider, models in LLM_MODELS.items()}


@app.put("/api/config")
async def update_config(request: Request):
    """Update system configuration."""
    global _system_config
    data = await request.json()

    cfg = get_system_config()

    if "llm" in data:
        llm_data = data["llm"]
        if "provider" in llm_data:
            cfg.llm.provider = LLMProvider(llm_data["provider"])
        if "model" in llm_data:
            cfg.llm.model = llm_data["model"]
        if "temperature" in llm_data:
            cfg.llm.temperature = float(llm_data["temperature"])

    if "mcp_connections" in data:
        for conn_type, conn_data in data["mcp_connections"].items():
            if conn_type in cfg.mcp_connections:
                cfg.mcp_connections[conn_type].enabled = conn_data.get("enabled", False)
                if "api_key" in conn_data and conn_data["api_key"]:
                    cfg.mcp_connections[conn_type].api_key = conn_data["api_key"]
                if "config" in conn_data:
                    cfg.mcp_connections[conn_type].config = conn_data["config"]

    _system_config = cfg

    # Save to .env file (optional - for persistence)
    save_config_to_env(cfg)

    return APIResponse(
        success=True,
        message="Configuration updated successfully",
    )


def save_config_to_env(cfg: SystemConfig):
    """Save configuration to .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    env_content = []

    # Read existing .env
    if env_file.exists():
        env_content = env_file.read_text(encoding="utf-8").split("\n")

    # Update or add values
    updates = {
        "DEFAULT_LLM_MODEL": cfg.llm.model,
        "TEMPERATURE": str(cfg.llm.temperature),
        "MAX_ITERATIONS": str(cfg.max_iterations),
    }

    for key, value in updates.items():
        found = False
        for i, line in enumerate(env_content):
            if line.startswith(f"{key}="):
                env_content[i] = f"{key}={value}"
                found = True
                break
        if not found:
            env_content.append(f"{key}={value}")

    env_file.write_text("\n".join(env_content))


# ============================================================================
# Prospect Management API Routes
# ============================================================================

@app.post("/api/prospects", response_model=ProspectResponse)
async def create_prospect(prospect: ProspectInput):
    """Create a new prospect and start the sales process."""
    import uuid

    session_id = str(uuid.uuid4())

    # Create initial message from prospect info
    initial_message = f"""Bonjour, je suis {prospect.name} de {prospect.company}.

Notre entreprise compte environ {_size_to_employees(prospect.company_size)} employés dans le secteur {prospect.sector}.
{"Je suis décideur sur ce type de projet." if prospect.decision_maker else ""}

{f"Nos problématiques principales : {', '.join(prospect.pain_points)}" if prospect.pain_points else ""}
{f"Nos centres d'intérêt : {', '.join(prospect.interests)}" if prospect.interests else ""}
{f"Notes additionnelles : {prospect.notes}" if prospect.notes else ""}
"""

    try:
        orchestrator = get_orchestrator()

        # Prepare lead_info from prospect input so contact data is preserved
        prospect_lead_info = {
            "name": prospect.name,
            "company": prospect.company,
            "email": prospect.email,
            "phone": prospect.phone,
            "sector": prospect.sector,
            "company_size": prospect.company_size,
            "decision_maker": prospect.decision_maker,
            "pain_points": prospect.pain_points or [],
            "interests": prospect.interests or [],
        }

        # Run the initial conversation with lead info
        state = orchestrator.run_conversation(initial_message, session_id, lead_info=prospect_lead_info)

        # Ensure session is saved in the memory store used by the web app
        memory = get_memory_store()
        memory.save_session(session_id, state)

        # Log the action
        add_agent_log(
            session_id=session_id,
            agent_name="system",
            action="prospect_created",
            input_state={"prospect": prospect.model_dump()},
            output_state={"lead_score": state.get("lead_score", 0)},
        )

        # Sync to HubSpot if enabled
        hubspot_id = None
        cfg = get_system_config()
        if cfg.mcp_connections.get(MCPConnectionType.HUBSPOT.value, MCPConnection(type=MCPConnectionType.HUBSPOT)).enabled:
            hubspot_id = await sync_to_hubspot(prospect, session_id)

        return ProspectResponse(
            success=True,
            session_id=session_id,
            hubspot_id=hubspot_id,
            message=f"Prospect créé avec succès. Score: {state.get('lead_score', 0)}",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _size_to_employees(size: str) -> str:
    """Convert company size to employee count."""
    sizes = {
        "startup": "1-19",
        "pme": "20-249",
        "eti": "250-4999",
        "grand_compte": "5000+",
    }
    return sizes.get(size, "inconnu")


async def sync_to_hubspot(prospect: ProspectInput, session_id: str) -> Optional[str]:
    """Sync prospect to HubSpot CRM."""
    # This would use the HubSpot API
    # For now, return a mock ID
    cfg = get_system_config()
    hubspot_conn = cfg.mcp_connections.get(MCPConnectionType.HUBSPOT.value)

    if not hubspot_conn or not hubspot_conn.enabled:
        return None

    # TODO: Implement actual HubSpot API call
    # import httpx
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         "https://api.hubapi.com/crm/v3/objects/contacts",
    #         headers={"Authorization": f"Bearer {hubspot_conn.api_key}"},
    #         json={
    #             "properties": {
    #                 "email": prospect.email,
    #                 "firstname": prospect.name.split()[0] if prospect.name else "",
    #                 "lastname": " ".join(prospect.name.split()[1:]) if prospect.name else "",
    #                 "company": prospect.company,
    #                 "phone": prospect.phone,
    #             }
    #         }
    #     )
    #     return response.json().get("id")

    return f"hubspot_mock_{session_id[:8]}"


@app.post("/api/prospects/{session_id}/message")
async def send_message(session_id: str, request: Request):
    """Send a message to an existing prospect conversation."""
    data = await request.json()
    message = data.get("message", "")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        orchestrator = get_orchestrator()
        state = orchestrator.continue_conversation(session_id, message)

        # Save updated session
        memory = get_memory_store()
        memory.save_session(session_id, state)

        # Get the last assistant message
        messages = state.get("messages", [])
        last_response = ""
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                last_response = msg.get("content", "")
                break

        return {
            "success": True,
            "response": last_response,
            "state": {
                "lead_score": state.get("lead_score", 0),
                "qualified": state.get("qualified", False),
                "converted": state.get("converted", False),
                "current_agent": state.get("current_agent"),
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
