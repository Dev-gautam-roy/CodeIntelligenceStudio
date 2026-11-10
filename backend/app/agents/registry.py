from typing import Dict, Type, List
from app.agents.base import BaseAgent
from app.agents.specialized import (
    RepositoryAgent,
    ArchitectureAgent,
    RagAgent,
    SecurityAgent,
    TestingAgent,
    DebuggingAgent,
    DocumentationAgent,
    ContributionAgent,
    DeploymentAgent,
)


class AgentRegistry:
    _agents: Dict[str, Type[BaseAgent]] = {
        "RepositoryAgent": RepositoryAgent,
        "ArchitectureAgent": ArchitectureAgent,
        "RagAgent": RagAgent,
        "SecurityAgent": SecurityAgent,
        "TestingAgent": TestingAgent,
        "DebuggingAgent": DebuggingAgent,
        "DocumentationAgent": DocumentationAgent,
        "ContributionAgent": ContributionAgent,
        "DeploymentAgent": DeploymentAgent,
    }

    @classmethod
    def get_agent(cls, name: str) -> BaseAgent:
        agent_cls = cls._agents.get(name)
        if not agent_cls:
            raise ValueError(f"Agent '{name}' is not registered in AgentRegistry.")
        return agent_cls()

    @classmethod
    def list_agents(cls) -> List[Dict[str, any]]:
        return [
            {
                "name": agent_cls.name,
                "role": agent_cls.role,
                "description": agent_cls.description,
                "allowed_tools": agent_cls.allowed_tools,
                "token_budget": agent_cls.default_token_budget,
                "timeout_seconds": agent_cls.timeout_seconds,
            }
            for agent_cls in cls._agents.values()
        ]
