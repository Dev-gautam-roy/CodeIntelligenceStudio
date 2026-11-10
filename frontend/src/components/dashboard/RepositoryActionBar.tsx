"use client";

import React, { useState } from "react";
import { Play, Loader2, GitPullRequest, ShieldCheck, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "../../services/api";

interface RepositoryActionBarProps {
  onActionComplete: () => void;
  onSetStatus: (status: string) => void;
}

export function RepositoryActionBar({ onActionComplete, onSetStatus }: RepositoryActionBarProps) {
  const [repoUrl, setRepoUrl] = useState("https://github.com/fastapi/fastapi");
  const [selectedAction, setSelectedAction] = useState("Analyse");
  const [isLoading, setIsLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);

  const actions = [
    "Analyse",
    "Clone",
    "Fork",
    "Test",
    "Debug",
    "Security Audit",
    "Prepare Contribution",
    "Deploy",
  ];

  const handleExecute = async () => {
    if (!repoUrl.trim()) return;
    setIsLoading(true);
    setIsError(false);
    setResultMessage(null);
    onSetStatus(`Executing ${selectedAction} on ${repoUrl}...`);

    try {
      if (selectedAction === "Clone") {
        const repo = await api.cloneRepository(repoUrl);
        setResultMessage(`Successfully cloned into workspace: ${repo.clone_path}`);
      } else if (selectedAction === "Fork") {
        const fork = await api.forkRepository(repoUrl);
        setResultMessage(fork.message);
      } else if (selectedAction === "Analyse") {
        // Validate & Clone if needed, then run architecture analysis
        const repo = await api.cloneRepository(repoUrl);
        const arch = await api.getArchitecture(repo.id);
        setResultMessage(`Analysis Complete: ${arch.summary}`);
      } else if (selectedAction === "Security Audit") {
        const repo = await api.cloneRepository(repoUrl);
        const sec = await api.getSecurityAudit(repo.id);
        setResultMessage(`Security Audit: ${sec.findings_count} findings discovered.`);
      } else {
        // Generic agent trigger via workflow
        const repo = await api.cloneRepository(repoUrl);
        const wf = await api.createWorkflow(repo.project_id, `Manual ${selectedAction}`, repoUrl);
        setResultMessage(`Workflow #${wf.id.slice(0, 8)} started in background (Status: ${wf.status}).`);
      }
      onActionComplete();
    } catch (err: any) {
      setIsError(true);
      setResultMessage(err.message || "Failed to execute selected repository action.");
    } finally {
      setIsLoading(false);
      onSetStatus("Ready");
    }
  };

  return (
    <div className="bg-surface-1 p-4 rounded-lg border border-border-default space-y-3">
      <div className="flex flex-col md:flex-row items-center gap-3">
        {/* Repo URL Input */}
        <div className="relative flex-1 w-full">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="Paste GitHub repository URL (e.g. https://github.com/owner/repo)"
            className="w-full bg-surface-2 border border-border-default rounded px-3 py-2 text-xs font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:border-border-focus"
          />
        </div>

        {/* Action Dropdown */}
        <select
          value={selectedAction}
          onChange={(e) => setSelectedAction(e.target.value)}
          className="bg-surface-2 border border-border-default rounded px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-border-focus"
        >
          {actions.map((act) => (
            <option key={act} value={act}>
              {act}
            </option>
          ))}
        </select>

        {/* Unified Execute Action Button */}
        <button
          onClick={handleExecute}
          disabled={isLoading}
          className="w-full md:w-auto flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs px-5 py-2 rounded transition-all shadow-md shadow-blue-600/20 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Executing...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Execute Repository Action</span>
            </>
          )}
        </button>
      </div>

      {/* Result / Notification Banner */}
      {resultMessage && (
        <div
          className={`flex items-start space-x-2 p-2.5 rounded text-xs border ${
            isError
              ? "bg-red-500/10 border-red-500/30 text-red-300"
              : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
          }`}
        >
          {isError ? (
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          ) : (
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
          )}
          <span className="font-mono">{resultMessage}</span>
        </div>
      )}
    </div>
  );
}
