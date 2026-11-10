import pytest
from app.agents.registry import AgentRegistry
from app.agents.base import AgentContext


@pytest.mark.asyncio
async def test_agent_registry_and_execution():
    agents = AgentRegistry.list_agents()
    assert len(agents) >= 9

    names = [a["name"] for a in agents]
    assert "RepositoryAgent" in names
    assert "ArchitectureAgent" in names
    assert "SecurityAgent" in names
    assert "TestingAgent" in names
    assert "ContributionAgent" in names

    # Run RepositoryAgent on empty dummy context
    repo_agent = AgentRegistry.get_agent("RepositoryAgent")
    ctx = AgentContext(
        project_id="test_p",
        task_id="test_t",
        parameters={},
    )
    res = await repo_agent.execute(ctx)
    assert res.agent_name == "RepositoryAgent"
    assert res.status == "COMPLETED"
