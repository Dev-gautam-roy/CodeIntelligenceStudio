import asyncio
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.agents.base import AgentContext, AgentResult
from app.agents.registry import AgentRegistry
from app.models.workflow import Workflow
from app.models.task import Task
from app.models.approval import Approval
from app.core.logging import logger


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
        """Executes the complete multi-wave autonomous pipeline with state persistence and approval pauses."""
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found.")

        workflow.status = "RUNNING"
        db.commit()

        results = {}

        # Wave 1: Independent Parallel Agents
        wave_1_agents = ["RepositoryAgent", "ArchitectureAgent", "SecurityAgent", "DocumentationAgent"]
        logger.info(f"Executing Wave 1 in parallel: {wave_1_agents}")

        tasks_wave_1 = []
        for name in wave_1_agents:
            agent = AgentRegistry.get_agent(name)
            ctx = AgentContext(
                project_id=project_id,
                workspace_path=workspace_path,
                task_id=f"{workflow_id}_{name}",
                parameters={"repo_url": repository_url},
            )
            # Create Task DB record
            t_record = Task(
                workflow_id=workflow_id,
                agent_name=name,
                status="RUNNING",
                input_payload=ctx.model_dump(),
            )
            db.add(t_record)
            db.commit()
            db.refresh(t_record)
            tasks_wave_1.append((agent, ctx, t_record))

        # Execute Wave 1 concurrently
        agent_executions = await asyncio.gather(
            *[agent.execute(ctx) for agent, ctx, _ in tasks_wave_1],
            return_exceptions=True,
        )

        for (agent, ctx, t_record), res in zip(tasks_wave_1, agent_executions):
            if isinstance(res, Exception):
                t_record.status = "FAILED"
                t_record.error_message = str(res)
                results[agent.name] = {"status": "FAILED", "error": str(res)}
            else:
                t_record.status = res.status
                t_record.output_payload = res.model_dump()
                t_record.token_usage = res.tokens_used
                t_record.execution_time_ms = res.duration_ms
                results[agent.name] = res.model_dump()
            db.commit()

        # Wave 2: Testing Agent (Prerequisite: Wave 1 complete)
        logger.info("Executing Wave 2: TestingAgent...")
        test_agent = AgentRegistry.get_agent("TestingAgent")
        test_ctx = AgentContext(
            project_id=project_id,
            workspace_path=workspace_path,
            task_id=f"{workflow_id}_TestingAgent",
        )
        t_record = Task(
            workflow_id=workflow_id,
            agent_name="TestingAgent",
            status="RUNNING",
            input_payload=test_ctx.model_dump(),
        )
        db.add(t_record)
        db.commit()
        db.refresh(t_record)

        test_res = await test_agent.execute(test_ctx)
        t_record.status = test_res.status
        t_record.output_payload = test_res.model_dump()
        t_record.token_usage = test_res.tokens_used
        t_record.execution_time_ms = test_res.duration_ms
        db.commit()
        results["TestingAgent"] = test_res.model_dump()

        # Wave 3: If tests fail, run DebuggingAgent
        if test_res.status == "FAILED":
            logger.info("Tests failed. Executing Wave 3: DebuggingAgent...")
            debug_agent = AgentRegistry.get_agent("DebuggingAgent")
            debug_ctx = AgentContext(
                project_id=project_id,
                workspace_path=workspace_path,
                task_id=f"{workflow_id}_DebuggingAgent",
                parameters={"error_context": test_res.summary},
            )
            debug_record = Task(
                workflow_id=workflow_id,
                agent_name="DebuggingAgent",
                status="RUNNING",
                input_payload=debug_ctx.model_dump(),
            )
            db.add(debug_record)
            db.commit()
            db.refresh(debug_record)

            debug_res = await debug_agent.execute(debug_ctx)
            debug_record.status = debug_res.status
            debug_record.output_payload = debug_res.model_dump()
            debug_record.token_usage = debug_res.tokens_used
            debug_record.execution_time_ms = debug_res.duration_ms
            db.commit()
            results["DebuggingAgent"] = debug_res.model_dump()

        # Wave 4: Contribution & Approval Gate
        logger.info("Staging Wave 4: ContributionAgent & Approval Gate...")
        contrib_agent = AgentRegistry.get_agent("ContributionAgent")
        contrib_ctx = AgentContext(
            project_id=project_id,
            workspace_path=workspace_path,
            task_id=f"{workflow_id}_ContributionAgent",
            parameters={"target_repo": repository_url},
        )
        contrib_record = Task(
            workflow_id=workflow_id,
            agent_name="ContributionAgent",
            status="WAITING_FOR_APPROVAL",
            input_payload=contrib_ctx.model_dump(),
        )
        db.add(contrib_record)
        db.commit()
        db.refresh(contrib_record)

        contrib_res = await contrib_agent.execute(contrib_ctx)
        contrib_record.output_payload = contrib_res.model_dump()

        # Create persistent approval record
        if contrib_res.requires_approval and contrib_res.approval_details:
            app_record = Approval(
                task_id=contrib_record.id,
                action_type=contrib_res.approval_details.get("action_type", "CREATE_PULL_REQUEST"),
                target_resource=contrib_res.approval_details.get("target_repo", repository_url),
                diff_payload=contrib_res.approval_details.get("diff_summary", ""),
                status="PENDING",
            )
            db.add(app_record)
            workflow.status = "WAITING_FOR_APPROVAL"
        else:
            workflow.status = "COMPLETED"

        db.commit()
        results["ContributionAgent"] = contrib_res.model_dump()

        return {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "results": results,
        }
