"use client";

import React, { useState, useEffect } from "react";
import { Header } from "../components/layout/Header";
import { Sidebar, NavTab } from "../components/layout/Sidebar";
import { MetricsGrid } from "../components/dashboard/MetricsGrid";
import { RepositoryActionBar } from "../components/dashboard/RepositoryActionBar";
import { ArchitectureGraph } from "../components/architecture/ArchitectureGraph";
import { WorkflowGraph } from "../components/workflows/WorkflowGraph";
import { AgentCardRail } from "../components/agents/AgentCardRail";
import { InteractiveTerminal } from "../components/terminal/InteractiveTerminal";
import { ApprovalModal } from "../components/approvals/ApprovalModal";
import { api } from "../services/api";
import {
  Repository,
  ArchitectureAnalysis,
  AgentInfo,
  Workflow,
  Task,
  Approval,
} from "../types";

export default function DashboardPage() {
  const [currentTab, setCurrentTab] = useState<NavTab>("overview");
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [statusMessage, setStatusMessage] = useState("System Ready");

  // Domain states
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [activeRepo, setActiveRepo] = useState<Repository | null>(null);
  const [architectureData, setArchitectureData] = useState<ArchitectureAnalysis | null>(null);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);

  // Initial Data Fetch
  const loadData = async () => {
    try {
      await api.checkHealth();
      setIsBackendConnected(true);
    } catch {
      setIsBackendConnected(false);
    }

    try {
      const [reposList, agentsList, wfsList, tasksList, appsList] = await Promise.all([
        api.listRepositories().catch(() => []),
        api.listAgents().catch(() => []),
        api.listWorkflows().catch(() => []),
        api.listTasks().catch(() => []),
        api.listApprovals("PENDING").catch(() => []),
      ]);

      setRepositories(reposList);
      setAgents(agentsList);
      setWorkflows(wfsList);
      setTasks(tasksList);
      setApprovals(appsList);

      if (reposList.length > 0 && !activeRepo) {
        setActiveRepo(reposList[0]);
        // Load architecture analysis
        api.getArchitecture(reposList[0].id)
          .then(setArchitectureData)
          .catch(() => null);
      }
    } catch (e) {
      console.error("Error refreshing dashboard state:", e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (id: string) => {
    await api.approveAction(id);
    setIsApprovalModalOpen(false);
    loadData();
  };

  const handleReject = async (id: string) => {
    await api.rejectAction(id);
    setIsApprovalModalOpen(false);
    loadData();
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-root">
      {/* Top Application Header */}
      <Header
        activeRepoUrl={activeRepo?.url}
        pendingApprovalsCount={approvals.length}
        onOpenApprovals={() => setIsApprovalModalOpen(true)}
        isBackendConnected={isBackendConnected}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          approvalsCount={approvals.length}
        />

        {/* Main Content Pane */}
        <main className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Unified Repository Action Bar */}
          <RepositoryActionBar
            onActionComplete={loadData}
            onSetStatus={setStatusMessage}
          />

          {/* Telemetry Metrics Grid */}
          <MetricsGrid
            reposCount={repositories.length}
            workflowsCount={workflows.length}
            agentsRunning={tasks.filter((t) => t.status === "RUNNING").length}
            completedTasks={tasks.filter((t) => t.status === "COMPLETED").length}
            failedTasks={tasks.filter((t) => t.status === "FAILED").length}
            securityFindings={0}
            tokenUsage={tasks.reduce((sum, t) => sum + t.token_usage, 0)}
          />

          {/* Dynamic Views Based on NavTab */}
          {currentTab === "overview" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ArchitectureGraph data={architectureData} />
                <WorkflowGraph tasks={tasks} />
              </div>
              <AgentCardRail agents={agents} tasks={tasks} />
              <InteractiveTerminal activeRepositoryId={activeRepo?.id} />
            </div>
          )}

          {currentTab === "architecture" && (
            <div className="space-y-4">
              <ArchitectureGraph data={architectureData} />
              {architectureData && (
                <div className="bg-surface-1 border border-border-default rounded-lg p-4 font-mono text-xs">
                  <h3 className="font-semibold text-slate-200 mb-2">Executive Architectural Summary</h3>
                  <p className="text-slate-400 mb-4">{architectureData.summary}</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-slate-300 mb-1">Detected Frameworks:</h4>
                      <ul className="list-disc pl-4 text-slate-400">
                        {architectureData.frameworks.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-300 mb-1">Entry Points:</h4>
                      <ul className="list-disc pl-4 text-slate-400">
                        {architectureData.entry_points.map((e, i) => (
                          <li key={i}>{e}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {currentTab === "workflows" && (
            <div className="space-y-4">
              <WorkflowGraph tasks={tasks} />
              <div className="bg-surface-1 border border-border-default rounded-lg p-4">
                <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
                  Task Execution Log ({tasks.length})
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="p-2.5 rounded bg-surface-2 border border-border-default flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center space-x-3">
                        <span className="font-semibold text-slate-200 font-mono">{task.agent_name}</span>
                        <span className="text-slate-400 truncate max-w-md">
                          {task.output_payload?.summary || "Executing task..."}
                        </span>
                      </div>
                      <div className="flex items-center space-x-3 font-mono text-[11px]">
                        <span className="text-cyan-400">{task.token_usage} tokens</span>
                        <span className="text-slate-400">{task.execution_time_ms}ms</span>
                        <span
                          className={`px-2 py-0.5 rounded font-bold ${
                            task.status === "COMPLETED"
                              ? "bg-emerald-500/20 text-emerald-300"
                              : task.status === "RUNNING"
                              ? "bg-blue-500/20 text-blue-300"
                              : "bg-amber-500/20 text-amber-300"
                          }`}
                        >
                          {task.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentTab === "agents" && (
            <AgentCardRail agents={agents} tasks={tasks} />
          )}

          {currentTab === "terminal" && (
            <InteractiveTerminal activeRepositoryId={activeRepo?.id} />
          )}

          {currentTab === "approvals" && (
            <div className="bg-surface-1 border border-border-default rounded-lg p-4 space-y-3">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Pending Human Approval Gates ({approvals.length})
              </h3>
              {approvals.map((app) => (
                <div key={app.id} className="p-3 rounded bg-surface-2 border border-border-default space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-blue-400 font-bold">{app.action_type}</span>
                    <span className="text-[11px] font-mono text-amber-300 font-bold">WAITING APPROVAL</span>
                  </div>
                  <p className="text-xs text-slate-300 font-mono">{app.target_resource}</p>
                  <div className="flex justify-end space-x-2 pt-2">
                    <button
                      onClick={() => handleReject(app.id)}
                      className="px-3 py-1 rounded bg-red-600/20 text-red-300 border border-red-500/30 text-xs"
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => handleApprove(app.id)}
                      className="px-3 py-1 rounded bg-emerald-600 text-white text-xs font-medium"
                    >
                      Approve Action
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Human-in-the-Loop Approval Modal */}
      <ApprovalModal
        isOpen={isApprovalModalOpen}
        onClose={() => setIsApprovalModalOpen(false)}
        approvals={approvals}
        onApprove={handleApprove}
        onReject={handleReject}
      />
    </div>
  );
}
