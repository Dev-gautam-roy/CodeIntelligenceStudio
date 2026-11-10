"use client";

import React from "react";
import { AlertTriangle, Check, X, Shield, GitPullRequest } from "lucide-react";
import { Approval } from "../../types";

interface ApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  approvals: Approval[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function ApprovalModal({
  isOpen,
  onClose,
  approvals,
  onApprove,
  onReject,
}: ApprovalModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-surface-1 border border-border-default rounded-lg max-w-2xl w-full p-5 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-border-default pb-3">
          <div className="flex items-center space-x-2 text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            <h2 className="font-semibold text-sm text-white">
              Human-in-the-Loop Approval Center ({approvals.length})
            </h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        {approvals.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">
            No pending approvals. All autonomous pipelines are running or complete.
          </div>
        ) : (
          <div className="space-y-4 max-h-[60vh] overflow-y-auto">
            {approvals.map((app) => (
              <div
                key={app.id}
                className="bg-surface-2 border border-border-default rounded p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono text-[10px] font-bold">
                      {app.action_type}
                    </span>
                    <span className="text-xs text-slate-300 font-mono truncate max-w-md">
                      {app.target_resource}
                    </span>
                  </div>
                  <span className="text-[10px] text-amber-400 font-mono font-bold">
                    PENDING SIGN-OFF
                  </span>
                </div>

                {app.diff_payload && (
                  <div className="bg-root p-3 rounded border border-border-default font-mono text-[11px] text-slate-300 max-h-48 overflow-y-auto whitespace-pre-wrap">
                    {app.diff_payload}
                  </div>
                )}

                <div className="flex items-center justify-end space-x-2 pt-2 border-t border-border-default">
                  <button
                    onClick={() => onReject(app.id)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/30 text-xs font-medium"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                  <button
                    onClick={() => onApprove(app.id)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-md shadow-emerald-600/20"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Approve & Publish</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
