"use client";

import React, { useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  Position,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Network, Layers, GitFork, FileCode, CheckCircle2 } from "lucide-react";
import { ArchitectureAnalysis } from "../../types";

interface ArchitectureGraphProps {
  data: ArchitectureAnalysis | null;
}

export function ArchitectureGraph({ data }: ArchitectureGraphProps) {
  const { nodes, edges } = useMemo(() => {
    if (!data) {
      // Default placeholder nodes
      const initialNodes: Node[] = [
        {
          id: "1",
          position: { x: 40, y: 130 },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          data: {
            label: (
              <div className="font-mono text-left">
                <div className="text-[11px] font-bold text-blue-300">FastAPI Gateway</div>
                <div className="text-[9px] text-slate-400">backend/app/main.py</div>
              </div>
            ),
          },
          style: {
            background: "#0F172A",
            border: "1.5px solid #3B82F6",
            borderRadius: "8px",
            padding: "10px",
            width: 190,
            boxShadow: "0 0 15px rgba(59, 130, 246, 0.2)",
          },
        },
        {
          id: "2",
          position: { x: 300, y: 50 },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          data: {
            label: (
              <div className="font-mono text-left">
                <div className="text-[11px] font-bold text-purple-300">LangGraph Pipeline</div>
                <div className="text-[9px] text-slate-400">orchestration/graph.py</div>
              </div>
            ),
          },
          style: {
            background: "#0F172A",
            border: "1.5px solid #8B5CF6",
            borderRadius: "8px",
            padding: "10px",
            width: 190,
          },
        },
        {
          id: "3",
          position: { x: 300, y: 140 },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          data: {
            label: (
              <div className="font-mono text-left">
                <div className="text-[11px] font-bold text-emerald-300">ChromaDB Vector Store</div>
                <div className="text-[9px] text-slate-400">services/rag_service.py</div>
              </div>
            ),
          },
          style: {
            background: "#0F172A",
            border: "1.5px solid #10B981",
            borderRadius: "8px",
            padding: "10px",
            width: 190,
          },
        },
        {
          id: "4",
          position: { x: 300, y: 230 },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          data: {
            label: (
              <div className="font-mono text-left">
                <div className="text-[11px] font-bold text-amber-300">Sandbox Test Runner</div>
                <div className="text-[9px] text-slate-400">services/sandbox_service.py</div>
              </div>
            ),
          },
          style: {
            background: "#0F172A",
            border: "1.5px solid #F59E0B",
            borderRadius: "8px",
            padding: "10px",
            width: 190,
          },
        },
      ];

      const initialEdges: Edge[] = [
        {
          id: "e1-2",
          source: "1",
          target: "2",
          type: "smoothstep",
          animated: true,
          style: { stroke: "#3B82F6", strokeWidth: 1.5 },
          markerEnd: { type: MarkerType.ArrowClosed, color: "#3B82F6" },
        },
        {
          id: "e1-3",
          source: "1",
          target: "3",
          type: "smoothstep",
          style: { stroke: "#10B981", strokeWidth: 1.5 },
          markerEnd: { type: MarkerType.ArrowClosed, color: "#10B981" },
        },
        {
          id: "e1-4",
          source: "1",
          target: "4",
          type: "smoothstep",
          style: { stroke: "#F59E0B", strokeWidth: 1.5 },
          markerEnd: { type: MarkerType.ArrowClosed, color: "#F59E0B" },
        },
      ];
      return { nodes: initialNodes, edges: initialEdges };
    }

    // Dynamic Nodes & Edges from real architecture analysis
    const dynamicNodes: Node[] = [];
    const dynamicEdges: Edge[] = [];

    // Identify primary language / framework properly
    let primaryStack = "Codebase";
    if (data.frameworks && data.frameworks.length > 0) {
      primaryStack = data.frameworks.join(" / ");
    } else if (data.languages && Object.keys(data.languages).length > 0) {
      const topLang = Object.entries(data.languages).sort((a, b) => b[1] - a[1])[0];
      primaryStack = topLang ? topLang[0] : "Codebase";
    }

    // 1. Root Architecture Node (Left)
    dynamicNodes.push({
      id: "root",
      position: { x: 30, y: 140 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div className="font-mono text-left">
            <div className="text-[10px] text-blue-400 font-bold tracking-wider uppercase flex items-center gap-1">
              <Layers className="w-3 h-3" />
              Repository Root
            </div>
            <div className="text-xs font-bold text-white mt-0.5">{primaryStack}</div>
            <div className="text-[9px] text-slate-400 mt-1 flex items-center gap-1">
              <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
              <span>{data.modules_count} modules mapped</span>
            </div>
          </div>
        ),
      },
      style: {
        background: "#0F172A",
        border: "2px solid #3B82F6",
        borderRadius: "10px",
        padding: "12px",
        width: 200,
        boxShadow: "0 0 20px rgba(59, 130, 246, 0.25)",
      },
    });

    // 2. Child Module Nodes (Column on Right)
    const moduleEntries = Object.entries(data.dependencies_graph || {}).slice(0, 10);
    const startY = Math.max(20, 150 - (moduleEntries.length * 52) / 2);

    moduleEntries.forEach(([mod, deps], idx) => {
      const nodeId = `mod_${idx}`;
      const isEntry = data.entry_points && data.entry_points.includes(mod);

      dynamicNodes.push({
        id: nodeId,
        position: { x: 300, y: startY + idx * 56 },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        data: {
          label: (
            <div className="font-mono text-left flex items-center justify-between">
              <div className="truncate max-w-[180px]">
                <div className={`text-[11px] font-semibold truncate ${isEntry ? "text-cyan-300" : "text-slate-200"}`}>
                  {mod}
                </div>
                <div className="text-[9px] text-slate-400">
                  {deps.length > 0 ? `${deps.length} imports` : "Leaf Module"}
                </div>
              </div>
              {isEntry && (
                <span className="text-[8px] px-1 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold ml-1">
                  ENTRY
                </span>
              )}
            </div>
          ),
        },
        style: {
          background: "#0F172A",
          border: isEntry ? "1.5px solid #06B6D4" : "1px solid #334155",
          borderRadius: "8px",
          padding: "8px 10px",
          width: 240,
          boxShadow: isEntry ? "0 0 10px rgba(6, 182, 212, 0.2)" : "none",
        },
      });

      // Smooth right-to-left connecting edges
      dynamicEdges.push({
        id: `e_root_${nodeId}`,
        source: "root",
        target: nodeId,
        type: "smoothstep",
        animated: isEntry,
        style: {
          stroke: isEntry ? "#06B6D4" : "#475569",
          strokeWidth: isEntry ? 2 : 1.2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isEntry ? "#06B6D4" : "#475569",
        },
      });
    });

    return { nodes: dynamicNodes, edges: dynamicEdges };
  }, [data]);

  return (
    <div className="h-[420px] w-full bg-surface-1 border border-border-default rounded-lg overflow-hidden relative flex flex-col shadow-lg">
      {/* Header bar */}
      <div className="bg-surface-2/90 border-b border-border-default px-4 py-2 flex items-center justify-between z-10 backdrop-blur">
        <div className="flex items-center space-x-2">
          <Network className="w-4 h-4 text-blue-400" />
          <span className="font-semibold text-xs text-slate-200">Architecture Dependency Map</span>
          {data && (
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-mono">
              {data.modules_count} modules &bull; {data.circular_dependencies.length} cycles
            </span>
          )}
        </div>
      </div>

      {/* React Flow Canvas */}
      <div className="flex-1 w-full relative">
        <ReactFlow nodes={nodes} edges={edges} fitView className="bg-root">
          <Background color="#1E293B" gap={16} />
          <Controls showInteractive={false} className="bg-surface-1 border border-border-default text-white" />
        </ReactFlow>
      </div>
    </div>
  );
}
