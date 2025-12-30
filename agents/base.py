"""Base agent class for all sales agents."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from config import config


class BaseAgent(ABC):
    """Base class for all sales agents."""

    def __init__(
        self,
        name: str,
        llm: Optional[BaseChatModel] = None,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ):
        """
        Initialize the base agent.

        Args:
            name: Name of the agent
            llm: Language model to use (if None, creates default)
            temperature: Temperature for LLM responses
            model: Model name to use
        """
        self.name = name
        self.temperature = temperature
        self.model = model or config.default_llm_model

        if llm:
            self.llm = llm
        else:
            # Create default LLM based on config
            if "gpt" in self.model.lower():
                self.llm = ChatOpenAI(
                    model=self.model,
                    temperature=self.temperature,
                    api_key=config.openai_api_key,
                )
            elif "claude" in self.model.lower():
                self.llm = ChatAnthropic(
                    model=self.model,
                    temperature=self.temperature,
                    api_key=config.anthropic_api_key,
                )
            else:
                # Default to OpenAI
                self.llm = ChatOpenAI(
                    model="gpt-4-turbo-preview",
                    temperature=self.temperature,
                    api_key=config.openai_api_key,
                )

    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current state and return updated state.

        Args:
            state: Current state of the sales process

        Returns:
            Updated state
        """
        pass

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return f"You are {self.name}, a specialized AI agent in a sales system."

    def format_conversation_history(self, messages: list) -> str:
        """Format conversation history for the LLM."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        return "\n".join(formatted)
