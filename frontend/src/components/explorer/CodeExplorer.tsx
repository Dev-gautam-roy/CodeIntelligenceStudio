"use client";

import React, { useState, useEffect } from "react";
import {
  Folder,
  FolderOpen,
  FileCode,
  FileText,
  FileJson,
  ChevronRight,
  ChevronDown,
  Copy,
  Check,
  Code2,
  File,
  Layers,
  Search,
  Loader2,
} from "lucide-react";
import { FileTreeNode, FileContentResponse, Repository } from "../../types";
import { api } from "../../services/api";

interface CodeExplorerProps {
  activeRepo: Repository | null;
  onOpenFile?: (path: string) => void;
  initialPath?: string;
}

function getFileIcon(extension?: string) {
  switch (extension) {
    case ".dart":
      return <FileCode className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />;
    case ".py":
      return <FileCode className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />;
    case ".ts":
    case ".tsx":
      return <FileCode className="w-3.5 h-3.5 text-sky-400 flex-shrink-0" />;
    case ".js":
    case ".jsx":
      return <FileCode className="w-3.5 h-3.5 text-yellow-400 flex-shrink-0" />;
    case ".json":
      return <FileJson className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />;
    case ".yaml":
    case ".yml":
    case ".toml":
      return <Layers className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />;
    case ".md":
      return <FileText className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />;
    default:
      return <File className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />;
  }
}

interface TreeNodeItemProps {
  node: FileTreeNode;
  depth: number;
  selectedPath: string | null;
  onSelect: (path: string) => void;
}

