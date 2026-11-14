import asyncio
import operator
from typing import TypedDict, Annotated, Dict, Any, List, Optional
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

from app.db.session import SessionLocal
from app.agents.base import AgentContext, AgentResult
from app.agents.registry import AgentRegistry
from app.models.workflow import Workflow
from app.models.task import Task
from app.models.approval import Approval
from app.core.logging import logger


class AgentWorkflowState(TypedDict):
    workflow_id: str
    project_id: str
    workspace_path: str
    repository_url: str
    current_wave: str
    active_agent: str
    results: Annotated[Dict[str, Any], operator.ior]
    errors: Annotated[List[str], operator.add]
    needs_debug: bool
    needs_approval: bool
    debug_iterations: int
    test_summary: str


def _record_task_start(db: Session, workflow_id: str, agent_name: str, input_payload: dict) -> Task:
    t = Task(
        workflow_id=workflow_id,
        agent_name=agent_name,
        status="RUNNING",
        input_payload=input_payload,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def _record_task_finish(db: Session, task_id: str, result: AgentResult):
    t = db.query(Task).filter(Task.id == task_id).first()
    if t:
        t.status = result.status
        t.output_payload = result.model_dump()
        t.token_usage = result.tokens_used
        t.execution_time_ms = result.duration_ms
        db.commit()


def _record_task_failure(db: Session, task_id: str, error_msg: str):
    t = db.query(Task).filter(Task.id == task_id).first()
    if t:
        t.status = "FAILED"
        t.error_message = error_msg
        db.commit()


# --- LangGraph Node Functions ---

async def supervisor_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """LangGraph Node: Goal analysis, wave planning, and seeding workspace context."""
    db: Session = SessionLocal()
    try:
        agent = AgentRegistry.get_agent("SupervisorAgent")
        ctx = AgentContext(
            project_id=state["project_id"],
            workspace_path=state["workspace_path"],
            task_id=f"{state['workflow_id']}_SupervisorAgent",
            parameters={"repo_url": state["repository_url"]},
        )
        t = _record_task_start(db, state["workflow_id"], "SupervisorAgent", ctx.model_dump())
        logger.info(f"[LangGraph:Supervisor] Planning execution waves for {state['repository_url']}")
        res = await agent.execute(ctx)
        _record_task_finish(db, t.id, res)
        return {
            "current_wave": "Wave 1: Parallel Topology & Audit",
            "active_agent": "SupervisorAgent",
            "results": {"SupervisorAgent": res.model_dump()},
        }
    except Exception as e:
        logger.error(f"[LangGraph:Supervisor] Error: {e}")
        return {
            "errors": [f"SupervisorAgent error: {str(e)}"],
            "results": {"SupervisorAgent": {"status": "FAILED", "error": str(e)}},
        }
    finally:
        db.close()


async def wave_1_parallel_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """LangGraph Node: Fan-out execution of Wave 1 agents (Repo, Architecture, Security, Docs)."""
    db: Session = SessionLocal()
    wave_1_agents = ["RepositoryAgent", "ArchitectureAgent", "SecurityAgent", "DocumentationAgent"]
    logger.info(f"[LangGraph:Wave 1] Executing concurrent fan-out: {wave_1_agents}")

    results_map = {}
    errors_list = []

    try:
        tasks_meta = []
        for name in wave_1_agents:
            agent = AgentRegistry.get_agent(name)
            ctx = AgentContext(
                project_id=state["project_id"],
                workspace_path=state["workspace_path"],
                task_id=f"{state['workflow_id']}_{name}",
                parameters={"repo_url": state["repository_url"]},
            )
            t_record = _record_task_start(db, state["workflow_id"], name, ctx.model_dump())
            tasks_meta.append((agent, ctx, t_record.id))

        executions = await asyncio.gather(
            *[agent.execute(ctx) for agent, ctx, _ in tasks_meta],
            return_exceptions=True,
        )

        for (agent, ctx, t_id), res in zip(tasks_meta, executions):
            if isinstance(res, Exception):
                _record_task_failure(db, t_id, str(res))
                errors_list.append(f"{agent.name} failed: {str(res)}")
                results_map[agent.name] = {"status": "FAILED", "error": str(res)}
            else:
                _record_task_finish(db, t_id, res)
                results_map[agent.name] = res.model_dump()

        return {
            "current_wave": "Wave 2: Sandbox Testing",
            "active_agent": "RepositoryAgent",
            "results": results_map,
            "errors": errors_list,
        }
    finally:
        db.close()


async def testing_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """LangGraph Node: Sandboxed execution of test suites."""
    db: Session = SessionLocal()
    try:
        agent = AgentRegistry.get_agent("TestingAgent")
        ctx = AgentContext(
            project_id=state["project_id"],
            workspace_path=state["workspace_path"],
            task_id=f"{state['workflow_id']}_TestingAgent",
        )
        t = _record_task_start(db, state["workflow_id"], "TestingAgent", ctx.model_dump())
        logger.info(f"[LangGraph:Testing] Executing sandbox test suite (Iteration {state.get('debug_iterations', 0)})...")
        res = await agent.execute(ctx)
        _record_task_finish(db, t.id, res)

        needs_debug = (res.status == "FAILED")
        return {
            "current_wave": "Wave 3: Evaluation & Feedback Loop",
            "active_agent": "TestingAgent",
            "needs_debug": needs_debug,
            "test_summary": res.summary,
            "results": {"TestingAgent": res.model_dump()},
        }
    except Exception as e:
        logger.error(f"[LangGraph:Testing] Error: {e}")
        return {
            "needs_debug": True,
            "test_summary": str(e),
            "errors": [f"TestingAgent error: {str(e)}"],
            "results": {"TestingAgent": {"status": "FAILED", "error": str(e)}},
        }
    finally:
        db.close()


def route_after_testing(state: AgentWorkflowState) -> str:
    """LangGraph Conditional Edge: Routes to Debugging loop or proceeds to Contribution."""
    if state.get("needs_debug", False) and state.get("debug_iterations", 0) < 2:
        logger.info("[LangGraph:Router] Tests failed -> Triggering DebuggingAgent feedback loop.")
        return "debugging"
    logger.info("[LangGraph:Router] Tests passed or max iterations reached -> Proceeding to Approval & Contribution.")
    return "contribution"


async def debugging_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """LangGraph Node: Root-cause diagnosis, AST patch generation, and loopback to sandbox re-testing."""
    db: Session = SessionLocal()
    try:
        agent = AgentRegistry.get_agent("DebuggingAgent")
        iter_count = state.get("debug_iterations", 0) + 1
        ctx = AgentContext(
            project_id=state["project_id"],
            workspace_path=state["workspace_path"],
            task_id=f"{state['workflow_id']}_DebuggingAgent_{iter_count}",
            parameters={"error_context": state.get("test_summary", "Test assertion failures detected.")},
        )
        t = _record_task_start(db, state["workflow_id"], "DebuggingAgent", ctx.model_dump())
        logger.info(f"[LangGraph:Debugging] Diagnosing failure & synthesizing patch (Iteration {iter_count})...")
        res = await agent.execute(ctx)
        _record_task_finish(db, t.id, res)

        return {
            "current_wave": f"Wave 3: Debugging (Loop {iter_count})",
            "active_agent": "DebuggingAgent",
            "debug_iterations": iter_count,
            "results": {"DebuggingAgent": res.model_dump()},
        }
    except Exception as e:
        logger.error(f"[LangGraph:Debugging] Error: {e}")
        return {
            "errors": [f"DebuggingAgent error: {str(e)}"],
            "results": {"DebuggingAgent": {"status": "FAILED", "error": str(e)}},
        }
    finally:
        db.close()


async def contribution_node(state: AgentWorkflowState) -> Dict[str, Any]:
    """LangGraph Node: Contribution staging, diff calculation, and human approval pause gate."""
    db: Session = SessionLocal()
    try:
        agent = AgentRegistry.get_agent("ContributionAgent")
        ctx = AgentContext(
            project_id=state["project_id"],
            workspace_path=state["workspace_path"],
            task_id=f"{state['workflow_id']}_ContributionAgent",
            parameters={"target_repo": state["repository_url"]},
        )

        contrib_record = Task(
            workflow_id=state["workflow_id"],
            agent_name="ContributionAgent",
            status="WAITING_FOR_APPROVAL",
            input_payload=ctx.model_dump(),
        )
        db.add(contrib_record)
        db.commit()
        db.refresh(contrib_record)

        logger.info("[LangGraph:Contribution] Staging PR contribution and configuring approval gate...")
        res = await agent.execute(ctx)
        contrib_record.output_payload = res.model_dump()
        contrib_record.status = "WAITING_FOR_APPROVAL" if res.requires_approval else res.status

        workflow = db.query(Workflow).filter(Workflow.id == state["workflow_id"]).first()

        if res.requires_approval and res.approval_details:
            app_record = Approval(
                task_id=contrib_record.id,
                action_type=res.approval_details.get("action_type", "CREATE_PULL_REQUEST"),
                target_resource=res.approval_details.get("target_repo", state["repository_url"]),
                diff_payload=res.approval_details.get("diff_summary", ""),
                status="PENDING",
            )
            db.add(app_record)
            if workflow:
                workflow.status = "WAITING_FOR_APPROVAL"
        else:
            if workflow:
                workflow.status = "COMPLETED"

        db.commit()
        return {
            "current_wave": "Wave 4: Human Approval Gate",
            "active_agent": "ContributionAgent",
            "needs_approval": res.requires_approval,
            "results": {"ContributionAgent": res.model_dump()},
        }
    except Exception as e:
        logger.error(f"[LangGraph:Contribution] Error: {e}")
        return {
            "errors": [f"ContributionAgent error: {str(e)}"],
            "results": {"ContributionAgent": {"status": "FAILED", "error": str(e)}},
        }
    finally:
        db.close()


def build_langgraph_pipeline():
    """Builds and compiles the official LangGraph StateGraph pipeline for Code Intelligence Studio."""
    builder = StateGraph(AgentWorkflowState)

    # Add Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("wave_1", wave_1_parallel_node)
    builder.add_node("testing", testing_node)
    builder.add_node("debugging", debugging_node)
    builder.add_node("contribution", contribution_node)

    # Add Directed & Conditional Edges
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "wave_1")
    builder.add_edge("wave_1", "testing")
    builder.add_conditional_edges(
        "testing",
        route_after_testing,
        {
            "debugging": "debugging",
            "contribution": "contribution",
        },
    )
    # Loopback edge from debugging back to sandbox re-testing
    builder.add_edge("debugging", "testing")
    builder.add_edge("contribution", END)

    return builder.compile()


