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
  SecurityAnalysis,
  AgentInfo,
  Workflow,
  Task,
  Approval,
} from "../types";
import { ShieldAlert, AlertTriangle, CheckCircle, FileCode } from "lucide-react";

export default function DashboardPage() {
  const [currentTab, setCurrentTab] = useState<NavTab>("overview");
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [statusMessage, setStatusMessage] = useState("System Ready");

  // Domain states
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [activeRepo, setActiveRepo] = useState<Repository | null>(null);
  const [architectureData, setArchitectureData] = useState<ArchitectureAnalysis | null>(null);
  const [securityData, setSecurityData] = useState<SecurityAnalysis | null>(null);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);

  const selectRepository = (repo: Repository) => {
    setActiveRepo(repo);
    api.getArchitecture(repo.id)
      .then(setArchitectureData)
      .catch(() => null);
    api.getSecurityAudit(repo.id)
      .then(setSecurityData)
      .catch(() => null);
  };

  // Initial Data Fetch
  const loadData = async (newRepo?: Repository) => {
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

      const targetRepo = newRepo || activeRepo || (reposList.length > 0 ? reposList[0] : null);
      if (targetRepo) {
        if (!activeRepo || newRepo) setActiveRepo(targetRepo);
        // Load architecture and security
        api.getArchitecture(targetRepo.id)
          .then(setArchitectureData)
          .catch(() => null);
        api.getSecurityAudit(targetRepo.id)
          .then(setSecurityData)
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
        repositories={repositories}
        activeRepo={activeRepo}
        onSelectRepo={selectRepository}
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
            onActionComplete={(repo) => loadData(repo)}
            onSetStatus={setStatusMessage}
            repositories={repositories}
            activeRepo={activeRepo}
            onSelectRepo={selectRepository}
          />

          {/* Telemetry Metrics Grid */}
          <MetricsGrid
            reposCount={repositories.length}
            workflowsCount={workflows.length}
            agentsRunning={tasks.filter((t) => t.status === "RUNNING").length}
            completedTasks={tasks.filter((t) => t.status === "COMPLETED").length}
            failedTasks={tasks.filter((t) => t.status === "FAILED").length}
            securityFindings={securityData ? securityData.findings_count : 0}
            tokenUsage={tasks.reduce((sum, t) => sum + t.token_usage, 0)}
          />

          {/* Dynamic Views Based on NavTab */}
          {currentTab === "overview" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ArchitectureGraph data={architectureData} />
                <WorkflowGraph
                  tasks={tasks}
                  activeRepo={activeRepo}
                  onRefresh={loadData}
                />
              </div>

              {/* Prominent Security Alert if Findings Exist */}
              {securityData && securityData.findings_count > 0 && (
                <div className="bg-surface-1 border border-red-500/40 rounded-lg p-4 space-y-3 shadow-lg shadow-red-500/10">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-red-400 font-semibold text-xs">
                      <ShieldAlert className="w-4 h-4" />
                      <span>Security Vulnerabilities Detected ({securityData.findings_count})</span>
                    </div>
                    <button
                      onClick={() => setCurrentTab("security")}
                      className="text-xs text-blue-400 hover:underline font-mono"
                    >
                      View all findings & remediation &rarr;
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    {securityData.findings.slice(0, 4).map((f, i) => (
                      <div key={i} className="p-2.5 rounded bg-surface-2 border border-border-default space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-red-400 font-mono text-[10px]">{f.type}</span>
                          <span className="px-1.5 py-0.2 rounded bg-red-500/20 text-red-300 text-[9px] font-bold">
                            {f.severity}
                          </span>
                        </div>
                        <p className="text-slate-300 font-mono text-[11px] truncate">{f.snippet}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <AgentCardRail agents={agents} tasks={tasks} />
              <InteractiveTerminal activeRepositoryId={activeRepo?.id} />
            </div>
          )}

          {currentTab === "security" && (
            <div className="space-y-4">
              <div className="bg-surface-1 border border-border-default rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-red-400" />
                      Security & Vulnerability Audit Report
                    </h3>
                    <p className="text-xs text-slate-400">
                      Scanned repository: <span className="font-mono text-slate-200">{activeRepo?.url}</span>
                    </p>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-surface-2 border border-border-default font-mono text-xs text-slate-300">
                    Scan Time: {securityData?.scan_duration_ms || 0}ms
                  </span>
                </div>

                {!securityData || securityData.findings_count === 0 ? (
                  <div className="py-12 text-center text-xs text-emerald-400 flex flex-col items-center gap-2">
                    <CheckCircle className="w-8 h-8 text-emerald-500" />
                    <span className="font-semibold text-sm">No security flaws detected!</span>
                    <span className="text-slate-400">Zero leaked credentials, prompt injections, or unsafe patterns found.</span>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {securityData.findings.map((f, i) => (
                      <div
                        key={i}
                        className="p-3 rounded bg-surface-2 border border-border-default space-y-2 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 font-mono text-[10px] font-bold">
                              {f.severity}
                            </span>
                            <span className="font-semibold text-slate-200 font-mono">{f.type}</span>
                            <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1">
                              <FileCode className="w-3 h-3" />
                              {f.file_path}:{f.line_number}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-500 font-mono">OWASP Top 10</span>
                        </div>

                        <div className="bg-root p-2 rounded font-mono text-[11px] text-red-300 border border-red-500/20">
                          {f.snippet}
                        </div>

                        <p className="text-slate-300">{f.description}</p>
                        <p className="text-[11px] text-emerald-400 font-mono">
                          <span className="font-bold">Remediation:</span> {f.recommendation}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
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
