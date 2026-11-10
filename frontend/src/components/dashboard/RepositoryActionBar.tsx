"use client";

import React, { useState } from "react";
import { Play, Loader2, GitPullRequest, ShieldCheck, CheckCircle2, AlertCircle, FolderGit2 } from "lucide-react";
import { api } from "../../services/api";
import { Repository } from "../../types";

interface RepositoryActionBarProps {
  onActionComplete: (repo?: Repository) => void;
  onSetStatus: (status: string) => void;
  repositories: Repository[];
  activeRepo: Repository | null;
  onSelectRepo: (repo: Repository) => void;
}

export function RepositoryActionBar({
  onActionComplete,
  onSetStatus,
  repositories,
  activeRepo,
  onSelectRepo,
}: RepositoryActionBarProps) {
  const [repoUrl, setRepoUrl] = useState(activeRepo?.url || "https://github.com/we45/Vulnerable-Flask-App");
  const [selectedAction, setSelectedAction] = useState("Security Audit");
  const [isLoading, setIsLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);

  const actions = [
    "Security Audit",
    "Analyse",
    "Clone",
    "Fork",
    "Test",
    "Debug",
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
      let targetRepo: Repository | null = null;
      if (selectedAction === "Clone") {
        targetRepo = await api.cloneRepository(repoUrl);
        setResultMessage(`Successfully cloned into workspace: ${targetRepo.clone_path}`);
      } else if (selectedAction === "Fork") {
        const fork = await api.forkRepository(repoUrl);
        setResultMessage(fork.message);
      } else if (selectedAction === "Analyse") {
        targetRepo = await api.cloneRepository(repoUrl);
        const arch = await api.getArchitecture(targetRepo.id);
        setResultMessage(`Analysis Complete: ${arch.summary}`);
      } else if (selectedAction === "Security Audit") {
        targetRepo = await api.cloneRepository(repoUrl);
        const sec = await api.getSecurityAudit(targetRepo.id);
        setResultMessage(`Security Audit: ${sec.findings_count} flaws detected in ${targetRepo.name}!`);
      } else {
        targetRepo = await api.cloneRepository(repoUrl);
        const wf = await api.createWorkflow(targetRepo.project_id, `Manual ${selectedAction}`, repoUrl);
        setResultMessage(`Workflow #${wf.id.slice(0, 8)} started in background (Status: ${wf.status}).`);
      }

      if (targetRepo) {
        onSelectRepo(targetRepo);
        onActionComplete(targetRepo);
      } else {
        onActionComplete();
      }
    } catch (err: any) {
      setIsError(true);
      setResultMessage(err.message || "Failed to execute selected repository action.");
    } finally {
      setIsLoading(false);
      onSetStatus("Ready");
    }
  };

  const handleSelectExisting = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = e.target.value;
    const found = repositories.find((r) => r.id === selectedId);
    if (found) {
      setRepoUrl(found.url);
      onSelectRepo(found);
    }
  };

  return (
    <div className="bg-surface-1 p-4 rounded-lg border border-border-default space-y-3">
      <div className="flex flex-col md:flex-row items-center gap-3">
        {/* Existing Repositories Selector */}
        {repositories.length > 0 && (
          <div className="flex items-center space-x-1.5 w-full md:w-auto">
            <FolderGit2 className="w-4 h-4 text-blue-400 flex-shrink-0" />
            <select
              value={activeRepo?.id || ""}
              onChange={handleSelectExisting}
              className="bg-surface-2 border border-border-default rounded px-2.5 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-border-focus max-w-[200px] truncate"
              title="Select previously cloned repository"
            >
              {repositories.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.owner}/{r.name}
                </option>
              ))}
            </select>
          </div>
        )}

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
          className="w-full md:w-auto flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs px-5 py-2 rounded transition-all shadow-md shadow-blue-600/20 disabled:opacity-50 flex-shrink-0"
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