function TreeNodeItem({ node, depth, selectedPath, onSelect }: TreeNodeItemProps) {
  const [isOpen, setIsOpen] = useState(depth === 0);

  if (node.type === "directory") {
    return (
      <div>
        <div
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-1.5 py-1 px-2 rounded hover:bg-surface-2 cursor-pointer text-xs text-slate-300 font-mono transition-colors"
          style={{ paddingLeft: `${depth * 14 + 8}px` }}
        >
          {isOpen ? (
            <ChevronDown className="w-3 h-3 text-slate-500" />
          ) : (
            <ChevronRight className="w-3 h-3 text-slate-500" />
          )}
          {isOpen ? (
            <FolderOpen className="w-3.5 h-3.5 text-blue-400" />
          ) : (
            <Folder className="w-3.5 h-3.5 text-blue-400" />
          )}
          <span className="truncate">{node.name}</span>
        </div>
        {isOpen && node.children && (
          <div>
            {node.children.map((child) => (
              <TreeNodeItem
                key={child.path}
                node={child}
                depth={depth + 1}
                selectedPath={selectedPath}
                onSelect={onSelect}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  const isSelected = selectedPath === node.path;

  return (
    <div
      onClick={() => onSelect(node.path)}
      className={`flex items-center space-x-2 py-1 px-2 rounded cursor-pointer text-xs font-mono transition-colors ${
        isSelected
          ? "bg-blue-600/20 text-blue-300 border border-blue-500/30"
          : "hover:bg-surface-2 text-slate-300"
      }`}
      style={{ paddingLeft: `${depth * 14 + 20}px` }}
    >
      {getFileIcon(node.extension)}
      <span className="truncate">{node.name}</span>
    </div>
  );
}

export function CodeExplorer({ activeRepo, initialPath }: CodeExplorerProps) {
  const [tree, setTree] = useState<FileTreeNode[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | null>(initialPath || null);
  const [fileContent, setFileContent] = useState<FileContentResponse | null>(null);
  const [isLoadingTree, setIsLoadingTree] = useState(false);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [copied, setCopied] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");

  // Load Tree when repository changes
  useEffect(() => {
    if (!activeRepo) return;
    setIsLoadingTree(true);
    api
      .getFileTree(activeRepo.id)
      .then((data) => {
        setTree(data);
        // Find default file (e.g. main.dart, app.py, README.md, or first file)
        if (!selectedPath && data.length > 0) {
          const findFirstFile = (nodes: FileTreeNode[]): string | null => {
            for (const n of nodes) {
              if (n.type === "file") return n.path;
              if (n.children) {
                const found = findFirstFile(n.children);
                if (found) return found;
              }
            }
            return null;
          };
          const defaultFile = findFirstFile(data);
          if (defaultFile) setSelectedPath(defaultFile);
        }
      })
      .catch((err) => console.error("Error loading file tree:", err))
      .finally(() => setIsLoadingTree(false));
  }, [activeRepo?.id]);

  // Load Content when selectedPath changes
  useEffect(() => {
    if (!activeRepo || !selectedPath) return;
    setIsLoadingContent(true);
    api
      .getFileContent(activeRepo.id, selectedPath)
      .then(setFileContent)
      .catch((err) => console.error("Error loading file content:", err))
      .finally(() => setIsLoadingContent(false));
  }, [activeRepo?.id, selectedPath]);

  const handleCopy = () => {
    if (!fileContent) return;
    navigator.clipboard.writeText(fileContent.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Filter tree flattened for search if searchFilter exists
  const filterNodes = (nodes: FileTreeNode[], term: string): FileTreeNode[] => {
    if (!term) return nodes;
    const lower = term.toLowerCase();
    const result: FileTreeNode[] = [];
    for (const n of nodes) {
      if (n.type === "file" && n.name.toLowerCase().includes(lower)) {
        result.push(n);
      } else if (n.children) {
        const filteredChildren = filterNodes(n.children, term);
        if (filteredChildren.length > 0) {
          result.push({ ...n, children: filteredChildren });
        }
      }
    }
    return result;
  };

  const displayedTree = filterNodes(tree, searchFilter);

  return (
    <div className="flex h-[620px] bg-surface-1 border border-border-default rounded-lg overflow-hidden shadow-xl">
      {/* Left Sidebar: File Tree Navigation */}
      <div className="w-72 bg-surface-2 border-r border-border-default flex flex-col flex-shrink-0">
        <div className="p-3 border-b border-border-default space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5 uppercase tracking-wider">
              <Code2 className="w-3.5 h-3.5 text-blue-400" />
              Repository Files
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              {activeRepo ? `${activeRepo.owner}/${activeRepo.name}` : "No Repo"}
            </span>
          </div>

          {/* Search File Filter */}
          <div className="relative">
            <Search className="w-3 h-3 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search files (e.g. main.dart)..."
              className="w-full bg-root border border-border-default rounded pl-7 pr-2 py-1 text-[11px] font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-border-focus"
            />
          </div>
        </div>

        {/* Tree Item List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {isLoadingTree ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500 text-xs gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              <span>Scanning workspace tree...</span>
            </div>
          ) : displayedTree.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500">
              No files found matching filter.
            </div>
          ) : (
            displayedTree.map((node) => (
              <TreeNodeItem
                key={node.path}
                node={node}
                depth={0}
                selectedPath={selectedPath}
                onSelect={(path) => setSelectedPath(path)}
              />
            ))
          )}
        </div>
      </div>

      {/* Right Column: Source Code Viewer */}
      <div className="flex-1 flex flex-col bg-root overflow-hidden">
        {/* File Header Bar */}
        <div className="h-10 bg-surface-1 border-b border-border-default px-4 flex items-center justify-between">
          <div className="flex items-center space-x-2 truncate">
            {fileContent && getFileIcon(PathExt(fileContent.path))}
            <span className="font-mono text-xs text-slate-200 font-semibold truncate">
              {fileContent ? fileContent.path : "Select a file to inspect"}
            </span>
            {fileContent && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                {fileContent.language}
              </span>
            )}
          </div>

          {fileContent && (
            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
              <span>{fileContent.lines_count} lines</span>
              <span>{(fileContent.size_bytes / 1024).toFixed(1)} KB</span>
              <button
                onClick={handleCopy}
                className="flex items-center space-x-1 px-2 py-1 rounded bg-surface-2 hover:bg-surface-3 text-slate-300 transition-colors"
                title="Copy code to clipboard"
              >
                {copied ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400 text-[10px]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span className="text-[10px]">Copy</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Code Content with Line Numbers */}
        <div className="flex-1 overflow-auto p-4 font-mono text-xs leading-relaxed">
          {isLoadingContent ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-2">
              <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
              <span>Loading file contents...</span>
            </div>
          ) : !fileContent ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Code2 className="w-12 h-12 text-slate-600 mb-2" />
              <span>Select any file from the explorer on the left to preview code.</span>
            </div>
          ) : (
            <div className="flex">
              {/* Line Numbers */}
              <div className="select-none text-right pr-4 text-slate-600 font-mono text-[11px] border-r border-border-default/50 space-y-0.5">
                {fileContent.content.split("\n").map((_, i) => (
                  <div key={i}>{i + 1}</div>
                ))}
              </div>

              {/* Source Code */}
              <pre className="pl-4 text-slate-200 overflow-x-auto flex-1 font-mono text-[11px] space-y-0.5">
                {fileContent.content.split("\n").map((line, i) => (
                  <div key={i} className="hover:bg-surface-2/40 px-1 rounded transition-colors whitespace-pre">
                    {line || " "}
                  </div>
                ))}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PathExt(path: string): string {
  const parts = path.split(".");
  return parts.length > 1 ? `.${parts[parts.length - 1]}` : "";
}
