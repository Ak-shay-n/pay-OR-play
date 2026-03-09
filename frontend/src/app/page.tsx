"use client";

import { useCallback } from "react";
import { useSocket } from "@/hooks/useSocket";
import HeaderBar from "@/components/HeaderBar";
import TargetSystemsPanel from "@/components/TargetSystemsPanel";
import AttackTimeline from "@/components/AttackTimeline";
import EventLog from "@/components/EventLog";
import CommandConsole from "@/components/CommandConsole";
import AlertsPanel from "@/components/AlertsPanel";
import MonitoringPanel from "@/components/MonitoringPanel";

export default function Dashboard() {
  const {
    connected,
    events,
    alerts,
    sessions,
    activeSession,
    setActiveSession,
    monitoring,
    consoleOutput,
    isRunning,
    sendCommand,
    createSession,
    runStage,
    clearEvents,
    clearAlerts,
  } = useSocket();

  const handleRunStage = useCallback(
    (stage: string) => {
      if (!activeSession) return;
      runStage(activeSession.id, stage);
    },
    [activeSession, runStage]
  );

  return (
    <div className="scanline-overlay flex flex-col h-screen bg-[#0a0e17] overflow-hidden">
      {/* ── Top bar ──────────────────────────────────────── */}
      <HeaderBar
        connected={connected}
        sessionId={activeSession?.id ?? null}
        eventCount={events.length}
        alertCount={alerts.length}
      />

      {/* ── Main grid ────────────────────────────────────── */}
      <div className="flex-1 grid grid-cols-[260px_1fr_300px] gap-2 p-2 min-h-0">

        {/* Column 1 — Targets + Timeline */}
        <div className="flex flex-col gap-2 min-h-0">
          <div className="flex-1 min-h-0">
            <TargetSystemsPanel
              sessions={sessions}
              activeSession={activeSession}
              onSelectSession={setActiveSession}
              onCreateSession={createSession}
              isRunning={isRunning}
            />
          </div>
          <div className="flex-1 min-h-0">
            <AttackTimeline
              session={activeSession}
              onRunStage={handleRunStage}
              isRunning={isRunning}
            />
          </div>
        </div>

        {/* Column 2 — Event Log + Console */}
        <div className="flex flex-col gap-2 min-h-0">
          <div className="flex-[2] min-h-0">
            <EventLog events={events} onClear={clearEvents} />
          </div>
          <div className="flex-1 min-h-0" style={{ maxHeight: "240px" }}>
            <CommandConsole
              output={consoleOutput}
              onCommand={sendCommand}
              connected={connected}
              sessionId={activeSession?.id ?? null}
            />
          </div>
        </div>

        {/* Column 3 — Alerts + Monitoring */}
        <div className="flex flex-col gap-2 min-h-0">
          <div className="flex-1 min-h-0">
            <AlertsPanel alerts={alerts} onClear={clearAlerts} />
          </div>
          <div className="flex-1 min-h-0">
            <MonitoringPanel data={monitoring} />
          </div>
        </div>
      </div>

      {/* ── Status footer ────────────────────────────────── */}
      <footer className="flex items-center justify-between px-5 py-1.5 border-t border-[#1e3a5f] bg-[#0d1117] text-[10px] text-[#4a5568] flex-shrink-0">
        <span>PAY OR PLAY © Defensive Research Platform — Educational Use Only</span>
        <div className="flex items-center gap-4">
          {isRunning && (
            <span className="text-[#f97316] alert-pulse">
              ⚡ SIMULATION ACTIVE
            </span>
          )}
          <span>
            {connected ? (
              <span className="text-[#22c55e]">● CONNECTED</span>
            ) : (
              <span className="text-[#ef4444]">● DISCONNECTED</span>
            )}
          </span>
          <span>EVENTS: {events.length}</span>
          <span className={alerts.length > 0 ? "text-[#ef4444]" : ""}>
            ALERTS: {alerts.length}
          </span>
        </div>
      </footer>
    </div>
  );
}
