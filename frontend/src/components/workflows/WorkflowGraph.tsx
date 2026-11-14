"use client";

import React, { useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Play, Loader2, GitCommit, CheckCircle2, AlertTriangle, RefreshCw } from "lucide-react";
import { Task, Repository } from "../../types";
import { api } from "../../services/api";

interface WorkflowGraphProps {
  tasks: Task[];
  activeRepo?: Repository | null;
  onRefresh?: () => void;
}

export function WorkflowGraph({ tasks, activeRepo, onRefresh }: WorkflowGraphProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [triggerMessage, setTriggerMessage] = useState<string | null>(null);

  const handleTriggerLangGraph = async () => {
    if (!activeRepo) return;
    setIsRunning(true);
    setTriggerMessage("Initiating LangGraph autonomous pipeline...");
    try {
      const wf = await api.createWorkflow(
        activeRepo.project_id,
        "LangGraph Multi-Wave Autonomous Pipeline",
        activeRepo.url
      );
      setTriggerMessage(`LangGraph Pipeline active (Workflow #${wf.id.slice(0, 8)})`);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setTriggerMessage(err.message || "Failed to launch LangGraph pipeline");
    } finally {
      setIsRunning(false);
    }
  };

  const { nodes, edges, activeCount, completedCount } = useMemo(() => {
    const pipelineSteps = [
      { id: "step_supervisor", name: "SupervisorAgent", x: 30, y: 130, label: "Supervisor Agent", sub: "Wave Planning & State Init" },
      { id: "step_repo", name: "RepositoryAgent", x: 260, y: 30, label: "Repository Agent", sub: "Wave 1: Topology & Files" },
      { id: "step_arch", name: "ArchitectureAgent", x: 260, y: 100, label: "Architecture Agent", sub: "Wave 1: AST & Tarjan SCC" },
      { id: "step_sec", name: "SecurityAgent", x: 260, y: 170, label: "Security Agent", sub: "Wave 1: OWASP & Injection" },
      { id: "step_doc", name: "DocumentationAgent", x: 260, y: 240, label: "Documentation Agent", sub: "Wave 1: API Docs & Spec" },
      { id: "step_test", name: "TestingAgent", x: 500, y: 130, label: "Testing Agent", sub: "Wave 2: Sandbox Pytest/Flutter" },
      { id: "step_debug", name: "DebuggingAgent", x: 720, y: 50, label: "Debugging Agent", sub: "Wave 3: Root-Cause & AST Patch" },
      { id: "step_contrib", name: "ContributionAgent", x: 720, y: 210, label: "Contribution Agent", sub: "Wave 4: PR & Human Approval" },
    ];

    let runningSum = 0;
    let completedSum = 0;

    const graphNodes: Node[] = pipelineSteps.map((step) => {
      // Find latest task matching this agent
      const matched = [...tasks].reverse().find((t) => t.agent_name === step.name);
      let statusColor = "#1E293B";
      let statusBorder = "#334155";
      let statusText = "IDLE";
      let textColor = "text-slate-400";
      let isAnimated = false;

      if (matched) {
        if (matched.status === "COMPLETED") {
          statusColor = "#064E3B";
          statusBorder = "#10B981";
          statusText = "COMPLETED";
          textColor = "text-emerald-300";
          completedSum++;
        } else if (matched.status === "RUNNING") {
          statusColor = "#311042";
          statusBorder = "#A855F7";
          statusText = "RUNNING";
          textColor = "text-purple-300";
          isAnimated = true;
          runningSum++;
        } else if (matched.status === "WAITING_FOR_APPROVAL") {
          statusColor = "#78350F";
          statusBorder = "#F59E0B";
          statusText = "APPROVAL GATE";
          textColor = "text-amber-300";
        } else if (matched.status === "FAILED") {
          statusColor = "#7F1D1D";
          statusBorder = "#EF4444";
          statusText = "FAILED";
          textColor = "text-red-300";
        }
      }

      return {
        id: step.id,
        position: { x: step.x, y: step.y },
        data: {
          label: (
            <div className="text-left font-mono">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[11px] text-slate-100">{step.label}</span>
                <span className={`text-[9px] font-bold ${textColor}`}>[{statusText}]</span>
              </div>
              <div className="text-[9px] mt-1 text-slate-400 truncate">{step.sub}</div>
            </div>
          ),
        },
        style: {
          background: statusColor,
          border: `1.5px solid ${statusBorder}`,
          borderRadius: "8px",
          padding: "10px",
          width: 200,
          boxShadow: isAnimated ? "0 0 15px rgba(168, 85, 247, 0.4)" : "none",
        },
      };
    });

    const graphEdges: Edge[] = [
      // Fan-out from supervisor to Wave 1
      { id: "e1", source: "step_supervisor", target: "step_repo", animated: true, style: { stroke: "#64748B" } },
      { id: "e2", source: "step_supervisor", target: "step_arch", animated: true, style: { stroke: "#64748B" } },
      { id: "e3", source: "step_supervisor", target: "step_sec", animated: true, style: { stroke: "#64748B" } },
      { id: "e4", source: "step_supervisor", target: "step_doc", animated: true, style: { stroke: "#64748B" } },

      // Wave 1 to Wave 2 Testing
      { id: "e5", source: "step_repo", target: "step_test", style: { stroke: "#64748B" } },
      { id: "e6", source: "step_arch", target: "step_test", style: { stroke: "#64748B" } },
      { id: "e7", source: "step_sec", target: "step_test", style: { stroke: "#64748B" } },
      { id: "e8", source: "step_doc", target: "step_test", style: { stroke: "#64748B" } },

      // Conditional Edge to Debugging Loop
      {
        id: "e9",
        source: "step_test",
        target: "step_debug",
        label: "on test fail",
        labelStyle: { fill: "#EF4444", fontSize: 9, fontFamily: "monospace" },
        style: { stroke: "#EF4444", strokeDasharray: "4 2" },
      },
      // Loopback Edge from Debugging back to Testing
      {
        id: "e11",
        source: "step_debug",
        target: "step_test",
        label: "re-test patch",
        labelStyle: { fill: "#F59E0B", fontSize: 9, fontFamily: "monospace" },
        style: { stroke: "#F59E0B", strokeDasharray: "4 2" },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#F59E0B" },
      },

      // Edge from Testing to Contribution Gate
      {
        id: "e10",
        source: "step_test",
        target: "step_contrib",
        label: "on pass",
        labelStyle: { fill: "#10B981", fontSize: 9, fontFamily: "monospace" },
        style: { stroke: "#10B981" },
      },
    ];

    return {
      nodes: graphNodes,
      edges: graphEdges,
      activeCount: runningSum,
      completedCount: completedSum,
    };
  }, [tasks]);

  return (
    <div className="h-[420px] w-full bg-surface-1 border border-border-default rounded-lg overflow-hidden relative flex flex-col">
      {/* Top Header & Actions Bar */}
      <div className="bg-surface-2/90 border-b border-border-default px-4 py-2 flex items-center justify-between z-10">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-xs text-slate-200">LangGraph Multi-Wave Orchestration Engine</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 font-mono">
            StateGraph v1.2
          </span>
          {activeCount > 0 && (
            <span className="flex items-center space-x-1 text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono animate-pulse">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
              <span>{activeCount} Agent(s) Active</span>
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleTriggerLangGraph}
            disabled={isRunning || !activeRepo}
            className="flex items-center space-x-1.5 bg-purple-600 hover:bg-purple-500 text-white font-medium text-xs px-3 py-1.5 rounded shadow-sm shadow-purple-600/30 disabled:opacity-50 transition-all font-mono"
            title="Execute LangGraph pipeline on active repository"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Running Graph...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>Run LangGraph Pipeline</span>
              </>
            )}
          </button>
        </div>
      </div>

      {triggerMessage && (
        <div className="bg-surface-2 border-b border-border-default px-4 py-1 text-[11px] font-mono text-purple-300 flex items-center justify-between">
          <span>{triggerMessage}</span>
          <button onClick={() => setTriggerMessage(null)} className="text-slate-400 hover:text-white">
            &times;
          </button>
        </div>
      )}

      {/* ReactFlow Interactive Canvas */}
      <div className="flex-1 w-full relative">
        <ReactFlow nodes={nodes} edges={edges} fitView className="bg-root">
          <Background color="#1E293B" gap={16} />
          <Controls className="bg-surface-2 border border-border-default text-white" />
        </ReactFlow>
      </div>
    </div>
  );
}
