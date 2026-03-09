export interface SimEvent {
  timestamp: string;
  stage: string;
  level: "INFO" | "WARNING" | "ALERT" | "ERROR" | "SIMULATION";
  message: string;
  details: Record<string, unknown>;
  session_id?: string;
}

export interface DetectionAlert {
  timestamp: string;
  rule_id: string;
  name: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  description: string;
  triggering_event?: string;
  recommendation?: string;
}

export interface Session {
  id: string;
  created: string;
  status: "active" | "running" | "completed";
  current_stage: string | null;
  completed_stages: string[];
  target: {
    ip: string;
    hostname: string;
    user: string;
    os: string;
  };
  discovery_data?: unknown;
}

export interface MonitoringData {
  cpu_usage?: number;
  memory_usage?: number;
  disk_write_rate?: number;
  network_connections?: number;
  registry_changes?: number;
  file_operations?: number;
  suspicious_processes?: string[];
  timestamp?: string;
}

export const ATTACK_STAGES = [
  { id: "initial_access",       label: "Initial Access",       icon: "🎣", color: "#3b82f6" },
  { id: "persistence",          label: "Persistence",          icon: "🔗", color: "#8b5cf6" },
  { id: "discovery",            label: "Discovery",            icon: "🔍", color: "#06b6d4" },
  { id: "credentials",          label: "Credentials",          icon: "🔑", color: "#f59e0b" },
  { id: "privilege_escalation", label: "Privilege Escalation", icon: "⬆",  color: "#ef4444" },
  { id: "lateral_movement",     label: "Lateral Movement",     icon: "↔",  color: "#ec4899" },
  { id: "evasion",              label: "Evasion",              icon: "👻", color: "#6366f1" },
  { id: "exfiltration",         label: "Exfiltration",         icon: "📤", color: "#f97316" },
  { id: "ransomware",           label: "Ransomware",           icon: "💀", color: "#dc2626" },
] as const;

export type StageId = typeof ATTACK_STAGES[number]["id"];
