export interface Repository {
  id: string;
  project_id: string;
  url: string;
  owner: string;
  name: string;
  default_branch: string;
  current_sha?: string;
  is_private: boolean;
  clone_path?: string;
  indexed_at?: string;
  created_at: string;
}

export interface ArchitectureAnalysis {
  repository_id: string;
  languages: Record<string, number>;
  frameworks: string[];
  entry_points: string[];
  modules_count: number;
  circular_dependencies: string[][];
  dependencies_graph: Record<string, string[]>;
  api_routes: Array<{ method: string; path: string; file: string }>;
  summary: string;
}

export interface SecurityFinding {
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  type: string;
  file_path: string;
  line_number: number;
  description: string;
  snippet: string;
  recommendation: string;
}

export interface SecurityAnalysis {
  repository_id: string;
  findings_count: number;
  findings: SecurityFinding[];
  scan_duration_ms: number;
}

export interface AgentInfo {
  name: string;
  role: string;
  description: string;
  allowed_tools: string[];
  token_budget: number;
  timeout_seconds: number;
}

export interface Workflow {
  id: string;
  project_id: string;
  name: string;
  status: "PENDING" | "RUNNING" | "WAITING_FOR_APPROVAL" | "COMPLETED" | "FAILED" | "CANCELLED";
  created_at: string;
  updated_at: string;
  plan_dag?: Record<string, any>;
}

export interface Task {
  id: string;
  workflow_id: string;
  agent_name: string;
  status: "PENDING" | "QUEUED" | "RUNNING" | "WAITING_FOR_APPROVAL" | "COMPLETED" | "FAILED" | "RETRY_PENDING";
  input_payload?: Record<string, any>;
  output_payload?: Record<string, any>;
  error_message?: string;
  token_usage: number;
  execution_time_ms: number;
  created_at: string;
  updated_at: string;
}

export interface Approval {
  id: string;
  task_id: string;
  action_type: string;
  target_resource: string;
  diff_payload?: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  decided_by?: string;
  decided_at?: string;
  created_at: string;
}
