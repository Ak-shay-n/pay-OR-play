"use client";

import { ATTACK_STAGES } from "@/types";
import type { Session } from "@/types";

interface AttackTimelineProps {
  session: Session | null;
  onRunStage: (stage: string) => void;
  isRunning: boolean;
}

export default function AttackTimeline({
  session,
  onRunStage,
  isRunning,
}: AttackTimelineProps) {
  const completed = new Set(session?.completed_stages ?? []);
  const current = session?.current_stage;

  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header">
        <span className="text-[#f97316]">⚡</span>
        Attack Timeline
        {isRunning && (
          <span className="ml-auto flex items-center gap-1 text-[#f97316] alert-pulse">
            <span className="typing-dot">●</span>
            <span className="typing-dot">●</span>
            <span className="typing-dot">●</span>
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {ATTACK_STAGES.map((stage, idx) => {
          const done = completed.has(stage.id);
          const running = current === stage.id;

          return (
            <div
              key={stage.id}
              className={`flex items-center gap-2 px-3 py-2 rounded border transition-all ${
                running
                  ? "border-[#f97316] bg-[#f9731610]"
                  : done
                  ? "border-[#1e3a5f] bg-[#0d1117]"
                  : "border-[#1e3a5f] bg-transparent hover:bg-[#0d1117]"
              }`}
            >
              {/* Index */}
              <span className="text-[#4a5568] text-[11px] w-5 shrink-0">
                {String(idx + 1).padStart(2, "0")}
              </span>

              {/* Icon */}
              <span className="text-lg leading-none">{stage.icon}</span>

              {/* Label */}
              <span
                className={`flex-1 text-[12px] ${
                  running
                    ? "text-[#f97316]"
                    : done
                    ? "text-[#22c55e]"
                    : "text-[#8892a4]"
                }`}
              >
                {stage.label}
              </span>

              {/* Status badge / run button */}
              {running ? (
                <span className="text-[10px] text-[#f97316] alert-pulse uppercase tracking-widest">
                  RUNNING
                </span>
              ) : done ? (
                <span className="text-[10px] text-[#22c55e] uppercase tracking-widest">
                  DONE
                </span>
              ) : (
                <button
                  disabled={!session || isRunning}
                  onClick={() => onRunStage(stage.id)}
                  className="text-[10px] px-2.5 py-0.5 rounded border border-[#1e3a5f] text-[#4a5568] hover:border-[#3b82f6] hover:text-[#3b82f6] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  RUN
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Progress bar */}
      <div className="px-3 py-2 border-t border-[#1e3a5f] flex-shrink-0">
        <div className="flex justify-between text-[10px] text-[#4a5568] mb-1">
          <span>PROGRESS</span>
          <span>
            {completed.size} / {ATTACK_STAGES.length}
          </span>
        </div>
        <div className="stage-bar">
          <div
            className="stage-bar-fill"
            style={{
              width: `${(completed.size / ATTACK_STAGES.length) * 100}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
}
