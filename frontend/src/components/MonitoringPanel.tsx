"use client";

import type { MonitoringData } from "@/types";

interface MonitoringPanelProps {
  data: MonitoringData | null;
}

interface Metric {
  label: string;
  value: number | undefined;
  max: number;
  unit: string;
  dangerThreshold: number;
  warnThreshold: number;
}

function MetricBar({ label, value, max, unit, dangerThreshold, warnThreshold }: Metric) {
  const pct = value !== undefined ? Math.min((value / max) * 100, 100) : 0;
  const color =
    value === undefined
      ? "#1e3a5f"
      : value >= dangerThreshold
      ? "#ef4444"
      : value >= warnThreshold
      ? "#eab308"
      : "#22c55e";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[11px]">
        <span className="text-[#8892a4]">{label}</span>
        <span style={{ color }}>
          {value !== undefined ? `${value.toFixed(1)}${unit}` : "—"}
        </span>
      </div>
      <div className="stage-bar">
        <div
          className="h-full rounded-sm transition-all duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}

export default function MonitoringPanel({ data }: MonitoringPanelProps) {
  const metrics: Metric[] = [
    {
      label: "CPU Usage",
      value: data?.cpu_usage,
      max: 100,
      unit: "%",
      dangerThreshold: 85,
      warnThreshold: 60,
    },
    {
      label: "Memory Usage",
      value: data?.memory_usage,
      max: 100,
      unit: "%",
      dangerThreshold: 90,
      warnThreshold: 70,
    },
    {
      label: "Disk Write Rate",
      value: data?.disk_write_rate,
      max: 500,
      unit: " MB/s",
      dangerThreshold: 300,
      warnThreshold: 100,
    },
    {
      label: "Network Connections",
      value: data?.network_connections,
      max: 200,
      unit: "",
      dangerThreshold: 150,
      warnThreshold: 80,
    },
    {
      label: "Registry Changes",
      value: data?.registry_changes,
      max: 100,
      unit: "",
      dangerThreshold: 50,
      warnThreshold: 20,
    },
    {
      label: "File Operations",
      value: data?.file_operations,
      max: 1000,
      unit: "/s",
      dangerThreshold: 700,
      warnThreshold: 300,
    },
  ];

  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header">
        <span className="text-[#a855f7]">📊</span>
        System Monitoring
        {data?.timestamp && (
          <span className="ml-auto text-[#4a5568]">
            {new Date(data.timestamp).toLocaleTimeString("en-US", { hour12: false })}
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Metrics */}
        <div className="space-y-2.5">
          {metrics.map((m) => (
            <MetricBar key={m.label} {...m} />
          ))}
        </div>

        {/* Suspicious processes */}
        {data?.suspicious_processes && data.suspicious_processes.length > 0 && (
          <div className="mt-3">
            <div className="text-[11px] text-[#ef4444] uppercase tracking-widest mb-1.5">
              ⚠ Suspicious Processes
            </div>
            <div className="space-y-1">
              {data.suspicious_processes.map((proc, i) => (
                <div
                  key={i}
                  className="text-[11px] text-[#f97316] bg-[#f9731608] border border-[#f9731620] rounded px-2 py-1 wrap-break-word"
                >
                  {proc}
                </div>
              ))}
            </div>
          </div>
        )}

        {!data && (
          <div className="flex items-center justify-center h-20 text-[#4a5568] text-[11px]">
            Waiting for telemetry…
          </div>
        )}
      </div>
    </div>
  );
}
