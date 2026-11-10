"use client";

import React from "react";
import { Terminal, Shield, CheckCircle, AlertTriangle, GitFork } from "lucide-react";

interface HeaderProps {
  activeRepoUrl?: string;
  pendingApprovalsCount: number;
  onOpenApprovals: () => void;
  isBackendConnected: boolean;
}

export function Header({
  activeRepoUrl,
  pendingApprovalsCount,
  onOpenApprovals,
  isBackendConnected,
}: HeaderProps) {
  return (
    <header className="h-14 border-b border-border-default bg-surface-1 px-4 flex items-center justify-between z-20">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
          CI
        </div>
        <div>
          <h1 className="font-semibold text-sm tracking-wide text-white flex items-center gap-2">
            Code Intelligence Studio
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
              v0.1.0
            </span>
          </h1>
          <p className="text-[11px] text-slate-400">Autonomous AI Engineering Platform</p>
        </div>
      </div>

      <div className="flex items-center space-x-4 text-xs">
        {/* Active Repository */}
        <div className="hidden md:flex items-center space-x-2 bg-surface-2 px-3 py-1 rounded border border-border-default">
          <GitFork className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-300 font-mono">
            {activeRepoUrl || "No Active Repository"}
          </span>
        </div>

        {/* Backend Connectivity Status */}
        <div className="flex items-center space-x-1.5 bg-surface-2 px-2.5 py-1 rounded border border-border-default">
          <span
            className={`w-2 h-2 rounded-full ${
              isBackendConnected ? "bg-emerald-500" : "bg-red-500 animate-pulse"
            }`}
          />
          <span className="text-slate-300 font-mono text-[11px]">
            {isBackendConnected ? "Backend Online" : "Backend Offline"}
          </span>
        </div>

        {/* Approvals Gate Pill */}
        <button
          onClick={onOpenApprovals}
          className={`flex items-center space-x-1.5 px-3 py-1 rounded border transition-all ${
            pendingApprovalsCount > 0
              ? "bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse"
              : "bg-surface-2 text-slate-400 border-border-default hover:text-white"
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Approvals ({pendingApprovalsCount})</span>
        </button>
      </div>
    </header>
  );
}
