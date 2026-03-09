"use client";

import type { SimEvent } from "@/types";
import { useEffect, useRef } from "react";

interface EventLogProps {
  events: SimEvent[];
  onClear: () => void;
}

const LEVEL_COLORS: Record<string, string> = {
  INFO:       "text-[#8892a4]",
  WARNING:    "text-[#eab308]",
  ALERT:      "text-[#ef4444]",
  ERROR:      "text-[#ef4444]",
  SIMULATION: "text-[#06b6d4]",
};

const LEVEL_BG: Record<string, string> = {
  ALERT: "bg-[#ef444408]",
  ERROR: "bg-[#ef444408]",
};

export default function EventLog({ events, onClear }: EventLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header">
        <span className="text-[#06b6d4]">📋</span>
        Event Log
        <span className="ml-1 text-[#4a5568]">({events.length})</span>
        <button
          onClick={onClear}
          className="ml-auto text-[10px] text-[#4a5568] hover:text-[#e0e6ed] transition-colors px-1"
        >
          CLEAR
        </button>
      </div>

      <div className="flex-1 overflow-y-auto font-mono text-[11px] leading-relaxed">
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-full text-[#4a5568]">
            Waiting for events…
          </div>
        ) : (
          events.map((ev, i) => (
            <div
              key={i}
              className={`log-entry flex gap-2 px-3 py-1 border-b border-[#0d1117] ${
                LEVEL_BG[ev.level] ?? ""
              }`}
            >
              {/* Timestamp */}
              <span className="text-[#4a5568] shrink-0 w-[72px]">
                {new Date(ev.timestamp).toLocaleTimeString("en-US", { hour12: false })}
              </span>

              {/* Level */}
              <span
                className={`shrink-0 w-14 ${LEVEL_COLORS[ev.level] ?? "text-[#8892a4]"}`}
              >
                {ev.level}
              </span>

              {/* Stage */}
              <span className="text-[#4a5568] shrink-0 w-[88px] truncate">
                [{ev.stage}]
              </span>

              {/* Message */}
              <span className="text-[#e0e6ed] wrap-break-word flex-1">
                {ev.message}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
