"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import type { SimEvent, DetectionAlert, Session, MonitoringData } from "@/types";

const SERVER_URL = "http://localhost:5000";

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);

  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<SimEvent[]>([]);
  const [alerts, setAlerts] = useState<DetectionAlert[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [monitoring, setMonitoring] = useState<MonitoringData | null>(null);
  const [consoleOutput, setConsoleOutput] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const addConsole = useCallback((line: string) => {
    setConsoleOutput((prev) => [...prev.slice(-499), line]);
  }, []);

  // Fetch all sessions via REST and merge into state
  const fetchSessions = useCallback(async () => {
    try {
      const res = await fetch(`${SERVER_URL}/api/sessions`);
      const data: { sessions: Session[] } = await res.json();
      setSessions((prev) => {
        const merged = [...prev];
        for (const s of data.sessions) {
          if (!merged.some((m) => m.id === s.id)) merged.push(s);
        }
        return merged;
      });
    } catch { /* ignore on startup */ }
  }, []);

  useEffect(() => {
    const socket = io(SERVER_URL, {
      transports: ["polling", "websocket"],
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
    });
    socketRef.current = socket;

    socket.on("connect", () => {
      setConnected(true);
      addConsole("[ CONNECTED ] Socket established → " + SERVER_URL);
      fetchSessions();
    });

    socket.on("disconnect", () => {
      setConnected(false);
      addConsole("[ DISCONNECTED ] Socket closed");
      setIsRunning(false);
    });

    socket.on("event", (data: SimEvent) => {
      setEvents((prev) => [...prev.slice(-999), data]);
    });

    socket.on("alert", (data: DetectionAlert) => {
      setAlerts((prev) => [...prev.slice(-199), data]);
    });

    socket.on("monitoring_update", (data: MonitoringData) => {
      setMonitoring(data);
    });

    // Backend emits session object directly (not wrapped in {session: ...})
    socket.on("session_created", (data: Session) => {
      setSessions((prev) =>
        prev.some((s) => s.id === data.id) ? prev : [...prev, data]
      );
      setActiveSession(data);
      addConsole(`[ SESSION ] Created → ${data.id}`);
      addConsole(`[ TARGET  ] ${data.target.hostname} (${data.target.ip}) | ${data.target.os}`);
    });

    socket.on("stage_started", (data: { stage: string; session_id: string }) => {
      setIsRunning(true);
      addConsole(`[ STAGE   ] Starting: ${data.stage}`);
      setSessions((prev) =>
        prev.map((s) =>
          s.id === data.session_id ? { ...s, current_stage: data.stage, status: "running" } : s
        )
      );
      setActiveSession((prev) =>
        prev?.id === data.session_id
          ? { ...prev, current_stage: data.stage, status: "running" }
          : prev
      );
    });

    // stage_complete: backend sends {session_id, stage} only
    socket.on(
      "stage_complete",
      (data: { stage: string; session_id: string }) => {
        setIsRunning(false);
        addConsole(`[ DONE    ] ${data.stage} completed`);
        setSessions((prev) =>
          prev.map((s) =>
            s.id === data.session_id
              ? {
                  ...s,
                  current_stage: null,
                  status: "active",
                  completed_stages: s.completed_stages.includes(data.stage)
                    ? s.completed_stages
                    : [...s.completed_stages, data.stage],
                }
              : s
          )
        );
        setActiveSession((prev) =>
          prev?.id === data.session_id
            ? {
                ...prev,
                current_stage: null,
                status: "active",
                completed_stages: prev.completed_stages.includes(data.stage)
                  ? prev.completed_stages
                  : [...prev.completed_stages, data.stage],
              }
            : prev
        );
      }
    );

    socket.on("sessions_list", (data: { sessions: Session[] }) => {
      setSessions((prev) => {
        const merged = [...prev];
        for (const s of data.sessions) {
          if (!merged.some((m) => m.id === s.id)) merged.push(s);
        }
        return merged;
      });
    });

    // help: backend sends {commands: string[]} — one line per entry
    socket.on("help", (data: { commands: string[] }) => {
      data.commands.forEach((line) => addConsole(line));
    });

    socket.on("error", (data: { message: string }) => {
      addConsole(`[ ERROR   ] ${data.message}`);
      setIsRunning(false);
    });

    socket.on("clear", () => {
      setConsoleOutput([]);
    });

    // status: backend emits the full session object directly
    socket.on("status", (data: Session) => {
      if (data?.id) {
        addConsole(`[ STATUS  ] ${data.id} | stage: ${data.current_stage ?? "none"} | ${data.status}`);
        setActiveSession((prev) => (prev?.id === data.id ? data : prev));
        setSessions((prev) => prev.map((s) => (s.id === data.id ? data : s)));
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [addConsole, fetchSessions]);

  /* ── REST helpers ─────────────────────────────────── */

  const createSession = useCallback(async (): Promise<Session | null> => {
    try {
      // POST /api/sessions — backend returns session object directly (201)
      const res = await fetch(`${SERVER_URL}/api/sessions`, { method: "POST" });
      const session: Session = await res.json();
      setSessions((prev) =>
        prev.some((s) => s.id === session.id) ? prev : [...prev, session]
      );
      setActiveSession(session);
      addConsole(`[ SESSION ] Created → ${session.id}`);
      addConsole(`[ TARGET  ] ${session.target.hostname} (${session.target.ip}) | ${session.target.os}`);
      return session;
    } catch (e) {
      addConsole(`[ ERROR   ] Failed to create session: ${String(e)}`);
      return null;
    }
  }, [addConsole]);

  const fetchSession = useCallback(
    async (sessionId: string): Promise<Session | null> => {
      try {
        // GET /api/sessions/<id> — backend returns session object directly
        const res = await fetch(`${SERVER_URL}/api/sessions/${sessionId}`);
        const session: Session = await res.json();
        setActiveSession(session);
        setSessions((prev) =>
          prev.map((s) => (s.id === session.id ? session : s))
        );
        return session;
      } catch {
        return null;
      }
    },
    []
  );

  const runStage = useCallback(
    async (sessionId: string, stage: string): Promise<unknown> => {
      try {
        setIsRunning(true);
        addConsole(`[ STAGE   ] Starting: ${stage}`);
        // POST /api/sessions/<id>/run/<stage> — no body needed
        const res = await fetch(`${SERVER_URL}/api/sessions/${sessionId}/run/${stage}`, {
          method: "POST",
        });
        return await res.json();
      } catch (e) {
        addConsole(`[ ERROR   ] Failed to run stage: ${String(e)}`);
        setIsRunning(false);
        return null;
      }
    },
    [addConsole]
  );

  const restoreSandbox = useCallback(async (sessionId?: string): Promise<void> => {
    const id = sessionId ?? activeSession?.id;
    if (!id) { addConsole("[ ERROR   ] No active session to restore."); return; }
    try {
      // POST /api/sessions/<id>/restore
      const res = await fetch(`${SERVER_URL}/api/sessions/${id}/restore`, { method: "POST" });
      const data: { status?: string } = await res.json();
      addConsole(`[ RESTORE ] ${data.status ?? "Sandbox restored"}`);
    } catch (e) {
      addConsole(`[ ERROR   ] Restore failed: ${String(e)}`);
    }
  }, [addConsole, activeSession]);

  const clearEvents = useCallback(() => setEvents([]), []);
  const clearAlerts = useCallback(() => setAlerts([]), []);

  /* ── Socket command sender ───────────────────────── */
  const sendCommand = useCallback(
    (cmd: string) => {
      if (!socketRef.current || !connected) {
        addConsole("[ ERROR   ] Not connected");
        return;
      }
      addConsole(`> ${cmd}`);
      const [verb, ...args] = cmd.trim().split(/\s+/);

      switch (verb.toLowerCase()) {
        case "create":
          createSession();
          break;
        case "run": {
          const [stage, sessId] = args;
          if (!stage) { addConsole("Usage: run <stage> [session_id]"); return; }
          const sid = sessId ?? activeSession?.id;
          if (!sid) { addConsole("[ ERROR   ] No active session. Run 'create' first."); return; }
          if (stage === "restore_sandbox" || stage === "restore") {
            restoreSandbox(sid);
          } else {
            runStage(sid, stage);
          }
          break;
        }
        case "status":
          socketRef.current.emit("run_command", {
            command: "status",
            session_id: args[0] ?? activeSession?.id,
          });
          break;
        case "restore":
          restoreSandbox(activeSession?.id);
          break;
        case "clear":
          setConsoleOutput([]);
          break;
        case "help":
          socketRef.current.emit("run_command", { command: "help" });
          break;
        case "sessions":
          socketRef.current.emit("run_command", {
            command: "sessions",
            session_id: activeSession?.id,
          });
          break;
        case "use":
          if (args[0]) {
            const s = sessions.find((x) => x.id.startsWith(args[0]));
            if (s) {
              setActiveSession(s);
              addConsole(`[ SESSION ] Active → ${s.id}`);
            } else {
              addConsole(`[ ERROR   ] Session not found: ${args[0]}`);
            }
          }
          break;
        default:
          // Pass through as a raw run_command
          socketRef.current.emit("run_command", {
            command: cmd,
            session_id: activeSession?.id,
          });
      }
    },
    [connected, activeSession, sessions, addConsole, createSession, runStage, restoreSandbox]
  );

  return {
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
    fetchSession,
    runStage,
    restoreSandbox,
    clearEvents,
    clearAlerts,
  };
}
