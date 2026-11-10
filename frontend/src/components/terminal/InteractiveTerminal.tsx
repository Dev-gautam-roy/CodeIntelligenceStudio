"use client";

import React, { useState } from "react";
import { Terminal as TerminalIcon, CornerDownLeft, Loader2, ShieldCheck } from "lucide-react";
import { api } from "../../services/api";

interface InteractiveTerminalProps {
  activeRepositoryId?: string;
}

export function InteractiveTerminal({ activeRepositoryId }: InteractiveTerminalProps) {
  const [command, setCommand] = useState("pytest -q");
  const [outputLogs, setOutputLogs] = useState<Array<{ cmd: string; out: string; err: string; code: number }>>([
    {
      cmd: "welcome",
      out: "Code Intelligence Studio Sandboxed Terminal [Active Policy: Normal]\nAllowed binaries: pytest, git, python, npm, cargo, go\nUntrusted execution sandboxed to workspace root.",
      err: "",
      code: 0,
    },
  ]);
  const [isExecuting, setIsExecuting] = useState(false);

  const handleRunCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim() || !activeRepositoryId) return;

    setIsExecuting(true);
    const cmdToRun = command.trim();
    setCommand("");

    try {
      const res = await api.executeTerminalCommand(activeRepositoryId, cmdToRun);
      setOutputLogs((prev) => [
        ...prev,
        {
          cmd: cmdToRun,
          out: res.stdout || (res.exit_code === 0 ? "Command completed with exit code 0." : ""),
          err: res.stderr,
          code: res.exit_code,
        },
      ]);
    } catch (err: any) {
      setOutputLogs((prev) => [
        ...prev,
        {
          cmd: cmdToRun,
          out: "",
          err: err.message || "Failed to execute command in sandbox.",
          code: 1,
        },
      ]);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="bg-surface-1 border border-border-default rounded-lg flex flex-col h-[320px] font-mono text-xs">
      <div className="px-3 py-2 bg-surface-2 border-b border-border-default flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <TerminalIcon className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-semibold text-slate-200">Interactive Sandboxed Terminal</span>
        </div>
        <div className="flex items-center space-x-1.5 text-[10px] text-emerald-400">
          <ShieldCheck className="w-3 h-3" />
          <span>Execution Jail Active</span>
        </div>
      </div>

      <div className="flex-1 p-3 overflow-y-auto space-y-3 bg-root text-slate-300">
        {outputLogs.map((log, i) => (
          <div key={i} className="space-y-1">
            <div className="flex items-center space-x-2 text-slate-400">
              <span className="text-blue-400">$</span>
              <span className="font-semibold text-slate-200">{log.cmd}</span>
              <span
                className={`text-[9px] px-1 rounded ${
                  log.code === 0 ? "text-emerald-400 bg-emerald-500/10" : "text-red-400 bg-red-500/10"
                }`}
              >
                code {log.code}
              </span>
            </div>
            {log.out && <pre className="text-slate-300 whitespace-pre-wrap pl-4">{log.out}</pre>}
            {log.err && <pre className="text-rose-400 whitespace-pre-wrap pl-4">{log.err}</pre>}
          </div>
        ))}
      </div>

      <form onSubmit={handleRunCommand} className="p-2 border-t border-border-default flex items-center space-x-2 bg-surface-1">
        <span className="text-blue-400 pl-2">$</span>
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder={activeRepositoryId ? "Enter sandboxed command (e.g. pytest -q, git status)" : "Select a repository to run commands"}
          disabled={!activeRepositoryId || isExecuting}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={!activeRepositoryId || isExecuting}
          className="p-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40"
        >
          {isExecuting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CornerDownLeft className="w-3.5 h-3.5" />}
        </button>
      </form>
    </div>
  );
}
