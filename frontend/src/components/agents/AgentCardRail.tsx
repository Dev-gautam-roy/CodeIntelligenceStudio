"use client";

import React from "react";
import { Cpu, Clock, Coins, CheckCircle, AlertTriangle, Play } from "lucide-react";
import { AgentInfo, Task } from "../../types";

interface AgentCardRailProps {
  agents: AgentInfo[];
  tasks: Task[];
}

export function AgentCardRail({ agents, tasks }: AgentCardRailProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Cpu className="w-3.5 h-3.5 text-blue-400" />
          Specialized Agent Rail ({agents.length})
        </h3>
        <span className="text-[11px] text-slate-500 font-mono">Parallel Concurrency: 4</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {agents.map((agent) => {
          const matchedTask = tasks.find((t) => t.agent_name === agent.name);
          const isRunning = matchedTask?.status === "RUNNING";
          const isDone = matchedTask?.status === "COMPLETED";
          const isWaiting = matchedTask?.status === "WAITING_FOR_APPROVAL";

          return (
            <div
              key={agent.name}
              className={`bg-surface-1 border rounded-lg p-3 transition-all ${
                isRunning
                  ? "border-blue-500 shadow-md shadow-blue-500/10"
                  : isWaiting
                  ? "border-amber-500"
                  : "border-border-default"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-white truncate">{agent.name}</span>
                <span
                  className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold ${
                    isRunning
                      ? "bg-blue-500/20 text-blue-300 animate-pulse"
                      : isDone
                      ? "bg-emerald-500/20 text-emerald-300"
                      : isWaiting
                      ? "bg-amber-500/20 text-amber-300"
                      : "bg-surface-2 text-slate-400"
                  }`}
                >
                  {matchedTask?.status || "IDLE"}
                </span>
              </div>

              <p className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                {agent.role}
              </p>

              <div className="mt-3 pt-2 border-t border-border-default flex items-center justify-between text-[10px] font-mono text-slate-400">
                <div className="flex items-center space-x-1">
                  <Coins className="w-3 h-3 text-cyan-400" />
                  <span>{matchedTask ? `${matchedTask.token_usage}t` : "0t"}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <span>{matchedTask ? `${matchedTask.execution_time_ms}ms` : "0ms"}</span>
                </div>
              </div>

              {matchedTask?.output_payload?.summary && (
                <div className="mt-2 text-[10px] text-slate-300 bg-surface-2 p-1.5 rounded truncate">
                  {matchedTask.output_payload.summary}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
