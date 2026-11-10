"use client";

import React from "react";
import {
  LayoutDashboard,
  GitBranch,
  Network,
  Cpu,
  Workflow as WorkflowIcon,
  ShieldAlert,
  Terminal as TerminalIcon,
  CheckSquare,
  BookOpen,
} from "lucide-react";

export type NavTab =
  | "overview"
  | "repositories"
  | "architecture"
  | "agents"
  | "workflows"
  | "security"
  | "terminal"
  | "approvals";

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  approvalsCount: number;
}

export function Sidebar({ currentTab, onSelectTab, approvalsCount }: SidebarProps) {
  const items = [
    { id: "overview", label: "Dashboard", icon: LayoutDashboard },
    { id: "repositories", label: "Repositories", icon: GitBranch },
    { id: "architecture", label: "Architecture", icon: Network },
    { id: "workflows", label: "Workflows (DAG)", icon: WorkflowIcon },
    { id: "agents", label: "Agent Rail", icon: Cpu },
    { id: "security", label: "Security & Threat", icon: ShieldAlert },
    { id: "terminal", label: "Terminal Console", icon: TerminalIcon },
    { id: "approvals", label: "Approvals Gate", icon: CheckSquare, badge: approvalsCount },
  ];

  return (
    <aside className="w-56 bg-surface-1 border-r border-border-default flex flex-col justify-between p-3 select-none">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
          Navigation
        </div>
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id as NavTab)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-all ${
                isActive
                  ? "bg-blue-600/20 text-blue-400 font-medium border border-blue-500/30"
                  : "text-slate-400 hover:bg-surface-2 hover:text-slate-200"
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon className={`w-4 h-4 ${isActive ? "text-blue-400" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-amber-500/30 text-amber-300 text-[10px] font-bold">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="p-2 border-t border-border-default text-[11px] text-slate-500 flex items-center justify-between">
        <span>Windows Workstation</span>
        <span className="font-mono text-emerald-400">16 GB RAM</span>
      </div>
    </aside>
  );
}
