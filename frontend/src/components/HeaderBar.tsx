"use client";

import { useEffect, useState } from "react";

interface HeaderBarProps {
  connected: boolean;
  sessionId: string | null;
  eventCount: number;
  alertCount: number;
}

export default function HeaderBar({
  connected,
  sessionId,
  eventCount,
  alertCount,
}: HeaderBarProps) {
  const [now, setNow] = useState("--:--:--");

  useEffect(() => {
    const fmt = () =>
      new Date().toLocaleTimeString("en-US", { hour12: false });
    setNow(fmt());
    const id = setInterval(() => setNow(fmt()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="flex items-center justify-between px-5 py-2.5 border-b border-[#1e3a5f] bg-[#0d1117] flex-shrink-0">
      {/* Left — brand */}
      <div className="flex items-center gap-3">
        <span className="text-[#ef4444] text-lg font-bold tracking-tight">
          💀 PAY OR PLAY
        </span>
        <span className="text-[#4a5568] text-[11px]">
          Ransomware Simulation Platform v1.0
        </span>
      </div>

      {/* Centre — session */}
      <div className="flex items-center gap-4 text-[11px]">
        <span className="text-[#4a5568]">SESSION:</span>
        <span className={sessionId ? "text-[#06b6d4]" : "text-[#4a5568]"}>
          {sessionId ? sessionId.slice(0, 16) + "…" : "—"}
        </span>
      </div>

      {/* Right — counters + status */}
      <div className="flex items-center gap-5 text-[11px]">
        <span className="text-[#4a5568]">
          EVENTS:{" "}
          <span className="text-[#e0e6ed]">{eventCount}</span>
        </span>
        <span className="text-[#4a5568]">
          ALERTS:{" "}
          <span className={alertCount > 0 ? "text-[#ef4444]" : "text-[#e0e6ed]"}>
            {alertCount}
          </span>
        </span>
        <div className="flex items-center gap-1">
          <span
            className={`w-2 h-2 rounded-full ${
              connected ? "bg-[#22c55e] alert-pulse" : "bg-[#4a5568]"
            }`}
          />
          <span className={connected ? "text-[#22c55e]" : "text-[#4a5568]"}>
            {connected ? "LIVE" : "OFFLINE"}
          </span>
        </div>
        <span className="text-[#4a5568]">{now}</span>
      </div>
    </header>
  );
}
