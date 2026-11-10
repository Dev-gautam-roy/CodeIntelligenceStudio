"use client";

import React, { useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
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
          position: { x: 50, y: 100 },
          data: { label: "FastAPI Gateway (app/main.py)" },
          style: { background: "#1F2937", color: "#F9FAFB", border: "1px solid #3B82F6", borderRadius: "8px", padding: "10px", fontSize: "12px", width: 220 },
        },
        {
          id: "2",
          position: { x: 350, y: 50 },
          data: { label: "LangGraph Orchestrator" },
          style: { background: "#1F2937", color: "#F9FAFB", border: "1px solid #8B5CF6", borderRadius: "8px", padding: "10px", fontSize: "12px", width: 200 },
        },
        {
          id: "3",
          position: { x: 350, y: 160 },
          data: { label: "RAG & ChromaDB Client" },
          style: { background: "#1F2937", color: "#F9FAFB", border: "1px solid #10B981", borderRadius: "8px", padding: "10px", fontSize: "12px", width: 200 },
        },
        {
          id: "4",
          position: { x: 650, y: 100 },
          data: { label: "Isolated Workspace Files" },
          style: { background: "#1F2937", color: "#F9FAFB", border: "1px solid #F59E0B", borderRadius: "8px", padding: "10px", fontSize: "12px", width: 200 },
        },
      ];
      const initialEdges: Edge[] = [
        { id: "e1-2", source: "1", target: "2", animated: true, style: { stroke: "#3B82F6" } },
        { id: "e1-3", source: "1", target: "3", style: { stroke: "#10B981" } },
        { id: "e2-4", source: "2", target: "4", animated: true, style: { stroke: "#8B5CF6" } },
      ];
      return { nodes: initialNodes, edges: initialEdges };
    }

    // Generate dynamic nodes from real architecture data
    const dynamicNodes: Node[] = [];
    const dynamicEdges: Edge[] = [];

    // Root repository node
    dynamicNodes.push({
      id: "root",
      position: { x: 50, y: 150 },
      data: { label: `Repository Root (${data.languages ? Object.keys(data.languages)[0] : "Code"})` },
      style: { background: "#1E293B", color: "#60A5FA", border: "2px solid #3B82F6", borderRadius: "8px", padding: "12px", fontWeight: "bold" },
    });

    let yOffset = 40;
    const moduleEntries = Object.entries(data.dependencies_graph || {}).slice(0, 10);
    moduleEntries.forEach(([mod, deps], idx) => {
      const nodeId = `mod_${idx}`;
      dynamicNodes.push({
        id: nodeId,
        position: { x: 320, y: yOffset },
        data: { label: mod },
        style: { background: "#1F2937", color: "#E2E8F0", border: "1px solid #475569", borderRadius: "6px", padding: "8px", fontSize: "11px", width: 220 },
      });
      dynamicEdges.push({
        id: `e_root_${nodeId}`,
        source: "root",
        target: nodeId,
        style: { stroke: "#64748B" },
      });
      yOffset += 55;
    });

    return { nodes: dynamicNodes, edges: dynamicEdges };
  }, [data]);

  return (
    <div className="h-[420px] w-full bg-surface-1 border border-border-default rounded-lg overflow-hidden relative">
      <div className="absolute top-3 left-3 z-10 bg-surface-2/80 backdrop-blur px-3 py-1.5 rounded border border-border-default text-xs flex items-center space-x-3">
        <span className="font-semibold text-slate-200">Architecture Dependency Map</span>
        {data && (
          <span className="text-[11px] text-emerald-400 font-mono">
            {data.modules_count} modules mapped
          </span>
        )}
      </div>

      <ReactFlow nodes={nodes} edges={edges} fitView className="bg-root">
        <Background color="#1E293B" gap={16} />
        <Controls className="bg-surface-2 border border-border-default text-white" />
        <MiniMap nodeColor="#3B82F6" className="bg-surface-1 border border-border-default rounded" />
      </ReactFlow>
    </div>
  );
}
