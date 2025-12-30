"""Pydantic models for the web API."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# LLM Provider Enums
class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROK = "grok"
    DEEPSEEK = "deepseek"


class LLMModel(BaseModel):
    """LLM model configuration."""
    provider: LLMProvider
    model_id: str
    display_name: str
    api_key_env: str


# MCP Connections
class MCPConnectionType(str, Enum):
    HUBSPOT = "hubspot"
    GMAIL = "gmail"
    GOOGLE_DRIVE = "google_drive"
    WEB = "web"
    LINKEDIN = "linkedin"


class MCPConnection(BaseModel):
    """MCP connection configuration."""
    type: MCPConnectionType
    enabled: bool = False
    api_key: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


# Configuration Models
class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4096


class SystemConfig(BaseModel):
    """System-wide configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mcp_connections: Dict[str, MCPConnection] = Field(default_factory=dict)
    max_iterations: int = 10


# Agent Prompts
class AgentPrompt(BaseModel):
    """Agent prompt configuration."""
    agent_name: str
    system_prompt: str
    last_modified: Optional[datetime] = None


# Prospect Models
class ProspectInput(BaseModel):
    """Input model for creating a new prospect."""
    name: str
    company: str
    email: str
    phone: Optional[str] = None
    sector: str = "autre"
    company_size: str = "pme"
    decision_maker: bool = False
    pain_points: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    source: str = "manual"


class ProspectResponse(BaseModel):
    """Response model for prospect operations."""
    success: bool
    session_id: Optional[str] = None
    hubspot_id: Optional[str] = None
    message: str


# Session/Log Models
class AgentLog(BaseModel):
    """Log entry for an agent action."""
    timestamp: datetime
    session_id: str
    agent_name: str
    action: str
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    duration_ms: Optional[float] = None


class SessionSummary(BaseModel):
    """Summary of a sales session."""
    session_id: str
    created_at: datetime
    updated_at: datetime
    lead_type: Optional[str] = None
    lead_score: float = 0
    qualified: bool = False
    converted: bool = False
    escalated: bool = False
    closed: bool = False
    message_count: int = 0
    agents_used: List[str] = Field(default_factory=list)


class SessionDetail(SessionSummary):
    """Detailed session information."""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    lead_info: Dict[str, Any] = Field(default_factory=dict)
    offers_made: List[Dict[str, Any]] = Field(default_factory=list)
    current_offer: Optional[Dict[str, Any]] = None
    objections: List[str] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)


class BlackboardState(BaseModel):
    """Current state of the shared blackboard/memory."""
    sessions: Dict[str, SessionSummary] = Field(default_factory=dict)
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    total_sessions: int = 0
    active_sessions: int = 0
    total_conversions: int = 0
    avg_lead_score: float = 0


# API Responses
class APIResponse(BaseModel):
    """Generic API response."""
    success: bool
    message: str
    data: Optional[Any] = None


class ConfigUpdateRequest(BaseModel):
    """Request to update configuration."""
    llm_provider: Optional[LLMProvider] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    mcp_connections: Optional[Dict[str, MCPConnection]] = None


# Available LLM Models Registry
LLM_MODELS = {
    LLMProvider.OPENAI: [
        {"id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo"},
        {"id": "gpt-4", "name": "GPT-4"},
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
    ],
    LLMProvider.ANTHROPIC: [
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
    ],
    LLMProvider.GROK: [
        {"id": "grok-beta", "name": "Grok Beta"},
        {"id": "grok-2", "name": "Grok 2"},
    ],
    LLMProvider.DEEPSEEK: [
        {"id": "deepseek-chat", "name": "DeepSeek Chat"},
        {"id": "deepseek-coder", "name": "DeepSeek Coder"},
    ],
}
