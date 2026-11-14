"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  MessageSquare,
  Send,
  Loader2,
  Bot,
  User,
  Sparkles,
  FileCode,
  Check,
  Copy,
  ExternalLink,
  Cpu,
  Trash2,
} from "lucide-react";
import { Repository, ChatMessage, CodeReference } from "../../types";
import { api } from "../../services/api";

interface CodebaseChatProps {
  activeRepo: Repository | null;
  onNavigateToFile?: (path: string) => void;
}

export function CodebaseChat({ activeRepo, onNavigateToFile }: CodebaseChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "assistant",
      text: activeRepo
        ? `Hello! I have indexed the codebase for **${activeRepo.name}**. You can ask me anything about the architecture, functions, entry points, or vulnerabilities.`
        : "Hello! Select or clone a repository to start conversing with its codebase.",
      model: "Local ChromaDB RAG Engine",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const starterQuestions = [
    "Where is the main entry point and setup?",
    "Explain the architecture and dependencies",
    "Are there any security vulnerabilities or leaked secrets?",
    "How does the core calculation or routing logic work?",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (questionText?: string) => {
    const textToSend = questionText || input.trim();
    if (!textToSend || !activeRepo || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!questionText) setInput("");
    setIsLoading(true);

    try {
      const resp = await api.chatWithCodebase(activeRepo.id, textToSend, messages.map(m => ({ role: m.sender, content: m.text })));
      const assistantMsg: ChatMessage = {
        id: `assistant_${Date.now()}`,
        sender: "assistant",
        text: resp.reply,
        references: resp.references,
        model: resp.model_used,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: "assistant",
        text: `Error querying codebase: ${err.message || "Failed to retrieve response."}`,
        model: "Error",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clearChat = () => {
    setMessages([
      {
        id: "reset",
        sender: "assistant",
        text: `Chat cleared for **${activeRepo?.name || "codebase"}**. What would you like to explore next?`,
        model: "Local ChromaDB RAG Engine",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  return (
    <div className="flex flex-col h-[620px] bg-surface-1 border border-border-default rounded-lg overflow-hidden shadow-xl">
      {/* Chat Header Bar */}
      <div className="h-12 bg-surface-2 border-b border-border-default px-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-purple-400" />
          <span className="text-xs font-semibold text-slate-200">
            Converse with Codebase
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 font-mono">
            {activeRepo ? `${activeRepo.owner}/${activeRepo.name}` : "No Repo Selected"}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={clearChat}
            className="text-xs text-slate-400 hover:text-slate-200 p-1.5 rounded hover:bg-surface-3 transition-colors"
            title="Clear Chat History"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Message List Pane */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-xs">
        {messages.map((m) => {
          const isUser = m.sender === "user";
          return (
            <div
              key={m.id}
              className={`flex items-start space-x-3 ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}
            >
              {/* Avatar */}
              <div
                className={`w-7 h-7 rounded flex items-center justify-center flex-shrink-0 text-white ${
                  isUser ? "bg-blue-600" : "bg-purple-600"
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div className={`max-w-[85%] space-y-2`}>
                <div
                  className={`p-3.5 rounded-lg border ${
                    isUser
                      ? "bg-blue-600/10 border-blue-500/30 text-blue-100"
                      : "bg-surface-2 border-border-default text-slate-200"
                  }`}
                >
                  {/* Sender meta */}
                  <div className="flex items-center justify-between gap-4 mb-1.5 text-[10px] text-slate-400 font-mono">
                    <span className="font-semibold text-slate-300">
                      {isUser ? "You" : "Code Intelligence Assistant"}
                    </span>
                    <span>{m.timestamp}</span>
                  </div>

                  {/* Message body */}
                  <div className="whitespace-pre-wrap leading-relaxed space-y-2">
                    {m.text}
                  </div>

                  {/* Code references if assistant provided them */}
                  {m.references && m.references.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-border-default/60 space-y-1.5">
                      <div className="text-[10px] font-mono text-purple-300 font-semibold flex items-center gap-1">
                        <FileCode className="w-3 h-3" />
                        <span>Referenced Code Chunks ({m.references.length}):</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {m.references.map((ref, idx) => (
                          <button
                            key={idx}
                            onClick={() => onNavigateToFile && onNavigateToFile(ref.file_path)}
                            className="text-[10px] px-2 py-0.5 rounded bg-root border border-border-default hover:border-purple-500/50 text-slate-300 hover:text-white font-mono flex items-center gap-1 transition-colors"
                            title="Click to view file in Code Explorer"
                          >
                            <span>{ref.file_path}:{ref.start_line}</span>
                            <ExternalLink className="w-2.5 h-2.5 text-purple-400" />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer model tag & copy button */}
                {!isUser && (
                  <div className="flex items-center justify-between px-1 text-[10px] text-slate-500 font-mono">
                    <span className="flex items-center gap-1">
                      <Cpu className="w-3 h-3 text-purple-400" />
                      {m.model || "Local ChromaDB"}
                    </span>
                    <button
                      onClick={() => handleCopy(m.text, m.id)}
                      className="hover:text-slate-300 flex items-center gap-1"
                    >
                      {copiedId === m.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center space-x-3">
            <div className="w-7 h-7 rounded bg-purple-600 flex items-center justify-center flex-shrink-0 text-white">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-surface-2 border border-border-default p-3 rounded-lg flex items-center space-x-2 text-xs text-purple-300 font-mono">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing repository embeddings & AST context...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Starter Question Pills */}
      <div className="px-4 py-2 bg-surface-2/60 border-t border-border-default/60 flex items-center gap-2 overflow-x-auto select-none">
        <Sparkles className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
        <span className="text-[10px] text-slate-400 font-mono flex-shrink-0">Suggested:</span>
        {starterQuestions.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSend(q)}
            disabled={isLoading || !activeRepo}
            className="text-[10px] px-2.5 py-1 rounded-full bg-surface-2 hover:bg-surface-3 border border-border-default hover:border-purple-500/50 text-slate-300 whitespace-nowrap transition-colors disabled:opacity-50 font-mono"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="p-3 bg-surface-2 border-t border-border-default">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading || !activeRepo}
            placeholder={
              activeRepo
                ? `Ask anything about ${activeRepo.name} (e.g., 'How does the calculator logic work?')...`
                : "Select an active repository to enable chat..."
            }
            className="flex-1 bg-root border border-border-default rounded px-3 py-2 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || !activeRepo}
            className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded text-xs font-medium flex items-center space-x-1.5 transition-all shadow-md shadow-purple-600/20 disabled:opacity-50 flex-shrink-0"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Send</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
