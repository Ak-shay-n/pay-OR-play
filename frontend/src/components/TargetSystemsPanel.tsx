"use client";

import type { Session } from "@/types";

interface TargetSystemsPanelProps {
  sessions: Session[];
  activeSession: Session | null;
  onSelectSession: (session: Session) => void;
  onCreateSession: () => void;
  isRunning: boolean;
}

export default function TargetSystemsPanel({
  sessions,
  activeSession,
  onSelectSession,
  onCreateSession,
  isRunning,
}: TargetSystemsPanelProps) {
  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header">
        <span className="text-[#22c55e]">🖥</span>
        Target Systems
        <span className="ml-1 text-[#4a5568]">({sessions.length})</span>
        <button
          onClick={onCreateSession}
          disabled={isRunning}
          className="ml-auto text-[10px] px-2.5 py-1 rounded border border-[#1e3a5f] text-[#22c55e] hover:border-[#22c55e] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          + NEW
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2 text-[#4a5568]">
            <span className="text-2xl">🖥</span>
            <span className="text-[10px]">No active sessions</span>
            <button
              onClick={onCreateSession}
              className="text-[10px] px-3 py-1.5 rounded border border-[#1e3a5f] text-[#22c55e] hover:border-[#22c55e] transition-colors"
            >
              Create Session
            </button>
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = activeSession?.id === session.id;
            const isThisRunning = session.status === "running";

            return (
              <button
                key={session.id}
                onClick={() => onSelectSession(session)}
                className={`w-full text-left p-2 rounded border transition-all ${
                  isActive
                    ? "border-[#22c55e] bg-[#22c55e10]"
                    : "border-[#1e3a5f] hover:border-[#2d5a8e] bg-transparent"
                }`}
              >
                {/* Header row */}
                <div className="flex items-center justify-between mb-1">
                  <span
                    className={`text-[11px] font-semibold ${
                      isActive ? "text-[#22c55e]" : "text-[#8892a4]"
                    }`}
                  >
                    {session.target.hostname}
                  </span>
                  <span
                    className={`text-[10px] uppercase tracking-widest ${
                      isThisRunning
                        ? "text-[#f97316] alert-pulse"
                        : session.status === "completed"
                        ? "text-[#22c55e]"
                        : "text-[#4a5568]"
                    }`}
                  >
                    {session.status}
                  </span>
                </div>

                {/* IP + OS */}
                <div className="text-[10px] text-[#4a5568] space-y-0.5">
                  <div>{session.target.ip}</div>
                  <div>{session.target.os}</div>
                  <div className="text-[#2d5a8e]">
                    {session.id.slice(0, 12)}…
                  </div>
                </div>

                {/* Completed stages mini bar */}
                {session.completed_stages.length > 0 && (
                  <div className="mt-1.5 flex gap-0.5">
                    {Array.from({ length: 9 }).map((_, i) => (
                      <div
                        key={i}
                        className={`flex-1 h-0.5 rounded-sm ${
                          i < session.completed_stages.length
                            ? "bg-[#22c55e]"
                            : "bg-[#1e3a5f]"
                        }`}
                      />
                    ))}
                  </div>
                )}
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
