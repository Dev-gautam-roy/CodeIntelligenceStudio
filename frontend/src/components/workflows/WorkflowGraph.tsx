"use client";

import React, { useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Task } from "../../types";

interface WorkflowGraphProps {
  tasks: Task[];
}

export function WorkflowGraph({ tasks }: WorkflowGraphProps) {
  const { nodes, edges } = useMemo(() => {
    const pipelineSteps = [
      { id: "step_supervisor", name: "SupervisorAgent", x: 40, y: 120, label: "Supervisor (Goal & Wave Planning)" },
      { id: "step_repo", name: "RepositoryAgent", x: 280, y: 40, label: "Wave 1: Repository Topology" },
      { id: "step_arch", name: "ArchitectureAgent", x: 280, y: 100, label: "Wave 1: Architecture Audit" },
      { id: "step_sec", name: "SecurityAgent", x: 280, y: 160, label: "Wave 1: Security & Injection" },
      { id: "step_doc", name: "DocumentationAgent", x: 280, y: 220, label: "Wave 1: Documentation" },
      { id: "step_test", name: "TestingAgent", x: 540, y: 120, label: "Wave 2: Sandbox Testing" },
      { id: "step_debug", name: "DebuggingAgent", x: 740, y: 60, label: "Wave 3: Root Cause & Patch" },
      { id: "step_contrib", name: "ContributionAgent", x: 740, y: 180, label: "Wave 4: PR & Human Approval Gate" },
    ];

    const graphNodes: Node[] = pipelineSteps.map((step) => {
      // Find real task status
      const matched = tasks.find((t) => t.agent_name === step.name);
      let statusColor = "#475569";
      let statusBorder = "#334155";
      let statusText = "IDLE";

      if (matched) {
        if (matched.status === "COMPLETED") {
          statusColor = "#064E3B";
          statusBorder = "#10B981";
          statusText = "COMPLETED";
        } else if (matched.status === "RUNNING") {
          statusColor = "#1E1B4B";
          statusBorder = "#8B5CF6";
          statusText = "RUNNING";
        } else if (matched.status === "WAITING_FOR_APPROVAL") {
          statusColor = "#78350F";
          statusBorder = "#F59E0B";
          statusText = "APPROVAL GATE";
        } else if (matched.status === "FAILED") {
          statusColor = "#7F1D1D";
          statusBorder = "#EF4444";
          statusText = "FAILED";
        }
      }

      return {
        id: step.id,
        position: { x: step.x, y: step.y },
        data: {
          label: (
            <div className="text-left font-mono">
              <div className="font-semibold text-[11px] text-slate-100">{step.label}</div>
              <div className="text-[9px] mt-1 text-slate-300 font-bold tracking-wider">
                [{statusText}]
              </div>
            </div>
          ),
        },
        style: {
          background: statusColor,
          border: `1.5px solid ${statusBorder}`,
          borderRadius: "6px",
          padding: "8px",
          width: 210,
        },
      };
    });

    const graphEdges: Edge[] = [
      { id: "e1", source: "step_supervisor", target: "step_repo", animated: true },
      { id: "e2", source: "step_supervisor", target: "step_arch", animated: true },
      { id: "e3", source: "step_supervisor", target: "step_sec", animated: true },
      { id: "e4", source: "step_supervisor", target: "step_doc", animated: true },
      { id: "e5", source: "step_repo", target: "step_test" },
      { id: "e6", source: "step_arch", target: "step_test" },
      { id: "e7", source: "step_sec", target: "step_test" },
      { id: "e8", source: "step_doc", target: "step_test" },
      { id: "e9", source: "step_test", target: "step_debug" },
      { id: "e10", source: "step_test", target: "step_contrib" },
    ];

    return { nodes: graphNodes, edges: graphEdges };
  }, [tasks]);

  return (
    <div className="h-[380px] w-full bg-surface-1 border border-border-default rounded-lg overflow-hidden relative">
      <div className="absolute top-3 left-3 z-10 bg-surface-2/80 backdrop-blur px-3 py-1.5 rounded border border-border-default text-xs flex items-center space-x-2">
        <span className="font-semibold text-slate-200">LangGraph Execution DAG</span>
        <span className="text-[10px] text-blue-400 font-mono">Multi-Wave Pipeline</span>
      </div>

      <ReactFlow nodes={nodes} edges={edges} fitView className="bg-root">
        <Background color="#1E293B" gap={16} />
        <Controls className="bg-surface-2 border border-border-default text-white" />
      </ReactFlow>
    </div>
  );
}
