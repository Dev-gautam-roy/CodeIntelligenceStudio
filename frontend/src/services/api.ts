import {
  Repository,
  ArchitectureAnalysis,
  SecurityAnalysis,
  AgentInfo,
  Workflow,
  Task,
  Approval,
  FileTreeNode,
  FileContentResponse,
  ChatResponse,
} from "../types";

const API_BASE = "/api/v1";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`API Error ${res.status}: ${errorBody}`);
  }
  return res.json();
}

export const api = {
  // Health
  checkHealth: () => fetchJSON<{ status: string; service: string }>("/health"),

  // GitHub
  validateGitHubUrl: (url: string) =>
    fetchJSON<{ valid: boolean; owner: string; repo: string; default_branch: string; is_private: boolean; message: string }>(
      `${API_BASE}/github/validate`,
      { method: "POST", body: JSON.stringify({ url }) }
    ),

  forkRepository: (url: string) =>
    fetchJSON<{ forked: boolean; fork_url: string; message: string }>(
      `${API_BASE}/github/fork`,
      { method: "POST", body: JSON.stringify({ url }) }
    ),

  // Repositories
  cloneRepository: (url: string, project_id?: string) =>
    fetchJSON<Repository>(`${API_BASE}/repositories/clone`, {
      method: "POST",
      body: JSON.stringify({ url, project_id }),
    }),

  listRepositories: () => fetchJSON<Repository[]>(`${API_BASE}/repositories`),

  indexRepository: (id: string) =>
    fetchJSON<{ repository_id: string; files_indexed: number; chunks_created: number; status: string }>(
      `${API_BASE}/repositories/${id}/index`,
      { method: "POST" }
    ),

  // Analysis
  getArchitecture: (repository_id: string) =>
    fetchJSON<ArchitectureAnalysis>(`${API_BASE}/analysis/architecture`, {
      method: "POST",
      body: JSON.stringify({ repository_id }),
    }),

  getSecurityAudit: (repository_id: string) =>
    fetchJSON<SecurityAnalysis>(`${API_BASE}/analysis/security`, {
      method: "POST",
      body: JSON.stringify({ repository_id }),
    }),

  // Agents
  listAgents: () => fetchJSON<AgentInfo[]>(`${API_BASE}/agents`),

  runAgent: (agent_name: string, project_id: string, goal: string) =>
    fetchJSON<{ task_id: string; agent_name: string; status: string; result: any }>(
      `${API_BASE}/agents/run`,
      {
        method: "POST",
        body: JSON.stringify({ agent_name, project_id, task_goal: goal }),
      }
    ),

  // Workflows
  createWorkflow: (project_id: string, name: string, repository_url: string) =>
    fetchJSON<Workflow>(`${API_BASE}/workflows`, {
      method: "POST",
      body: JSON.stringify({ project_id, name, repository_url }),
    }),

  listWorkflows: () => fetchJSON<Workflow[]>(`${API_BASE}/workflows`),

  listTasks: (workflow_id?: string) =>
    fetchJSON<Task[]>(
      workflow_id ? `${API_BASE}/tasks?workflow_id=${workflow_id}` : `${API_BASE}/tasks`
    ),

  // Approvals
  listApprovals: (status?: string) =>
    fetchJSON<Approval[]>(
      status ? `${API_BASE}/approvals?status=${status}` : `${API_BASE}/approvals`
    ),

  approveAction: (id: string) =>
    fetchJSON<Approval>(`${API_BASE}/approvals/${id}/approve`, { method: "POST" }),

  rejectAction: (id: string) =>
    fetchJSON<Approval>(`${API_BASE}/approvals/${id}/reject`, { method: "POST" }),

  // Codebase File Explorer & Chat
  getFileTree: (repoId: string) =>
    fetchJSON<FileTreeNode[]>(`${API_BASE}/repositories/${repoId}/file-tree`),

  getFileContent: (repoId: string, path: string) =>
    fetchJSON<FileContentResponse>(
      `${API_BASE}/repositories/${repoId}/file-content?path=${encodeURIComponent(path)}`
    ),

  chatWithCodebase: (repoId: string, message: string, history: any[] = []) =>
    fetchJSON<ChatResponse>(`${API_BASE}/repositories/${repoId}/chat`, {
      method: "POST",
      body: JSON.stringify({ message, history }),
    }),

  // Terminal
  executeTerminalCommand: (repository_id: string, command: string) =>
    fetchJSON<{ command: string; exit_code: number; stdout: string; stderr: string; timed_out: boolean }>(
      `${API_BASE}/terminal/execute`,
      {
        method: "POST",
        body: JSON.stringify({ repository_id, command }),
      }
    ),
};
