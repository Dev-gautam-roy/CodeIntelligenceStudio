"use client";

import React from "react";
import { GitBranch, Activity, Cpu, CheckCircle, AlertOctagon, ShieldAlert, TestTube, Coins } from "lucide-react";

interface MetricsGridProps {
  reposCount: number;
  workflowsCount: number;
  agentsRunning: number;
  completedTasks: number;
  failedTasks: number;
  securityFindings: number;
  tokenUsage: number;
}

export function MetricsGrid({
  reposCount,
  workflowsCount,
  agentsRunning,
  completedTasks,
  failedTasks,
  securityFindings,
  tokenUsage,
}: MetricsGridProps) {
  const cards = [
    { title: "Connected Repos", value: reposCount, icon: GitBranch, color: "text-blue-400" },
    { title: "Active Workflows", value: workflowsCount, icon: Activity, color: "text-indigo-400" },
    { title: "Agents Registered", value: 10, icon: Cpu, color: "text-purple-400" },
    { title: "Completed Tasks", value: completedTasks, icon: CheckCircle, color: "text-emerald-400" },
    { title: "Failed / Retries", value: failedTasks, icon: AlertOctagon, color: "text-rose-400" },
    { title: "Security Findings", value: securityFindings, icon: ShieldAlert, color: "text-amber-400" },
    { title: "Tests Executed", value: completedTasks > 0 ? "PASSED" : "IDLE", icon: TestTube, color: "text-teal-400" },
    { title: "Tokens Tracked", value: `${tokenUsage.toLocaleString()} t`, icon: Coins, color: "text-cyan-400" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div
            key={i}
            className="bg-surface-1 border border-border-default rounded-lg p-3 flex items-center justify-between"
          >
            <div>
              <p className="text-[11px] text-slate-400 font-medium">{c.title}</p>
              <p className="text-lg font-semibold text-white mt-0.5 font-mono">{c.value}</p>
            </div>
            <div className={`p-2 rounded bg-surface-2 ${c.color}`}>
              <Icon className="w-4 h-4" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
