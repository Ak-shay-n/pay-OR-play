"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import type { SimEvent, DetectionAlert, Session, MonitoringData } from "@/types";

const SERVER_URL = "http://localhost:5000";

interface CommandResult {
  status: string;
  message?: string;
  [key: string]: unknown;
}

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
      socket.emit("get_sessions");
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

    socket.on("session_created", (data: { session: Session }) => {
      const session = data.session;
      setSessions((prev) =>
        prev.some((s) => s.id === session.id) ? prev : [...prev, session]
      );
      setActiveSession(session);
      addConsole(`[ SESSION ] Created → ${session.id}`);
      addConsole(`[ TARGET  ] ${session.target.hostname} (${session.target.ip}) | ${session.target.os}`);
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

    socket.on(
      "stage_complete",
      (data: { stage: string; session_id: string; status: string; summary?: string }) => {
        setIsRunning(false);
        addConsole(
          `[ DONE    ] ${data.stage} → ${data.status}${data.summary ? " | " + data.summary : ""}`
        );
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

    socket.on("help", (data: { commands: string }) => {
      addConsole(data.commands);
    });

    socket.on("error", (data: { message: string }) => {
      addConsole(`[ ERROR   ] ${data.message}`);
      setIsRunning(false);
    });

    socket.on("clear", () => {
      setConsoleOutput([]);
    });

    socket.on("status", (data: { status: string; session_id?: string; current_stage?: string }) => {
      addConsole(`[ STATUS  ] ${data.status}${data.current_stage ? " | stage: " + data.current_stage : ""}`);
    });

    return () => {
      socket.disconnect();
    };
  }, [addConsole]);

  /* ── REST helpers ─────────────────────────────────── */

  const createSession = useCallback(async (): Promise<Session | null> => {
    try {
      const res = await fetch(`${SERVER_URL}/api/session/create`, { method: "POST" });
      const data: { session: Session } = await res.json();
      const session = data.session;
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
        const res = await fetch(`${SERVER_URL}/api/session/${sessionId}`);
        const data: { session: Session } = await res.json();
        setActiveSession(data.session);
        setSessions((prev) =>
          prev.map((s) => (s.id === data.session.id ? data.session : s))
        );
        return data.session;
      } catch {
        return null;
      }
    },
    []
  );

  const runStage = useCallback(
    async (sessionId: string, stage: string): Promise<CommandResult | null> => {
      try {
        const res = await fetch(`${SERVER_URL}/api/simulate/${stage}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        });
        return await res.json();
      } catch (e) {
        addConsole(`[ ERROR   ] Failed to run stage: ${String(e)}`);
        return null;
      }
    },
    [addConsole]
  );

  const restoreSandbox = useCallback(async (): Promise<void> => {
    try {
      const res = await fetch(`${SERVER_URL}/api/session/restore`, { method: "POST" });
      const data: CommandResult = await res.json();
      addConsole(`[ RESTORE ] ${data.message ?? "Sandbox restored"}`);
    } catch (e) {
      addConsole(`[ ERROR   ] Restore failed: ${String(e)}`);
    }
  }, [addConsole]);

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
          socketRef.current.emit("create_session");
          break;
        case "run": {
          const [stage, sessId] = args;
          if (!stage) { addConsole("Usage: run <stage> [session_id]"); return; }
          socketRef.current.emit("run_stage", {
            stage,
            session_id: sessId ?? activeSession?.id,
          });
          break;
        }
        case "status":
          socketRef.current.emit("get_status", { session_id: args[0] ?? activeSession?.id });
          break;
        case "restore":
          restoreSandbox();
          break;
        case "clear":
          setConsoleOutput([]);
          break;
        case "help":
          socketRef.current.emit("help");
          break;
        case "sessions":
          socketRef.current.emit("get_sessions");
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
          socketRef.current.emit("command", { command: cmd });
      }
    },
    [connected, activeSession, sessions, addConsole, restoreSandbox]
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
