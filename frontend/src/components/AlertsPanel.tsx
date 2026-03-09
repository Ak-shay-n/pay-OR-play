"use client";

import type { DetectionAlert } from "@/types";
import { useEffect, useRef } from "react";

interface AlertsPanelProps {
  alerts: DetectionAlert[];
  onClear: () => void;
}

const SEV_COLORS: Record<string, string> = {
  LOW:      "text-[#22c55e] border-[#22c55e20]",
  MEDIUM:   "text-[#eab308] border-[#eab30820]",
  HIGH:     "text-[#f97316] border-[#f9731620]",
  CRITICAL: "text-[#ef4444] border-[#ef444420]",
};

const SEV_BG: Record<string, string> = {
  LOW:      "bg-[#22c55e08]",
  MEDIUM:   "bg-[#eab30808]",
  HIGH:     "bg-[#f9731608]",
  CRITICAL: "bg-[#ef444408]",
};

export default function AlertsPanel({ alerts, onClear }: AlertsPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [alerts.length]);

  const critCount = alerts.filter((a) => a.severity === "CRITICAL").length;
  const highCount = alerts.filter((a) => a.severity === "HIGH").length;

  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header">
        <span className="text-[#ef4444]">🚨</span>
        Detection Alerts
        <span className="ml-1 text-[#4a5568]">({alerts.length})</span>
        {critCount > 0 && (
          <span className="text-[#ef4444] text-[10px] alert-pulse ml-1">
            {critCount} CRITICAL
          </span>
        )}
        {highCount > 0 && (
          <span className="text-[#f97316] text-[10px] ml-1">
            {highCount} HIGH
          </span>
        )}
        <button
          onClick={onClear}
          className="ml-auto text-[10px] text-[#4a5568] hover:text-[#e0e6ed] transition-colors px-1"
        >
          CLEAR
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-[#4a5568] gap-1">
            <span className="text-xl">✅</span>
            <span className="text-[10px]">No alerts triggered</span>
          </div>
        ) : (
          alerts.map((alert, i) => (
            <div
              key={i}
              className={`rounded border px-3 py-2.5 text-[11px] log-entry ${
                SEV_COLORS[alert.severity] ?? "text-[#8892a4] border-[#1e3a5f]"
              } ${SEV_BG[alert.severity] ?? ""}`}
            >
              {/* Title row */}
              <div className="flex items-start justify-between gap-2 mb-1">
                <span className="font-semibold wrap-break-word flex-1">
                  {alert.name}
                </span>
                <span className="shrink-0 text-[10px] uppercase tracking-widest">
                  {alert.severity}
                </span>
              </div>

              {/* Description */}
              <p className="text-[#8892a4] wrap-break-word mb-1">
                {alert.description}
              </p>

              {/* Recommendation */}
              {alert.recommendation && (
                <p className="text-[#4a5568] italic wrap-break-word">
                  → {alert.recommendation}
                </p>
              )}

              {/* Timestamp + rule_id */}
              <div className="flex justify-between text-[10px] text-[#4a5568] mt-1">
                <span>{alert.rule_id}</span>
                <span>
                  {new Date(alert.timestamp).toLocaleTimeString("en-US", {
                    hour12: false,
                  })}
                </span>
              </div>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