# Global compiled LangGraph instance
langgraph_app = build_langgraph_pipeline()


class WorkflowOrchestrator:
    @classmethod
    async def run_full_pipeline(
        cls,
        db: Session,
        workflow_id: str,
        project_id: str,
        workspace_path: str,
        repository_url: str,
    ) -> Dict[str, Any]:
        """Executes the complete autonomous pipeline using compiled LangGraph StateGraph."""
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found.")

        workflow.status = "RUNNING"
        db.commit()

        initial_state: AgentWorkflowState = {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "workspace_path": workspace_path,
            "repository_url": repository_url,
            "current_wave": "Supervisor Planning",
            "active_agent": "SupervisorAgent",
            "results": {},
            "errors": [],
            "needs_debug": False,
            "needs_approval": False,
            "debug_iterations": 0,
            "test_summary": "",
        }

        logger.info(f"Initiating LangGraph autonomous pipeline for workflow {workflow_id}...")
        final_state = await langgraph_app.ainvoke(initial_state)

        # Re-query workflow to obtain updated status after graph execution
        wf_refresh = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if wf_refresh and wf_refresh.status not in ["WAITING_FOR_APPROVAL", "FAILED"]:
            wf_refresh.status = "COMPLETED"
            db.commit()

        return {
            "workflow_id": workflow_id,
            "status": wf_refresh.status if wf_refresh else "COMPLETED",
            "results": final_state.get("results", {}),
            "errors": final_state.get("errors", []),
        }
