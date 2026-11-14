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
  FolderGit2,
  MessageSquareCode,
} from "lucide-react";

export type NavTab =
  | "overview"
  | "chat"
  | "explorer"
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
    { id: "chat", label: "Codebase Chat", icon: MessageSquareCode },
    { id: "explorer", label: "Code Explorer", icon: FolderGit2 },
    { id: "repositories", label: "Repositories", icon: GitBranch },
    { id: "architecture", label: "Architecture", icon: Network },
    { id: "workflows", label: "Workflows (DAG)", icon: WorkflowIcon },
    { id: "agents", label: "Agent Rail", icon: Cpu },
    { id: "security", label: "Security & Threat", icon: ShieldAlert },
    { id: "terminal", label: "Terminal Console", icon: TerminalIcon },
    { id: "approvals", label: "Approvals Gate", icon: CheckSquare, badge: approvalsCount },
  ];

  return (
    <aside className="w-56 bg-surface-1 border-r border-border-default flex flex-col justify-between p-3 select-none flex-shrink-0">
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
              className={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${
                isActive
                  ? "bg-blue-600/15 text-blue-400 font-semibold border border-blue-500/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-surface-2"
              }`}
            >
              <div className="flex items-center space-x-2.5 truncate">
                <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-blue-400" : "text-slate-400"}`} />
                <span className="truncate">{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="p-3 bg-surface-2 rounded-lg border border-border-default space-y-1">
        <div className="flex items-center space-x-1.5 text-[11px] font-medium text-slate-300">
          <BookOpen className="w-3.5 h-3.5 text-blue-400" />
          <span>Documentation</span>
        </div>
        <p className="text-[10px] text-slate-500">
          Autonomous AI Engineering Platform v0.1.0 with LangGraph orchestration.
        </p>
      </div>
    </aside>
  );
}
